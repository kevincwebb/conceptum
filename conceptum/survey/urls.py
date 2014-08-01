from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.SurveyListView.as_view(), name='survey_index'),
    #url(r'^(?P<pk>\d+)/$', views.SurveyCreateView.as_view(), name='survey_create'),
    url(r'^(?P<pk>\d+)/(?P<question_type>\w+)/$',views.SurveyCreateView.as_view(), name='survey_create'),
    url(r'^edit/fr/(?P<pk>\d+)$', views.FreeResponseEditView.as_view(), name='freeresponse_edit'),
    url(r'^edit/mc/(?P<pk>\d+)$', views.MultipleChoiceEditView.as_view(), name='multiplechoice_edit'),
    #url(r'^(?P<pk>\d+)/addFR', views.SurveyAddQuestionView.as_view(), name='survey_addFR'),
    #url(r'^(?P<pk>\d+)/addMC', views.SurveyAddQuestionView.as_view(), name='survey_addMC'),
    url(r'^select/$', views.SelectConceptView.as_view(), name='survey_select'), 
    
    #url(r'^(?P<pk>\d+)/delete/$', views.DeleteView.as_view(), name='interview_delete'),
)