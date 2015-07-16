import datetime
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from allauth.account.models import EmailAddress

from profiles.models import ContributorProfile
from .models import InterviewGroup, Interview, Excerpt, get_concept_list
from .forms import AddForm

User = get_user_model()


def set_up_user():
    """
    A function to be called by setUp in order to get a user for all authenticated activity.
    This function creates a User and related ContributorProfile and EmailAddress, and
    returns the new user object
    
    Important attributes of the user:
        password='password'
        is_active=True
        is_staff=False
        profile.is_contrib=False
        
    EmailAddress has verified=True.
    """
    user, created = User.objects.get_or_create(email='interview_email@test.com',
                                                    name='Dave Test',
                                                    is_active=True)
    if created:
        user.set_password('password')
        user.save()
        ContributorProfile.objects.create(user=user,
                                          institution='Test University',
                                          homepage='http://www.test.com/',
                                          text_info='Here is info about me')
        EmailAddress.objects.create(user=user,
                                    email=user.email,
                                    primary=True,
                                    verified=True)
    else:
        # just in case permissions have been modified
        user.is_staff = False
        user.save()
        user.profile.is_contrib = False
        user.profile.save()
    return user

def get_or_create_interview(user, group, interviewee='Dr. Test', date=datetime.date(2014,01,01)):
    """
    Gets or creates an interview with fields set to the given arguments.
    Does not create any excerpts.
    
    Required arguments:
        user - in most cases just use self.user if it exists
        group - use self.group
    """
    interview, created = Interview.objects.get_or_create(group=group,
                                                         interviewee=interviewee,
                                                         date_of_interview=date,
                                                         uploaded_by=user)
    return interview

def create_excerpt(interview, index=0, response='This is a response'):
    """
    Creates an excerpt according to the given arguments.
    Index is the index of the desired concept in the list get_concept_list()
    """
    concept = get_concept_list()[index]
    excerpt = Excerpt(content_object=concept,
                      interview=interview,
                      response='This is a response to %s' % concept)
    excerpt.save()
    return excerpt

class FormsTest(TestCase):
    def setUp(self):
        self.user = set_up_user()
        self.user.profile.is_contrib = True
        self.user.profile.save()
        self.client.login(email=self.user.email, password='password')
        self.group, created = InterviewGroup.objects.get_or_create(name='Test Interviews',
                                                                   unlocked=True)
    
    def test_add_form_group_field(self):
        locked_group = InterviewGroup.objects.create(name="Locked Interviews",
                                                     unlocked=False)
        
        # group!=None, so there is no field to select group
        form = AddForm(group=1)
        self.assertFalse(form.fields.get('group'))
        
        # group=None, so there will be a field to select group
        form = AddForm(group=None)
        self.assertTrue(form.fields.get('group'))
        
        # make sure field's queryset only contains unlocked groups
        field = form.fields.get('group')
        self.assertIn(self.group, field.queryset)
        self.assertNotIn(locked_group, field.queryset)
    
    def test_add_form_correct(self):
        interviewee = 'Santa Claus'
        date_of_interview = datetime.date(2013,12,25)
        concept = get_concept_list()[0]
        concept_response = "This is a response."
        response = self.client.post(reverse('interview_add', args=[self.group.id]),
                                    {'interviewee': interviewee,
                                     'date_of_interview': date_of_interview,
                                     'response_%d' % concept.id: concept_response})
        
        # If the interview & excerpt were saved correctly, get_or_create should get
        interview, created = Interview.objects.get_or_create(interviewee=interviewee)
        self.assertFalse(created)
        concept_type = ContentType.objects.get_for_model(concept)
        excerpt, created = Excerpt.objects.get_or_create(interview=interview,
                                                         content_type__pk=concept_type.id,
                                                         object_id=concept.id)
        self.assertFalse(created)
        
        # Check that data were saved
        self.assertEquals(interview.interviewee, interviewee)
        self.assertEquals(interview.date_of_interview, date_of_interview)
        self.assertEquals(interview.uploaded_by, self.user)
        self.assertEquals(excerpt.content_object, concept)
        self.assertEquals(excerpt.response, concept_response)
                    
        # Check redirect
        self.assertRedirects(response, reverse('interview_detail', args=(interview.id,)))
        
    def test_add_form_errors(self):
        # Blank Fields
        response = self.client.post(reverse('interview_add', args=[self.group.id]),
                                    {'interviewee': '', 'date_of_interview': '' })
        error = _("This field is required.")
        self.assertFormError(response, 'form', 'interviewee', error, "" )
        self.assertFormError(response, 'form', 'date_of_interview', error, "" )
        
        # Invalid date
        response = self.client.post(reverse('interview_add', args=[self.group.id]),
                                    {'interviewee': 'Dad', 'date_of_interview': '1234' })
        error = _("Enter a valid date.")
        self.assertFormError(response, 'form', 'date_of_interview', error, "" )

    
    def test_edit_form_correct(self):
        """
        Change interviewee and date.
        Change response to a concept (0), delete response to a concept (1), and responsd
        to a new concept (2).
        """
        interview = get_or_create_interview(self.user, self.group)
        excerpt_0 = create_excerpt(interview, 0)
        excerpt_1 = create_excerpt(interview, 1)
        
        new_interviewee = 'John Test'
        new_date_of_interview = datetime.date(1999,12,31)
        new_response_0 = "A new response to concept 0."
        new_concept_2 = get_concept_list()[2]
        new_response_2 = "This is a new response."
        response = self.client.post(reverse('interview_edit', args=(interview.id,)),
                                    {'interviewee': new_interviewee,
                                     'date_of_interview': new_date_of_interview,
                                     'response_%d' % excerpt_0.content_object.id: new_response_0,
                                     'response_%d' % excerpt_1.content_object.id: '',
                                     'response_%d' % new_concept_2.id: new_response_2 })

        # If the interview & excerpts were saved correctly, get_or_create should get
        interview, created = Interview.objects.get_or_create(pk=interview.id)
        self.assertFalse(created)
        
        concept_type = ContentType.objects.get_for_model(excerpt_0.content_object)
        excerpt_0, created = Excerpt.objects.get_or_create(interview=interview,
                                                           content_type__pk=concept_type.id,
                                                           object_id=excerpt_0.content_object.id)
        self.assertFalse(created)
        concept_type = ContentType.objects.get_for_model(new_concept_2)
        excerpt_2, created = Excerpt.objects.get_or_create(interview=interview,
                                                           content_type__pk=concept_type.id,
                                                           object_id=new_concept_2.id)
        self.assertFalse(created)
        
        # excerpt_1 should have been deleted
        concept_type = ContentType.objects.get_for_model(excerpt_1.content_object)
        self.assertFalse(Excerpt.objects.filter(interview=interview,
                                                content_type__pk=concept_type.id,
                                                object_id=excerpt_1.content_object.id))
        
        # Check that data were saved
        self.assertEquals(interview.interviewee, new_interviewee)
        self.assertEquals(interview.date_of_interview, new_date_of_interview)
        self.assertEquals(interview.uploaded_by, self.user)
        self.assertEquals(excerpt_0.response, new_response_0)        
        self.assertEquals(excerpt_2.content_object, new_concept_2)
        self.assertEquals(excerpt_2.response, new_response_2)
            
        # Check redirect
        self.assertRedirects(response, reverse('interview_detail', args=(interview.id,)))
        
    def test_edit_form_errors(self):
        interview = get_or_create_interview(self.user, self.group)
        
        # Blank Fields
        response = self.client.post(reverse('interview_edit', args=(interview.id,)),
                                    {'interviewee': '',
                                     'date_of_interview': ''})
        error = _("This field is required.")
        self.assertFormError(response, 'form', 'interviewee', error, "" )
        self.assertFormError(response, 'form', 'date_of_interview', error, "" )
        
        # Invalid date
        response = self.client.post(reverse('interview_edit', args=(interview.id,)),
                                    {'interviewee': '',
                                     'date_of_interview': '5678' })
        error = _("Enter a valid date.")
        self.assertFormError(response, 'form', 'date_of_interview', error, "" )
    
    def test_confirm_delete(self):
        interview = get_or_create_interview(self.user, self.group)
        response = self.client.post(reverse('interview_delete', args=(interview.id,)),{})
        self.assertRedirects(response, reverse('interview_index'))
        self.assertFalse(Interview.objects.filter(pk=interview.id))