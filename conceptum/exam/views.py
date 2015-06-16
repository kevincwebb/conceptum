import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views.generic import FormView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils import timezone

from braces.views import LoginRequiredMixin, UserPassesTestMixin, StaffuserRequiredMixin

from .models import Exam, ResponseSet, ExamResponse, FreeResponseResponse, MultipleChoiceResponse
from .forms import NewResponseSetForm, DistributeForm, ExamResponseForm, BlankForm

# Create your views here.

def index(request):
    all_exams = Exam.objects.all()
    template = loader.get_template('exam/index.html')
    context = RequestContext(request,
                             { 'all_exams': all_exams},)
    return HttpResponse(template.render(context))

def description(request, exam_id):
    exam_desc = Exam.objects.get(pk=exam_id).description
    template = loader.get_template('exam/description.html')
    context = RequestContext(request,
                             { 'exam_desc': exam_desc,
                               'exam_id': exam_id},)
    return HttpResponse(template.render(context))

def discuss(request, exam_id):
    exam = Exam.objects.get(pk=exam_id)
    template=loader.get_template('exam/discuss.html')
    context = RequestContext(request,
                             {'exam': exam,
                              'exam_id': exam_id},)
    return HttpResponse(template.render(context))


class NewResponseSetView(LoginRequiredMixin,
                         FormView):
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
                     FormView):
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
    
    # Raise a 403 if user is denied access
    raise_exception = True
    
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
                 DeleteView):
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
    
    # Raise a 403 if user is denied access
    raise_exception = True
    
    def test_func(self, user):
        """
        This function is required by the UserPassesTestMixin.
        Requires that the user is staff or the original uploader
        """
        response_set = get_object_or_404(ResponseSet, pk=self.kwargs['pk'])
        return (user.is_staff or user.profile==response_set.instructor)

class CleanupView(LoginRequiredMixin,
                  StaffuserRequiredMixin,
                  FormView):
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

    
class ExamResponseView(UpdateView):
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
