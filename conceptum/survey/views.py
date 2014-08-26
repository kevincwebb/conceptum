from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse_lazy, resolve, reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.utils.translation import ugettext_lazy as _
from braces.views import LoginRequiredMixin, UserPassesTestMixin
from exam.models import Exam, FreeResponseQuestion, FreeResponseResponse, MultipleChoiceQuestion, MultipleChoiceOption, MultipleChoiceResponse 
from .forms import AddFreeResponseForm, SelectConceptForm, AddMultipleChoiceForm, MultipleChoiceEditForm
from interviews.models import get_concept_list, Excerpt, DummyConcept
from profiles.mixins import ContribRequiredMixin
import reversion
from itertools import chain
from collections import defaultdict

SURVEY_NAME = 'Survey'

class SelectConceptView(LoginRequiredMixin, ContribRequiredMixin, generic.FormView,):
    """
    Lists all Concepts in the database, Select a concept to view the SurveyCreateView
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
    #shows interviews for chosen topic
    def get(self, request, *args, **kwargs):
        view = ExcerptDetailView.as_view()
        return view(request, *args, **kwargs)

    #chooses form and view based on 'question_type' POST kwarg (either fr or mc)
    def post(self, request, *args, **kwargs):
        if(self.kwargs['question_type'] == 'fr'):
            form = AddFreeResponseForm(request.POST)
            if (form.is_valid() ):
                view = AddFreeResponseView.as_view()
                return view(request, *args, **kwargs)
        
        elif(self.kwargs['question_type'] == 'mc'):
            form = AddMultipleChoiceForm(request.POST)
            if(form.is_valid() ) :
                view = AddMultipleChoiceView.as_view()
                return view(request, *args, **kwargs)
        
        
        return HttpResponseRedirect(reverse('survey_create', kwargs ={ 'pk' : self.kwargs['pk'], 'question_type' : self.kwargs['question_type']}))

class ExcerptDetailView(LoginRequiredMixin, ContribRequiredMixin, generic.DetailView):
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
        form.instance.exam_id = Exam.objects.get(name = SURVEY_NAME).id
        return super(AddFreeResponseView, self).form_valid(form)

    def get_success_url(self):
        return reverse('survey_index')
    
    def get_context_data(self,**kwargs):
        context = super(AddFreeResponseView, self).get_context_data(**kwargs)
        context['concept_id'] = self.kwargs['pk']
        return context


class AddMultipleChoiceView(LoginRequiredMixin, ContribRequiredMixin, generic.FormView):
    model = MultipleChoiceQuestion
    template_name = 'survey/create.html'
    form_class = AddMultipleChoiceForm
    
    def form_valid(self, form):
        form.instance.content_object = DummyConcept.objects.get(pk = self.kwargs['pk'])
        form.instance.exam_id = Exam.objects.get(name = SURVEY_NAME).id
        response = super(AddMultipleChoiceView, self).form_valid(form)
        form.form_valid()
        return response
    
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
    
    def get_data(self, **kwargs):
        mc = {}
        fr = {}
        for concept in get_concept_list():
            concept_type = ContentType.objects.get_for_model(concept)
            fr_question_list = FreeResponseQuestion.objects.filter(exam = Exam.objects.get(name = SURVEY_NAME).id,
                                                                   content_type__pk=concept_type.id, object_id=concept.id)
            mc_question_list = MultipleChoiceQuestion.objects.filter(exam = Exam.objects.get(name = SURVEY_NAME).id,
                                                                   content_type__pk=concept_type.id, object_id=concept.id)
            fr[concept] = fr_question_list
            mc[concept] = mc_question_list
        return [fr, mc]
    
    def get_context_data(self, **kwargs):
        context = super(SurveyListView, self).get_context_data(**kwargs)
        data = self.get_data()
        context['freeresponsequestion_list']=data[0]
        context['multiplechoicequestion_list']=data[1]
        context['option_list']= MultipleChoiceOption.objects.all()
        return context
 

class FreeResponseEditView(LoginRequiredMixin,
                           ContribRequiredMixin,
                           generic.UpdateView):
    """
    UpdateView for a user to edit an existing Question
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
    UpdateView for a user to edit an existing Question
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


#view for reverting a question back to a previous version   
def revert_freeresponse(request, pk):
    q = get_object_or_404(FreeResponseQuestion, pk=pk)
    version_list = reversion.get_unique_for_object(q)
    
    if 'version' in request.POST.keys():
        for version in version_list:
            if version.id == int(request.POST['version']):
                version.revert()
                #version.revision.revert(delete = True)
                break
        return HttpResponseRedirect(reverse('survey_index'))
    else:
        return HttpResponseRedirect(reverse('freeresponse_versions', kwargs={'pk' : pk}))


    
class FreeResponseVersionView(LoginRequiredMixin,
               ContribRequiredMixin,
               generic.UpdateView):
    model = FreeResponseQuestion
    template_name = 'survey/versions.html'
    success_url = reverse_lazy('survey_index')
    
    def get_question(self, **kwargs):
        return FreeResponseQuestion.objects.get(exam = Exam.objects.get(name = SURVEY_NAME).id, id = self.kwargs['pk'])

    def get_versions(self,**kwargs):
        version_list = reversion.get_unique_for_object(self.get_question())
        d = {}
        for version in version_list:
            if(version.field_dict['question'] not in d.values() ):
                d[version]=(version.field_dict['question'])
        return d
    
    def get_context_data(self, **kwargs):
        context = super(FreeResponseVersionView, self).get_context_data(**kwargs)
        context['question']=self.get_question()
        context['version_list'] = self.get_versions().items()
        context['question_type'] = 'fr'
        return context

def revert_multiplechoice(request, pk):
    q = get_object_or_404(MultipleChoiceQuestion, pk=pk)
    version_list = reversion.get_for_object(q)
    
    if 'version' in request.POST.keys():
        for version in version_list:
            print request.POST['version']
            print version.id
            if version.id == int(request.POST['version']):
                print "reverting"
                #version.revert()
                version.revision.revert(delete=True)
                break
        return HttpResponseRedirect(reverse('survey_index'))
    else:
        return HttpResponseRedirect(reverse('multiplechoice_versions', kwargs={'pk' : pk}))
    
class MultipleChoiceVersionView(LoginRequiredMixin,
               ContribRequiredMixin,
               generic.UpdateView):
    model = MultipleChoiceQuestion
    template_name = 'survey/versions.html'
    success_url = reverse_lazy('survey_index')

    def get_question(self, **kwargs):
        return MultipleChoiceQuestion.objects.get(exam = Exam.objects.get(name = SURVEY_NAME).id, id = self.kwargs['pk'])
    
    def get_version_options(self, **kwargs):
        version_list = kwargs['version_list']
        d = {}
        for version in version_list:
            option_list = version.revision.version_set.filter(content_type__name='multiple choice option')
            options = []
            for option in option_list:
                if option.field_dict:
                    fd = option.field_dict
                    options.append(fd['text'])
            d[version] = options               

        return d
    
    def get_options_for_version(self, version, **kwargs):
        options = self.get_version_options(version_list = kwargs['version_list'])[version]
        return options
    
    def get_current_options(self, **kwargs):
        option_list = MultipleChoiceOption.objects.filter(question= self.get_question())
        d = []
        for option in option_list:
            d.append(option)
        return d

    def get_versions(self,**kwargs):
        version_list = reversion.get_for_object(self.get_question())
        versions = []
        questions = []
        options = []
        for version in version_list:
            versions.append(version)
        for version in reversed(version_list):
            questions.append(version.field_dict['question'])
            options.append(self.get_options_for_version(version, version_list = version_list))
        return [versions, questions, options]


    def get_context_data(self, **kwargs):
        data = self.get_versions()
        context = super(MultipleChoiceVersionView, self).get_context_data(**kwargs)
        context['current_question']=self.get_question()
        context['version_list'] = data[0]
        context['question_list'] = data[1]
        context['options_list'] = data[2]
        context['current_option_list'] = self.get_current_options()
        context['question_type'] = 'mc'
        return context

class FreeResponseDeleteView(LoginRequiredMixin,
                 ContribRequiredMixin,
                 generic.DeleteView):
    """
    Issue With how Questions are deleted with version control:
    When a question is created it is automatically assigned the next largest pk.
    If you create a question, say its pk = 5 and its concept is Concept A.
    Now you delete that question, and create another question under Concept B. It is also given pk = 5
    because thats the next available pk. This isn't a problem until you try to revert to old
    versions of the question for Concept B. The deleted question for Concept A will appear under old versions
    of the current question even though it isn't actually a version of same question, or even necessarily the same concept.
    
    This isn't an issue if the question you delete isn't the newest one.
    If you have questions with pk = 1, 2, 3, 4, and delete question 2, then create
    a new question, you will now have questions with pk= 1, 3, 4, 5, which does not create this issue.
    
    Could probably fix by creating a custom form to handle deleting the questions.
    If the pk of the question being deleted is equal to FreeResponseQuestion.objects.all().order_by("-id")[0].id
    then it is going to cause the version problem. The logic to fix this could also be put in the FreeResponse/MultipleChoice Add views. 
    
    """
    model = FreeResponseQuestion
    template_name = 'survey/confirm_delete.html'
    success_url = reverse_lazy('survey_index')
    

class MultipleChoiceDeleteView(LoginRequiredMixin,
                 ContribRequiredMixin,
                 generic.DeleteView):
       
    model = MultipleChoiceQuestion
    template_name = 'survey/confirm_delete.html'
    success_url = reverse_lazy('survey_index')
    
    
    
