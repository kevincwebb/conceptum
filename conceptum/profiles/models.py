from django.conf import settings
from django.db import models
from django.contrib.auth.models import BaseUserManager


class ProfileManager(BaseUserManager):
    pass


class ContributorProfile(models.Model):
    """
    A user profile for contributors
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    homepage = models.URLField(max_length=200)
    interest_in_devel = models.BooleanField("interested in CI development")
    interest_in_deploy = models.BooleanField("interested in CI deployment")
    text_info = models.TextField()

    objects = ProfileManager()

    #def __init__(self, profile_user, *args, **kwargs):
    #    super(ContributorProfile, self).__init__(*args, **kwargs)
    #    self.user = profile_user
        
    def __str__(self):
        return "{name}'s profile".format(name=self.user.name)