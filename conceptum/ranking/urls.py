from django.conf.urls import patterns, url, include

from ranking import views

urlpatterns = patterns('',
                       url(r'^setup$', views.setup, name='setup'),
                       url(r'^form$', views.form, name='form'),
                       url(r'^closed$', views.closed, name = 'closed'),
)
