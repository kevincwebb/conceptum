from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db import models
from django.test import SimpleTestCase
from django.utils.translation import ugettext_lazy as _

from profiles.tests import set_up_user
from interviews.models import get_concept_list, DummyConcept as Concept
from .models import Exam, FreeResponseQuestion, MultipleChoiceQuestion, MultipleChoiceOption,\
                    ExamKind, QUESTION_LENGTH, REQUIRED_CHOICES
from .forms import MultipleChoiceEditForm

#class DummyConcept(models.Model):
#    """
#    Since Questions are related to Concept by generic foreign key, we can use
#    this simple model instead of importing.
#    """
#    name = models.CharField(max_length=31, unique=True)
#    
#    def __str__(self):
#        return self.name
#
#def create_concepts():
#    """
#    Creates 4 concepts for use in testing.
#    Does not return anything, queryset accessible via objects.all()
#    """
#    for x in ['A','B','C','D']:
#        DummyConcept.objects.get_or_create(name="Concept %s" % x)

def get_or_create_exam():
    """
    gets or creates an exam and some questions
    """
    exam, created = Exam.objects.get_or_create(name='Test Exam',
                                               kind=ExamKind.CI,
                                               description='an exam for testing')
    if created:
        concept_type = ContentType.objects.get_for_model(Concept)
        concept = Concept.objects.get(name = "Concept A")
        FreeResponseQuestion.objects.create(exam=exam,
                                            question="What is the answer to this FR question?",
                                            number=1,
                                            content_type=concept_type,
                                            object_id=concept.id)
        concept = Concept.objects.get(name = "Concept B")
        mcq = MultipleChoiceQuestion.objects.create(exam=exam,
                                                    question="What is the answer to this MC question?",
                                                    number=2,
                                                    content_type=concept_type,
                                                    object_id=concept.id)
        MultipleChoiceOption.objects.create(question=mcq, text="choice 1", index=1, is_correct=True);
        MultipleChoiceOption.objects.create(question=mcq, text="choice 2", index=2);
        MultipleChoiceOption.objects.create(question=mcq, text="choice 3", index=3);
    return exam

class DevFormsTest(SimpleTestCase):
    def setUp(self):
        get_concept_list()
        self.user = set_up_user()
        self.user.profile.is_contrib = True
        self.user.profile.save()
        self.client.login(email=self.user.email, password='password')
 
    def test_add_free_response_form(self):
        exam = get_or_create_exam()
        concept = Concept.objects.get(name = "Concept A")
        question_text = 'Is this a new free response question?'
        
        # Make sure new question is saved
        response = self.client.post(reverse('CI_exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'fr'}),
            {'question':question_text})
        question = FreeResponseQuestion.objects.filter(question=question_text).first()
        self.assertTrue(question)
        
        # Blank Fields
        response = self.client.post(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'fr'}),
            {})
        error = _("This field is required.")
        self.assertFormError(response, 'form', 'question', error, "" )
        
        # Question Too Long
        long_text = ''
        for x in range(QUESTION_LENGTH):
            long_text+=str(x)
        response = self.client.post(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'fr'}),
            {'question':long_text})
        error = _("Ensure this value has at most %d characters (it has %d)." %
                  (QUESTION_LENGTH, len(long_text)))
        self.assertFormError(response, 'form', 'question', error, "" )
    
    def test_add_multiple_choice_form(self):
        exam = get_or_create_exam()
        concept = DummyConcept.objects.get(name = "Concept A")
        question_text = 'Is this a new multiplce choice question?'
        
        # Make sure new question is saved
        response = self.client.post(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'mc'}),
            {'question':question_text, 'choice_1':'yes', 'choice_2':'no', 'correct':'1'})
        self.assertEqual(response.status_code, 200)
        q = MultipleChoiceQuestion.objects.filter(question=question_text).first()
        self.assertTrue(q)
        c1 = MultipleChoiceOption.objects.filter(question=q,text='yes').first()
        self.assertTrue(c1)
        self.assertTrue(c1.is_correct)
        self.assertEqual(c1.index, 1)
        c2 = MultipleChoiceOption.objects.filter(question=q,text='no').first()
        self.assertTrue(c2)
        self.assertFalse(c2.is_correct)
        self.assertEqual(c2.index, 2)
        q.delete()
        
        # Blank Fields
        response = self.client.post(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'mc'}),
            {})
        error = _("This field is required.")
        self.assertFormError(response, 'form', 'question', error, "" )
        self.assertFormError(response, 'form', 'correct', error, "")
        error = _("You must provide at least %d choice." % REQUIRED_CHOICES)
        self.assertFormError(response, 'form', None, error, "" )
        
    
        # Question Too Long
        long_text = ''
        for x in range(QUESTION_LENGTH):
            long_text+=str(x)
        response = self.client.post(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'mc'}),
            {'question':long_text})
        error = _("Ensure this value has at most %d characters (it has %d)." %
                  (QUESTION_LENGTH, len(long_text)))
        self.assertFormError(response, 'form', 'question', error, "" )
        
        # Duplicate Question
        response = self.client.post(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'mc'}),
            {'question':question_text, 'choice_1':'yes', 'choice_2':'yes'})
        error = _("You have two identical choices.")
        self.assertFormError(response, 'form', None, error, "")
        
        # Marked wrong field correct
        response = self.client.post(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'mc'}),
            {'question':question_text, 'choice_1':'yes', 'choice_2':'no', 'correct':'3'})
        error = _("The choice you marked correct is blank.")
        self.assertFormError(response, 'form', None, error, "")
        
        # Non-consecutive choices filled out
        response = self.client.post(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'mc'}),
            {'question':question_text, 'choice_2':'A', 'choice_5':'B', 'correct':'2'})
        q = MultipleChoiceQuestion.objects.filter(question=question_text).first()
        self.assertTrue(q)
        c1 = MultipleChoiceOption.objects.filter(question=q,text='A').first()
        self.assertTrue(c1)
        self.assertTrue(c1.is_correct)
        self.assertEqual(c1.index, 1)
        c2 = MultipleChoiceOption.objects.filter(question=q,text='B').first()
        self.assertTrue(c2)
        self.assertFalse(c2.is_correct)
        self.assertEqual(c2.index, 2)
        q.delete()
    
    #def test_multiple_choice_edit_form(self):
    #    exam = get_or_create_exam()
    #    question = MultipleChoiceQuestion.objects.get(exam=exam)
    #    
    #    # check initial data
    #    response = self.client.get(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}))
    #    self.assertEqual(response.context['form'].initial['question'],question.question)
    #    
    #    # basic updates
    #    #   - text
    #    #   - order
    #    #   - correct question
    #    # save question
    #    
    #    # blank fields
    #    response = self.client.post(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}),
    #                                {})
        
        # duplicate question
        
        # indices not successive / don't start at 1
        
        # question and index don't match up
        
        # marked wrong field correct
        
        # non-consecutive fields filled out