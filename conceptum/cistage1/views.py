from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from nodemanager.models import CITreeInfo
# Create your views here.

def landing(request):

    root = CITreeInfo.get_master_tree_root()
    master_tree_set = root.get_descendants(include_self=True)
    user = request.user

    template = loader.get_template('cistage1/landing.html')
    context = RequestContext(request,
                             {'master_tree_set': master_tree_set,
                              'user': request.user})
    return HttpResponse(template.render(context))
