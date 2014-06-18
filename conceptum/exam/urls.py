from django.conf.urls import patterns, url, include

from exam import models, views

urlpatterns = patterns('',
                       #/exams/
                       url(r'^$', views.index, name='index'),

                       #/exams/1
                       url(r'^(?P<exam_id>\d+)/$', views.description, name='description'),

                       #/exams/1/discuss
                       url(r'^(?P<exam_id>\d+)/discuss/$',views.discuss, name='discuss'),

                       #.*comments/
                       url(r'comments/', include('django_comments.urls')),

                   )
