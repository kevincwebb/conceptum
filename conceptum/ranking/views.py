from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse

from nodemanager.models import ConceptNode
from ranking.models import RankingProcess

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

def setup(request, node_id, admin=False):

    user = request.user
    node = ConceptNode.objects.filter(pk=node_id).get()

    if user in node.admin_set():
        return render(request,'ranking/rank_setup.html',)
    else:
        return render(request,'ranking/rank_cannot_setup.html',)

def submit(request, node_id):

    user = request.user
    node = ConceptNode.objects.filter(pk=node_id).get()

    if user not in node.users_contributed_set():

        if user in node.admin_set():
            return render(request, 'ranking/rank_submit_admin.html',)
        else:
            return render(request, 'ranking/rank_submit_user.html',)

    else: #user has already voted

        if user in node.admin_set():
            return render(request, 'ranking/rank_already_voted_admin.html',)
        else:
            return render(request, 'ranking/rank_already_voted_user.html',)

def closed(request, node_id ):
    return render(request, 'ranking/rank_closed.html')


# return render(request, 'nodemanager/entry.html',
#                   {'node': get_object_or_404(ConceptNode,pk=node_id),
#                    'user': request.user,
#                    'form': form}
# )
