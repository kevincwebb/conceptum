from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='interview_index'),
    url(r'^add$', views.AddView.as_view(), name='interview_add'),
    url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='interview_detail'),
    url(r'^(?P<pk>\d+)/edit/$', views.EditView.as_view(), name='interview_edit'),
)