from sky_visitor import views
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from sky_visitor.views import InvitationStartView
from sky_visitor.views import InvitationCompleteView
from sky_visitor.views import RegisterView as BaseRegisterView
from sky_visitor.forms import RegisterForm



class RegisterView(BaseRegisterView):
    template_name = 'mysky_visitor/registration_form.html'
   

class CustomInvitationStartView(InvitationStartView):
    template_name = 'exampleapp/invitation_start.html'
    success_message = _("Invitation successfully delivered. Invite more friends!")
 
    def get_email_kwargs(self, user):
        kwargs = super(CustomInvitationStartView, self).get_email_kwargs(user)
        # Custom subject line
        kwargs['subject'] = "Your friend invited you to join the community!"
        return kwargs
    
class CustomInvitationCompleteView(InvitationCompleteView):
    template_name = 'exampleapp/invitation_complete.html'
 
    def get_success_url(self):
        return reverse('home')