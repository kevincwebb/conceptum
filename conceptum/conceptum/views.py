from django.shortcuts import render
from django.views.generic.base import TemplateView
# For CI variable names.
from django.conf import settings

from braces.views import LoginRequiredMixin, StaffuserRequiredMixin

def home(request):
    context = {'CI_COURSE': settings.CI_COURSE}
    return render(request, 'home.html', context)

def ci_info(request):
    context = {'CI_COURSE': settings.CI_COURSE}
    return render(request, 'ci_info.html', context)


class StaffView(LoginRequiredMixin,
                StaffuserRequiredMixin,
                TemplateView):
    template_name='conceptum/staff.html'