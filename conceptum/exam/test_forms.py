from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db import models
from django.test import SimpleTestCase
from django.utils.translation import ugettext_lazy as _

from profiles.tests import set_up_user
from .models import Exam, FreeResponseQuestion, MultipleChoiceQuestion, MultipleChoiceOption,\
                    QUESTION_LENGTH, REQUIRED_CHOICES


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

class FormsTest(SimpleTestCase):
    def setUp(self):
        create_concepts()
        self.user = set_up_user()
        self.user.profile.is_contrib = True
        self.user.profile.save()
        self.client.login(email=self.user.email, password='password')
 
    def test_add_free_response_form(self):
        exam = get_or_create_exam()
        concept = DummyConcept.objects.get(name = "Concept A")
        question_text = 'Is this a new free response question?'
        
        # Make sure new question is saved
        response = self.client.post(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'fr'}),
            {'question':question_text})
        question, created = FreeResponseQuestion.objects.get_or_create(question=question_text)
        self.assertFalse(created)
        
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
            {'question':question_text, 'choice_1':'yes', 'choice_2':'no'})
        q, created = MultipleChoiceQuestion.objects.get_or_create(question=question_text)
        self.assertFalse(created)
        c1, created = MultipleChoiceOption.objects.get_or_create(question=q,text='yes')
        self.assertFalse(created)
        c2, created = MultipleChoiceOption.objects.get_or_create(question=q,text='no')
        self.assertFalse(created)
        
        # Blank Fields
        response = self.client.post(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'mc'}),
            {})
        error = _("This field is required.")
        self.assertFormError(response, 'form', 'question', error, "" )
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
        
        # Non-consecutive choices filled out
        response = self.client.post(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'mc'}),
            {'question':question_text, 'choice_2':'A', 'choice_5':'B'})
        c1, created = MultipleChoiceOption.objects.get_or_create(question=q,text='yes')
        self.assertFalse(created)
        c2, created = MultipleChoiceOption.objects.get_or_create(question=q,text='no')
        self.assertFalse(created)