from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    #/interviews/
    url(r'^$', views.IndexView.as_view(), name='interview_index'),
    #/interviews/add/
    url(r'^add/$', views.AddView.as_view(), name='interview_add'),
    #/interviews/1/
    url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='interview_detail'),
    #/interviews/1/edit/
    url(r'^(?P<pk>\d+)/edit/$', views.EditView.as_view(), name='interview_edit'),
    #/interviews/1/delete/
    url(r'^(?P<pk>\d+)/delete/$', views.DeleteView.as_view(), name='interview_delete'),
)