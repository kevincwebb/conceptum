from django.contrib.auth import get_user_model

from allauth.account.models import EmailAddress

from profiles.models import ContributorProfile

User = get_user_model()


def set_up_user():
    """
    A function to be called by setUp in order to get a user for all authenticated activity.
    This function creates a User and related ContributorProfile and EmailAddress, and
    returns the new user object
    
    Important attributes of the user:
        password='password'
        is_active=True
        is_staff=False
        profile.is_contrib=False
        
    EmailAddress has verified=True.
    """
    user, created = User.objects.get_or_create(email='interview_email@test.com',
                                                    name='Dave Test',
                                                    is_active=True)
    if created:
        user.set_password('password')
        user.save()
        ContributorProfile.objects.create(user=user,
                                          institution='Test University',
                                          homepage='http://www.test.com/',
                                          text_info='Here is info about me')
        EmailAddress.objects.create(user=user,
                                    email=user.email,
                                    primary=True,
                                    verified=True)
    else:
        # just in case permissions have been modified
        user.is_staff = False
        user.save()
        user.profile.is_contrib = False
        user.profile.save()
    return user