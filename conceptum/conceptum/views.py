from django.shortcuts import render

# For CI variable names.
from django.conf import settings

def home(request):
    context = {}
    return render(request, 'home.html', context)
