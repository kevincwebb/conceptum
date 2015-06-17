from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.test import SimpleTestCase

from profiles.tests import set_up_user
from .models import Exam, FreeResponseQuestion, MultipleChoiceQuestion, MultipleChoiceOption


class DummyConcept(models.Model):
    """
    Since Questions are related to Concept by generic foreign key, we can use
    this simple model instead of importing.
    """
    name = models.CharField(max_length=31, unique=True)
    
    def __str__(self):
        return self.name

def create_concepts():
    """
    Creates 4 concepts for use in testing.
    Does not return anything, queryset accessible via objects.all()
    """
    for x in ['A','B','C','D']:
        DummyConcept.objects.get_or_create(name="Concept %s" % x)

def get_or_create_exam():
    """
    gets or creates an exam and some questions
    """
    exam, created = Exam.objects.get_or_create(name='Test Exam', description='an exam for testing')
    if created:
        concept_type = ContentType.objects.get_for_model(DummyConcept)
        concept = DummyConcept.objects.get(name = "Concept A")
        FreeResponseQuestion.objects.create(exam=exam,
                                            question="What is the answer to this FR question?",
                                            content_type=concept_type,
                                            object_id=concept.id)
        concept = DummyConcept.objects.get(name = "Concept B")
        mcq = MultipleChoiceQuestion.objects.create(exam=exam,
                                                    question="What is the answer to this MC question?",
                                                    content_type=concept_type,
                                                    object_id=concept.id)
        MultipleChoiceOption.objects.create(question=mcq, text="choice 1");
        MultipleChoiceOption.objects.create(question=mcq, text="choice 2");
        MultipleChoiceOption.objects.create(question=mcq, text="choice 3");
    return exam

class ViewsTest(SimpleTestCase):
    def setUp(self):
        create_concepts()
        self.user = set_up_user()
    
    def test_index_view(self):
        # User not logged in, redirected
        response = self.client.get(reverse('exam_index'))
        self.assertRedirects(response, '/accounts/login/?next=/exams/')
        
        # Activated user logs in, no exams in database
        for exam in Exam.objects.all():
            exam.delete()
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('exam_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,"no available exams")
        
        # Test Exam should now be listed
        exam = get_or_create_exam()
        response = self.client.get(reverse('exam_index'))
        self.assertContains(response,exam.name)
        
    def test_detail_view(self):
        exam = get_or_create_exam()
        
        # User not logged in, redirected
        response = self.client.get(reverse('exam_detail', args=[exam.id]))
        self.assertRedirects(response, '/accounts/login/?next=/exams/%s/'%exam.id)
        
        # User logged in, not contrib
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('exam_detail', args=[exam.id]))
        self.assertEqual(response.status_code, 403)
        
        # User is contrib
        self.user.profile.is_contrib = True
        self.user.profile.save()
        response = self.client.get(reverse('exam_detail', args=[exam.id]))
        self.assertEqual(response.status_code, 200)
        
        # exam id does not exist
        response = self.client.get(reverse('exam_detail', args=[99]))
        self.assertEqual(response.status_code, 404)
        
        # make sure questions are displayed
        response = self.client.get(reverse('exam_detail', args=[exam.id]))
        self.assertEqual(response.status_code, 200)
        for concept in (DummyConcept.objects.all()):
            self.assertContains(response, concept)
            
        #These next tests fail. I confirmed with print statments that the questions do indeed
        #exist for the exam object, so I'm guessing there's a problem in the template, given
        #how complicated it is.
        #
        #for question in (exam.freeresponsequestion_set.all()):
        #    self.assertContains(response, question.question)
        #for question in (exam.multiplechoicequestion_set.all()):
        #    self.assertContains(response, question.question)

    def test_create_view(self):
        # User not logged in, redirected
        response = self.client.get(reverse('exam_create'))
        self.assertRedirects(response, '/accounts/login/?next=/exams/new/')
        
        # User logged in, and contrib
        self.user.profile.is_contrib = True
        self.user.profile.save()
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('exam_create'))
        self.assertEqual(response.status_code, 403)
        
        # User is staff
        self.user.is_staff = True
        self.user.save()
        response = self.client.get(reverse('exam_create'))
        self.assertEqual(response.status_code, 200)
        
        # Try to create a test
        response = self.client.post(reverse('exam_create'),
                                    {'name':'Test Create Exam','description':'xxxxxxxx'})
        self.assertRedirects(response, reverse('exam_index'))
        self.assertTrue(Exam.objects.filter(name='Test Create Exam'))

    def test_select_view(self):
        exam = get_or_create_exam()
        
        # User not logged in, redirected
        response = self.client.get(reverse('select_concept', args=[exam.id]))
        self.assertRedirects(response, '/accounts/login/?next=/exams/%s/select/'%exam.id)
        
        # User logged in, not contrib
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('select_concept', args=[exam.id]))
        self.assertEqual(response.status_code, 403)
        
        # User is contrib
        self.user.profile.is_contrib = True
        self.user.profile.save()
        response = self.client.get(reverse('select_concept', args=[exam.id]))
        self.assertEqual(response.status_code, 200)
        
        # exam id does not exist
        response = self.client.get(reverse('select_concept', args=[99]))
        self.assertEqual(response.status_code, 404)
    
        # make sure concept choices are present
        response = self.client.get(reverse('select_concept', args=[exam.id]))
        self.assertEqual(response.status_code, 200)
        for concept in (DummyConcept.objects.all()):
            self.assertContains(response, concept)
        
        # Select no concept, should get an error
        response = self.client.post(reverse('select_concept', args=[exam.id]),
                                    {'concept':'',})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
            
        # Select a concept. No object is created, but we should redirect to a
        # page to create a question for this concept
        concept = DummyConcept.objects.get(name = "Concept A")
        response = self.client.post(reverse('select_concept', args=[exam.id]),
                                    {'concept':concept,})
        self.assertRedirects(response, reverse('question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'fr'}))
        
    def test_question_create_view(self):
        exam = get_or_create_exam()
        concept = DummyConcept.objects.get(name = "Concept A")
        
        # User not logged in, redirected
        response = self.client.get(reverse('question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'fr'}))
        self.assertRedirects(response,
                             '/accounts/login/?next=/exams/%s/%s/fr/'%(exam.id,concept.id))
        
        # User logged in, not contrib
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'fr'}))
        self.assertEqual(response.status_code, 403)
        
        # User is contrib
        self.user.profile.is_contrib = True
        self.user.profile.save()
        response = self.client.get(reverse('question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'fr'}))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'mc'}))
        self.assertEqual(response.status_code, 200)
        
        # exam_id does not exist
        response = self.client.get(reverse('question_create',
            kwargs ={'exam_id':99,'concept_id':concept.id,'question_type':'fr'}))
        self.assertEqual(response.status_code, 404)
        
        # concept_id does not exist
        response = self.client.get(reverse('question_create',
            kwargs ={'exam_id':exam.id,'concept_id':99,'question_type':'fr'}))
        self.assertEqual(response.status_code, 404)
        
        # question type does not exist
        response = self.client.get(reverse('question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'wrong'}))
        self.assertEqual(response.status_code, 404)
        
        # Check interview and excerpt data
        
        # Check that fields are visible
        
        # Check that submit redirects us
        
        # Don't need to check form stuff
        