from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse

from nodemanager.models import CITreeInfo, ConceptNode, ConceptAtom
from nodemanager.forms import AtomFormSet, CreateMergeForm, UpdateMergeFormSet

# add/edit/remove interface for concept atoms
def entry(request, node_id, redirected=False):
    """
    Dispatches a form to the user that allows them to enter in
    concepts freely. If they have already submitted choices, it
    returns a list of the choices.
    """

    node = get_object_or_404(ConceptNode,pk=node_id)
    user = request.user
    atoms = ConceptAtom.objects.filter(user=user) #only get the user's
                                                  #atoms
    context = RequestContext(request,
                             {'node': node,
                              'user': user,
                              'redirected': redirected},)
    
    # Only nodes in the "free entry" state can have nodes entered
    if not node.node_type == 'F':
        return render(request, 'nodemanager/stage_error.html')

    # If the user has already visited, show them their picks
    if user in node.users_contributed_set():
        template = loader.get_template('nodemanager/atomlist.html')
        context['atoms'] = atoms
    
    # Otherwise, give them a form (which will be populated with their
    # choices if they have already made some)
    else:
        formset = AtomFormSet(initial=[{'text': atom.text,
                                        'pk': atom.pk} for atom in atoms])
        context['formset'] = formset
        template = loader.get_template('nodemanager/entry.html')

    return HttpResponse(template.render(context))

def get_entry(request, node_id):
    """
    This function processes a user-submitted form containing their
    brainstormed picks. It handles users deleting/modifying
    pre-entered picks, as well as entering new ones.
    """
    if request.method == 'POST':
        
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
                            concept_node=get_object_or_404(ConceptNode,pk=node_id),
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

            return redirect('redirected free entry',
                            node_id=node_id, redirected=True)
        else:
            return redirect('free entry', node_id=node_id)

    return render(request, 'nodemanager/entry.html',
                  {'node': get_object_or_404(ConceptNode,pk=node_id),
                   'user': request.user,
                   'form': form})

def merge(request, node_id):
    """
    This function gets all the concepts for a specified node and
    renders a form that allows an admin to merge/unmerge concept atoms
    """

    user = request.user
    node = get_object_or_404(ConceptNode,pk=node_id)

    # only for the merging stage
    if not node.node_type == 'P':
        return render(request, 'nodemanager/stage_error.html')

    #populate the form with all the existing concept atoms for that
    #node
    create_form = CreateMergeForm(node=node)
    edit_formset = UpdateMergeFormSet(initial=[{'pk': atom.pk} for atom in ConceptAtom.get_final_atoms(node)])

    template = loader.get_template('nodemanager/merge.html')
    context = RequestContext(request,
                             {'node': node,
                              'user': request.user,
                              'create_form': create_form,
                              'edit_formset': edit_formset},)
    return HttpResponse(template.render(context))

def get_merge(request, node_id, merge_type=None):
    """
    This function handles a submitted form containing information
    about merging concepts.
    """

    node = get_object_or_404(ConceptNode,pk=node_id)
    user = request.user

    if request.method == 'POST':

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
                                       user=user,
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
                           'user': user}

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

            template = loader.get_template('nodemanager/merge.html')
            context = RequestContext(request, render_args)
            return HttpResponse(template.render(context))

def finalize_merge(request, node_id):
    """
    Once the admin has okayed the merged state of the concept atoms,
    this function updates the database accordingly
    """

    node = get_object_or_404(ConceptNode,pk=node_id)
    for atom in ConceptAtom.get_unmerged_atoms(node):
        atom.final_choice = True
        atom.save()

    return redirect(reverse('final sub', args=[node_id]))

def add_finished_user(request, node_id):
    """
    This function is called when a user makes a final submission, and
    needs to be added to the list of users that have submitted items
    """

    node = get_object_or_404(ConceptNode,pk=node_id)
    user = request.user
    if not user in node.users_contributed_set(): #no duplicates
        node.user.add(user)

    return redirect(reverse('landing'))
