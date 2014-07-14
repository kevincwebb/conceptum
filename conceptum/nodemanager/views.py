from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from nodemanager.models import CITreeInfo, ConceptNode
from nodemanager.forms import AtomForm
# Create your views here.

def entry(request, node_id):

    node = ConceptNode.objects.filter(pk=node_id).get()
    form = AtomForm();

    template = loader.get_template('nodemanager/entry.html')
    context = RequestContext(request,
                             {'node': node,
                              'user': request.user,
                              'form': form},)
    return HttpResponse(template.render(context))

def prune(request, node_id):

    node = ConceptNode.objects.filter(pk=node_id).get()

    template = loader.get_template('nodemanager/prune.html')
    context = RequestContext(request,
                             {'node': node,
                              'user': request.user},)
    return HttpResponse(template.render(context))



def rank(request, node_id):
    return HttpResponse("this is rank")
