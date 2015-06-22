import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext, loader
from django.views import generic
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import user_passes_test #TEMPORARY

import reversion
from braces.views import LoginRequiredMixin, UserPassesTestMixin, StaffuserRequiredMixin

from profiles.mixins import ContribRequiredMixin, StaffRequiredMixin
from interviews.models import get_concept_list, DummyConcept as Concept #TEMPORARY: DummyConcept
from interviews.models import Excerpt #not temporary
from .models import Exam, ResponseSet, ExamResponse, QuestionResponse, FreeResponseQuestion,\
                    MultipleChoiceQuestion, MultipleChoiceOption, FreeResponseResponse,\
                    MultipleChoiceResponse, ExamKind, ExamStage
from .forms import SelectConceptForm, AddFreeResponseForm, AddMultipleChoiceForm, \
                   NewResponseSetForm, DistributeForm, ExamResponseForm, BlankForm, \
                   MultipleChoiceEditForm, FreeResponseVersionForm
from .mixins import DevelopmentMixin, CurrentAppMixin

####DELETE AFTER SURVEY MERGE####
#def index(request):
#    all_exams = Exam.objects.all()
#    template = loader.get_template('exam/index.html')
#    context = RequestContext(request,
#                             { 'all_exams': all_exams},)
#    return HttpResponse(template.render(context))

####DELETE AFTER EXAM MERGE####
#def description(request, exam_id):
#    exam_desc = Exam.objects.get(pk=exam_id).description
#    template = loader.get_template('exam/description.html')
#    context = RequestContext(request,
#                             { 'exam_desc': exam_desc,
#                               'exam_id': exam_id},)
#    return HttpResponse(template.render(context))


def contrib_check(user):
    """
    For the user_passes_test decorator. Returns true if the user is a contributor.
    
    TODO!!!! THIS SHOULD BE MOVED SOMEWHERE ELSE (D.R.Y.)
    then you can remove the user_passes_test import, too
    """
    return user.profile.is_contrib

def staff_check(user):
    """
    For the user_passes_test decorator. Returns true if the user is staff.
    
    TODO!!!! THIS SHOULD BE MOVED SOMEWHERE ELSE (D.R.Y.)
    """
    return user.is_staff


def discuss(request, exam_id):
    exam = Exam.objects.get(pk=exam_id)
    template=loader.get_template('exam/discuss.html')
    context = RequestContext(request,
                             {'exam': exam,
                              'exam_id': exam_id},)
    return HttpResponse(template.render(context))


class ExamIndexView(LoginRequiredMixin,
                    CurrentAppMixin,
                    generic.ListView):
    """
    Landing page for exam development. This page will list all surveys or CI exams that
    are in the Development stage.
    
    Only staff users have the ability to create new Surveys and Exams.
    
    TODO:
        - Development should only be available to contributors
        - Control what exams are available for development and deployment.
          Only finished versions should be available for deployment, and these should
          not be available for development.
    """
    model = Exam
    
    def get_template_names(self, *args, **kwargs):
        if (not Exam.objects.filter(kind=self.exam_kind)):
            return 'exam/index_empty.html'
        else:
            return 'exam/index.html'
       
    def get_context_data(self,**kwargs):
        context = super(ExamIndexView, self).get_context_data(**kwargs)
        context['exams'] = Exam.objects.filter(kind=self.exam_kind, stage=ExamStage.DEV)
        return context
    

class ExamCreateView(LoginRequiredMixin,
                     StaffRequiredMixin,
                     CurrentAppMixin,
                     generic.CreateView):
    """
    CreateView to create a survey/exam.
    
    We may want to make this happen automatically as follows:
        - working survey is created automatically
        - once approved by staff user, frozen version can be sent out
        - working survey could continue to be improved, and new frozen versions made
        - the same process would go for exams, once that stage is activated
    """
    model = Exam
    fields = ['name',
              'description',
              'randomize']
    template_name = 'exam/new_exam.html'

    def form_valid(self, form):
        form.instance.kind = self.exam_kind
        return super(ExamCreateView,self).form_valid(form)

    def get_success_url(self):
        return reverse('exam:index', current_app=self.current_app)


class ExamDetailView(LoginRequiredMixin,
                ContribRequiredMixin,
                DevelopmentMixin,
                CurrentAppMixin,
                generic.DetailView):
    """
    View exam details:
        - description
        - id
        - all questions
    
    TODO:
        - update this view after revising the exam model
        - the template is currently a mess
    """
    model = Exam
    pk_url_kwarg = 'exam_id'
    template_name = 'exam/detail.html'
    
    def get_data(self, **kwargs):
        mc = {}
        fr = {}
        for concept in get_concept_list():
            concept_type = ContentType.objects.get_for_model(concept)
            fr_question_list = FreeResponseQuestion.objects.filter(exam = self.object,
                                                                   content_type__pk=concept_type.id,
                                                                   object_id=concept.id)
            mc_question_list = MultipleChoiceQuestion.objects.filter(exam = self.object,
                                                                   content_type__pk=concept_type.id,
                                                                   object_id=concept.id)
            fr[concept] = fr_question_list
            mc[concept] = mc_question_list
        return [fr, mc]
    
    def get_context_data(self, **kwargs):
        context = super(ExamDetailView, self).get_context_data(**kwargs)
        data = self.get_data()
        context['freeresponsequestion_list']=data[0]
        context['multiplechoicequestion_list']=data[1]
        context['option_list']= MultipleChoiceOption.objects.all()
        return context


class SelectConceptView(LoginRequiredMixin,
                        ContribRequiredMixin,
                        CurrentAppMixin,
                        generic.FormView):
    """
    Lists all Concepts in the database, Select a concept to add a question
    about that concept
    """
    template_name = 'exam/select.html'
    form_class = SelectConceptForm
    
    def dispatch(self, *args, **kwargs):
        self.exam = get_object_or_404(Exam, pk=self.kwargs['exam_id'])
        return super(SelectConceptView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(SelectConceptView, self).get_context_data(**kwargs)
        context['exam'] = self.exam
        return context
 
    def form_valid(self, form):
        concept = form.cleaned_data.get('concept')
        return HttpResponseRedirect(reverse('exam:question_create', current_app=self.current_app,
            kwargs ={'exam_id':self.exam.id,'concept_id':concept.id,'question_type':'fr' }))


class QuestionCreateView(LoginRequiredMixin,
                         ContribRequiredMixin,
                         CurrentAppMixin,
                         generic.FormView):
    """
    FormView to add a new question
    """
    
    template_name = 'exam/question_create.html'

    # make sure our url arguments are good
    def dispatch(self, *args, **kwargs):
        self.exam = get_object_or_404(Exam, pk=self.kwargs['exam_id'])
        self.concept = get_object_or_404(Concept, pk=self.kwargs['concept_id'])
        self.question_type = self.kwargs['question_type']
        if (self.question_type != 'fr' and self.question_type != 'mc'):
            raise Http404
        return super(QuestionCreateView, self).dispatch(*args, **kwargs)

    # different form depending on type of question
    def get_form_class(self):
        if(self.question_type == 'fr'):
            return AddFreeResponseForm
        if(self.question_type == 'mc'):
            return AddMultipleChoiceForm
    
    def get_context_data(self,**kwargs):
        context = super(QuestionCreateView, self).get_context_data(**kwargs)
        concept_type = ContentType.objects.get_for_model(Concept)
        
        if(self.question_type == 'mc'):
            context['question_type'] = 'multiple_choice'   
        elif(self.question_type == 'fr'):
            context['question_type'] = 'free_response'
        
        context['exam'] = self.exam
        context['concept'] = self.concept
        context['excerpt_list']=Excerpt.objects.filter(content_type__pk=concept_type.id,
                                                       object_id=self.concept.id)
        return context
    
    def get_success_url(self):
        return reverse('exam:detail', args=[self.exam.id], current_app=self.current_app)
    
    def form_valid(self, form):
        concept_type = ContentType.objects.get_for_model(Concept)
        # we could move the object creation to each form's save() method, however,
        # we would need to pass self.exam and self.concept to the form
        if (self.question_type == 'fr'):
            FreeResponseQuestion.objects.create(exam = self.exam,
                                                question = form.cleaned_data.get('question'),
                                                content_type = concept_type,
                                                object_id = self.concept.id)
        if (self.question_type == 'mc'):
            q = MultipleChoiceQuestion.objects.create(exam = self.exam,
                                                      question = form.cleaned_data.get('question'),
                                                      content_type = concept_type,
                                                      object_id = self.concept.id)
            x=1
            while (True):
                choice_text = form.cleaned_data.get("choice_%d" % x)
                if (choice_text):
                    MultipleChoiceOption.objects.create(question = q, text = choice_text)
                    x+=1
                else:
                    break
        return HttpResponseRedirect(self.get_success_url())


class QuestionEditView(LoginRequiredMixin,
                       ContribRequiredMixin,
                       CurrentAppMixin,
                       generic.UpdateView):
    """
    UpdateView for a user to edit an existing Question
    """
    pk_url_kwarg = 'question_id'
    
    def get_success_url(self):
        return reverse('exam:detail', args=[self.object.exam.id], current_app=self.current_app)

class FreeResponseEditView(QuestionEditView):
    model = FreeResponseQuestion
    fields = ['question','image']
    template_name = 'exam/frquestion_update_form.html'
    
class MultipleChoiceEditView(QuestionEditView):
    model = MultipleChoiceQuestion
    form_class = MultipleChoiceEditForm
    template_name = 'exam/mcquestion_update_form.html'


class FreeResponseVersionView(LoginRequiredMixin,
                              ContribRequiredMixin,
                              CurrentAppMixin,
                              generic.UpdateView):
    """
    A view for viewing old versions of Free Response Questions
    """
    model = FreeResponseQuestion
    pk_url_kwarg = 'question_id'
    template_name = 'exam/versions_new.html'
    form_class = FreeResponseVersionForm
    
    def get_context_data(self, **kwargs):
        context = super(FreeResponseVersionView, self).get_context_data(**kwargs)
        context['question_type'] = 'fr'
        return context

    def get_success_url(self):
        return reverse('exam:detail', args=[self.get_object().exam.id], current_app=self.current_app)


#class FreeResponseVersionView(LoginRequiredMixin,
#                              ContribRequiredMixin,
#                              CurrentAppMixin,
#                              generic.UpdateView):
#    """
#    A view for viewing old versions of Free Response Questions
#    """
#    model = FreeResponseQuestion
#    pk_url_kwarg = 'question_id'
#    template_name = 'exam/versions.html'
#    form_class = FreeResponseVersionForm
#
#    def get_versions(self,**kwargs):
#        version_list = reversion.get_unique_for_object(self.object)
#
#        d = {}
#        for version in version_list:
#            #if the version question isn't a duplicate
#            if(version.field_dict['question'] not in d.values()
#               #and if the version belongs to the same concept as the current question 
#               and int(version.field_dict['object_id']) == self.object.object_id):
#                #add the version to the return dictionary
#                d[version]=(version.field_dict['question'])
#        return d
#    
#    def get_context_data(self, **kwargs):
#        context = super(FreeResponseVersionView, self).get_context_data(**kwargs)
#        context['question']=self.object
#        context['version_list'] = self.get_versions().items()
#        context['question_type'] = 'fr'
#        return context
#
#    def get_success_url(self):
#        return reverse('exam:detail', args=[self.object.exam.id], current_app=self.current_app)


@user_passes_test(contrib_check)
def revert_freeresponse(request, question_id):
    """
    View for reverting a question back to a previous version
    """
    print request.user.profile
    q = get_object_or_404(FreeResponseQuestion, pk=question_id)
    version_list = reversion.get_unique_for_object(q)
    
    if 'version' in request.POST.keys():
        for version in version_list:
            if version.id == int(request.POST['version']):
                version.revert()
                break
        return HttpResponseRedirect(reverse('exam:detail',
                                            args=[q.exam.id],
                                            current_app=request.resolver_match.namespace))
    else:
        return HttpResponseRedirect(reverse('exam:fr_versions',
                                            kwargs={'question_id' : q.id},
                                            current_app=request.resolver_match.namespace))


class MultipleChoiceVersionView(LoginRequiredMixin,
                                ContribRequiredMixin,
                                CurrentAppMixin,
                                generic.UpdateView):
    """
    A view for viewing old versions of Multiple Choice Questions and their
    corresponding options. 
    """
    model = MultipleChoiceQuestion
    pk_url_kwarg = 'question_id'
    template_name = 'exam/versions_new.html'
    
    #returns the current version of the question
    def get_question(self, **kwargs):
        return self.object
    
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
    
    def get_success_url(self):
        return reverse('exam:detail', args=[self.object.exam.id], current_app=self.current_app)





@user_passes_test(contrib_check)
def revert_multiplechoice(request, question_id):
    """
    View for reverting a multiple choice question back to a previous version
    """
    q = get_object_or_404(MultipleChoiceQuestion, pk=question_id)
    version_list = reversion.get_for_object(q)
    
    if 'version' in request.POST.keys():
        for version in version_list:
            if version.id == int(request.POST['version']):
                version.revision.revert(delete=True)
                break
        return HttpResponseRedirect(reverse('exam:detail',
                                            args=[q.exam.id],
                                            current_app=request.resolver_match.namespace))
    else:
        return HttpResponseRedirect(reverse('exam:mc_versions',
                                            kwargs={'question_id' : q.id},
                                            current_app=request.resolver_match.namespace))


class QuestionDeleteView(LoginRequiredMixin,
                             ContribRequiredMixin,
                             CurrentAppMixin,
                             generic.DeleteView):
    """
    "Abstract" view subclassed by FreeResponse and MultipleChoice versions.
    
    TODO: also delete related version objects
    """
    pk_url_kwarg = 'question_id'
    template_name = 'exam/confirm_delete.html'
    
    def get_success_url(self):
        return reverse('exam:detail', args=[self.object.exam.id], current_app=self.current_app)

class FreeResponseDeleteView(QuestionDeleteView):
    model = FreeResponseQuestion

class MultipleChoiceDeleteView(QuestionDeleteView):
    model = MultipleChoiceQuestion


#################################################
#                                               #
#   Finalization currently does not work.       #
#   This app is being redesigned, after which   #
#   the finalization process will be very       #
#   different (and simpler) than it is now.     ##################################################
#                                               #
#################################################

class FinalizeView(LoginRequiredMixin,
                StaffRequiredMixin,
                generic.ListView):
    """
    !THIS VIEW WILL CHANGE!
    
    View all questions created for the survey and select the ones meant for the final survey.
    
    TODO: MultipleChoiceOption should not be the model here.
    """
    
    model = MultipleChoiceOption
    template_name = 'exam/finalize.html'
    
    def dispatch(self, *args, **kwargs):
        self.exam = get_object_or_404(Exam, pk=self.kwargs['exam_id'])
        return super(FinalizeView, self).dispatch(*args, **kwargs)
    
    def get_data(self, **kwargs):
        """
        this has been copied pasted from somewhere else, bad design.
        TODO: fix it ^
        """
        mc = {}
        fr = {}
        for concept in get_concept_list():
            concept_type = ContentType.objects.get_for_model(concept)
            fr_question_list = FreeResponseQuestion.objects.filter(exam = self.exam,
                                                                   content_type__pk=concept_type.id,
                                                                   object_id=concept.id)
            mc_question_list = MultipleChoiceQuestion.objects.filter(exam = self.exam,
                                                                   content_type__pk=concept_type.id,
                                                                   object_id=concept.id)
            fr[concept] = fr_question_list
            mc[concept] = mc_question_list
        return [fr, mc]
    
    def get_context_data(self, **kwargs):
        context = super(FinalizeView, self).get_context_data(**kwargs)
        data = self.get_data()
        context['exam']=self.exam
        context['freeresponsequestion_list']=data[0]
        context['multiplechoicequestion_list']=data[1]
        context['option_list']= MultipleChoiceOption.objects.all()
        return context


@user_passes_test(staff_check)
def finalize_survey(request):
    """
    !THIS VIEW WILL CHANGE!
    
    This view takes selected checkboxes corresponding to survey questions, and copys them
    into the Final Survey
    
    TODO: right now this assumes there is only one final (the final survey)
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
    return HttpResponseRedirect(reverse('final_exam'))


class FinalView(LoginRequiredMixin,
                ContribRequiredMixin,
                generic.ListView):
    """
    !THIS VIEW WILL CHANGE!
    
    View all questions in the Final Survey
    
    TODO: right now this assumes there is only one final (the final survey)
    """
    
    model = MultipleChoiceOption
    template_name = 'exam/final.html'
    
    def get_data(self, **kwargs):
        """
        redundant method
        """
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
    """
    !THIS VIEW WILL CHANGE!
    """
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
    return HttpResponseRedirect(reverse('final_exam'))

#################################
#                               ##################################################################
#   End of finalization views   #
#                               #
#################################


class NewResponseSetView(LoginRequiredMixin,
                         generic.FormView):
    """
    Creates a new ResponseSet object.  This view is similar to a CreateView.
    
    When a contributor wants to distribute an exam, this page records information
    specific to that distribution.  It redirects to DistributeView, which is where
    emails are provided and the exam is sent out.
    
    attributes:
        exam - refers to the exam being distributed. This is set in the dispatch
            function, and comes from the url
        object - refers to the created ResponseSet. This is set in the form_valid
            function.
            
    TODO: incorporate modules
    """
    template_name = 'exam/distribute_new.html'
    form_class = NewResponseSetForm
    
    def dispatch(self, *args, **kwargs):
        """
        Get exam_id from url
        """
        self.exam = get_object_or_404(Exam, pk=self.kwargs['exam_id'])
        return super(NewResponseSetView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """
        Pass exam object to template
        """
        context = super(NewResponseSetView, self).get_context_data(**kwargs)
        context['exam'] = self.exam
        return context

    def get_success_url(self):
        return reverse('distribute_send', args=(self.object.id,))
    
    def form_valid(self, form):
        """
        This is where the ResponseSet is created.
        
        TODO: process selected modules from form
        """
        course = form.cleaned_data.get('course')
        pre_test = form.cleaned_data.get('pre_test')
        # modules = ...
        self.object=ResponseSet.objects.create(instructor=self.request.user.profile,
                                               course=course,
                                               pre_test=pre_test,
                                               exam=self.exam,
                                               # modules = ... 
                                               )
        return HttpResponseRedirect(self.get_success_url())


class DistributeView(LoginRequiredMixin,
                     UserPassesTestMixin,
                     generic.FormView):
    """
    View for sending ExamResponses. After a ResponseSet is created, this is
    where emails addresses are entered and the ExamResponses are sent.

    This page also provides details about a ResponseSet. It displays which email
    addresses have submitted responses and which have yet to submit. Unsubmitted
    ExamResponses can be resent; doing so deletes the pending ER and creates a new one.
    
    This view is similar to the generic UpdateView and DetailView.
    """
    template_name = 'exam/distribute_send.html'
    form_class = DistributeForm
    success_url = reverse_lazy('profile')
    
    raise_exception = True
    redirect_unauthenticated_users = True
    
    def test_func(self, user):
        """
        This function is used by the UserPassesTestMixin.
        Make sure that the user is staff or the original distributor.
        """
        response_set = get_object_or_404(ResponseSet, pk=self.kwargs['set_id'])
        return (user.is_staff or user.profile==response_set.instructor)
    
    def dispatch(self, *args, **kwargs):
        """
        Get the ResponseSet id from the url
        """
        self.object = get_object_or_404(ResponseSet, pk=self.kwargs['set_id'])
        return super(DistributeView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """
        Pass ResponseSet object and submitted ER list to template
        """
        context = super(DistributeView, self).get_context_data(**kwargs)
        context['object'] = self.object
        context['submitted_exams'] = self.object.examresponse_set.filter(submitted__isnull=False)
        return context
    
    def get_form_kwargs(self):
        """
        Pass ResponseSet object to form as 'instance' (like an UpdateForm)
        """
        kwargs = super(DistributeView, self).get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs
    
    def form_valid(self, form):
        """
        Create new ExamResponses and *QuestionResponses for each email address listed.
        
        TODO: apply filter by modules
        """
        # Get submitted data from form
        date = form.cleaned_data.get('expiration_date')
        time = form.cleaned_data.get('expiration_time')
        expiration_datetime = datetime.datetime.combine(date, time)
        to_send = form.cleaned_data.get('recipients') # a list of email strings
        
        # For each ExamResponse to be re-sent, delete the existing ER and add its
        # email to the list of emails to_send.
        for response in form.cleaned_data.get('resend'): # a list of ExamResponses
            to_send.append(response.respondent)
            response.delete()
            
        # For each email in the recipient list, create a new ExamResponse and create
        # associated FreeResponse- and MultipleChoiceResponses for every question
        # in the selected modules.
        for email in to_send:
            
            # If there is already an ExamResponse for this email, do not make a new one.
            # This situation will arise if an email is given twice in the recipients field.
            if not self.object.examresponse_set.filter(respondent__exact=email):
                exam_response = ExamResponse.objects.create(response_set=self.object,
                                                            respondent=email,
                                                            expiration_datetime=expiration_datetime)
                # TODO: instead of all(), filter by module
                for question in self.object.exam.freeresponsequestion_set.all():
                    FreeResponseResponse.objects.create(question=question,
                                                        exam_response=exam_response)
                for question in self.object.exam.multiplechoicequestion_set.all():
                    MultipleChoiceResponse.objects.create(question=question,
                                                      exam_response=exam_response)
                exam_response.send(self.request, email)    
        return HttpResponseRedirect(self.get_success_url())
    

class DeleteView(LoginRequiredMixin,
                 UserPassesTestMixin,
                 generic.DeleteView):
    """
    Confirm that an instructor would like to delete a ResponseSet. This exists in
    case an instructor accidentally creates a ResponseSet they did not intend to create.
    This will delete all associated ExamResponses and their respectice *QuestionResponses,
    so this should not be done if students have already submitted responses.
    
    A ResponseSet can only be deleted by its associated instructor or a staff user.
    """
    model = ResponseSet
    template_name = 'exam/delete_responses.html'
    success_url = reverse_lazy('profile')
    
    raise_exception = True
    redirect_unauthenticated_users = True
    
    def test_func(self, user):
        """
        This function is required by the UserPassesTestMixin.
        Requires that the user is staff or the original uploader
        """
        response_set = get_object_or_404(ResponseSet, pk=self.kwargs['pk'])
        return (user.is_staff or user.profile==response_set.instructor)


class CleanupView(LoginRequiredMixin,
                  StaffuserRequiredMixin,
                  generic.FormView):
    """
    A view for staff to manually delete expired, unsubmitted ExamResponses.
    
    This cleanup does not happen automatically, but this S.O. post suggests a good design,
    in case automatic cleanup is desired.  http://stackoverflow.com/a/11789141
    """
    template_name = 'exam/cleanup.html'
    form_class = BlankForm
    success_url = reverse_lazy('distribute_cleanup')
    
    def get_context_data(self, **kwargs):
        """
        Pass the list of expired, unsubmitted ERs to the template
        """
        context = super(CleanupView, self).get_context_data(**kwargs)
        context['expired'] = ExamResponse.objects.filter(
            expiration_datetime__lt=timezone.now()).filter(submitted__isnull=True)
        return context
    
    def form_valid(self, form):
        """
        Delete expired, unsubmitted ERs. This also deletes the associated *QuestionResponses.
        """
        for exam_response in ExamResponse.objects.filter(
            expiration_datetime__lt=timezone.now()).filter(submitted__isnull=True):
                exam_response.delete()
        return HttpResponseRedirect(self.get_success_url())

    
class ExamResponseView(generic.UpdateView):
    """
    This is where students take the Exam. A student will get a URL that ends with the
    key to a specific ExamResponse. If that ER has expired or already been submitted, or
    if there is no exam with the given key, then the student will be redirected to an
    "Exam Unavailable" page.
    """
    model = ExamResponse
    template_name='exam/exam_response.html'
    form_class = ExamResponseForm
    success_url = reverse_lazy('response_complete')
    
    def dispatch(self, *args, **kwargs):
        """
        Check that the ER is available.
        """
        try:
            if self.get_object().is_available():
                print 'got_object'
                return super(ExamResponseView, self).dispatch(*args, **kwargs)
        except Http404:
            pass
        return HttpResponseRedirect(reverse('exam_unavailable'))
        
    def form_valid(self, form):
        """
        Mark the time the exam has been submitted, and call the form's save() method,
        which saves the responses.
        """
        form.save()
        self.object.submitted = timezone.now()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
