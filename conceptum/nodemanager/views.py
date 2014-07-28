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

    top_level_merged_atoms = ConceptAtom.get_final_atoms()

    # for atom in top_level_merged_atoms:
    #     initial['pk']=atom.pk
    #     qset_dict['pk']=

    edit_formset = UpdateMergeFormSet(initial=[{'pk': atom.pk} for atom in top_level_merged_atoms])

    # for form in edit_formset:
    #     #print form.as_p()
    #     atom_pk = form['pk'].value()
    #     print "atom_pk", atom_pk
    #     qset = ConceptAtom.objects.filter(merged_atoms__pk=atom_pk)
    #     print "THE QUERYSET: ", qset
    #     print "THE OLD FORM: ", form['choices'].data()
    #     form['choices'].queryset = qset
    #     print "THE FORM: ", form['choices'].value()



    template = loader.get_template('nodemanager/merge.html')
    context = RequestContext(request,
                             {'node': node,
                              'user': request.user,
                              'create_form': create_form,
                              'edit_formset': edit_formset},)
    return HttpResponse(template.render(context))

def get_merge(request, node_id):

    node = getNode(node_id)
    user = request.user

    if request.method == 'POST':

        form = CreateMergeForm(request.POST)

        if form.is_valid():

            if form.new_merge_id in request.POST:
                new_atom = ConceptAtom(concept_node=node,
                                       user=user,
                                       text=form.cleaned_data.get('new_atom_name'),
                                       final_choice=True,)
                new_atom.save()
                new_atom.add_merge_atoms(form.cleaned_data.get('free_atoms'))
            else:
                curr_atom = form.cleaned_data.get('merged_atoms')

                curr_atom.add_merge_atoms(form.cleaned_data.get('free_atoms'))

                return redirect('merge', node_id=node.id)

        else:
            return render(request, 'nodemanager/merge.html',
                          {'node': node,
                           'user': user,
                           'form': form})

def rank(request, node_id):
    return HttpResponse("this is rank")

def add_finished_user(request, node_id):

    node = getNode(node_id)
    user = request.user
    if not user in node.users_contributed_set():
        node.user.add(user)

    return redirect(reverse('landing'))
