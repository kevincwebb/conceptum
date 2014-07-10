from django.views.generic.base import TemplateView
from django.views.generic import FormView
from django.views.generic import ListView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect

from profiles.models import ContributorProfile

from .forms import EditProfileForm



class ProfileView(TemplateView):
    template_name = 'profiles/profile.html'
    model = ContributorProfile

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProfileView, self).dispatch(*args, **kwargs)
    

class EditProfileView(FormView):
    template_name = 'profiles/edit.html'
    form_class = EditProfileForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        form.save(self.request)
        return HttpResponseRedirect(self.get_success_url())