import datetime
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import SimpleTestCase, TestCase
#from django.contrib.contenttypes.models import ContentType

from allauth.account.models import EmailAddress

from profiles.tests import set_up_user
from profiles.models import ContributorProfile
from .models import Interview, Excerpt, get_concept_list, DummyConcept

User = get_user_model()
concept_list = get_concept_list()

### function moved to profiles.tests
#def set_up_user():
#    """
#    this function has been moved to profiles.tests.py
#    """

def get_or_create_interview(user, interviewee='Dr. Test', date=datetime.date(2014,01,01)):
    """
    Gets or creates an interview with fields set to the given arguments.
    Does not create any excerpts.
    The only required argument is user: in most cases just use self.user if it exists
    """
    interview, created = Interview.objects.get_or_create(interviewee=interviewee,
                                                         date_of_interview=date,
                                                         uploaded_by=user)
    return interview

def create_excerpt(interview, index=0, response='This is a response'):
    """
    Creates an excerpt according to the given arguments.
    Index is the index of the desired concept in the list get_concept_list()
    """
    # This works
    #concept = DummyConcept.objects.get(name=get_concept_list()[index].name)
    
    # or this works
    concept = get_concept_list()[index]
    excerpt = Excerpt(content_object=concept,
                      interview=interview,
                      response='This is a response to %s' % concept)
    excerpt.save()
    return excerpt

class ViewsPermissionsTest(SimpleTestCase):
    def setUp(self):
        self.user = set_up_user()
        
    def test_index_view(self):
        """
        User must be authenticated to view this page
        """
        # User not logged in
        response = self.client.get(reverse('interview_index'))
        self.assertRedirects(response, '/accounts/login/?next=/interviews/')
        
        # User logged in, not contrib
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('interview_index'))
        self.assertEqual(response.status_code, 403)
        
        # User is contrib
        self.user.profile.is_contrib = True
        self.user.profile.save()
        response = self.client.get(reverse('interview_index'))
        self.assertEqual(response.status_code, 200)
    
    def test_detail_view(self):
        """
        User must be authenticated to view this page
        """
        interview = get_or_create_interview(self.user)
        
        # User not logged in
        response = self.client.get(reverse('interview_detail', args=(interview.id,)))
        self.assertRedirects(response, '/accounts/login/?next=/interviews/%s/' % interview.id)
        
        # User logged in, not contrib
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('interview_detail', args=(interview.id,)))
        self.assertEqual(response.status_code, 403)

        # User is contrib
        self.user.profile.is_contrib = True
        self.user.profile.save()
        response = self.client.get(reverse('interview_detail', args=(interview.id,)))
        self.assertEqual(response.status_code, 200)
        
    def test_add_view(self):
        """
        User must be authenticated* to view this page
        """
        # User not logged in
        response = self.client.get(reverse('interview_add'))
        self.assertRedirects(response, '/accounts/login/?next=/interviews/add/')
        
        # User logged in, not contrib
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('interview_add'))
        self.assertEqual(response.status_code, 403)
        
        # User is contrib
        self.user.profile.is_contrib = True
        self.user.profile.save()
        response = self.client.get(reverse('interview_add'))
        self.assertEqual(response.status_code, 200)
        
    def test_edit_view(self):
        """
        User must be staff or the original uploader to view this page
        """
        uploader = User.objects.create(email='interview_test_edit_view_email@test.com',
                                   name='Dave Test',
                                   is_active=True)
        uploader.set_password('password')
        uploader.save()
        ContributorProfile.objects.create(user=uploader, is_contrib=True)
        interview = get_or_create_interview(uploader)
        
        # Unauthenticated user (anonymous)
        response = self.client.get(reverse('interview_edit', args=(interview.id,)))
        self.assertRedirects(response, '/accounts/login/?next=/interviews/%s/edit/' % interview.id)
        
        # Non-staff arbitraty user (self.user)
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('interview_edit', args=(interview.id,)))
        self.assertEqual(response.status_code, 403)
        
        # Staff user (self.user)
        self.user.is_staff = True
        self.user.save()
        response = self.client.get(reverse('interview_edit', args=(interview.id,)))
        self.assertEqual(response.status_code, 200)
        self.user.is_staff = False
        self.user.save()
        self.client.logout()
        
        # Original uploader (uploader)
        self.client.login(email=uploader.email, password='password')
        response = self.client.get(reverse('interview_edit', args=(interview.id,)))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_delete_view(self):
        """
        User must be staff or the original uploader to view this page
        """
        uploader = User.objects.create(email='interview_test_delete_view_email@test.com',
                                   name='Dave Test',
                                   is_active=True)
        uploader.set_password('password')
        uploader.save()
        ContributorProfile.objects.create(user=uploader, is_contrib=True)        
        interview = get_or_create_interview(uploader)
        
        # Unauthenticated user (anonymous)
        response = self.client.get(reverse('interview_delete', args=(interview.id,)))
        self.assertRedirects(response, '/accounts/login/?next=/interviews/%s/delete/' % interview.id)
        
        # Non-staff arbitraty user (self.user)
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('interview_delete', args=(interview.id,)))
        self.assertEqual(response.status_code, 403)
        
        # Staff user (self.user)
        self.user.is_staff = True
        self.user.save()
        response = self.client.get(reverse('interview_delete', args=(interview.id,)))
        self.assertEqual(response.status_code, 200)
        self.user.is_staff = False
        self.user.save()
        self.client.logout()
        
        # Original uploader (uploader)
        self.client.login(email=uploader.email, password='password')
        response = self.client.get(reverse('interview_delete', args=(interview.id,)))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

class ViewsTest(TestCase):
    def setUp(self):
        self.user = set_up_user()
        self.user.profile.is_contrib = True
        self.user.profile.save()
        self.client.login(email=self.user.email, password='password')

    def test_index_view_with_no_interviews(self):
        """
        If no interviews exist, an appropriate message should be displayed
        """
        response = self.client.get(reverse('interview_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No interviews are available.")
        self.assertQuerysetEqual(response.context['interview_list'],[])
    
    def test_index_view_with_two_interviews(self):
        get_or_create_interview(self.user)
        get_or_create_interview(self.user, 'The Professor')
        response = self.client.get(reverse('interview_index'))
        self.assertQuerysetEqual(response.context['interview_list'],
                                 ['<Interview: Interview with The Professor on 2014-01-01>',
                                 '<Interview: Interview with Dr. Test on 2014-01-01>'],
                                 ordered=False )
    
    def test_add_view_concept_list(self):
        response = self.client.get(reverse('interview_add'))
        for concept in get_concept_list():
            self.assertContains(response, concept)
    
    def test_detail_view_valid_pk(self):
        """
        The detail view of an interview should display the interviewee, date, and uploader
        as well as all excerpts which were not empty
        """
        interview = get_or_create_interview(self.user)
        
        # First with no excerpts
        response = self.client.get(reverse('interview_detail', args=(interview.id,)))
        self.assertContains(response, interview.interviewee, status_code=200)
        self.assertContains(response, interview.date_of_interview, status_code=200)
        self.assertContains(response, interview.uploaded_by.name, status_code=200)
        self.assertNotContains(response,"Topic")
        self.assertNotContains(response,"Response")
        
        # With one excerpt, manually created (without get_concept_list)
        concept = DummyConcept(name='Concept X')
        concept.save()
        excerpt_0 = Excerpt(content_object=concept,
                      interview=interview,
                      response='This is a response to Concept X')
        excerpt_0.save()
        
        response = self.client.get(reverse('interview_detail', args=(interview.id,)))
        self.assertContains(response, excerpt_0.response, status_code=200)
        self.assertContains(response, excerpt_0.content_object, status_code=200)
        
        # Looping over all excerpts in get_concept_list
        excerpts = []
        for concept in get_concept_list():
            excerpt = Excerpt(content_object=concept,
                              interview=interview,
                              response='This is a response to %s' % concept)
            excerpt.save()
            excerpts.append(excerpt)
        
        response = self.client.get(reverse('interview_detail', args=(interview.id,)))
        for excerpt in excerpts:
            self.assertContains(response, excerpt.response, status_code=200)
            self.assertContains(response, excerpt.content_object, status_code=200)
        
    def test_detail_view_invalid_pk(self):
        """
        The detail view for a nonexistant pk should return a 404 not found.
        """
        # This test assumes that there less than 99 interviews in the test database
        response = self.client.get(reverse('interview_detail', args=(99,)))
        self.assertEqual(response.status_code, 404)


    def test_edit_view_initial(self):
        interview = get_or_create_interview(self.user)
        excerpt_0 = create_excerpt(interview)
        response = self.client.get(reverse('interview_edit', args=(interview.id,)))
        
        self.assertContains(response, interview.interviewee)
        self.assertContains(response, interview.date_of_interview)    

        self.assertContains(response, "response", status_code=200)
        for concept in get_concept_list():
            self.assertContains(response, concept)

        self.assertContains(response, excerpt_0.content_object, status_code=200)            
        self.assertContains(response, excerpt_0.response, status_code=200)
