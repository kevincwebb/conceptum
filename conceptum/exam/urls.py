from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView

from exam import models, views

urlpatterns = patterns('',
                       #/exams/
                       url(r'^$', views.index, name='exam_index'),

                       #/exams/1/
                       url(r'^(?P<exam_id>\d+)/$', views.description, name='exam_description'),

                       #/exams/1/discuss/
                       url(r'^(?P<exam_id>\d+)/discuss/$',views.discuss, name='exam_discuss'),
                       
                       #/exams/1/distribute/new/
                       url(r'^(?P<exam_id>\d+)/distribute/new/$', views.NewResponseSetView.as_view(),
                           name='distribute_new'),
                                              
                       #/exams/distribute/1/
                       url(r'^distribute/(?P<set_id>\d+)/$', views.DistributeView.as_view(),
                           name='distribute_send'),
                       
                       #/exams/distribute/1/delete/
                       url(r'^distribute/(?P<pk>\d+)/delete/$', views.DeleteView.as_view(),
                           name='distribute_delete'),
                       
                       url(r'^distribute/cleanup/$', views.CleanupView.as_view(),
                           name='distribute_cleanup'),
                       
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


                       ####################################### WIP #####################################################
                       
                       # exams/1/responses/
                       url(r'^(?P<exam_id>\d+)/responses/$', views.response_sets, name = 'exam_response_sets'),

                        #exams/1/responses/1/       (exam 1, response set 1)
                        url(r'^(?P<exam_id>\d+)/responses/(?P<rsid>\d+)/$', views.responses, name = 'exam_responses'),


                        #exams/1/responses/1/1234567...        (exam 1, response set 1, key 1234567...)
                        url(r'^(?P<exam_id>\d+)/responses/(?P<rsid>\d+)/(?P<key>\w+)/$', views.ExamResponseDetail, name = 'exam_response_detail')

            

                       ####################################### WIP #####################################################

                   )
