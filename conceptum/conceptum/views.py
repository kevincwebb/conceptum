from django.shortcuts import render

# For CI variable names.
from django.conf import settings


def home(request):
    context = {'CI_COURSE': settings.CI_COURSE}
    return render(request, 'home.html', context)

def ci_info(request):
    context = {'CI_COURSE': settings.CI_COURSE}
    return render(request, 'ci_info.html', context)
