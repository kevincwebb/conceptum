from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.shortcuts import render, redirect

from forms import Stage1Configure

from nodemanager.models import CITreeInfo, ConceptNode
from profiles.models import ContributorProfile

def dispatch(request):
    """
    Redirects to the correct view function based on whether or not a
    Stage 1 process has been started.
    """

    auth = ContributorProfile.auth_status(request.user)
    if not auth:
        raise PermissionDenied

    if not CITreeInfo.get_master_tree_root() and auth == 'staff':
        return redirect('stage1 setup')
    else:
        return landing(request)

def setup(request):
    """
    If the Stage 1 Process hasn't been set up yet, allow a superuser
    to configure it.
    """

    auth = ContributorProfile.auth_status(request.user)
    if auth != 'staff':
        raise PermissionDenied

    # If the stage has already been set up, issue a warning to the user.
    root = CITreeInfo.get_master_tree_root()
    if root:
        warning = True
    else:
        warning = False

    form = Stage1Configure()
    return render(request, 'cistage1/configure.html', {'form': form, 'warning': warning})

def configure(request):
    """
    Process the configuration form for a Stage 1 Process.

    TODO: add form error checking/redirects
    """

    auth = ContributorProfile.auth_status(request.user)
    if auth != 'staff' or request.method != 'POST':
        raise PermissionDenied

    form = Stage1Configure(request.POST)
    if form.is_valid():

        # If there is an old root, make it no longer the master.
        old_master = CITreeInfo.get_master_tree_root()
        if old_master is not None:
            old_master.is_master = False
            old_master.save()

        #Create the initial stage1 hierarchy from the submission
        #form. We need the CI Tree Info as well as one root node
        #to begin
        master_tree_info = CITreeInfo(is_master=True)
        master_tree_info.save()

        root_node = ConceptNode(
            ci_tree_info = master_tree_info,
            content = form.cleaned_data['root_name'],
            max_children = form.cleaned_data['max_children'],
            child_typename = form.cleaned_data['child_typename']
        )
        root_node.save()

        return redirect('stage1 dispatch')
    else:
        raise SuspiciousOperation

def landing(request):

    auth = ContributorProfile.auth_status(request.user)
    if not auth:
        raise PermissionDenied

    root = CITreeInfo.get_master_tree_root()
    if root:
        tree = root.get_descendants(include_self=True)

        # TODO: this probably shouldn't be here.  Move to nodemanager
        #for node in tree:
        #    if node.is_stage_finished():
        #        node.transition_node_state()

        return render(request,
                      'cistage1/landing.html',
                      {'tree': tree,
                       'user': request.user})
    else:
        if auth == 'staff':
            return redirect('stage1 setup')
        else:
            return render(request, 'cistage1/notstarted.html')
