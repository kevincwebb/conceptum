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
        #url(r'^copy/(?P<exam_id>\d+)/$', views.ExamCopyView.as_view(), name='copy'),
        url(r'^(?P<exam_id>\d+)/$', views.ExamDetailView.as_view(), name='detail'),
        url(r'^(?P<exam_id>\d+)/select/$', views.SelectConceptView.as_view(), name='select_concept'),
        url(r'^(?P<exam_id>\d+)/(?P<concept_id>\d+)/(?P<question_type>\w{2})/$',
            views.QuestionCreateView.as_view(), name='question_create'),
        
        url(r'^(?P<exam_id>\d+)/discuss/$',views.discuss, name='discuss'),
        
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
    url(r'^finalize/(?P<exam_id>\d+)/$', views.FinalizeView.as_view(), name = 'finalize_view'),
    #url(r'^finalize/(?P<exam_id>\d+)/confirm/$', views.FinalizeConfirmView.as_view(),
    #    name = 'finalize_view'),
    
    # DISTRIBUTION
    url(r'^dist/', include(patterns('',
        #index
        url(r'^$', views.ExamDistIndexView.as_view(), name='distribute_index'),
        #detail
        url(r'^(?P<exam_id>\d+)/new/$', views.NewResponseSetView.as_view(),
            name='distribute_new'),
        url(r'^send/(?P<set_id>\d+)/$', views.DistributeView.as_view(), name='distribute_send'),
        url(r'^(?P<pk>\d+)/delete/$', views.DeleteView.as_view(), name='distribute_delete'),
        
        #detail view of distribution page
        url(r'^(?P<exam_id>\d+)/$', views.description, name='distribute_detail'),
        
        #1/discuss
        url(r'^(?P<exam_id>\d+)/discuss/$',views.discuss, name='distribute_discuss'),
        
        # exams/1/responses/
        url(r'^(?P<exam_id>\d+)/responses/$', views.response_sets, name = 'response_sets'),

         #exams/1/responses/1/       (exam 1, response set 1)
        url(r'^(?P<exam_id>\d+)/responses/(?P<rsid>\d+)/$', views.responses, name = 'responses'),

         #exams/1/responses/1/1234567...        (exam 1, response set 1, key 1234567...)
        url(r'^(?P<exam_id>\d+)/responses/(?P<rsid>\d+)/(?P<key>\w+)/$', views.ExamResponseDetail, name = 'response_detail'),

        
    ))),    
    #url(r'^/', DistributeIndexView.as_view()), #just a default, something we might want
    
    # TAKE TEST
    url(r'^taketest/(?P<pk>\w+)/$', views.ExamResponseIRB,
        name='take_test_IRB'), 
    url(r'^taketest/(?P<pk>\w+)/form/$', views.ExamResponseView.as_view(),
        name='take_test'), #formerly exam_response
    url(r'^response_complete/$', TemplateView.as_view(
        template_name='exam/response_complete.html'), name='response_complete'),
    url(r'^unavailable/$', TemplateView.as_view(
        template_name='exam/exam_unavailable.html'), name='unavailable'),
    
    (r'^comments/', include('django_comments.urls')),
)

urlpatterns = patterns('',

    url(r'^survey/', include(exam_patterns, app_name='exam', namespace='survey')),
    url(r'^CI/', include(exam_patterns, app_name='exam', namespace='CI_exam')),
    url(r'^cleanup/$', views.CleanupView.as_view(), name='distribute_cleanup'),
)
