import json

from django.core.exceptions import PermissionDenied
from django.forms.formsets import formset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from nodemanager.models import CITreeInfo, ConceptAtom, ConceptNode
from nodemanager.forms import AtomForm, CreateMergeForm, UpdateMergeFormSet
from profiles.models import ContributorProfile

def display(request, node_id):
    auth = ContributorProfile.auth_status(request.user)

    if not auth:
        raise PermissionDenied

    node = get_object_or_404(ConceptNode,pk=node_id)

    context = {
        'node': node,
        'user': request.user
    }

    if auth == 'staff':
        context['staff'] = node.get_contribution_sets()
    else:
        context['staff'] = False

    return display_func[(node.node_type, auth)](request, node, context)

def entry(request, node, context):
    """
    Dispatches a form to the user that allows them to enter in
    concepts freely. If they have already submitted choices, it
    returns a list of the choices.
    """

    # Only nodes in the "free entry" state can have nodes entered
    if node.node_type != 'F':
        return render(request, 'nodemanager/stage_error.html')

    # Only get this user's atoms for the node.
    atoms = ConceptAtom.objects.filter(concept_node=node.id).filter(user=request.user)

    # If the user has already visited, show them their picks
    if request.user in node.users_contributed_set():
        context['atoms'] = atoms
        return render(request, 'nodemanager/node_finalizedentry.html', context)

    # Otherwise, give them a form (which will be populated with their
    # choices if they have already made some)
    else:
        AtomFormSet = formset_factory(AtomForm, can_delete=True,
                                      max_num=node.max_children,
                                      extra=node.max_children,
                                      validate_max=True)
        context['formset'] = AtomFormSet(initial=[{'text': atom.text, 'pk': atom.pk} for atom in atoms])
        return render(request, 'nodemanager/node_entry.html', context)

def show_entries(request, node, context):
    # Only get this user's atoms for the node.
    atoms = ConceptAtom.objects.filter(concept_node=node.id).filter(user=request.user)

    context['node'] = node
    context['user'] = request.user

    context['atoms'] = atoms
    return render(request, 'nodemanager/node_finalizedentry.html', context)

def submit_entry(request, node_id):
    """
    This function processes a user-submitted form containing their
    brainstormed picks. It handles users deleting/modifying
    pre-entered picks, as well as entering new ones.
    """

    auth = ContributorProfile.auth_status(request.user)

    if not auth:
        raise PermissionDenied

    if request.method == 'POST':
        node = get_object_or_404(ConceptNode,pk=node_id)
        AtomFormSet = formset_factory(AtomForm, can_delete=True,
                                      max_num=node.max_children,
                                      extra=node.max_children,
                                      validate_max=True)

        formset = AtomFormSet(request.POST)

        if formset.is_valid():

            #We iterate through each form in the formset, which
            #represents a different concept entered. If there is data
            #in the form, the user has either edited an existing
            #concept or entered a new one.
            for form in formset:
                form_text = form.cleaned_data.get('text')
                pk = form.cleaned_data.get('pk')

                if form_text:

                    if not pk:
                        new_atom = ConceptAtom(
                            concept_node=node,
                            user=request.user,
                            text=form_text,
                            final_choice=False
                        )
                        new_atom.save()
                        continue

                    #if there is an associated pk, get the model instance
                    atom = ConceptAtom.objects.filter(pk=pk).get()

                    if not form_text == atom.text: #update if necessary
                        atom.text = form_text
                        atom.save()
                    if form in formset.deleted_forms: #or delete it
                        atom.delete()

            return HttpResponse('{"success": true}')
        else:
            reason = ''
            for (i, form) in enumerate(formset.errors):
                for field, problems in form.iteritems():
                    reason += 'Entry %d, %s:\\n'
                    for problem in problems:
                        reason += '  %s\\n' % problem
            return HttpResponse('{"success": false, "reason": "%s"}' % reason)
    else:
        return redirect('stage1 dispatch')

def finalize(request, node_id):
    """
    This function is called when a user makes a final submission, and
    needs to be added to the list of users that have submitted items
    """

    auth = ContributorProfile.auth_status(request.user)

    if not auth or request.method != 'POST':
        raise PermissionDenied

    node = get_object_or_404(ConceptNode,pk=node_id)
    if not request.user in node.users_contributed_set(): #no duplicates
        node.user.add(request.user)

    if node.is_stage_finished():
        node.transition_node_state()

    return HttpResponse('{"success": true}')

def advance(request, node_id):
    """
    Administratively advance a node to the next step.
    """

    auth = ContributorProfile.auth_status(request.user)

    if auth != 'staff' or request.method != 'POST':
        raise PermissionDenied

    node = get_object_or_404(ConceptNode,pk=node_id)
    node.transition_node_state()

    return HttpResponse('{"success": true}')

def merge(request, node, context):
    """
    This function gets all the concepts for a specified node and
    renders a form that allows an admin to merge/unmerge concept atoms
    """

    # Hack to disable the "admin" dropdown, since it makes no sense on the merge page.
    context['staff'] = False

    # Only if we're in the merging stage.
    if node.node_type != 'M':
        return render(request, 'nodemanager/stage_error.html')

    #populate the form with all the existing concept atoms for that node
    create_form = CreateMergeForm(node=node)
    edit_formset = UpdateMergeFormSet(initial=[{'pk': atom.pk} for atom in ConceptAtom.get_final_atoms(node)])

    context['create_form'] = create_form
    context['edit_formset'] = edit_formset

    return render(request, 'nodemanager/node_merge.html', context)

def submit_merge(request, node_id):
    """
    This function handles a submitted form containing information
    about merging concepts.
    """

    auth = ContributorProfile.auth_status(request.user)

    if auth != 'staff':
        raise PermissionDenied

    if request.method == 'POST':
        node = get_object_or_404(ConceptNode,pk=node_id)

        print request.POST
        return HttpResponse('{"success": true}')


        # note that "form" could be either a single form or a formset
        # depending on whether the user did a 'add merge' or an
        # 'update merge'. For this reason, we have to do an additional
        # attribute check
        if form.is_valid(): #could be a form or a formset depending on request

            # user merged under a new concept atom
            if hasattr(form,'add_merge_id') and form.add_merge_id in request.POST:
                new_atom = ConceptAtom(concept_node=node,
                                       user=request.user,
                                       text=form.cleaned_data.get('new_atom_name'),
                                       final_choice=True,)
                new_atom.save()
                new_atom.add_merge_atoms(form.cleaned_data.get('free_atoms'))
            #user merged atoms to an existing concept atom
            elif hasattr(form,'subtract_merge_id') and form.subtract_merge_id in request.POST:
                curr_atom = form.cleaned_data.get('merged_atoms')

                curr_atom.add_merge_atoms(form.cleaned_data.get('free_atoms'))

            #user has edited an existing concept atom
            else:
                formset = form #small name-change to enhance clarity

                for form in formset:

                    if form.cleaned_data.get('delete'):
                        atom = ConceptAtom.objects.filter(pk=form.cleaned_data.get('pk')).get()
                        atom.delete()
                    else:
                        for atom in form.cleaned_data.get('choices'):
                            atom.merged_atoms = None
                            atom.save()

            return redirect('merge', node_id=node.id)

        #the form is invalid, and we redirect the errors to the user
        else:
            render_args = {'node': node,
                           'user': request.user}

            #need to set arguments differently based on whether it was
            #an add merge or subtract merge, since this chooses
            #between a form or formset
            if merge_type == 'add merge':
                render_args['create_form'] = form
                render_args['edit_formset'] = UpdateMergeFormSet(initial=[{'pk': atom.pk} for atom in ConceptAtom.get_final_atoms(node)])

            elif merge_type == 'subtract merge':
                render_args['create_form'] = CreateMergeForm(node)
                render_args['edit_formset'] = form
            else:
                #again, should never be here
                print "ERROR unknown merge type"

            return render(request, 'nodemanager/merge.html', context)
    else:
        return redirect('stage1 dispatch')







def get_merge(request, node_id, merge_type=None):
    """
    This function handles a submitted form containing information
    about merging concepts.
    """

    auth = ContributorProfile.auth_status(request.user)

    if auth != 'staff':
        raise PermissionDenied

    if request.method == 'POST':
        node = get_object_or_404(ConceptNode,pk=node_id)

        #differentiate between different forms
        if merge_type == 'add merge':
            form = CreateMergeForm(request.POST, node=node)
        elif merge_type == 'subtract merge':
            form = UpdateMergeFormSet(request.POST)
        else:
            #should never get here
            print "ERROR No Merge type was called"

        # note that "form" could be either a single form or a formset
        # depending on whether the user did a 'add merge' or an
        # 'update merge'. For this reason, we have to do an additional
        # attribute check
        if form.is_valid(): #could be a form or a formset depending on request

            # user merged under a new concept atom
            if hasattr(form,'add_merge_id') and form.add_merge_id in request.POST:
                new_atom = ConceptAtom(concept_node=node,
                                       user=request.user,
                                       text=form.cleaned_data.get('new_atom_name'),
                                       final_choice=True,)
                new_atom.save()
                new_atom.add_merge_atoms(form.cleaned_data.get('free_atoms'))
            #user merged atoms to an existing concept atom
            elif hasattr(form,'subtract_merge_id') and form.subtract_merge_id in request.POST:
                curr_atom = form.cleaned_data.get('merged_atoms')

                curr_atom.add_merge_atoms(form.cleaned_data.get('free_atoms'))

            #user has edited an existing concept atom
            else:
                formset = form #small name-change to enhance clarity

                for form in formset:

                    if form.cleaned_data.get('delete'):
                        atom = ConceptAtom.objects.filter(pk=form.cleaned_data.get('pk')).get()
                        atom.delete()
                    else:
                        for atom in form.cleaned_data.get('choices'):
                            atom.merged_atoms = None
                            atom.save()

            return redirect('merge', node_id=node.id)

        #the form is invalid, and we redirect the errors to the user
        else:
            render_args = {'node': node,
                           'user': request.user}

            #need to set arguments differently based on whether it was
            #an add merge or subtract merge, since this chooses
            #between a form or formset
            if merge_type == 'add merge':
                render_args['create_form'] = form
                render_args['edit_formset'] = UpdateMergeFormSet(initial=[{'pk': atom.pk} for atom in ConceptAtom.get_final_atoms(node)])

            elif merge_type == 'subtract merge':
                render_args['create_form'] = CreateMergeForm(node)
                render_args['edit_formset'] = form
            else:
                #again, should never be here
                print "ERROR unknown merge type"

            return render(request, 'nodemanager/merge.html', context)
    else:
        return redirect('stage1 dispatch')

def finalize_merge(request, node_id):
    """
    Once the admin has okayed the merged state of the concept atoms,
    this function updates the database accordingly
    """

    node = get_object_or_404(ConceptNode,pk=node_id)
    for atom in ConceptAtom.get_unmerged_atoms(node):
        atom.final_choice = True
        atom.save()

    #return redirect(reverse('final sub', args=[node_id]))
    return HttpResponse('fix finalize_merge')



# Maps node state to the appropriate display function.
display_func = {
    ('F', 'staff'): entry,
    ('F', 'contrib'): entry,

    ('M', 'staff'): merge,
    ('M', 'contrib'): show_entries,
}
