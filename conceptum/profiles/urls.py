from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.ProfileView.as_view(), name='profile'),
    url(r'^edit/$', views.EditProfileView.as_view(), name='edit_profile')
)