from django.views.generic import FormView, TemplateView
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect

from braces.views import LoginRequiredMixin

from profiles.models import ContributorProfile
from .forms import EditProfileForm



class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profiles/profile.html'
    model = ContributorProfile
    

class EditProfileView(LoginRequiredMixin, FormView):
    template_name = 'profiles/edit.html'
    form_class = EditProfileForm
    success_url = reverse_lazy('profile')

    def get_initial(self):
        user = self.request.user
        initial = { 'name' : user.name,
                    'institution' : user.profile.institution,
                    'homepage' : user.profile.homepage,
                    'text_info' : user.profile.text_info }
        return initial
    

    def form_valid(self, form):
        form.save(self.request)
        return HttpResponseRedirect(self.get_success_url())
