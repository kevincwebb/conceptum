from profiles.models import ContributorProfile
from django.views import generic


class UserApprovalView(generic.ListView):
    template_name = 'custom_auth/user_approval.html'
    context_object_name = 'unapproved_profiles'
    #model = ContributorProfile
  
#    def get_queryset(self):
#		#Returns the last five published polls.
#		return Poll.objects.filter(
#			pub_date__lte=timezone.now()
#		).order_by('-pub_date')[:5]

    def get_queryset(self):
        return ContributorProfile.objects.filter(user__is_active__exact=False)

def approve(request, profile):
    """
    this method will set profile.user.is_active = True, save the user,
    and send an email to notify the user
    """
    pass

def reject(request, profile):
    """
    this method will send an email to notify the user, then delete the user and profile
    """
    pass

def ignore(request, profile):
    """
    this method will delete the user and profile without notifying the user
    """