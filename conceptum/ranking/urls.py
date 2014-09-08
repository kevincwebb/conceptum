from django.conf.urls import patterns, url, include

from ranking import views

urlpatterns = patterns('',

    url(r'^$', views.dispatch, name='dispatch'),

    url(r'^setup$', views.setup, name='setup'),
    url(r'^getsetup$', views.get_setup, name='get setup'),

    url(r'^submit$', views.submit, name='submit'),
    url(r'^closed$', views.closed, name = 'closed'),
)
