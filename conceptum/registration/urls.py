from django.conf.urls import patterns, url

from registration.views import RegistrationView

urlpatterns = patterns('',
    url(r'^register/$', RegistrationView.as_view(), name='register'),
    )