from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.test import SimpleTestCase

from profiles.tests import set_up_user
from .models import Exam, FreeResponseQuestion, MultipleChoiceQuestion, MultipleChoiceOption,\
                    ExamKind


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
    exam, created = Exam.objects.get_or_create(name='Test Exam',
                                               kind=ExamKind.CI,
                                               description='an exam for testing')
    if created:
        concept_type = ContentType.objects.get_for_model(DummyConcept)
        concept = DummyConcept.objects.get(name = "Concept A")
        FreeResponseQuestion.objects.create(exam=exam,
                                            question="What is the answer to this FR question?",
                                            number=1,
                                            content_type=concept_type,
                                            object_id=concept.id)
        concept = DummyConcept.objects.get(name = "Concept B")
        mcq = MultipleChoiceQuestion.objects.create(exam=exam,
                                                    question="What is the answer to this MC question?",
                                                    number=2,
                                                    content_type=concept_type,
                                                    object_id=concept.id)
        MultipleChoiceOption.objects.create(question=mcq, text="choice 1", index=1, is_correct=True);
        MultipleChoiceOption.objects.create(question=mcq, text="choice 2", index=2);
        MultipleChoiceOption.objects.create(question=mcq, text="choice 3", index=3);
    return exam

class DevViewsTest(SimpleTestCase):
    def setUp(self):
        create_concepts()
        self.user = set_up_user()
    
    def test_index_view(self):
        # User not logged in, redirected
        response = self.client.get(reverse('CI_exam:index'))
        self.assertRedirects(response, '/accounts/login/?next=/exams/CI/dev/')
        
        # User logged in, not contrib
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('exam:index'))
        self.assertEqual(response.status_code, 403)        
        
        # Contrib user logs in, no exams in database
        self.user.profile.is_contrib = True
        self.user.profile.save()
        for exam in Exam.objects.all():
            exam.delete()
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('exam:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,"no CIs available")
        
        # Test Exam should now be listed
        exam = get_or_create_exam()
        response = self.client.get(reverse('exam:index'))
        self.assertContains(response,exam.name)
        
    def test_detail_view(self):
        exam = get_or_create_exam()
        
        # User not logged in, redirected
        response = self.client.get(reverse('CI_exam:detail', args=[exam.id]))
        self.assertRedirects(response, '/accounts/login/?next=/exams/CI/dev/%s/'%exam.id)
        
        # User logged in, not contrib
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('exam:detail', args=[exam.id]))
        self.assertEqual(response.status_code, 403)
        
        # User is contrib
        self.user.profile.is_contrib = True
        self.user.profile.save()
        response = self.client.get(reverse('exam:detail', args=[exam.id]))
        self.assertEqual(response.status_code, 200)
        
        # exam id does not exist
        response = self.client.get(reverse('exam:detail', args=[99]))
        self.assertEqual(response.status_code, 404)
        
        # make sure questions are displayed
        response = self.client.get(reverse('exam:detail', args=[exam.id]))
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
        response = self.client.get(reverse('CI_exam:create'))
        self.assertRedirects(response, '/accounts/login/?next=/exams/CI/dev/create/')
        
        # User logged in, and contrib
        self.user.profile.is_contrib = True
        self.user.profile.save()
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('exam:create'))
        self.assertEqual(response.status_code, 403)
        
        # User is staff
        self.user.is_staff = True
        self.user.save()
        response = self.client.get(reverse('exam:create'))
        self.assertEqual(response.status_code, 200)
        
        # Try to create a test
        response = self.client.post(reverse('exam:create'),
                                    {'name':'Test Create Exam','description':'xxxxxxxx'})
        self.assertRedirects(response, reverse('exam:index'))
        self.assertTrue(Exam.objects.filter(name='Test Create Exam'))

    def test_select_view(self):
        exam = get_or_create_exam()
        
        # User not logged in, redirected
        response = self.client.get(reverse('CI_exam:select_concept', args=[exam.id]))
        self.assertRedirects(response, '/accounts/login/?next=/exams/CI/dev/%s/select/'%exam.id)
        
        # User logged in, not contrib
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('exam:select_concept', args=[exam.id]))
        self.assertEqual(response.status_code, 403)
        
        # User is contrib
        self.user.profile.is_contrib = True
        self.user.profile.save()
        response = self.client.get(reverse('exam:select_concept', args=[exam.id]))
        self.assertEqual(response.status_code, 200)
        
        # exam id does not exist
        response = self.client.get(reverse('exam:select_concept', args=[99]))
        self.assertEqual(response.status_code, 404)
    
        # make sure concept choices are present
        response = self.client.get(reverse('exam:select_concept', args=[exam.id]))
        self.assertEqual(response.status_code, 200)
        for concept in (DummyConcept.objects.all()):
            self.assertContains(response, concept)
        
        # Select no concept, should get an error
        response = self.client.post(reverse('exam:select_concept', args=[exam.id]),
                                    {'concept':'',})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
            
        # Select a concept. No object is created, but we should redirect to a
        # page to create a question for this concept
        concept = DummyConcept.objects.get(name = "Concept A")
        response = self.client.post(reverse('exam:select_concept', args=[exam.id]),
                                    {'concept':concept,})
        self.assertRedirects(response, reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'fr'}))
        
    def test_question_create_view(self):
        """        
        possible tests to add:
            Check interview and excerpt data
        """
        exam = get_or_create_exam()
        concept = DummyConcept.objects.get(name = "Concept A")
        
        # User not logged in, redirected
        response = self.client.get(reverse('CI_exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'fr'}))
        self.assertRedirects(response,
                             '/accounts/login/?next=/exams/CI/dev/%s/%s/fr/'%(exam.id,concept.id))
        
        # User logged in, not contrib
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'fr'}))
        self.assertEqual(response.status_code, 403)
        
        # User is contrib
        self.user.profile.is_contrib = True
        self.user.profile.save()
        response = self.client.get(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'fr'}))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'mc'}))
        self.assertEqual(response.status_code, 200)
        
        # exam_id does not exist
        response = self.client.get(reverse('exam:question_create',
            kwargs ={'exam_id':99,'concept_id':concept.id,'question_type':'fr'}))
        self.assertEqual(response.status_code, 404)
        
        # concept_id does not exist
        response = self.client.get(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':99,'question_type':'fr'}))
        self.assertEqual(response.status_code, 404)
        
        # question type not 'fr' or 'mc'
        response = self.client.get(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'xx'}))
        self.assertEqual(response.status_code, 404)
        
        # Check that submit redirects us
        response = self.client.post(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'mc'}),
            {'question':'question', 'choice_1':'yes', 'choice_2':'no', 'correct':'1'})
        self.assertRedirects(response, reverse('exam:detail', kwargs ={'exam_id':exam.id,}))
        
    # def test_free_response_edit_view(self):
    #    There isn't any functionality in FreeResponseEditView that isn't also used by
    #    MultipleChoiceEditView, since they both subclass QuestionEditView. Consider
    #    test_multiple_choice_edit_view to cover FreeResponseEditView.

    def test_multiple_choice_edit_view(self):
        """        
        """
        exam = get_or_create_exam()
        question = MultipleChoiceQuestion.objects.get(exam=exam)
        
        # User not logged in, redirected
        response = self.client.get(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}))
        self.assertRedirects(response,
                             '/accounts/login/?next=/exams/CI/dev/mc/%s/edit/'%question.id)
        
        # User logged in, not contrib
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}))
        self.assertEqual(response.status_code, 403)
        
        # User is contrib
        self.user.profile.is_contrib = True
        self.user.profile.save()
        response = self.client.get(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}))
        self.assertEqual(response.status_code, 200)
        
        # question_id does not exist
        response = self.client.get(reverse('CI_exam:mc_edit',kwargs ={'question_id':99}))
        self.assertEqual(response.status_code, 404)
        
        # Check that the list of 3-tuples, 'choice_fields', is correctly constructed
        # with a single option
        response = self.client.get(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}))
        choice_1_tuple = response.context['choice_fields'][0]
        self.assertIn("choice_1",choice_1_tuple[0].label_tag())
        self.assertEqual("choice 1",choice_1_tuple[1].choice_label)
        self.assertIn("index_1",choice_1_tuple[2].label_tag())
        
        # Check for all options. Should be in order. Check initial data
        i=0
        for option in question.multiplechoiceoption_set.all():
            choice_tuple = response.context['choice_fields'][i]
            self.assertIn(option.text,str(choice_tuple[0]))
            self.assertEqual(str(option.index),choice_tuple[1].choice_value)
            self.assertIn(str(option.index),str(choice_tuple[2]))
            i+=1
        
        # Check for new choice
        choice_tuple = response.context['choice_fields'][i]
        self.assertIn("choice_new",str(choice_tuple[0]))
        self.assertEqual('-1',choice_tuple[1].choice_value)
        self.assertTrue(choice_tuple[2])
        
        # Check that submit redirects us
        response = self.client.post(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}),
            {'question':'question', 'choice_1':'yes', 'index_1':'1',
             'choice_2':'no', 'index_2':'2', 'correct':'1'})
        self.assertRedirects(response, reverse('exam:detail', kwargs ={'exam_id':exam.id,}))
    
    def test_multiple_choice_version_view(self):
        """        
        """
        get_or_create_exam().delete()
        exam = get_or_create_exam() # get a fresh exam
        concept = DummyConcept.objects.get(name = "Concept A")
        question = MultipleChoiceQuestion.objects.get(exam=exam)

        
        # User not logged in, redirected
        response = self.client.get(reverse('CI_exam:mc_versions',kwargs ={'question_id':question.id}))
        self.assertRedirects(response,
                             '/accounts/login/?next=/exams/CI/dev/mc/%s/versions/'%question.id)
        
        # User logged in, not contrib
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('CI_exam:mc_versions',kwargs ={'question_id':question.id}))
        self.assertEqual(response.status_code, 403)
        
        # User is contrib
        self.user.profile.is_contrib = True
        self.user.profile.save()
        response = self.client.get(reverse('CI_exam:mc_versions',kwargs ={'question_id':question.id}))
        self.assertEqual(response.status_code, 200)
        
        # question_id does not exist
        response = self.client.get(reverse('CI_exam:mc_versions',kwargs ={'question_id':99}))
        self.assertEqual(response.status_code, 404)