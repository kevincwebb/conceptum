from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import SimpleTestCase
from django.utils.translation import ugettext_lazy as _

from allauth.account.models import EmailAddress

from .models import ContributorProfile


User = get_user_model()


class EditProfileFormTest(SimpleTestCase):
    
    def setUp(self):
        self.user, created = User.objects.get_or_create(email='vt_email@test.com',
                                                        is_active=True)
        self.user.name='Dave Test',
        self.user.set_password('password')
        self.user.save()
        if created:
            ContributorProfile.objects.create(user=self.user,
                                              institution='Test University',
                                              homepage='http://www.test.com/',
                                              text_info='Here is info about me')
            EmailAddress.objects.create(user=self.user,
                                        email=self.user.email,
                                        primary=True,
                                        verified=True)
        self.client.login(email=self.user.email, password='password')
            
    def test_form_correct(self):
        new_name = 'Santa Claus'
        new_institution = 'UNP'
        new_homepage = 'http://www.christmas.com/'
        new_text_info = '' # this field should be allowed to be blank
        response = self.client.post(reverse('edit_profile'), {'name': new_name,
                                                              'institution': new_institution,
                                                              'homepage': new_homepage,
                                                              'text_info': new_text_info })
        self.assertRedirects(response, reverse('profile'))
        
        self.user = User.objects.get(pk=self.user.id)
        self.assertEquals(self.user.name, new_name)
        self.assertEquals(self.user.profile.homepage, new_homepage)
        self.assertEquals(self.user.profile.institution, new_institution)
        self.assertEquals(self.user.profile.text_info, new_text_info)
        
    def test_form_errors(self):       
        # Blank Fields
        response = self.client.post(reverse('edit_profile'), {'name': '',
                                                              'institution': '',
                                                              'homepage': '' })
        error = _("This field is required.")
        self.assertFormError(response, 'form', 'name', error, "" )
        self.assertFormError(response, 'form', 'institution', error, "" )
        self.assertFormError(response, 'form', 'homepage', error, "" )