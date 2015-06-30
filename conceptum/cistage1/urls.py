from django.conf.urls import patterns, url, include

from cistage1 import views

urlpatterns = patterns('',
            #/stage1/
            url(r'^$', views.dispatch, name='stage1 dispatch'),
            
            #/stage1/setup/
            url(r'^setup', views.setup, name='stage1 setup'),
            
            #/stage1/getsetup/
            url(r'^getsetup$', views.get_setup, name = 'stage 1 get setup'),
            
            #/stage1/landing/
            url(r'^landing$', views.landing, name='landing'),
            
            url(r'^node/', include('nodemanager.urls')),
        )
