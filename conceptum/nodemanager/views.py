from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse

from nodemanager.models import CITreeInfo, ConceptNode, ConceptAtom
from nodemanager.forms import AtomFormSet, CreateMergeForm

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

def prune(request, node_id):

    node = getNode(node_id)
    form = CreateMergeForm()

    template = loader.get_template('nodemanager/prune.html')
    context = RequestContext(request,
                             {'node': node,
                              'user': request.user,
                              'form': form},)
    return HttpResponse(template.render(context))

def get_merge(request, node_id):

    node = getNode(node_id)
    user = request.user

    if request.method == 'POST':

        form = CreateMergeForm(request.POST)

        if form.is_valid():

            # TODO: DB code goes here
            if form.new_merge_id in request.POST:
                print form.cleaned_data.get('new_atom_name')
            else:
                print form.cleaned_data.get('merged_atoms')

            print form.cleaned_data.get('free_atoms')

            return redirect('prune', node_id=node.id)

        else:
            print form.errors

            return render(request, 'nodemanager/prune.html',
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
