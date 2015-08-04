from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext, loader

from nodemanager.models import CITreeInfo, ConceptNode
from forms import Stage1SetupForm

def check_admin(request):
    """
    Authentication helper.  Returns False if the user is not authenticated.  If
    the user is authenticated, returns their account status (i.e., 'staff' or
    'contrib').
    """

    if request.user.is_anonymous() or not request.user.is_authenticated():
        return False
    if not request.user.is_staff and not request.user.profile.is_contrib:
        return False

    if request.user.is_staff:
        return 'staff'

    if request.user.profile.is_contrib:
        return 'contrib'

    # Shouldn't get here.
    return False

# Create your views here.

def dispatch(request):
    """
    Redirects to the correct view function based on whether or not a
    Stage 1 process has been started.
    """

    auth = check_admin(request)
    if not auth:
        return render(request, 'cistage1/forbidden.html')

    if not CITreeInfo.get_master_tree_root() and auth == 'staff':
        return redirect('stage1 setup')
    else:
        return landing(request)

def setup(request):
    """
    If the Stage 1 Process hasn't been set up yet, allow a superuser
    to configure it.
    """

    auth = check_admin(request)
    if auth != 'staff':
        return render(request, 'cistage1/forbidden.html')

    # If the stage has already been set up, issue a warning to the user.
    root = CITreeInfo.get_master_tree_root()
    if root:
        warning = True
    else:
        warning = False

    form = Stage1SetupForm()
    return render(request, 'cistage1/configure.html', {'form': form, 'warning': warning})
    
def configure(request):
    """
    Process the configuration form for a Stage 1 Process.

    TODO: add form error checking/redirects
    """

    auth = check_admin(request)
    if auth != 'staff':
        return render(request, 'cistage1/forbidden.html')

    if request.method == 'POST':

        form = Stage1SetupForm(request.POST)
        if form.is_valid():

            #TODO: If there is an old root, nuke it.

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

    return HttpResponse("Something went wrong.  Sorry!")

def landing(request):

    auth = check_admin(request)
    if not auth:
        return render(request, 'cistage1/forbidden.html')

    root = CITreeInfo.get_master_tree_root()
    if root:
        master_tree_set = root.get_descendants(include_self=True)
    
        for node in master_tree_set:
            if node.is_stage_finished():
                node.transition_node_state()
    
        return render(request,
                      'cistage1/landing.html',
                      {'master_tree_set': master_tree_set,
                       'user': request.user})
    else:
        return HttpResponse("No Stage 1 process has been started.")
