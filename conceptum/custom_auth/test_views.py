from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
#from django.utils.translation import ugettext_lazy as _

from allauth.account.models import EmailAddress

#from profiles.models import ContributorProfile
#import custom_auth.forms.LoginForm


User = get_user_model()


class SimpleViewsTest(SimpleTestCase):
    
    def create_basic_user(active=True):
        user, created = User.objects.get_or_create(email='svt_email@test.com')
        user.is_active=active
        user.set_password('password')
        user.save()
        if created:
            EmailAddress.objects.create(user=user,
                                        email=user.email,
                                        primary=True,
                                        verified=True)
        return user

    def test_signup(self):
        # User not logged in
        response = self.client.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)
        
        # User logged in
        user = self.create_basic_user()
        self.client.login(email=user.email, password='password')
        response = self.client.get('/accounts/signup/')
        self.assertRedirects(response, '/accounts/profile/')
    
    def test_login(self):
        # User not logged in
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        
        # User logged in
        user = self.create_basic_user()
        self.assertTrue(self.client.login(email=user.email, password='password'))
        response = self.client.get('/accounts/login/')
        self.assertRedirects(response, '/accounts/profile/')
        self.assertEqual(self.client.session['_auth_user_id'], user.pk)       
        
    def test_logout(self):
        # User not logged in
        response = self.client.get('/accounts/logout/')
        self.assertRedirects(response, '/')
        
        # User logged in
        user = self.create_basic_user()
        self.assertTrue(self.client.login(email=user.email, password='password'))
        
        # GET should not log out user yet
        response = self.client.get('/accounts/logout/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['_auth_user_id'], user.pk)
        
        # check that POST successfully logs out user
        response =  self.client.post('/accounts/logout/')
        self.assertRedirects(response, '/')
        self.assertNotIn('_auth_user_id', self.client.session)
    
    def test_inactive(self):
        # User not logged in
        response = self.client.get('/accounts/inactive/')
        self.assertEqual(response.status_code, 200)
        
        # User logged in
        user = self.create_basic_user()
        self.client.login(email=user.email, password='password')
        response = self.client.get('/accounts/inactive/')
        self.assertRedirects(response, '/accounts/profile/')
        
    def test_confirm_email(self):
        # User not logged in
        response = self.client.get('/accounts/confirm-email/')
        self.assertEqual(response.status_code, 200)
        
        # User logged in
        user = self.create_basic_user()
        self.client.login(email=user.email, password='password')
        response = self.client.get('/accounts/confirm-email/')
        self.assertRedirects(response, '/accounts/profile/')


class UserApprovalTest(SimpleTestCase):
    index = 0
    
    def create_indexed_user(active=True, verified=True):
        index+=1
        user = User.objects.create(email=index+'uat_email@test.com', is_active=active)
        user.set_password('password')
        user.save()
        EmailAddress.objects.create(user=user,
                                    email=user.email,
                                    primary=True,
                                    verified=verified)
        return user
    
    def test_pending_users_list(self):
        pass
    
    def test_approve_user(self):
        pass
    
    def test_reject_user(self):
        pass
    