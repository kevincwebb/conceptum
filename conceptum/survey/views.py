from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse_lazy, resolve, reverse
from django.views import generic
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.utils.translation import ugettext_lazy as _
from braces.views import LoginRequiredMixin, UserPassesTestMixin
from exam.models import Exam, FreeResponseQuestion, FreeResponseResponse, MultipleChoiceQuestion, MultipleChoiceOption, MultipleChoiceResponse 
from .forms import AddFreeResponseForm, SelectConceptForm, AddMultipleChoiceForm, MultipleChoiceEditForm
from interviews.models import get_concept_list, Excerpt, DummyConcept
from profiles.mixins import ContribRequiredMixin, StaffRequiredMixin
import reversion
from itertools import chain
from collections import defaultdict


#This is the name of the Exam object used to store the survey as it is built
SURVEY_NAME = 'Survey'
#This is the name of the exam object used to store the final version of the survey
FINAL_SURVEY_NAME = 'FINAL_SURVEY'

class SelectConceptView(LoginRequiredMixin, ContribRequiredMixin, generic.FormView,):
    """
    Lists all Concepts in the database, Select a concept to add a question
    about that concept
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
    #get requests show interviews for chosen topic
    def get(self, request, *args, **kwargs):
        view = ExcerptDetailView.as_view()
        return view(request, *args, **kwargs)

    #post requests choose form and view based on 'question_type' POST kwarg (either fr or mc)
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
        context['concept'] = get_concept_list().get(pk = self.kwargs['pk'])
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
    """
    View to let a user add a Multiple Choice Question
    """
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


    
class FreeResponseVersionView(LoginRequiredMixin,
               ContribRequiredMixin,
               generic.UpdateView):
    """
    A view for viewing old versions of Free Response Questions
    """
    model = FreeResponseQuestion
    template_name = 'survey/versions.html'
    success_url = reverse_lazy('survey_index')
    
    def get_question(self, **kwargs):
        return FreeResponseQuestion.objects.get(exam = Exam.objects.get(name = SURVEY_NAME).id, id = self.kwargs['pk'])

    def get_versions(self,**kwargs):
        version_list = reversion.get_unique_for_object(self.get_question())

        d = {}
        for version in version_list:
            #if the version question isn't a duplicate
            if(version.field_dict['question'] not in d.values()
               #and if the version belongs to the same concept as the current question 
               and int(version.field_dict['object_id']) == self.get_question().object_id):
                #add the version to the return dictionary
                d[version]=(version.field_dict['question'])
        return d
    
    def get_context_data(self, **kwargs):
        context = super(FreeResponseVersionView, self).get_context_data(**kwargs)
        context['question']=self.get_question()
        context['version_list'] = self.get_versions().items()
        context['question_type'] = 'fr'
        return context


    
class MultipleChoiceVersionView(LoginRequiredMixin,
               ContribRequiredMixin,
               generic.UpdateView):
    """
    A view for viewing old versions of Multiple Choice Questions and their
    corresponding options. 
    """
    model = MultipleChoiceQuestion
    template_name = 'survey/versions.html'
    success_url = reverse_lazy('survey_index')
    
    #returns the current version of the question
    def get_question(self, **kwargs):
        return MultipleChoiceQuestion.objects.get(exam = Exam.objects.get(name = SURVEY_NAME).id, id = self.kwargs['pk'])
    
    #returns a dictionary of all versions paired to a list of the text of their options
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
    
    #returns a list of options for an old version of the question
    def get_options_for_version(self, version, **kwargs):
        options = self.get_version_options(version_list = kwargs['version_list'])[version]
        return options
    
    #returns a list of options for the current version of the question
    def get_current_options(self, **kwargs):
        option_list = MultipleChoiceOption.objects.filter(question= self.get_question())
        d = []
        for option in option_list:
            d.append(option)
        return d

    #preps the data to be passed into the template
    def get_versions(self,**kwargs):
        version_list = reversion.get_for_object(self.get_question())
        
        #filters the versions to exclude ones which belong to a different concept than the question
        #this could happen when questions get deleted and then a new question belonging to a different concept takes
        #the deleted question's pk.
        wrong_concept_versions = []
        for version in version_list:
            if int(version.field_dict['object_id']) != self.get_question().object_id:
                wrong_concept_versions.append(version.id)
        version_list = version_list.exclude(id__in = wrong_concept_versions)
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


def contrib_check(user):
    """
    For the user_passes_test decorator. Returns true if the user is a contributor. 
    """
    return user.profile.is_contrib

def staff_check(user):
    """
    For the user_passes_test decorator. Returns true if the user is staff. 
    """
    return user.is_staff

@user_passes_test(contrib_check)
def revert_freeresponse(request, pk):
    """
    View for reverting a question back to a previous version
    """
    print request.user.profile
    q = get_object_or_404(FreeResponseQuestion, pk=pk)
    version_list = reversion.get_unique_for_object(q)
    
    if 'version' in request.POST.keys():
        for version in version_list:
            if version.id == int(request.POST['version']):
                version.revert()
                break
        return HttpResponseRedirect(reverse('survey_index'))
    else:
        return HttpResponseRedirect(reverse('freeresponse_versions', kwargs={'pk' : pk}))


@user_passes_test(contrib_check)
def revert_multiplechoice(request, pk):
    """
    View for reverting a multiple choice question back to a previous version
    """
    q = get_object_or_404(MultipleChoiceQuestion, pk=pk)
    version_list = reversion.get_for_object(q)
    
    if 'version' in request.POST.keys():
        for version in version_list:
            if version.id == int(request.POST['version']):
                version.revision.revert(delete=True)
                break
        return HttpResponseRedirect(reverse('survey_index'))
    else:
        return HttpResponseRedirect(reverse('multiplechoice_versions', kwargs={'pk' : pk}))


@user_passes_test(staff_check)
def finalize_survey(request):
    """
    This view takes selected checkboxes corresponding to survey questions, and copys them
    into the Final Survey
    """
    mc = []
    fr = []
    for item in request.POST.lists():
        if item[0] == 'fr_selected':
            fr = item[1]
        elif item[0] == 'mc_selected':
            mc = item[1]
    final, created = Exam.objects.get_or_create(name=FINAL_SURVEY_NAME)
    for key in fr:
        q = FreeResponseQuestion.objects.get(pk = key)
        if not final.freeresponsequestion_set.filter(question= q.question):
            #setting q.pk and q.id to None then saving it creates a copy of q
            q.pk = None
            q.id = None
            q.exam = final
            q.save()
    for key in mc:
        q = MultipleChoiceQuestion.objects.get(pk = key)
        if not final.multiplechoicequestion_set.filter(question= q.question):
            options = q.multiplechoiceoption_set.all()
            q.pk = None
            q.id = None
            q.exam = final
            q.save()
            for option in options:
                option.pk = None
                option.id = None
                option.question = q
                option.save()
    return HttpResponseRedirect(reverse('final_survey'))

class FinalizeView(LoginRequiredMixin,
                StaffRequiredMixin,
                generic.ListView):
    """
    View all questions created for the survey and select the ones meant for the final survey
    """
    
    model = MultipleChoiceOption
    template_name = 'survey/finalize.html'
    
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
        context = super(FinalizeView, self).get_context_data(**kwargs)
        data = self.get_data()
        context['freeresponsequestion_list']=data[0]
        context['multiplechoicequestion_list']=data[1]
        context['option_list']= MultipleChoiceOption.objects.all()
        return context
    
class FinalView(LoginRequiredMixin,
                ContribRequiredMixin,
                generic.ListView):
    """
    View all questions in the Final Survey
    """
    
    model = MultipleChoiceOption
    template_name = 'survey/final.html'
    
    def get_data(self, **kwargs):
        mc = {}
        fr = {}
        for concept in get_concept_list():
            concept_type = ContentType.objects.get_for_model(concept)
            fr_question_list = FreeResponseQuestion.objects.filter(exam = Exam.objects.get(name = FINAL_SURVEY_NAME).id,
                                                                   content_type__pk=concept_type.id, object_id=concept.id)
            mc_question_list = MultipleChoiceQuestion.objects.filter(exam = Exam.objects.get(name = FINAL_SURVEY_NAME).id,
                                                                   content_type__pk=concept_type.id, object_id=concept.id)
            fr[concept] = fr_question_list
            mc[concept] = mc_question_list
        return [fr, mc]
    
    def get_context_data(self, **kwargs):
        context = super(FinalView, self).get_context_data(**kwargs)
        data = self.get_data()
        context['freeresponsequestion_list']=data[0]
        context['multiplechoicequestion_list']=data[1]
        context['option_list']= MultipleChoiceOption.objects.all()
        return context
    
#function view for deleting a question from the final survey
@user_passes_test(staff_check)
def delete_final_question(request):
    mc = []
    fr = []
    for item in request.POST.lists():
        if item[0] == 'fr_selected':
            fr = item[1]
        elif item[0] == 'mc_selected':
            mc = item[1]
    final = Exam.objects.get(name=FINAL_SURVEY_NAME)
    for key in fr:
        q = FreeResponseQuestion.objects.get(pk = key)
        q.delete()
    for key in mc:
        q = MultipleChoiceQuestion.objects.get(pk = key)
        q.delete()
    return HttpResponseRedirect(reverse('final_survey'))

class FreeResponseDeleteView(LoginRequiredMixin,
                 ContribRequiredMixin,
                 generic.DeleteView):

    model = FreeResponseQuestion
    template_name = 'survey/confirm_delete.html'
    success_url = reverse_lazy('survey_index')
    

class MultipleChoiceDeleteView(LoginRequiredMixin,
                 ContribRequiredMixin,
                 generic.DeleteView):
       
    model = MultipleChoiceQuestion
    template_name = 'survey/confirm_delete.html'
    success_url = reverse_lazy('survey_index')
    
    
    
