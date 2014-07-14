from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext, loader

from nodemanager.models import CITreeInfo, ConceptNode, ConceptAtom
from nodemanager.forms import AtomForm
# Create your views here.

def entry(request, node_id, redirected=False):

    node = ConceptNode.objects.filter(pk=node_id).get()
    form = AtomForm();

    template = loader.get_template('nodemanager/entry.html')
    context = RequestContext(request,
                             {'node': node,
                              'user': request.user,
                              'form': form,
                              'redirected': redirected},)
    return HttpResponse(template.render(context))

def get_entry(request, node_id):
    print node_id
    if not ConceptNode.objects.filter(pk=node_id).get() == None:
        print "we have a concept node!"
    if request.method == 'POST':
        form = AtomForm(request.POST)
        if form.is_valid():
            new_atom = ConceptAtom(
                concept_node=ConceptNode.objects.filter(pk=node_id).get(),
                user=request.user,
                text=form.cleaned_data['text'],
                final_choice=False
            )
            # new_atom.text = form.cleaned_data['text']
            # new_atom.user = request.user
            # new_atom.concept_node =
            new_atom.save()


        print "i got this text:", form['text']
        return redirect('redirected free entry',
                        node_id=node_id, redirected=True)
    else:
        return HttpResponse("Uh oh, didn't get the entry.")

def prune(request, node_id):

    node = ConceptNode.objects.filter(pk=node_id).get()

    template = loader.get_template('nodemanager/prune.html')
    context = RequestContext(request,
                             {'node': node,
                              'user': request.user},)
    return HttpResponse(template.render(context))



def rank(request, node_id):
    return HttpResponse("this is rank")
