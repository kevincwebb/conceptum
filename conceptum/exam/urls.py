from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView

from exam import models, views

urlpatterns = patterns('',
                       #/exams/
                       url(r'^$', views.index, name='index'),

                       #/exams/1
                       url(r'^(?P<exam_id>\d+)/$', views.description, name='description'),

                       #/exams/1/discuss
                       url(r'^(?P<exam_id>\d+)/discuss/$',views.discuss, name='discuss'),
                       
                       #/exams/1/distribute/
                       url(r'^(?P<exam_id>\d+)/distribute/$', views.DistributeView.as_view(),
                           name='distribute'),
                       
                       # the pk is the 64-digit exam key
                       #/exams/taketest/123456789abcdef.../
                       url(r'^taketest/(?P<pk>\w+)/$', views.ExamResponseView.as_view(),
                           name='exam_response'),

                       url(r'^response_complete/$', TemplateView.as_view(
                           template_name='exam/response_complete.html'), name='response_complete'),

                       url(r'^unavailable/$', TemplateView.as_view(
                           template_name='exam/exam_unavailable.html'), name='exam_unavailable'),

                       #.*comments/
                       url(r'comments/', include('django_comments.urls')),

                   )
