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
    Creates a new ResponseSet object.  This view is similar to a CreateView
    
    When a contributor wants to distribute an exam, this page records information
    specific to that distribution.  It redirects to DistributeView, which is where
    emails are provided an the exam is sent out
    
    attributes:
        exam - refers to the exam being distributed. This is set in the dispatch
            function, and comes from the url
        object - refers to the created ResponseSet. This is set in the form_valid
            function. 
    """
    template_name = 'exam/distribute_new.html'
    form_class = NewResponseSetForm
    
    def dispatch(self, *args, **kwargs):
        self.exam = get_object_or_404(Exam, pk=self.kwargs['exam_id'])
        return super(NewResponseSetView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(NewResponseSetView, self).get_context_data(**kwargs)
        context['exam'] = self.exam
        return context

    def get_success_url(self):
        return reverse('distribute_send', args=(self.object.id,))
    
    def form_valid(self, form):
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
    
    This page also provides details about a ResponseSet, and shows which email
    addresses have submitted responses and which have yet to submit.  ExamResponses
    can be re-sent.
    
    """
    template_name = 'exam/distribute_send.html'
    form_class = DistributeForm
    success_url = reverse_lazy('profile')
    
    # Raise a 403 if user is denied access
    raise_exception = True
    
    def test_func(self, user):
        """
        This function is required by the UserPassesTestMixin.
        Requires that the user is staff or the original distributor
        """
        response_set = get_object_or_404(ResponseSet, pk=self.kwargs['set_id'])
        return (user.is_staff or user.profile==response_set.instructor)
    
    def dispatch(self, *args, **kwargs):
        self.object = get_object_or_404(ResponseSet, pk=self.kwargs['set_id'])
        return super(DistributeView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(DistributeView, self).get_context_data(**kwargs)
        context['object'] = self.object
        context['submitted_exams'] = self.object.examresponse_set.filter(submitted__isnull=False)
        return context
    
    def get_form_kwargs(self):
        kwargs = super(DistributeView, self).get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs
    
    def form_valid(self, form):
        date = form.cleaned_data.get('expiration_date')
        time = form.cleaned_data.get('expiration_time')
        expiration_datetime = datetime.datetime.combine(date, time)
        to_send = form.cleaned_data.get('recipients') # a list of email strings
        for response in form.cleaned_data.get('resend'): # a list of ExamResponses
            to_send.append(response.respondent)
            response.delete()
        for email in to_send:
            if not self.object.examresponse_set.filter(respondent__exact=email):
            # If there is already an ExamResponse for this email, do not make a new one.
            # This situation will arise if an email is entered twice in the same input.
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
    template_name = 'exam/cleanup.html'
    form_class = BlankForm
    success_url = reverse_lazy('distribute_cleanup')
    
    def get_context_data(self, **kwargs):
        context = super(CleanupView, self).get_context_data(**kwargs)
        context['expired'] = ExamResponse.objects.filter(
            expiration_datetime__lt=timezone.now()).filter(submitted__isnull=True)
        return context
    
    def form_valid(self, form):
        for exam_response in ExamResponse.objects.filter(
            expiration_datetime__lt=timezone.now()).filter(submitted__isnull=True):
                exam_response.delete()
        return HttpResponseRedirect(self.get_success_url())
    
    #def get_success_url(self):
    #   return reverse('profile')
    
class ExamResponseView(UpdateView):
    model = ExamResponse
    template_name='exam/exam_response.html'
    form_class = ExamResponseForm
    success_url = reverse_lazy('response_complete')
    
    def dispatch(self, *args, **kwargs):
        try:
            if self.get_object().is_available():
                print 'got_object'
                return super(ExamResponseView, self).dispatch(*args, **kwargs)
        except Http404:
            pass
        return HttpResponseRedirect(reverse('exam_unavailable'))
        
    def form_valid(self, form):
        form.save()
        self.object.submitted = timezone.now()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
