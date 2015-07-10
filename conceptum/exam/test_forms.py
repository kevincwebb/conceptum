from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.test import SimpleTestCase
from django.utils.translation import ugettext_lazy as _

import reversion

from profiles.tests import set_up_user
from interviews.models import get_concept_list, DummyConcept as Concept
from .models import Exam, FreeResponseQuestion, MultipleChoiceQuestion, MultipleChoiceOption,\
                    ExamKind, QUESTION_LENGTH, REQUIRED_CHOICES
from .forms import MultipleChoiceEditForm, FreeResponseVersionForm


def get_or_create_exam(suffix=''):
    """
    gets or creates an exam and some questions
    """
    exam, created = Exam.objects.get_or_create(name='Test Exam%s' % suffix,
                                               kind=ExamKind.CI,
                                               description='an exam for testing')
    if created:
        concept_type = ContentType.objects.get_for_model(Concept)
        concept = Concept.objects.get(name = "Concept A")
        with transaction.atomic(), reversion.create_revision():
            FreeResponseQuestion.objects.create(exam=exam,
                                    question="What is the answer to this FR question?%s" % suffix,
                                    number=1,
                                    content_type=concept_type,
                                    object_id=concept.id)
        concept = Concept.objects.get(name = "Concept B")
        with transaction.atomic(), reversion.create_revision():
            mcq = MultipleChoiceQuestion.objects.create(exam=exam,
                                    question="What is the answer to this MC question?%s" % suffix,
                                    number=2,
                                    content_type=concept_type,
                                    object_id=concept.id)
            MultipleChoiceOption.objects.create(question=mcq, text="choice 1", index=1, is_correct=True)
            MultipleChoiceOption.objects.create(question=mcq, text="choice 2", index=2)
            MultipleChoiceOption.objects.create(question=mcq, text="choice 3", index=3)
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
        concept = Concept.objects.get(name = "Concept A")
        question_text = 'Is this a new multiplce choice question?'
        
        # Make sure new question is saved
        response = self.client.post(reverse('exam:question_create',
            kwargs ={'exam_id':exam.id,'concept_id':concept.id,'question_type':'mc'}),
            {'question':question_text, 'choice_1':'yes', 'choice_2':'no', 'correct':'1'})
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
    
    def test_multiple_choice_edit_form(self):
        exam = get_or_create_exam(suffix=' edit_form')
        question = MultipleChoiceQuestion.objects.get(exam=exam)
        options = question.multiplechoiceoption_set.all()
        
        # Check initial data
        response = self.client.get(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}))
        initial = response.context['form'].initial
        self.assertEqual(initial['question'],question.question)
        self.assertEqual(initial['image'],question.image)
        # Unfortunately, initial[] does not have entries for the fields added in the form's init method
        # In views_test we test that the list of 3-tuples is correctly constructed, which mostly
        # covers initial data
        
        # Basic updates
        #   - change question text
        #   - change option text
        #   - change correct option
        #   - delete an option (by leaving it blank)
        post_dict = {'question':'new question',
                     'correct':options[1].id,
                     'choice_%d' % options[0].id:'A',
                     'index_%d' % options[0].id:1,
                     'choice_%d' % options[1].id:'B',
                     'index_%d' % options[1].id:2}
        response = self.client.post(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}),
                                    post_dict)
        print response
        self.assertEqual(response.status_code, 302)
        question = MultipleChoiceQuestion.objects.get(id=question.id)
        options = question.multiplechoiceoption_set.all()
        self.assertEqual(question.question,'new question')
        self.assertEqual(options[0].text,'A')
        self.assertEqual(options[0].index,1)
        self.assertFalse(options[0].is_correct)
        self.assertEqual(options[1].text,'B')
        self.assertEqual(options[1].index,2)
        self.assertTrue(options[1].is_correct)
        self.assertEqual(len(options),2) #before, there were 3
        
        # Change option order
        post_dict['index_%d' % options[0].id]=2
        post_dict['index_%d' % options[1].id]=1
        response = self.client.post(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}),
                                    post_dict)
        options = MultipleChoiceQuestion.objects.get(id=question.id).multiplechoiceoption_set.all()
        self.assertEqual(len(options),2)
        self.assertEqual(options[0].text,'B')
        self.assertEqual(options[1].text,'A')
        
        # Add an option
        post_dict['choice_new']='C'
        post_dict['index_new']=3
        post_dict['correct']=-1
        response = self.client.post(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}),
                                    post_dict)
        options = MultipleChoiceQuestion.objects.get(id=question.id).multiplechoiceoption_set.all()
        self.assertEqual(len(options),3)
        self.assertEqual(options[2].text,'C')
        self.assertTrue(options[2].is_correct)
        
        # Blank fields
        response = self.client.post(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}),
                                    {})
        error = _("This field is required.")
        self.assertFormError(response, 'form', 'question', error, "" )
        self.assertFormError(response, 'form', 'correct', error, "")
        error = _("You must provide at least %d choice." % REQUIRED_CHOICES)
        self.assertFormError(response, 'form', None, error, "" )
        
        # Bad correct value
        post_dict['correct']=99999
        response = self.client.post(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}),
                                    post_dict)
        self.assertFormError(response, 'form', 'correct', None, "" )
        
        # Duplicate option
        post_dict['choice_%d' % options[0].id]='same'
        post_dict['choice_%d' % options[1].id]='same'
        response = self.client.post(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}),
                                    post_dict)
        error = _("You have two identical choices.")
        self.assertFormError(response, 'form', None, error, "" )
        post_dict['choice_new']='same'
        post_dict['choice_%d' % options[1].id]='B'
        response = self.client.post(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}),
                                    post_dict)
        self.assertFormError(response, 'form', None, error, "" )
        
        # indices not successive / don't start at 1
        post_dict = {'question':'new question',
                     'correct':options[0].id,
                     'choice_%d' % options[0].id:'A',
                     'choice_%d' % options[1].id:'B',
                     'choice_new':'C',
                     'index_%d' % options[0].id:2,
                     'index_%d' % options[1].id:3,
                     'index_new':4}
        response = self.client.post(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}),
                                    post_dict)
        error = _("Order must begin with 1, with no doubles or gaps")
        self.assertFormError(response, 'form', None, error, "" )
        post_dict['index_%d' % options[1].id]=1 #we have 1, 2, 4
        response = self.client.post(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}),
                                    post_dict)
        self.assertFormError(response, 'form', None, error, "" )
        post_dict['index_new']=2 #we have 1, 2, 2
        response = self.client.post(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}),
                                    post_dict)
        self.assertFormError

        # question and index don't match up
        post_dict = {'question':'new question',
                     'correct':options[0].id,
                     'choice_%d' % options[0].id:'A'}
        response = self.client.post(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}),
                                    post_dict)
        error = _("Make sure all non-blank choices have an order.")
        self.assertFormError(response, 'form', None, error, "" )
        post_dict = {'question':'new question',
                     'correct':options[0].id,
                     'index_%d' % options[0].id:'1'}
        response = self.client.post(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}),
                                    post_dict)
        error = _("Make sure all blank choices do not have an order.")
        self.assertFormError(response, 'form', None, error, "" )

        # marked wrong field correct
        post_dict = {'question':'new question',
                     'correct':-1,
                     'choice_%d' % options[0].id:'A',
                     'choice_%d' % options[1].id:'C',
                     'index_%d' % options[0].id:1,
                     'index_%d' % options[1].id:2}
        response = self.client.post(reverse('CI_exam:mc_edit',kwargs ={'question_id':question.id}),
                                    post_dict)
        error = _("The choice you marked correct is blank.")
        self.assertFormError(response, 'form', None, error, "" )

    def test_free_response_version_form(self):
        exam = get_or_create_exam()    
        concept_type = ContentType.objects.get_for_model(Concept)
        concept = Concept.objects.get(name = "Concept A")
        # Have to create a new question with never-before-used pk because there are version\
        # objects still lingering in the database from old deleted questions.
        with transaction.atomic(), reversion.create_revision():
            question = FreeResponseQuestion.objects.create(
                id = 3691,
                exam=exam,
                question="A FR question for versioning?",
                number=1,
                content_type=concept_type,
                object_id=concept.id)
        
        # choosing current version should make a new non-unique version
        self.assertEqual(len(reversion.get_for_object(question)),1)
        response = self.client.post(reverse('CI_exam:fr_versions',
                                            kwargs ={'question_id':question.id}),
                                    {'version':0})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(reversion.get_for_object(question)),2)
        self.assertEqual(len(question.get_unique_versions()), 1)
        
        # make a new version, this should be first in the list
        with transaction.atomic(), reversion.create_revision():
            question.question = 'updated question?'
            question.save()
        form = FreeResponseVersionForm(instance=question)
        self.assertEqual(len(form.get_version_choices()),2)
        self.assertEqual(form.get_version_choices()[0][1],question.question)
        
        # choose old version and update question
        response = self.client.post(reverse('CI_exam:fr_versions',
                                            kwargs ={'question_id':question.id}),
                                    {'version':1})
        self.assertEqual(response.status_code, 302)
        question = FreeResponseQuestion.objects.get(id=question.id)
        self.assertEqual(question.question, 'A FR question for versioning?')

    def test_multiple_choice_version_form(self):
        exam = get_or_create_exam()    
        concept_type = ContentType.objects.get_for_model(Concept)
        concept = Concept.objects.get(name = "Concept A")
        # Have to create a new question with never-before-used pk because there are version\
        # objects still lingering in the database from old deleted questions.
        with transaction.atomic(), reversion.create_revision():
            question = MultipleChoiceQuestion.objects.create(
                id = 9875,
                exam=exam,
                question="A MC question for versioning?",
                number=1,
                content_type=concept_type,
                object_id=concept.id)
            MultipleChoiceOption.objects.create(id=2048, question=question, text="choice 1",
                                                index=1, is_correct=True)
            MultipleChoiceOption.objects.create(id=3810, question=question, text="choice 2",
                                                index=2)
        
        # choosing current version should make a new non-unique version
        self.assertEqual(len(reversion.get_for_object(question)),1)
        response = self.client.post(reverse('CI_exam:mc_versions',
                                            kwargs ={'question_id':question.id}),
                                    {'version':0})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(reversion.get_for_object(question)),2)
        self.assertEqual(len(question.get_unique_versions()), 1)
        
        # make a new version, this should be first in the list
        with transaction.atomic(), reversion.create_revision():
            question.question = 'updated question?'
            question.save()
        form = FreeResponseVersionForm(instance=question)
        self.assertEqual(len(form.get_version_choices()),2)
        self.assertEqual(form.get_version_choices()[0][1],question.question)
        
        # choose old version and update question
        response = self.client.post(reverse('CI_exam:mc_versions',
                                            kwargs ={'question_id':question.id}),
                                    {'version':1})
        self.assertEqual(response.status_code, 302)
        question = MultipleChoiceQuestion.objects.get(id=question.id)
        self.assertEqual(question.question, 'A MC question for versioning?')