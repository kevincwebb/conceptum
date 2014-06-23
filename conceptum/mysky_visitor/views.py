from sky_visitor import views
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from sky_visitor.views import InvitationStartView
from sky_visitor.views import InvitationCompleteView
from sky_visitor.views import RegisterView as BaseRegisterView
from sky_visitor.views import LoginView as BaseLoginView
from sky_visitor.views import ChangePasswordView as BaseChangePasswordView
from sky_visitor.views import ForgotPasswordView as BaseForgotPasswordView



class RegisterView(BaseRegisterView):
    template_name = 'mysky_visitor/registration_form.html'


class LoginView(BaseLoginView):
    template_name = 'mysky_visitor/login.html'

    
class ChangePasswordView(BaseChangePasswordView):
    template_name = 'mysky_visitor/change_password.html'

    
class ForgotPasswordView(BaseForgotPasswordView):
    
    def form_valid(self, form):
        user = form.user_cache[0]
        self.send_email(user)
        return super(ForgotPasswordView, self).form_valid(form)  # Do redirect


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