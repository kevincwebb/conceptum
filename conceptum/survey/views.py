from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse_lazy, resolve, reverse
from django.views import generic
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.template import Context, Template
from django.views.generic.detail import SingleObjectMixin
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.utils.translation import ugettext_lazy as _
from braces.views import LoginRequiredMixin, UserPassesTestMixin
from exam.models import Exam, FreeResponseQuestion, FreeResponseResponse, MultipleChoiceQuestion, MultipleChoiceOption, MultipleChoiceResponse 
from .forms import AddFreeResponseForm, SelectConceptForm, AddMultipleChoiceForm, MultipleChoiceEditForm
from interviews.models import get_concept_list, Excerpt, DummyConcept
from profiles.mixins import ContribRequiredMixin


class SelectConceptView(LoginRequiredMixin, ContribRequiredMixin, generic.FormView,):
    """
    Lists all Concepts in the database, Select a concept to view the SurveyView
    """
    template_name = 'survey/select.html'
    form_class = SelectConceptForm
    
    def select(self, request):
        if request.method == 'POST':
            form = SelectConceptForm(request.POST)
            if form.is_valid():
                concept = form.cleaned_data.get('concept')
                return HttpResponseRedirect(reverse('survey_create', kwargs ={'pk' : concept.pk, 'question_type' : 'fr' }))
        else:
            form = SelectConceptForm()

        return render_to_response('index.html', {
        'form': form,
        })
    
    def form_valid(self, form):
        return self.select(self.request)
       

class SurveyCreateView(LoginRequiredMixin, ContribRequiredMixin, generic.View):

    def get(self, request, *args, **kwargs):
        view = ExcerptDetailView.as_view()
        return view(request, *args, **kwargs)

    
    def post(self, request, *args, **kwargs):
        if(self.kwargs['question_type'] == 'fr'):
            form = AddFreeResponseForm(request.POST)
            if (form.is_valid() ):
                view = AddFreeResponseView.as_view()
                return view(request, *args, **kwargs)
        
        elif(self.kwargs['question_type'] == 'mc'):
            form = AddMultipleChoiceForm(request.POST)
            if(form.is_valid()) :
                view = AddMultipleChoiceView.as_view()
                return view(request, *args, **kwargs)
        
        
        return HttpResponseRedirect(reverse('survey_create', kwargs ={ 'pk' : self.kwargs['pk']}))

class ExcerptDetailView(LoginRequiredMixin, generic.DetailView):
    """
    Lists All Excerpts related to a concept
    """
    model = DummyConcept
    template_name = 'survey/create.html'
    
    def get_context_data(self,**kwargs):
        context = super(ExcerptDetailView, self).get_context_data(**kwargs)
        concept_type = ContentType.objects.get_for_model(self.get_object())
        
        if(self.kwargs['question_type'] == 'mc'):
            context['form'] = AddMultipleChoiceForm
            context['question_type'] = 'multiple_choice'
            
        elif(self.kwargs['question_type'] == 'fr'):
            context['form'] = AddFreeResponseForm
            context['question_type'] = 'free_response'
            
        context['concept_id'] = self.kwargs['pk']
        context['excerpt_list']=Excerpt.objects.filter(content_type__pk=concept_type.id, object_id=self.get_object().id)
        return context
    
class AddFreeResponseView(LoginRequiredMixin, ContribRequiredMixin, generic.CreateView):
    """
    CreateView for a user to add a free response question to the survey.
    """
    model = FreeResponseQuestion
    template_name = 'survey/create.html'
    form_class = AddFreeResponseForm
    
    def form_valid(self, form):
        form.instance.content_object = DummyConcept.objects.get(pk = self.kwargs['pk'])
        form.instance.exam_id = Exam.objects.get(name = 'Survey').id
        return super(AddFreeResponseView, self).form_valid(form)

    def get_success_url(self):
        return reverse('survey_index')
    
    def get_context_data(self,**kwargs):
        context = super(AddFreeResponseView, self).get_context_data(**kwargs)
        context['concept_id'] = self.kwargs['pk']
        return context


class AddMultipleChoiceView(LoginRequiredMixin, ContribRequiredMixin, generic.CreateView):
    model = MultipleChoiceQuestion
    template_name = 'survey/create.html'
    form_class = AddMultipleChoiceForm
    
    def form_valid(self, form):
        form.instance.content_object = DummyConcept.objects.get(pk = self.kwargs['pk'])
        form.instance.exam_id = Exam.objects.get(name = 'Survey').id
        form.form_valid()
        return super(AddMultipleChoiceView, self).form_valid(form)
    
    def get_success_url(self):
        return reverse('survey_index')
    
    def get_context_data(self,**kwargs):
        context = super(AddMultipleChoiceView, self).get_context_data(**kwargs)
        context['concept_id'] = self.kwargs['pk']
        return context



class SurveyListView(LoginRequiredMixin,
                ContribRequiredMixin,
                generic.ListView):
    """
    View all questions created for the survey
    """
    
    model = MultipleChoiceOption
    template_name = 'survey/index.html'
    
    def get_context_data(self, **kwargs):
        context = super(SurveyListView, self).get_context_data(**kwargs)
        context['freeresponsequestion_list']=FreeResponseQuestion.objects.filter(exam = Exam.objects.get(name = 'Survey').id)
        context['multiplechoicequestion_list']=MultipleChoiceQuestion.objects.filter(exam = Exam.objects.get(name = 'Survey').id) 
        context['option_list']= MultipleChoiceOption.objects.all()
        return context


class FreeResponseEditView(LoginRequiredMixin,
               ContribRequiredMixin,
               generic.UpdateView):
    """
    FormView for a user to edit an existing Question
    """
    model = FreeResponseQuestion
    fields =['question']
    template_name = 'survey/frquestion_update_form.html'
    
    def get_success_url(self):
        return reverse('survey_index')
    
    
class MultipleChoiceEditView(LoginRequiredMixin,
               ContribRequiredMixin,
               generic.UpdateView):
    """
    FormView for a user to edit an existing Question
    """
    model = MultipleChoiceQuestion
    template_name = 'survey/mcquestion_update_form.html'
    form_class = MultipleChoiceEditForm
    
    def get_initial(self):
        initial = {}
        for choice in self.object.multiplechoiceoption_set.all():
            initial['choice_%d' % choice.pk] = choice.text
        return initial
    
    def get_success_url(self):
        return reverse('survey_index')
    