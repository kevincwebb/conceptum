from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from exam.models import Exam

# Create your views here.

def index(request):
    all_exams = Exam.objects.all()
    exam_list_ordered__scores = Exam.sort_by_score.all()
    template = loader.get_template('exam/index.html')
    context = RequestContext(request,
                             { 'all_exams': all_exams,
                               'exam_list_ordered__scores' : exam_list_ordered__scores},)
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
