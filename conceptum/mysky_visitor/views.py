from sky_visitor import views
from django.contrib import auth
from sky_visitor.views import RegisterView as BaseRegisterView
from sky_visitor.forms import RegisterForm

class RegisterView(BaseRegisterView):
    template_name = 'mysky_visitor/registration_form.html'
   