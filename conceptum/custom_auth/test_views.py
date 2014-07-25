from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.core import mail
from django.test import SimpleTestCase, TransactionTestCase

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


class UserApprovalTest(TransactionTestCase):
    
    def create_basic_user(self, prefix='', active=True, verified=True):
        user, created = User.objects.get_or_create(email=prefix+'uat_email@test.com')
        user.is_active=active
        user.set_password('password')
        user.save()
        if created:
            ContributorProfile.objects.create(user=user)
            EmailAddress.objects.create(user=user,
                                        email=user.email,
                                        primary=True,
                                        verified=verified)
        return user

    def test_pending_users_list(self):
        users = (self.create_basic_user('0', active=False, verified=False),
                 self.create_basic_user('1', active=False, verified=True),
                 self.create_basic_user('2', active=True, verified=True))
        
        staff_user = self.create_basic_user()

        
        # Not logged in
        response = self.client.get('/accounts/pending/')
        #self.assertRedirects(response, '/accounts/login/?next=/accounts/pending/')
        self.assertEqual(response.status_code, 403)
        
        # Logged in, not staff
        self.assertTrue(self.client.login(email=staff_user.email, password='password'))
        response = self.client.get('/accounts/pending/')
        self.assertEqual(response.status_code, 403)
        
        # Now as staff
        staff_user.is_staff = True
        staff_user.save()
        response = self.client.get('/accounts/pending/')
        self.assertContains(response, 'These users have requested conceptum accounts')
        
        # Only inactive but verified users should be in the list
        self.assertContains(response, users[1].email)
        self.assertNotContains(response, users[0].email)
        self.assertNotContains(response, users[2].email)

    def test_approve_contrib(self):
        user = self.create_basic_user('A', active=False)
        
        # Login and try to approve, first w/o staff permission
        staff_user = self.create_basic_user()
        self.client.login(email=staff_user.email, password='password')
        response = self.client.post(reverse('pending_action', kwargs={'profile_id':user.profile.id}),
                                    {'approve_contrib':'Approve as Contributor'},
                                    follow=True)
        self.assertEqual(response.status_code, 403)
        user = User.objects.get(pk=user.id)
        self.assertFalse(user.is_active)
        
        # Now staff, approve as contributor
        staff_user.is_staff = True
        staff_user.save()
        response = self.client.post(reverse('pending_action', kwargs={'profile_id':user.profile.id}),
                                    {'approve_contrib':'Approve as Contributor'},
                                    follow=True)
        self.assertRedirects(response, '/accounts/pending/')
        user = User.objects.get(pk=user.id) # (make user match the database)
        self.assertTrue(user.is_active)
        self.assertTrue(user.profile.is_contrib)
        
        # Test that email has been sent.
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Approved', mail.outbox[0].subject)
        
    def test_approve_base(self):
        user = self.create_basic_user('A', active=False)
        
        # Login and try to approve, first w/o staff permission
        staff_user = self.create_basic_user()
        self.client.login(email=staff_user.email, password='password')
        response = self.client.post(reverse('pending_action', kwargs={'profile_id':user.profile.id}),
                                    {'approve_base':'Approve as User'},
                                    follow=True)
        self.assertEqual(response.status_code, 403)
        user = User.objects.get(pk=user.id)
        self.assertFalse(user.is_active)
        
        # Now staff, approve as base user
        staff_user.is_staff = True
        staff_user.save()
        response = self.client.post(reverse('pending_action', kwargs={'profile_id':user.profile.id}),
                                    {'approve_base':'Approve as User'},
                                    follow=True)
        self.assertRedirects(response, '/accounts/pending/')
        user = User.objects.get(pk=user.id) # (make user match the database)
        self.assertTrue(user.is_active)
        self.assertFalse(user.profile.is_contrib)
        
        # Test that email has been sent.
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Approved', mail.outbox[0].subject)
    
    def test_reject_user(self):
        user = self.create_basic_user('A', active=False)
        
        # Login and try to reject, first w/o staff permission
        staff_user = self.create_basic_user()
        self.client.login(email=staff_user.email, password='password')
        response = self.client.post(reverse('pending_action', kwargs={'profile_id':user.profile.id}),
                                    {'reject':'Reject'},
                                    follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(User.objects.get(pk=user.id))

        # Now staff, reject
        staff_user.is_staff = True
        staff_user.save()
        response = self.client.post(reverse('pending_action', kwargs={'profile_id':user.profile.id}),
                                    {'reject':'Reject'},
                                    follow=True)
        self.assertRedirects(response, '/accounts/pending/')
        self.assertRaises(User.DoesNotExist, User.objects.get, pk=user.id)
        self.assertRaises(ContributorProfile.DoesNotExist, ContributorProfile.objects.get, pk=user.profile.id)
        self.assertRaises(EmailAddress.DoesNotExist, EmailAddress.objects.get, email=user.email)
        
        # Test that email has been sent.
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Rejected', mail.outbox[0].subject)

    def test_ignore_user(self):
        user = self.create_basic_user('A', active=False)
        
        # Login and try to reject, first w/o staff permission
        staff_user = self.create_basic_user()
        self.client.login(email=staff_user.email, password='password')
        response = self.client.post(reverse('pending_action', kwargs={'profile_id':user.profile.id}),
                                    {'ignore':'Ignore'},
                                    follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(User.objects.get(pk=user.id))

        # Now staff, reject
        staff_user.is_staff = True
        staff_user.save()
        response = self.client.post(reverse('pending_action', kwargs={'profile_id':user.profile.id}),
                                    {'ignore':'Ignore'},
                                    follow=True)
        self.assertRedirects(response, '/accounts/pending/')
        self.assertRaises(User.DoesNotExist, User.objects.get, pk=user.id)
        self.assertRaises(ContributorProfile.DoesNotExist, ContributorProfile.objects.get, pk=user.profile.id)
        self.assertRaises(EmailAddress.DoesNotExist, EmailAddress.objects.get, email=user.email)
        
        # Test that email has not been sent.
        self.assertEqual(len(mail.outbox), 0)