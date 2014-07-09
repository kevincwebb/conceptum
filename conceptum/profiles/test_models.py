from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import ContributorProfile


class ContributorProfileTest(TestCase):
    
    def setUp(self):
        self.User = get_user_model()
    
    def test_user_relationship(self):
        user = self.User(email='test@email.com', name='Dave Test')
        profile = ContributorProfile(user=user)
        self.assertEqual( user, profile.user )
        self.assertEqual("%s"%profile, "Dave Test")
        
    def test_boolean_defaults(self):
        profile = ContributorProfile()
        self.assertFalse(profile.interest_in_devel)
        profile.interest_in_devel = True
        self.assertTrue(profile.interest_in_devel)
        
    def test_text_defaults(self):
        profile = ContributorProfile()
        self.assertEquals(profile.homepage,"")
        self.assertEquals(profile.text_info,"")
