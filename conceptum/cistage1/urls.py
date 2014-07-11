from django.conf.urls import patterns, url, include

from cistage1 import views

urlpatterns = patterns('',
                       url(r'^$', views.landing, name='landing'),
                       url(r'^node/', include('nodemanager.urls')),
                       )
