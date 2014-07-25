from django.conf import settings
from django.db import models
from django.contrib.auth.models import BaseUserManager


class ProfileManager(BaseUserManager):
    pass


class ContributorProfile(models.Model):
    """
    A user profile for all users.
    We may want to rename this to UserProfile, as all users will use this profile model,
    not just Contributors
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile')
    is_contrib = models.BooleanField(default=False)
    institution = models.CharField(max_length=200, default="")
    homepage = models.URLField(max_length=200, default="")
    interest_in_devel = models.BooleanField("interested in CI development", default=False)
    interest_in_deploy = models.BooleanField("interested in CI deployment", default=False)
    text_info = models.TextField(default="", blank=True)
    
    objects = ProfileManager()

    def __str__(self):
        return self.user.name

    def can_contrib(self):
        """
        All staff users should be allowed to contribute. However, it's possible
        to set user.is_staff=True and user.profile.is_contrib=false. Use this
        method to check is_contrib and all staff users will pass.
        """
        return self.is_contrib or self.user.is_staff
