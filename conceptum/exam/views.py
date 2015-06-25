import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext, loader
from django.views import generic
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

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
                   MultipleChoiceEditForm, FreeResponseVersionForm, MultipleChoiceVersionForm
from .mixins import DevelopmentMixin, DistributionMixin, CurrentAppMixin


#def discuss(request, exam_id):
#    exam = Exam.objects.get(pk=exam_id)
#    template=loader.get_template('exam/discuss.html')
#    context = RequestContext(request,
#                             {'exam': exam,
#                              'exam_id': exam_id},)
#    return HttpResponse(template.render(context))


class ExamIndexView(LoginRequiredMixin,
                    ContribRequiredMixin,
                    CurrentAppMixin,
                    generic.ListView):
    """
    Landing page for exam development. This page will list all surveys or CI exams that
    are in the Development stage.
    
    Only staff users have the ability to create new Surveys and Exams.
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
        context['finished_exams'] = Exam.objects.filter(kind=self.exam_kind, stage=ExamStage.DIST)
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
    View exam details and questions.
    """
    model = Exam
    pk_url_kwarg = 'exam_id'
    template_name = 'exam/detail.html'
    
    def get_data(self, **kwargs):
        """
        Returns 2 dictionaries (in a tuple), each dict maps each concept to a list of
        all associated questions of that question type.
        """
        mc = {}
        fr = {}
        for concept in get_concept_list():
            concept_type = ContentType.objects.get_for_model(concept)
            fr[concept] = FreeResponseQuestion.objects.filter(exam = self.object,
                                                              content_type__pk=concept_type.id,
                                                              object_id=concept.id)
            mc[concept] = MultipleChoiceQuestion.objects.filter(exam = self.object,
                                                                content_type__pk=concept_type.id,
                                                                object_id=concept.id)
        return (fr, mc)
    
    def get_context_data(self, **kwargs):
        context = super(ExamDetailView, self).get_context_data(**kwargs)
        data = self.get_data()
        context['freeresponsequestion_list']=data[0]
        context['multiplechoicequestion_list']=data[1]
        return context


class SelectConceptView(LoginRequiredMixin,
                        ContribRequiredMixin,
                        DevelopmentMixin,
                        CurrentAppMixin,
                        generic.FormView):
    """
    Lists all Concepts in the database, Select a concept to add a question
    about that concept
    """
    template_name = 'exam/select.html'
    form_class = SelectConceptForm
    
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
                         DevelopmentMixin,
                         CurrentAppMixin,
                         generic.FormView):
    """
    FormView to add a new question
    """
    
    template_name = 'exam/question_create.html'

    # make sure our url arguments are good
    def dispatch(self, *args, **kwargs):
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
    
    @transaction.atomic()
    @reversion.create_revision()
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
                       DevelopmentMixin,
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


class QuestionVersionView(LoginRequiredMixin,
                          ContribRequiredMixin,
                          DevelopmentMixin,
                          CurrentAppMixin,
                          generic.UpdateView):
    """
    
    """
    pk_url_kwarg = 'question_id'
    template_name = 'exam/versions.html'
    
    def get_success_url(self):
        return reverse('exam:detail', args=[self.exam.id], current_app=self.current_app)


class FreeResponseVersionView(QuestionVersionView):
    model = FreeResponseQuestion
    form_class = FreeResponseVersionForm
    
    def get_context_data(self, **kwargs):
        context = super(FreeResponseVersionView, self).get_context_data(**kwargs)
        context['question_type'] = 'fr'
        # change to get_unique
        context['version_list'] = reversion.get_for_object(self.object)
        return context


class MultipleChoiceVersionView(QuestionVersionView):
    model = MultipleChoiceQuestion
    form_class = MultipleChoiceVersionForm
    
    def get_option_list(self):
        """
        Returns a list of lists of MultipleChoiceOptions, oldest version first.
        e.g. l[0] is all MCOs associated with the oldest version.
        
        List is reversed so that when items are popped from the list in the template,
        the latest version will come first.
        """
        l=[]
        option_type = ContentType.objects.get_for_model(MultipleChoiceOption)
        # change to get_unique
        for version in reversed(reversion.get_for_object(self.object)):
            l.append(version.revision.version_set.filter(content_type__pk=option_type.id))
        return l
        
    def get_context_data(self, **kwargs):
        context = super(MultipleChoiceVersionView, self).get_context_data(**kwargs)
        context['question_type'] = 'mc'
        # change to get_unique
        context['version_list'] = reversion.get_for_object(self.object)
        context['option_list'] = self.get_option_list()
        return context


class QuestionDeleteView(LoginRequiredMixin,
                         ContribRequiredMixin,
                         DevelopmentMixin,
                         CurrentAppMixin,
                         generic.DeleteView):
    """
    "Abstract" view subclassed by FreeResponse and MultipleChoice versions.
    
    Deletes a Question, and also deletes all related revisions (deleted question can't be recovered).
    
    The reason for deleting revisions is that if a new question is created, it can be assigned
    the same pk that a deleted question had, in which case its list of revisions will include
    revisions from the deleted question.
    """
    pk_url_kwarg = 'question_id'
    template_name = 'exam/confirm_delete.html'
    
    def delete(self, request, *args, **kwargs):
        versions = reversion.get_for_object(self.get_object())
        self.get_object().delete()
        for version in versions:
            version.revision.delete()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse('exam:detail', args=[self.exam.id], current_app=self.current_app)

class FreeResponseDeleteView(QuestionDeleteView):
    model = FreeResponseQuestion

class MultipleChoiceDeleteView(QuestionDeleteView):
    model = MultipleChoiceQuestion


class FinalizeView(LoginRequiredMixin,
                   StaffRequiredMixin,
                   DevelopmentMixin,
                   CurrentAppMixin,
                   generic.TemplateView):
    template_name = 'exam/finalize.html'
    #model = Exam
    #pk_url_kwarg = 'exam_id'
    
    def get_context_data(self, **kwargs):
        context = super(FinalizeView, self).get_context_data(**kwargs)
        context['exam'] = self.exam
        return context
    
    def post(self, request, *args, **kwargs):
        self.exam.stage = ExamStage.DIST
        self.exam.save()
        return HttpResponseRedirect(self.get_success_url())

    # in the future, this should maybe return to the distribute index
    def get_success_url(self):
        return reverse('exam:index', current_app=self.current_app)


class NewResponseSetView(LoginRequiredMixin,
                         DistributionMixin,
                         CurrentAppMixin,
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
                     CurrentAppMixin,
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
                 CurrentAppMixin,
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

    
class ExamResponseView(CurrentAppMixin,
                       generic.UpdateView):
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
