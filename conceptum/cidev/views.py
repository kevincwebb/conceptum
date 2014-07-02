from django.shortcuts import render

# For CI variable names.
from django.conf import settings

def index(request):
    context = {'CI_COURSE': settings.CI_COURSE}
    return render(request, 'cidev/index.html', context)
