from django.conf.urls import patterns, url

from exam import models, views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       )
