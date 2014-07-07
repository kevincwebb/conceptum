from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
#from django.utils.translation import ugettext_lazy as _

from allauth.account.models import EmailAddress

from profiles.models import ContributorProfile


User = get_user_model()


class SimpleViewsTest(SimpleTestCase):
    
    def create_basic_user(self, active=True):
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
    
    def create_unique_user(self, prefix, active=True, verified=True):
        user = User.objects.create(email=prefix+'uat_email@test.com', is_active=active)
        user.set_password('password')
        user.save()
        ContributorProfile.objects.create(user=user)
        EmailAddress.objects.create(user=user,
                                    email=user.email,
                                    primary=True,
                                    verified=verified)
        return user

    def test_pending_users_list(self):
        users = (self.create_unique_user('1', active=False, verified=False),
                 self.create_unique_user('2', active=False, verified=True),
                 self.create_unique_user('3', active=True, verified=True))
        
        staff_user = self.create_unique_user('4')
        staff_user.is_staff = True
        staff_user.save()
        
        # Not logged in
        response = self.client.get('/accounts/pending/')
        #    The behavior of the /accounts/pending/ for un-authorized users may change in
        #    the near future, in which case this test will fail and need to be updated
        self.assertContains(response, 'This page is for staff only')
        
        # Logged in, not staff
        self.assertTrue(self.client.login(email=users[2].email, password='password'))
        response = self.client.get('/accounts/pending/')
        #    The behavior of thhe /accounts/pending/ for non-staff users may change in
        #    the near future, in which case this test will fail and need to be updated
        self.assertContains(response, 'This page is for staff only')
        self.client.logout()
        
        # Login as staff
        self.assertTrue(self.client.login(email=staff_user.email, password='password'))
        response = self.client.get('/accounts/pending/')
        self.assertContains(response, 'These users have requested conceptum accounts')
        
        # Only inactive but verified users should be in the list
        self.assertContains(response, users[1].email)
        self.assertNotContains(response, users[0].email)
        self.assertNotContains(response, users[2].email)

    def test_approve_user(self):
        user = self.create_unique_user('10', active=False)
        staff_user = self.create_unique_user('11')
        staff_user.is_staff = True
        staff_user.save()
        self.assertTrue(self.client.login(email=staff_user.email, password='password'))
        
        # user is in the list
        response = self.client.get('/accounts/pending/')
        self.assertContains(response, user.email)
        
        self.assertFalse(user.is_active)
        #response = self.client.post('/accounts/pending/',
        #                            {'approve_contrib':'Approve as Contributor', 'profile_id':user.profile.id},
        #                            follow=True)
        #response = self.client.get('/accounts/pending/action/%s' %user.profile.id,{'approve_contrib':'Approve as Contributor'})
        #self.assertRedirects(response, '/accounts/pending/')
        #self.assertTrue(user.is_active)
        
    
    def test_reject_user(self):
        pass


