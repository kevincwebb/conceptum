from django.views.generic import TemplateView, ListView
#from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
#from django.contrib.auth.decorators import login_required
#from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.conf import settings
import os

from braces.views import AnonymousRequiredMixin,\
                         LoginRequiredMixin,\
                         StaffuserRequiredMixin

from profiles.models import ContributorProfile


class EmailVerificationSentView(AnonymousRequiredMixin, TemplateView):
    template_name = 'account/verification_sent.html'
    authenticated_redirect_url = reverse_lazy("profile")


class AccountInactiveView(AnonymousRequiredMixin, TemplateView):
    template_name = 'account/account_inactive.html'
    authenticated_redirect_url = reverse_lazy("profile")
    

class PendingUsersView(LoginRequiredMixin,
                       StaffuserRequiredMixin,
                       ListView):
    template_name = 'custom_auth/pending_users.html'
    context_object_name = 'pending_profiles'
    
    # Raise a 403 if user is denied access
    raise_exception = True

    def get_queryset(self):
        return ContributorProfile.objects.filter(
            user__is_active__exact=False).filter(
            user__emailaddress__verified__exact=True)


def which_action(request, profile_id):
    if not request.user.is_staff:
        raise PermissionDenied
    profile = get_object_or_404(ContributorProfile, pk=profile_id)
    if 'approve_contrib' in request.POST:
        approve(profile, True)
    elif 'approve_base' in request.POST:
        approve(profile, False)
    elif 'reject' in request.POST:
        reject(profile)
    elif 'ignore' in request.POST:
        ignore(profile)    
    return HttpResponseRedirect(reverse('pending_users'))

def approve(profile, approve_as_contrib):
    """
    This method will set profile.user.is_active = True, save the user,
    and send an email to notify the user.
    
    approve_as_contrib is a boolean, when True user will be given contributor privileges
    (profile.is_contrib=True).
    """
    file = open(settings.SITE_ROOT + os.path.sep +
                'templates/custom_auth/email/account_approved_subject.txt', 'r')
    subject = file.read()
    file.close()
    if approve_as_contrib:
        file = open(settings.SITE_ROOT + os.path.sep +
                    'templates/custom_auth/email/contrib_approved_message.txt', 'r')
        content = file.read()
        file.close()
        profile.is_contrib = True
        profile.save()
    else:
        file = open(settings.SITE_ROOT + os.path.sep +
                    'templates/custom_auth/email/user_approved_message.txt', 'r')
        content = file.read()
        file.close()
    
    profile.user.is_active = True
    profile.user.save()
    send_mail(subject, content, settings.DEFAULT_FROM_EMAIL,
        [profile.user.email], fail_silently=False)
        
def reject(profile):
    """
    This method will send an email to notify the user, then delete the user and profile
    """
    file = open(settings.SITE_ROOT + os.path.sep +
                'templates/custom_auth/email/account_rejected_subject.txt', 'r')
    subject = file.read()
    file.close()
    file = open(settings.SITE_ROOT + os.path.sep +
                'templates/custom_auth/email/account_rejected_message.txt', 'r')
    content = file.read()
    file.close()
    
    send_mail(subject, content, settings.DEFAULT_FROM_EMAIL,
        [profile.user.email], fail_silently=False)
    for emailaddress in profile.user.emailaddress_set.all():
        emailaddress.delete()
    profile.user.delete()
    profile.delete()    

def ignore(profile):
    """
    This method will delete the user and profile without notifying the user
    """
    for emailaddress in profile.user.emailaddress_set.all():
        emailaddress.delete()
    profile.user.delete()
    profile.delete()
    
    
