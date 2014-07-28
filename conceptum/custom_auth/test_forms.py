from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from django.utils.translation import ugettext_lazy as _

from allauth.account.models import EmailAddress

from profiles.models import ContributorProfile


User = get_user_model()


def create_basic_user(active=True, verified=True):
    if verified:
        user, created = User.objects.get_or_create(email='email@test.com')
        user.is_active = active
        user.set_password('password')
        user.save()
        if created:
            EmailAddress.objects.create(user=user,
                                        email=user.email,
                                        primary=True,
                                        verified=True)
    else:
        user, created = User.objects.get_or_create(email='uv_email@test.com')
        user.is_active = active
        user.set_password('password')
        user.save()
        if created:
            EmailAddress.objects.create(user=user,
                                        email=user.email,
                                        primary=True,
                                        verified=False)
    return user

class LoginFormTest(SimpleTestCase):
         
    def test_login_active_user(self):
        user = create_basic_user()
        response = self.client.post('/accounts/login/', {'login': user.email, 'password': 'password'})
        self.assertRedirects(response, '/accounts/profile/')
        self.assertEqual(self.client.session['_auth_user_id'], user.pk)

    def test_login_unverified_user(self):
        # With inactive user
        user = create_basic_user(active=False, verified=False)
        response = self.client.post('/accounts/login/', {'login': user.email, 'password': 'password'})
        self.assertRedirects(response, '/accounts/confirm-email/')
        self.assertNotIn('_auth_user_id', self.client.session)
        
        # With active user, though this case should never occur because users are not
        # available for approval (and thus never actived) until email is verified
        user = create_basic_user(active=True, verified=False)
        response = self.client.post('/accounts/login/', {'login': user.email, 'password': 'password'})
        self.assertRedirects(response, '/accounts/confirm-email/')
        self.assertNotIn('_auth_user_id', self.client.session)
    
    def test_login_inactive_user(self):
        # Note, the user has verified email
        user = create_basic_user(active=False)
        response = self.client.post('/accounts/login/', {'login': user.email, 'password': 'password'})
        self.assertRedirects(response, '/accounts/inactive/')
        self.assertNotIn('_auth_user_id', self.client.session)
    
    def test_login_username_password_errors(self):
        user = create_basic_user()
        
        # Empty Username
        response = self.client.post('/accounts/login/', {'login': '', 'password': 'password'})
        error = "This field is required."
        self.assertFormError(response, 'form', 'login', error, "" )
        
        # Empty Password for real user
        response = self.client.post('/accounts/login/', {'login': user.email, 'password': ''})
        error = "This field is required."
        self.assertFormError(response, 'form', 'password', error, "" )

        # Invalid Username
        response = self.client.post('/accounts/login/', {'login': 'bad@email.com', 'password': 'password'})
        error = _("The e-mail address and/or password you specified are not correct.")
        self.assertFormError(response, 'form', None, error, "" )
        
        # Wrong Password for real user
        response = self.client.post('/accounts/login/', {'login': user.email, 'password': 'wrongpassword'})
        error = _("The e-mail address and/or password you specified are not correct.")
        self.assertFormError(response, 'form', None, error, "" )


class SignupFormTest(SimpleTestCase):
    
    def test_sign_up_correct(self):
        user_email = 'tsuc_email@test.com' # this must be unique from other tests
        user_name = 'Dave Test'
        user_institution = 'Oberlin College'
        user_homepage = 'http://www.example.com/'
        user_password = 'password'
        
        # Try to sign up
        response = self.client.post('/accounts/signup/', {'email': user_email,
                                                          'name': user_name,
                                                          'institution': user_institution,
                                                          'homepage': user_homepage,
                                                          'password1': user_password,
                                                          'password2': user_password})
        self.assertRedirects(response, '/accounts/confirm-email/')
        
        # The user is not logged in after signup
        self.assertNotIn('_auth_user_id', self.client.session)
        
        # If the user was signed up and saved correctly, get_or_create should get, not create
        user, created = User.objects.get_or_create(email='tsuc_email@test.com')
        self.assertFalse(created)
        profile, created = ContributorProfile.objects.get_or_create(user=user)
        self.assertFalse(created)
        
        # Check that User and Profile data saved
        self.assertEquals(user.name, user_name)
        self.assertEquals(profile.homepage, user_homepage)
        self.assertEquals(profile.institution, user_institution)
        
    
    def test_sign_up_errors(self):
        user_email = 'tsue_email@test.com' # this must be unique from other tests
        user_name = 'Dave Test'
        user_institution = 'Oberlin College'
        user_homepage = 'http://www.example.com/'
        user_password = 'password'
        
        # Blank Fields
        response = self.client.post('/accounts/signup/', {'email': '',
                                                          'name': '',
                                                          'homepage': '',
                                                          'institution': '',
                                                          'password1': '',
                                                          'password2': ''})
        error = "This field is required."
        self.assertFormError(response, 'form', 'email', error, "" )
        self.assertFormError(response, 'form', 'name', error, "" )
        self.assertFormError(response, 'form', 'homepage', error, "" )
        self.assertFormError(response, 'form', 'institution', error, "" )
        self.assertFormError(response, 'form', 'password1', error, "" )
        self.assertFormError(response, 'form', 'password2', error, "" )

        # Paswords don't match
        response = self.client.post('/accounts/signup/', {'email': user_email,
                                                          'name': user_name,
                                                          'institution': user_institution,
                                                          'homepage': user_homepage,
                                                          'password1': user_password,
                                                          'password2': user_password+"wrong"})        
        error = "You must type the same password each time."
        self.assertFormError(response, 'form', None, error, "" )
        
        # Email not unique
        self.client.post('/accounts/signup/', {'email': user_email,
                                                          'name': user_name,
                                                          'institution': user_institution,
                                                          'homepage': user_homepage,
                                                          'password1': user_password,
                                                          'password2': user_password})
        response = self.client.post('/accounts/signup/', {'email': user_email,
                                                          'name': user_name,
                                                          'institution': user_institution,
                                                          'homepage': user_homepage,
                                                          'password1': user_password,
                                                          'password2': user_password})
        error = "A user is already registered with this e-mail address."
    