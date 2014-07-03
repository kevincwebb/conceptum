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
    user = models.OneToOneField(settings.AUTH_USER_MODEL)  
    homepage = models.URLField(max_length=200, default="")
    interest_in_devel = models.BooleanField("interested in CI development", default=False)
    interest_in_deploy = models.BooleanField("interested in CI deployment", default=False)
    text_info = models.TextField(default="")
    
    objects = ProfileManager()
    
    #def __init__(self, profile_user, *args, **kwargs):
    #    super(ContributorProfile, self).__init__(*args, **kwargs)
    #    self.user = profile_user

    def __str__(self):
        return self.user.name
