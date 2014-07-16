from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import SimpleTestCase

from allauth.account.models import EmailAddress

from .models import ContributorProfile


User = get_user_model()


class ViewsTest(SimpleTestCase):
    
    def setUp(self):
        self.user, created = User.objects.get_or_create(email='vt_email@test.com',
                                                        name='Dave Test',
                                                        is_active=True)
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
    
    def test_profile_view(self):
        # User not logged in
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, '/accounts/login/?next=/accounts/profile/')
        
        # User logged in
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        
    def test_edit_profile_view(self):
        # User not logged in
        response = self.client.get(reverse('edit_profile'))
        self.assertRedirects(response, '/accounts/login/?next=/accounts/profile/edit/')
        
        # User logged in
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)
    
    def test_edit_profile_initial_data(self):
        self.client.login(email=self.user.email, password='password')
        response = self.client.get(reverse('edit_profile'))
        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.profile.institution)
        self.assertContains(response, self.user.profile.homepage)
        self.assertContains(response, self.user.profile.text_info)