from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext, loader

from nodemanager.models import CITreeInfo
from forms import Stage1SetupForm

# Create your views here.


def dispatch(request):
    """
    Redirects to the correct view function based on whether or not a
    Stage 1 process has been started.
    """

    if not CITreeInfo.get_master_tree_root():
        return redirect('stage1 setup')
    else:
        return redirect('landing')

def setup(request):

    user = request.user

    if not user.is_superuser:
        return render(request, 'cistage1/setup_error.html')
    else:
        form = Stage1SetupForm()
        return render(request, 'cistage1/stage1_setup_form.html', {'form': form})
    
    return HttpResponse("yo lets set this up")

def get_setup(request):
    return HttpResponse("Got it!")

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
