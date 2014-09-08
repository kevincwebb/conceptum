from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse

from nodemanager.models import ConceptNode
from ranking.models import RankingProcess
from ranking.forms import RankingProcessSetupForm, BinaryChoiceForm

# TODO: get_or_404s for all nodes, ranking processes, etc

def dispatch(request, node_id):

    node = ConceptNode.objects.filter(pk=node_id).get()
    ranking_process = RankingProcess.objects.filter(parent__pk=node_id).get()

    if ranking_process.status == ranking_process.not_initialized:
        return redirect('setup', node_id=node_id)
    elif ranking_process.status == ranking_process.in_progress:
        return redirect('submit', node_id=node_id)
    else:
        return redirect('closed', node_id=node_id)

def setup(request, node_id):

    user = request.user
    node = ConceptNode.objects.filter(pk=node_id).get()
    form = RankingProcessSetupForm()

    ranking_process = RankingProcess.objects.filter(parent__id=node_id).get()
    if not ranking_process.status == ranking_process.not_initialized:
        return redirect('dispatch', node_id=node_id)

    if user in node.admin_set():
        return render(request,'ranking/rank_setup.html',
                      {"node": node,
                       "form": form})
    else:
        return render(request,'ranking/rank_cannot_setup.html',)


def get_setup(request, node_id):

    node = get_object_or_404(ConceptNode,pk=node_id)
    user = request.user

    if request.method == 'POST':

        form = RankingProcessSetupForm(request.POST)
        if form.is_valid():

            ranking_process = RankingProcess.objects.filter(parent__pk=node_id).get()
            ranking_process.choices = node.get_final_choices()
            ranking_process.value_choices = form.cleaned_data.get('value_choices')
            ranking_process.status = ranking_process.in_progress
            ranking_process.save()

            return redirect('dispatch', node_id=node_id)
            #return HttpResponse("valid form!...db code tba, {0}".format(form.cleaned_data.get('value_choices')))
        else:
            return render(request,'ranking/rank_setup.html',
                          {"node": node,
                           "form": form})
    else:
        return HttpResponse("error you're not supposed to be here")

def submit(request, node_id):

    user = request.user
    node = ConceptNode.objects.filter(pk=node_id).get()

    form = BinaryChoiceForm(node_id=node_id)
    
    if user not in node.users_contributed_set():

        if user in node.admin_set():
            return render(request, 'ranking/rank_submit_admin.html',
                          {'node': node,
                           'user': user,
                           'form': form}
                      )

        else:
            return render(request, 'ranking/rank_submit_user.html',)

    else: #user has already voted

        if user in node.admin_set():
            return render(request, 'ranking/rank_already_voted_admin.html',)
        else:
            return render(request, 'ranking/rank_already_voted_user.html',)

def get_submit(request, node_id):

    user = request.user
    node = ConceptNode.objects.filter(pk=node_id).get()

    
    #return redirect('final sub', node_id=node_id)

def closed(request, node_id ):
    return render(request, 'ranking/rank_closed.html')


# return render(request, 'nodemanager/entry.html',
#                   {'node': get_object_or_404(ConceptNode,pk=node_id),
#                    'user': request.user,
#                    'form': form}
# )
