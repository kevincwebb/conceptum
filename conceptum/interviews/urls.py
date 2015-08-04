from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='interview_index'),
    url(r'^create/$', views.CreateGroupView.as_view(), name='interview_create'),
    url(r'^(?P<group_id>\d+)/$', views.GroupView.as_view(), name='interview_group'),
    url(r'^(?P<group_id>\d+)/rename/$', views.RenameView.as_view(), name='interview_rename'),
    url(r'^(?P<group_id>\d+)/lock/$', views.lock_group, name='interview_lock'),
    url(r'^(?P<group_id>\d+)/unlock/$', views.unlock_group, name='interview_unlock'),
    url(r'^(?P<group_id>\d+)/add/$', views.AddView.as_view(), name='interview_add'),
    url(r'^(?P<pk>\d+)/detail/$', views.DetailView.as_view(), name='interview_detail'),
    url(r'^(?P<pk>\d+)/edit/$', views.EditView.as_view(), name='interview_edit'),
    url(r'^(?P<pk>\d+)/delete/$', views.DeleteView.as_view(), name='interview_delete'),
    
    
    # #/interviews/concept/1
    # url(r'^concept/(?P<pk>\d+)/detail$', views.ConceptInterviewDetailView.as_view(), name='conceptinterview_detail'),
    # #/interviews/concept/1/create
    # url(r'^concept/create/$', views.ConceptInterviewAddView.as_view(), name='conceptinterview_create'),
    # #/interviews/concept/1/edit/add
    # url(r'^concept/(?P<pk>\d+)/edit/add$', views.ConceptExcerptAddView.as_view(), name='conceptexcerpt_add'),
    # #/interviews/concept/1/edit
    # url(r'^concept/(?P<pk>\d+)/edit/$', views.ConceptInterviewEditView.as_view(), name='conceptinterview_edit'),
       
    # #/interviews/concept/1/1/edit
    # url(r'^concept/(?P<pk>\d+)/(?P<excerpt_id>\d+)/edit/$', views.ConceptExcerptEditView.as_view(), name='conceptexcerpt_edit'),
    #/interviews/concept/1/1/delete
    # url(r'^concept/(?P<pk>\d+)/(?P<excerpt_id>\d+)/delete/$', views.ConceptExcerptDeleteView.as_view(), name='conceptexcerpt_delete'),

)