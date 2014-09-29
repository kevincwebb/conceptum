from django.conf.urls import patterns, url, include

from cistage1 import views

urlpatterns = patterns('',
            url(r'^$', views.dispatch, name='stage1 dispatch'),
            url(r'^setup', views.setup, name='stage1 setup'),
            url(r'^getsetup$', views.get_setup, name = 'stage 1 get setup'),
            url(r'^landing$', views.landing, name='landing'),
            url(r'^node/', include('nodemanager.urls')),
        )
