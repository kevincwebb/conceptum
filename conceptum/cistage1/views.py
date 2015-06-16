from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext, loader

from nodemanager.models import CITreeInfo, ConceptNode
from forms import Stage1SetupForm

# Create your views here.


def dispatch(request):
    """
    Redirects to the correct view function based on whether or not a
    Stage 1 process has been started.
    """

    if not CITreeInfo.get_master_tree_root():
        print "going to setup"
        return redirect('stage1 setup')
    else:
        print "going to landing"
        return redirect('landing')

def setup(request):
    """
    If the Stage 1 Process hasn't been set up yet, allow a superuser
    to configure it.
    """

    user = request.user
    if not user.is_superuser:
        return render(request, 'cistage1/setup_error.html')
    else:
        form = Stage1SetupForm()
        return render(request, 'cistage1/stage1_setup_form.html', {'form': form})
    
def get_setup(request):
    """
    Process the setup form for a Stage 1 Process.

    TODO: add form error checking/redirects
    """

    if request.method == 'POST':

        form = Stage1SetupForm(request.POST)
        if form.is_valid():

            #Create the initial stage1 hierarchy from the submission
            #form. We need the CI Tree Info as well as one root node
            #to begin
            master_tree_info = CITreeInfo(is_master=True)
            master_tree_info.save()
            master_tree_info.admins.add(*form.cleaned_data.get('admins'))
            master_tree_info.users.add(*form.cleaned_data.get('users'))

            root_node = ConceptNode(
                ci_tree_info=master_tree_info,
                content="Topic: Testing Things!"
            )
            root_node.save()
            
            return redirect('stage1 dispatch')
        else:
            return HttpResponse("some error handling here")
            #do some error handling

            


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
