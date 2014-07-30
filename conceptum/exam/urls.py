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
                       
                       #/exam/distribute
                       # may need to change to /exam/1/distribute
                       # or find a way to select what exams to include
                       url(r'^distribute/$', views.DistributeView.as_view(), name='distribute'),
                       
                       #/exams/taketest/asdfghjkl...
                       url(r'^taketest/(?P<key>\w+)/$',TemplateView.as_view(
                           template_name='exam/exam_response.html'), name='exam_response'),

                       #.*comments/
                       url(r'comments/', include('django_comments.urls')),

                   )
