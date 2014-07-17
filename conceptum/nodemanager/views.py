from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory

from nodemanager.models import CITreeInfo, ConceptNode, ConceptAtom
from nodemanager.forms import AtomForm, AtomFormSet
# Create your views here.

getNode = lambda node_id: ConceptNode.objects.filter(pk=node_id).get()

# Displays a form and allows users to enter new concept atoms.
def entry(request, node_id, redirected=False):

    node = getNode(node_id)
    user = request.user
    atoms = ConceptAtom.objects.filter(user=user)

    form_params = {
        'extra' : 5,
    }
    formset = formset_factory(AtomForm, **form_params)

    template = loader.get_template('nodemanager/entry.html')
    context = RequestContext(request,
                             {'node': node,
                              'user': user,
                              'formset': formset,
                              'redirected': redirected},)
    return HttpResponse(template.render(context))

# Upon entering a concept form, get_entry() verifies it and prompts
# the user to enter another, or returns a new form if the atom was
# incorrectly entered
def get_entry(request, node_id):
    if request.method == 'POST':
        formset = AtomFormSet(request.POST)
        if formset.is_valid():

            for form in formset:
                print form.cleaned_data.get('text')#['text']

                text = form.cleaned_data.get('text')

                if text: #only non-empty forms have text
                    new_atom = ConceptAtom(
                        concept_node=getNode(node_id),
                        user=request.user,
                        text=form.cleaned_data['text'],
                        final_choice=False
                    )
                    new_atom.save()

            return redirect('redirected free entry',
                            node_id=node_id, redirected=True)
        else:
            form = AtomFormSet(AtomForm, extra=5) #return new form

    return render(request, 'nodemanager/entry.html',
                  {'node': getNode(node_id),
                   'user': request.user,
                   'form': form})

def detail(request, node_id):

    node = getNode(node_id)
    user = request.user

    user_atoms = ConceptAtom.objects.filter(user=user)
    if user in node.users_contributed_set():
        template = 'nodemanager/atomlist.html'
    else:
        template = 'nodemanager/editatomlist.html'

    return render(request, template,
                  {'node': node,
                   'user': user,
                   'atoms': user_atoms,})

def prune(request, node_id):

    node = getNode(node_id)

    template = loader.get_template('nodemanager/prune.html')
    context = RequestContext(request,
                             {'node': node,
                              'user': request.user},)
    return HttpResponse(template.render(context))



def rank(request, node_id):
    return HttpResponse("this is rank")

def add_finished_user(request, node_id):

    node = getNode(node_id)
    user = request.user
    if not user in node.users_contributed_set():
        node.user.add(user)

    return redirect(reverse('landing'))
