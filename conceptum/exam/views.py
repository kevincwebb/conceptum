from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views.generic import FormView
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect

from .models import Exam, ExamResponse
from .forms import DistributeForm

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

class DistributeView(FormView):
    template_name = 'exam/exam_distribute.html'
    form_class = DistributeForm
    success_url = reverse_lazy('index')
    
    def form_valid(self, form):
        to_email = form.cleaned_data.get('email')
        exam_response = ExamResponse.objects.create()
        exam_response.send(self.request, to_email)
        return HttpResponseRedirect(self.get_success_url())
    
    
