from django.shortcuts import render
from django.views.generic.base import TemplateView
# For CI variable names.
from django.conf import settings

from braces.views import LoginRequiredMixin, StaffuserRequiredMixin

def home(request):
    if request.user.is_authenticated():
        user = request.user
        priv_list = ["user"]
        if (user.is_superuser):
            priv_list = ["superuser", "admin", "contributor", "user"]
        elif(user.is_staff):
            priv_list = ["admin", "contributor", "user"]
        elif(user.profile.is_contrib):
            priv_list = ["contributor", "user"]
            
        context = {'CI_COURSE': settings.CI_COURSE,
                   'priv_list':priv_list}
        return render(request, 'home_user.html', context)
    else:
        context = {'CI_COURSE': settings.CI_COURSE}
        return render(request, 'home.html', context)

def ci_info(request):
    context = {'CI_COURSE': settings.CI_COURSE}
    return render(request, 'ci_info.html', context)


class StaffView(LoginRequiredMixin,
                StaffuserRequiredMixin,
                TemplateView):
    template_name='conceptum/staff.html'