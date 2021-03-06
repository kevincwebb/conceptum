from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from nodemanager.models import ConceptNode
from ranking.models import RankingProcess, ValueCounter
from ranking.forms import RankingProcessSetupForm, BinaryChoiceForm

# TODO: get_or_404s for all nodes, ranking processes, etc

### Some helper functions ###
###############################################################################
def get_ct(model):
    """
    Given a model, return its ContentType (needed for generic keys
    declared in ranking app models).
    """
    return ContentType.objects.get_for_model(model)


def get_ranking_process(node):
    """
    Given a node, get the ranking process attached to it (via generic
    query).
    """
    return RankingProcess.objects.filter(object_id=node.id,
                                         content_type=get_ct(node)).get()
###############################################################################
    
def dispatch(request, node_id):
    """
    Depending on the state of the ranking process and whether or not
    the user is an admin, redirect to the correct view function with
    appropriate arguments.
    """

    node = ConceptNode.objects.filter(pk=node_id).get()
    ranking_process = get_ranking_process(node)

    if ranking_process.status == ranking_process.not_initialized:
        return redirect('setup', node_id=node_id)
    elif ranking_process.status == ranking_process.in_progress:
        return redirect('submit', node_id=node_id)
    else:
        return redirect('closed', node_id=node_id)

def setup(request, node_id):
    """
    Renders the admin setup form. Users who are not admin cannot set
    up a ranking process.
    """

    user = request.user
    node = ConceptNode.objects.filter(pk=node_id).get()
    form = RankingProcessSetupForm()

    ranking_process = get_ranking_process(node)
    if not ranking_process.status == ranking_process.not_initialized:
        return redirect('dispatch', node_id=node_id)

    if user in node.admin_set():
        return render(request,'ranking/rank_setup.html',
                      {"node": node,
                       "form": form})
    else:
        return render(request,'ranking/rank_cannot_setup.html',)


def get_setup(request, node_id):
    """
    Processes the data from a ranking process setup form appropriately.
    """

    node = get_object_or_404(ConceptNode,pk=node_id)
    user = request.user

    if request.method == 'POST':

        form = RankingProcessSetupForm(request.POST)
        if form.is_valid():

            #update ranking_process state based on admin form submission
            ranking_process = get_ranking_process(node)
            ranking_process.value_choices = form.cleaned_data.get('value_choices')
            ranking_process.status = ranking_process.in_progress
            ranking_process.save()

            #add corresponding value counter to each choice
            for choice in node.get_final_choices():
                value_counter = ValueCounter(content_type=get_ct(choice),
                                             object_id=choice.id,
                                             ranking_process=ranking_process,
                                             value=0)
                value_counter.save()

            return redirect('dispatch', node_id=node_id)

        else: #form has errors
            return render(request,'ranking/rank_setup.html',
                          {"node": node,
                           "form": form})
    else:
        return HttpResponse("error you're not supposed to be here")

def submit(request, node_id):
    """
    Renders the ranking submission form. Users are not allowed to
    submit twice.
    """

    user = request.user
    node = ConceptNode.objects.filter(pk=node_id).get()

    render_args = {'node': node,
                   'user': user,
                   'user_is_admin': user in node.admin_set()} #is boolean

    #users who already visited are assumed to have voted
    if user not in node.users_contributed_set():
        render_args['form'] = BinaryChoiceForm(node_id=node_id)
        return render(request, 'ranking/submit.html', render_args)
    else:
        return render(request, 'ranking/already_voted.html', render_args)

def get_submit(request, node_id):
    """
    Processes a ranking submission form from a user.
    """

    user = request.user
    node = ConceptNode.objects.filter(pk=node_id).get()

    if request.method == 'POST':

        form = BinaryChoiceForm(request.POST, node_id=node_id)
        if form.is_valid():

            choices = form.cleaned_data['final_choices']

            for choice in choices:
                counter = ValueCounter.objects.filter(object_id=choice.id, content_type=get_ct(choice)).get()
                counter.value += 1
                counter.save()

            return redirect('final sub', node_id)

        else: #form has errors
            return render(request, 'ranking/submit.html',
                          {'node': node,
                           'user': user,
                           'form': form,
                           'user_is_admin': user in node.admin_set()} #bool
                          )
    else:
        HttpResponse("not supposed to be here?")
    

def closed(request, node_id):
    """
    Only called if the ranking process is closed
    """
    return render(request, 'ranking/rank_closed.html')
