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
from django.contrib.auth.decorators import login_required

from braces.views import LoginRequiredMixin, UserPassesTestMixin, StaffuserRequiredMixin

from .models import Exam, ResponseSet, ExamResponse, FreeResponseResponse, MultipleChoiceResponse
from .forms import NewResponseSetForm, DistributeForm, ExamResponseForm, BlankForm

# Create your views here.

@login_required
def index(request):
    all_exams = Exam.objects.all()
    template = loader.get_template('exam/index.html')
    context = RequestContext(request,
                             { 'all_exams': all_exams},)
    return HttpResponse(template.render(context))

@login_required
def description(request, exam_id):
    
    exam = Exam.objects.get(pk=exam_id)
    exam_desc = Exam.objects.get(pk=exam_id).description
    exam_questions = exam.multiplechoicequestion_set.all()
    responses = exam.responseset_set.order_by('created').all();
    if (len(responses) > 5):
        responses = responses[:5]
    ######
    qList = []
    q = []
    for question in exam_questions:
        q = [question.question]     #name of question, correct answer id
        qOptions = []
        qOptions.extend(question.multiplechoiceoption_set.all())
        q.append(qOptions)
        qList.append(q)
    
    ######
    template = loader.get_template('exam/description.html')
    context = RequestContext(request,
                             { 'exam': exam,
                                'qList' : qList,
                               'exam_id': exam_id,
                               'responses':responses},)
    return HttpResponse(template.render(context))

@login_required
def discuss(request, exam_id):
    exam = Exam.objects.get(pk=exam_id)
    template=loader.get_template('exam/discuss.html')
    context = RequestContext(request,
                             {'exam': exam,
                              'exam_id': exam_id},)
    return HttpResponse(template.render(context))


####################################### WIP #####################################################
@login_required
def ExamResponseDetail(request, exam_id, rsid, key):

        template = loader.get_template('exam/response_detail.html')
    
        response_set = ResponseSet.objects.get(pk=rsid)       #response set to connect exam and exam response key (?)
        exam = response_set.exam            #exam
        response = response_set.examresponse_set.get(pk=key)      #exam response
        responses = response.multiplechoiceresponse_set.all()
        stats = qstats(responses)
        qList = []
        q = []
        for question in responses:
            q = [question.question, question.option_id]     #name of question, answer chosen
            qOptions = []
            qOptions.extend(question.question.multiplechoiceoption_set.all())
            q.append(qOptions)
            qList.append(q)
        context = RequestContext(request,
                                 {'qList':qList,
                                  'response':response,
                                  'stats': stats,
                                  'exam': exam},)
        return HttpResponse(template.render(context))
        #return render(request, 'exam/response_detail.html', {'response': response, 'exam': exam})
    
# page with all response sets for a given exam
@login_required
def response_sets(request, exam_id):
    
    exam = Exam.objects.get(pk=exam_id)
    responses = exam.responseset_set.all()

    """
    eventually do statistical analysis here to pass to template
    """
    
    template = loader.get_template('exam/response_sets.html')
    context = RequestContext(request,
                             { 'responses': responses,
                               'exam_id': exam_id},)
    return HttpResponse(template.render(context))

# page with all exam responses for a given exam and response set id (rsid)
@login_required
def responses(request, exam_id, rsid):
    response_set = ResponseSet.objects.get(pk=rsid)
    exam = Exam.objects.get(pk=exam_id)
    responses = response_set.examresponse_set.order_by('respondent').all()

    """
    eventually do statistical analysis here to pass to template
    """
    stats = []
    for mcrs in responses:
        stats.append(qstats(mcrs.multiplechoiceresponse_set.all()))
        
    set_stats = respSetStats(stats)
    template = loader.get_template('exam/responses.html')
    context = RequestContext(request,
                             { 'responses': responses,
                                'response_set': response_set,
                               'exam_id': exam_id,
                                'stats': set_stats},
                                )
    return HttpResponse(template.render(context))



def respSetStats(qStats):
    if (qStats):
        numQuestions = qStats[0][0]
        numCorrect = 0
        maxScore = 0
        lowScore = 100
        medianScore = 0
        for stats in qStats:
            if(stats):
                numCorrect+=stats[1]
                if (numQuestions < stats[0]):
                    numQuestions = stats[0]
                if (maxScore < stats[2]):
                    maxScore = stats[2]
                if (lowScore > stats[2]):
                    lowScore = stats[2]
        medianScore = numCorrect / float(numQuestions * len(qStats))
        medianScore = medianScore *10000 //1 /100
        return [numQuestions, numCorrect, medianScore, maxScore, lowScore]
    else:
        return [0,0,0,0,0]
    

#returns a list with [numquestions, numcorrect, percent correct]
def qstats(mcRespSet):
    numQuestions = 0
    numCorrect = 0
    for question in mcRespSet:
        numQuestions+=1
        if question.option_id == 1:     #later if option_id == correct_id
            numCorrect+=1
    if (numQuestions != 0):
        percCorrect = numCorrect/float(numQuestions)
        percFormatted = percCorrect * 10000 //1 /100
        return [numQuestions, numCorrect, percFormatted]
    
        
            
 ####################################### WIP #####################################################


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
