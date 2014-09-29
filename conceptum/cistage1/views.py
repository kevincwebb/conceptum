from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext, loader

from nodemanager.models import CITreeInfo
from extras import close_rank_export_choices

# Create your views here.


def dispatch(request):

    if not CITreeInfo.get_master_tree_root():
        return redirect('stage1 setup')
    else:
        return redirect('landing')

def setup(request):
    return HttpResponse("yo lets set this up")

def landing(request):

    root = CITreeInfo.get_master_tree_root()
    master_tree_set = root.get_descendants(include_self=True)

    for node in master_tree_set:
        if node.is_stage_finished():
            node.transition_node_state()

    user = request.user

    template = loader.get_template('cistage1/landing.html')
    context = RequestContext(request,
                             {'master_tree_set': master_tree_set,
                              'user': request.user})
    return HttpResponse(template.render(context))
