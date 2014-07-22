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

#A Template View that redirects to Profile for logged in users
#class RedirectView(TemplateView):
#    redirect_field_name = "profile"
#    
#    def get_redirect_url(self):
#        return self.redirect_field_name
#    
#    def get(self, request, *args, **kwargs):
#        '''
#        Overriding TemplateView.get() in order to
#        prevent active user from seeing inactive page
#        '''
#        # Redirect to Profile if user is active
#        if  self.request.user.is_authenticated():
#            return redirect(self.get_redirect_url())
#        # Process normally if User is not activated yet
#        context = self.get_context_data(**kwargs)
#        return self.render_to_response(context)


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

    #@method_decorator(login_required)
    #def dispatch(self, *args, **kwargs):
    #    if not self.request.user.is_staff:
    #        raise PermissionDenied
    #    return super(PendingUsersView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return ContributorProfile.objects.filter(
            user__is_active__exact=False).filter(
            user__emailaddress__verified__exact=True)


def which_action(request, profile_id):
    if not request.user.is_staff:
        raise PermissionDenied
    profile = get_object_or_404(ContributorProfile, pk=profile_id)
    if 'approve_contrib' in request.POST:
        #the pk for group can_contribCI is 1
        approve(profile, 1)
    elif 'approve_base' in request.POST:
        #the pk for group can_useCI is 2
        approve(profile, 2)
    elif 'reject' in request.POST:
        reject(profile)
    elif 'ignore' in request.POST:
        ignore(profile)    
    return HttpResponseRedirect(reverse('pending_users'))

def approve(profile, group):
    """
    this method will set profile.user.is_active = True, save the user,
    and send an email to notify the user
    """
    
    file = open(settings.SITE_ROOT + os.path.sep +
                'templates/custom_auth/email/account_approved_subject.txt', 'r')
    subject = file.read()
    file.close()    
    if group == 2:
        file = open(settings.SITE_ROOT + os.path.sep +
                    'templates/custom_auth/email/user_approved_message.txt', 'r')
        content = file.read()
        file.close()
    elif group == 1:
        file = open(settings.SITE_ROOT + os.path.sep +
                    'templates/custom_auth/email/contrib_approved_message.txt', 'r')
        content = file.read()
        file.close()
    
    profile.user.is_active = True
    profile.user.groups.add(group)
    profile.user.save()
    send_mail(subject, content, settings.DEFAULT_FROM_EMAIL,
        [profile.user.email], fail_silently=False)
        
def reject(profile):
    """
    this method will send an email to notify the user, then delete the user and profile
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
    this method will delete the user and profile without notifying the user
    """
    for emailaddress in profile.user.emailaddress_set.all():
        emailaddress.delete()
    profile.user.delete()
    profile.delete()
    
    
