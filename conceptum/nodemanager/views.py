from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse

from nodemanager.models import CITreeInfo, ConceptNode, ConceptAtom
from nodemanager.forms import AtomFormSet, CreateMergeForm, UpdateMergeFormSet

getNode = lambda node_id: ConceptNode.objects.filter(pk=node_id).get()

# add/edit/remove interface for concept atoms
def entry(request, node_id, redirected=False):

    node = getNode(node_id)
    user = request.user
    atoms = ConceptAtom.objects.filter(user=user)
    context = RequestContext(request,
                             {'node': node,
                              'user': user,
                              'redirected': redirected},)
    if user in node.users_contributed_set():
        template = loader.get_template('nodemanager/atomlist.html')
        context['atoms'] = atoms
    else:
        formset = AtomFormSet(initial=[{'text': atom.text,
                                        'pk': atom.pk} for atom in atoms])
        context['formset'] = formset
        template = loader.get_template('nodemanager/entry.html')


    return HttpResponse(template.render(context))

def get_entry(request, node_id):
    if request.method == 'POST':
        formset = AtomFormSet(request.POST)

        if formset.is_valid():
            for form in formset:
                form_text = form.cleaned_data.get('text')
                pk = form.cleaned_data.get('pk')

                if form_text: #if there was initial data in the form

                    if not pk: #new entries do not have a pk
                        new_atom = ConceptAtom(
                            concept_node=getNode(node_id),
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
                  {'node': getNode(node_id),
                   'user': request.user,
                   'form': form})

def merge(request, node_id):

    node = getNode(node_id)
    create_form = CreateMergeForm()
    edit_formset = UpdateMergeFormSet(initial=[{'pk': atom.pk} for atom in ConceptAtom.get_final_atoms()])

    template = loader.get_template('nodemanager/merge.html')
    context = RequestContext(request,
                             {'node': node,
                              'user': request.user,
                              'create_form': create_form,
                              'edit_formset': edit_formset},)
    return HttpResponse(template.render(context))

def get_merge(request, node_id, merge_type=None):

    node = getNode(node_id)
    user = request.user

    if request.method == 'POST':

        #differentiate between different forms
        if merge_type == 'new merge':
            form = CreateMergeForm(request.POST)
            print "new merge form!"
        elif merge_type == 'edit merge':
            form = UpdateMergeFormSet(request.POST)
            print "update merge form!"
        else:
            print "No Merge type was called"


        # note that "form" could be either a single form or a formset
        # depending on whether the user did a 'new merge' or an
        # 'update merge'. For this reason, we have to do an additional
        # attribute check
        if form.is_valid(): #could be a form or a formset depending on request

            # user merged under a new concept atom
            if hasattr(form,'new_merge_id') and form.new_merge_id in request.POST:
                print "new merge id"
                new_atom = ConceptAtom(concept_node=node,
                                       user=user,
                                       text=form.cleaned_data.get('new_atom_name'),
                                       final_choice=True,)
                new_atom.save()
                new_atom.add_merge_atoms(form.cleaned_data.get('free_atoms'))
            #user merged atoms to an existing concept atom
            elif hasattr(form,'edit_merge_id') and form.edit_merge_id in request.POST:
                print "edit merge id"
                curr_atom = form.cleaned_data.get('merged_atoms')

                curr_atom.add_merge_atoms(form.cleaned_data.get('free_atoms'))

            #user has edited an existing concept atom
            else:
                print "it's a formset!"
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

        else:
            print "form is invalid"
            print form.errors

            render_args = {'node': node,
                           'user': user}
            if merge_type == 'new merge':
                print "new merge!"
                render_args['create_form'] = form
                render_args['edit_formset'] = UpdateMergeFormSet(initial=[{'pk': atom.pk} for atom in ConceptAtom.get_final_atoms()])

            elif merge_type == 'update merge':
                print "update merge!"
                render_args['create_form'] = CreateMergeForm()
                render_args['edit_formset'] = form
            else:
                print "whatwhatwhat"

            print render_args
            template = loader.get_template('nodemanager/merge.html')
            context = RequestContext(request, render_args)
            return HttpResponse(template.render(context))
            # create_form = CreateMergeForm()
            # edit_formset = UpdateMergeFormSet(initial=[{'pk': atom.pk} for atom in ConceptAtom.get_final_atoms()])


            # print render_args
            # return render(request, 'nodemanager/merge.html', render_args)

def rank(request, node_id):
    return HttpResponse("this is rank")

def add_finished_user(request, node_id):

    node = getNode(node_id)
    user = request.user
    if not user in node.users_contributed_set():
        node.user.add(user)

    return redirect(reverse('landing'))
