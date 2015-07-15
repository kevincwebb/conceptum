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
)