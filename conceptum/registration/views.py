from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from django.shortcuts import redirect
from django.views.generic.edit import FormView

from authtools.forms import UserCreationForm

class RegistrationView(FormView):
    """
    Base class for user registration views, based on Django-Registration
    
    possible methods to add
        registration.RegistrationView.dispatch
        registration.RegistrationView.registration_allowed
        
        clean methods to UserCreationForm (see registration.forms.RegistrationForm)
        
    
    """
#    disallowed_url = 'registration_disallowed'
    form_class = UserCreationForm
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    success_url = None
    template_name = 'registration/registration_form.html'
    
    def form_valid(self, request, form):
        new_user = self.registerFAIL(request, **form.cleaned_data)
        success_url = self.get_success_url(request, new_user)
        
        # success_url may be a simple string, or a tuple providing the
        # full argument set for redirect(). Attempting to unpack it
        # tells us which one it is.
        try:
            to, args, kwargs = success_url
            return redirect(to, *args, **kwargs)
        except ValueError:
            return redirect(success_url)

    def register(self, request, **cleaned_data):
        username = cleaned_data['email']
        password = cleaned_data['password']
        
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        #need to use AUTH_USER_MODEL
        new_user = authtools.models.UserManagerFAIL.create_user(username, password, site)
        #now we need to send an email
        return new_user