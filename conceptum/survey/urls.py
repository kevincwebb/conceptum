from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.SurveyListView.as_view(), name='survey_index'),
    url(r'^(?P<pk>\d+)/(?P<question_type>\w+)/$',views.SurveyCreateView.as_view(), name='survey_create'),
    
    url(r'^edit/fr/(?P<pk>\d+)$', views.FreeResponseEditView.as_view(), name='freeresponse_edit'),
    url(r'^edit/mc/(?P<pk>\d+)$', views.MultipleChoiceEditView.as_view(), name='multiplechoice_edit'),
    
    url(r'^edit/fr/(?P<pk>\d+)/versions/$', views.FreeResponseVersionView.as_view(), name='freeresponse_versions'),
    url(r'^edit/mc/(?P<pk>\d+)/versions/$', views.MultipleChoiceVersionView.as_view(), name='multiplechoice_versions'),
    
    url(r'^edit/fr/(?P<pk>\d+)/versions/revert/$', views.revert_freeresponse, name='freeresponse_revert'),
    
    
    url(r'^select/$', views.SelectConceptView.as_view(), name='survey_select'), 
    url(r'^delete/mc/(?P<pk>\d+)$', views.MultipleChoiceDeleteView.as_view(), name='multiplechoice_delete'),
    url(r'^delete/fr/(?P<pk>\d+)$', views.FreeResponseDeleteView.as_view(), name='freeresponse_delete'),

)