import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views.generic import FormView, UpdateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.http import Http404

from braces.views import LoginRequiredMixin

from .models import Exam, ExamResponse, FreeResponseResponse, MultipleChoiceResponse
from .forms import DistributeForm, ExamResponseForm

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


class DistributeView(LoginRequiredMixin, FormView):
    template_name = 'exam/distribute.html'
    form_class = DistributeForm
    success_url = reverse_lazy('index')
    
    def dispatch(self, *args, **kwargs):
        self.exam = get_object_or_404(Exam, pk=self.kwargs['exam_id'])
        return super(DistributeView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(DistributeView, self).get_context_data(**kwargs)
        context['exam'] = self.exam
        return context
    
    def form_valid(self, form):
        date = form.cleaned_data.get('expiration_date')
        time = form.cleaned_data.get('expiration_time')
        expiration_datetime = datetime.datetime.combine(date, time)
        for email in form.cleaned_data.get('recipients'):
            exam_response = ExamResponse.objects.create(
                                                        respondent=email,
                                                        expiration_datetime=expiration_datetime)
            
            # TODO: instead of all(), filter by module
            for question in self.exam.freeresponsequestion_set.all():
                FreeResponseResponse.objects.create(question=question,
                                                    exam_response=exam_response)
            
            for question in self.exam.multiplechoicequestion_set.all():
                MultipleChoiceResponse.objects.create(question=question,
                                                      exam_response=exam_response)
                
            exam_response.send(self.request, email)
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse_lazy('description', args=(self.exam.id,))
    
class ExamResponseView(UpdateView):
    model = ExamResponse
    template_name='exam/exam_response.html'
    form_class = ExamResponseForm
    success_url = reverse_lazy('response_complete')
    
    def dispatch(self, *args, **kwargs):
        try:
            if self.get_object().check_available():
                print 'got_object'
                return super(ExamResponseView, self).dispatch(*args, **kwargs)
        except Http404:
            pass
        return HttpResponseRedirect(reverse('exam_unavailable'))
        
    def form_valid(self, form):
        form.save()
        self.object.is_available = False
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
