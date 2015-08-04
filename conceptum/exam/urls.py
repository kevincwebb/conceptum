from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView

from exam import models, views

"""
For Conceptum, we have 2 instances of the exam app: survey and CI_exam.
We differentiate between theme by giving them different namespaces.

There are 3 ways to reference the url names in exam_patterns:
    'survey:index' - This will redirect to the survey's detail page
    "CI_exam:index' - This will redirecct to the CI's detail page
    'exam:index' - This will redirect to the detail page for whichever is currently active
"""

exam_patterns = patterns('',
    # DEVELOPMENT
    url(r'^dev/', include(patterns('',
        url(r'^$', views.ExamDevIndexView.as_view(), name='index'),
        url(r'^create/$', views.ExamCreateView.as_view(), name='create'),
        url(r'^(?P<exam_id>\d+)/$', views.DevDetailView.as_view(), name='detail'),
        url(r'^(?P<exam_id>\d+)/edit/$', views.ExamEditView.as_view(), name='edit'),
        url(r'^(?P<exam_id>\d+)/delete/$', views.ExamDeleteView.as_view(), name='delete_exam'),
        url(r'^(?P<exam_id>\d+)/select/$', views.SelectConceptView.as_view(), name='select_concept'),
        url(r'^(?P<exam_id>\d+)/(?P<concept_id>\d+)/(?P<question_type>\w{2})/$',
            views.QuestionCreateView.as_view(), name='question_create'),
        
        url(r'^fr/(?P<question_id>\d+)/', include(patterns('',
            url(r'^edit/$', views.FreeResponseEditView.as_view(), name='fr_edit'),
            url(r'^versions/$', views.FreeResponseVersionView.as_view(), name='fr_versions'),
            url(r'^delete/$', views.FreeResponseDeleteView.as_view(), name='fr_delete'),
        ))),
        
        url(r'^mc/(?P<question_id>\d+)/', include(patterns('',
            url(r'^edit/$', views.MultipleChoiceEditView.as_view(), name='mc_edit'),
            url(r'^versions/$', views.MultipleChoiceVersionView.as_view(), name='mc_versions'),
            url(r'^delete/$', views.MultipleChoiceDeleteView.as_view(), name='mc_delete'),
        ))),
    ))),

    # FINALIZING
    url(r'^finalize/(?P<exam_id>\d+)/$', views.FinalizeView.as_view(), name = 'finalize'),
    
    # DISTRIBUTION
    url(r'^dist/', include(patterns('',
        url(r'^$', views.ExamDistIndexView.as_view(), name='distribute_index'),
        url(r'^(?P<exam_id>\d+)/$', views.DistDetailView.as_view(), name='distribute_detail'),
        url(r'^(?P<exam_id>\d+)/copy/$', views.ExamCopyView.as_view(), name='copy'),
        url(r'^(?P<exam_id>\d+)/copy/denied/$', views.CopyDeniedView.as_view(), name='copy_denied'),
        url(r'^(?P<exam_id>\d+)/close/$', views.ExamCloseView.as_view(), name='close'),
        url(r'^(?P<exam_id>\d+)/responses/$', views.ResponseSetIndexView.as_view(), name = 'response_sets'),
        url(r'^(?P<exam_id>\d+)/new/$', views.NewResponseSetView.as_view(), name='distribute_new'),
        url(r'^response_set/(?P<rs_id>\d+)/$', views.ResponseSetDetailView.as_view(), name = 'responses'),
        url(r'^response_set/(?P<rs_id>\d+)/send/$', views.DistributeView.as_view(), name='distribute_send'),
        url(r'^response_set/(?P<rs_id>\d+)/delete/$', views.DeleteView.as_view(), name='distribute_delete'),
        url(r'^response/(?P<key>\w+)/$', views.ExamResponseDetailView.as_view(), name = 'response_detail'),
    ))),    
    
    
    
    #(r'^comments/', include('django_comments.urls')),
)

urlpatterns = patterns('',
    url(r'^survey/', include(exam_patterns, app_name='exam', namespace='survey')),
    url(r'^CI/', include(exam_patterns, app_name='exam', namespace='CI_exam')),
    url(r'^cleanup/$', views.CleanupView.as_view(), name='distribute_cleanup'),
    
    # TAKE TEST
    url(r'^taketest/(?P<pk>\w+)/$', views.TakeTestIRBView.as_view(),
        name='take_test_IRB'), 
    url(r'^taketest/(?P<pk>\w+)/form/$', views.TakeTestView.as_view(),
        name='take_test'), #formerly exam_response
    url(r'^response_complete/$', TemplateView.as_view(
        template_name='exam/response_complete.html'), name='response_complete'),
    url(r'^unavailable/$', TemplateView.as_view(
        template_name='exam/exam_unavailable.html'), name='exam_unavailable'),
)
