from django.views import generic
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required


from profiles.models import ContributorProfile


class PendingUsersView(generic.ListView):
    template_name = 'custom_auth/pending_users.html'
    context_object_name = 'pending_profiles'
    #model = ContributorProfile
  
#    def get_queryset(self):
#		#Returns the last five published polls.
#		return Poll.objects.filter(
#			pub_date__lte=timezone.now()
#		).order_by('-pub_date')[:5]

    def get_queryset(self):
        return ContributorProfile.objects.filter(user__is_active__exact=False)

def approve(request, profile_id):
    """
    this method will set profile.user.is_active = True, save the user,
    and send an email to notify the user
    """
    if request.user.is_staff:
        p = get_object_or_404(ContributorProfile, pk=profile_id)
        p.user.is_active = True
        p.user.save()
    return HttpResponseRedirect(reverse('pending_users'))
        

def reject(request, profile):
    """
    this method will send an email to notify the user, then delete the user and profile
    """
    pass

def ignore(request, profile):
    """
    this method will delete the user and profile without notifying the user
    """
    pass