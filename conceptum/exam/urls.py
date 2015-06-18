from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView

from exam import models, views

# these urls use namespaces. This way, we have to different instances of the exam app,
# Survey and CI
exam_patterns = patterns('',
    url(r'^dev/', include(patterns('',
        # index and detail views probably need to change to be dev specific
        url(r'^$', views.ExamIndexView.as_view(), name='index'),
        url(r'^create$', views.ExamCreateView.as_view(), name='create'),
        url(r'^(?P<exam_id>\d+)/$', views.ExamDetailView.as_view(), name='detail'),
        url(r'^(?P<exam_id>\d+)/(?P<concept_id>\d+)/(?P<question_type>\w+)/$',
            views.QuestionCreateView.as_view(), name='question_create'),
        
        url(r'^fr/(?P<question_id>\d+)/', include(patterns('',
            url(r'^edit/$', views.FreeResponseEditView.as_view(), name='freeresponse_edit'),
            url(r'^versions/$', views.FreeResponseVersionView.as_view(), name='freeresponse_versions'),
            url(r'^revert/$', views.revert_freeresponse, name='freeresponse_revert'),
            url(r'^delete/$', views.FreeResponseDeleteView.as_view(), name='freeresponse_delete'),
        ))),
        
        url(r'^mc/(?P<question_id>\d+)/', include(patterns('',
            url(r'^edit/$', views.MultipleChoiceEditView.as_view(), name='multiplechoice_edit'),
            url(r'^versions/$', views.MultipleChoiceVersionView.as_view(), name='multiplechoice_versions'),
            url(r'^revert/$', views.revert_multiplechoice, name='multiplechoice_revert'),
            url(r'^delete/$', views.MultipleChoiceDeleteView.as_view(), name='multiplechoice_delete'),
        ))),
    ))),
    
    url(r'^dist/', include(patterns('',
        #index
        #detail
        url(r'^(?P<exam_id>\d+)/new/$', views.NewResponseSetView.as_view(),
            name='distribute_new'),
        url(r'^(?P<set_id>\d+)/$', views.DistributeView.as_view(), name='distribute_send'),
        url(r'^(?P<pk>\d+)/delete/$', views.DeleteView.as_view(), name='distribute_delete'),
        url(r'^cleanup/$', views.CleanupView.as_view(), name='distribute_cleanup'),
    ))),    
    
    #this could go under urls 'dev/'
    url(r'^(?P<exam_id>\d+)/finalize/$', views.FinalizeView.as_view(), name = 'finalize_view'),
    url(r'^finalize/finalize/$', views.finalize_survey, name = 'finalize_exam'),
    url(r'^final/$', views.FinalView.as_view(), name = 'final_exam'),
    url(r'^final/delete/$', views.delete_final_question, name = 'delete_final_question'),
)


urlpatterns = patterns('',
    url(r'^survey/', include(exam_patterns, app_name='exam', namespace='survey')),
    url(r'^CI/', include(exam_patterns, app_name='exam', namespace='CI_exam')),
    
    url(r'^taketest/(?P<pk>\w+)/$', views.ExamResponseView.as_view(),
        name='exam_response'),
    url(r'^response_complete/$', TemplateView.as_view(
        template_name='exam/response_complete.html'), name='response_complete'),
    url(r'^unavailable/$', TemplateView.as_view(
        template_name='exam/exam_unavailable.html'), name='exam_unavailable'),
)


# kept in case things go really bad
oldpatterns = patterns('',

    url(r'^$', views.ExamIndexView.as_view(), name='exam_index'),
    url(r'^new/$', views.ExamCreateView.as_view(), name='exam_create'),
    url(r'^(?P<exam_id>\d+)/$', views.ExamDetailView.as_view(), name='exam_detail'),
    url(r'^(?P<exam_id>\d+)/select/$', views.SelectConceptView.as_view(), name='select_concept'),
    url(r'^(?P<exam_id>\d+)/(?P<concept_id>\d+)/(?P<question_type>\w+)/$',
        views.QuestionCreateView.as_view(), name='question_create'),
    url(r'^(?P<exam_id>\d+)/discuss/$',views.discuss, name='discuss'),
    
    url(r'^edit/fr/(?P<question_id>\d+)$', views.FreeResponseEditView.as_view(),
        name='freeresponse_edit'),
    url(r'^edit/mc/(?P<question_id>\d+)$', views.MultipleChoiceEditView.as_view(),
        name='multiplechoice_edit'),
    url(r'^edit/fr/(?P<question_id>\d+)/versions/$', views.FreeResponseVersionView.as_view(),
        name='freeresponse_versions'),
    url(r'^edit/mc/(?P<question_id>\d+)/versions/$', views.MultipleChoiceVersionView.as_view(),
        name='multiplechoice_versions'),
    url(r'^edit/fr/(?P<question_id>\d+)/versions/revert/$', views.revert_freeresponse,
        name='freeresponse_revert'),
    url(r'^edit/mc/(?P<question_id>\d+)/versions/revert/$', views.revert_multiplechoice,
        name='multiplechoice_revert'),
    url(r'^delete/fr/(?P<question_id>\d+)$', views.FreeResponseDeleteView.as_view(),
        name='freeresponse_delete'),
    url(r'^delete/mc/(?P<question_id>\d+)$', views.MultipleChoiceDeleteView.as_view(),
        name='multiplechoice_delete'),


    url(r'^(?P<exam_id>\d+)/finalize/$', views.FinalizeView.as_view(), name = 'finalize_view'),
    url(r'^finalize/finalize/$', views.finalize_survey, name = 'finalize_exam'),
    url(r'^final/$', views.FinalView.as_view(), name = 'final_exam'),
    url(r'^final/delete/$', views.delete_final_question, name = 'delete_final_question'),
    
    url(r'^(?P<exam_id>\d+)/distribute/new/$', views.NewResponseSetView.as_view(),
        name='distribute_new'),
    url(r'^distribute/(?P<set_id>\d+)/$', views.DistributeView.as_view(),
        name='distribute_send'),
    url(r'^distribute/(?P<pk>\d+)/delete/$', views.DeleteView.as_view(),
        name='distribute_delete'),
    url(r'^distribute/cleanup/$', views.CleanupView.as_view(),
        name='distribute_cleanup'),
    
    # the pk is the 64-digit exam key, url looks like /exams/taketest/123456789abcdef.../
    url(r'^taketest/(?P<pk>\w+)/$', views.ExamResponseView.as_view(),
        name='exam_response'),
    url(r'^response_complete/$', TemplateView.as_view(
        template_name='exam/response_complete.html'), name='response_complete'),
    url(r'^unavailable/$', TemplateView.as_view(
        template_name='exam/exam_unavailable.html'), name='exam_unavailable'),

    #.*comments/
    url(r'comments/', include('django_comments.urls')),

)
