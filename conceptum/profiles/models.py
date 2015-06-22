from django.conf import settings
from django.db import models


class ContributorProfile(models.Model):
    """
    A user profile for all users. Holds institution, homepage, and text info about
    a user. The name ContributorProfile may be misleading: all users have
    ContributorProfiles, whether they have contributor permissions or not.
    
    The is_contrib field determines whether the user is allowed to access the site
    as a "contributor" (will be involved in the development process) or as a base
    user (can deploy the finished CI).  This field is set when a staff user approves
    an account.
    
    The interest_in_ booleans are only used during account registration and approval. 
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile')
    is_contrib = models.BooleanField(default=False)
    institution = models.CharField(max_length=200, default="")
    homepage = models.URLField(max_length=200, default="")
    interest_in_devel = models.BooleanField("interested in CI development", default=False)
    interest_in_deploy = models.BooleanField("interested in CI deployment", default=False)
    text_info = models.TextField(default="", blank=True)

    def __str__(self):
        return self.user.name

    def can_contrib(self):
        """
        Use this method to check a user's contributor privileges.
        
        All staff users should be allowed to contribute (have is_contrib=True). However,
        it is possible to set user.is_staff=True and user.profile.is_contrib=false.
        This method ensures that all staff users will pass the contrib test. 
        """
        return self.is_contrib or self.user.is_staff
