from django.conf.urls import include, patterns, url
from django.views.generic import TemplateView

from allauth.account.views import LoginView

from . import views
from .forms import LoginForm

urlpatterns = patterns('',
    url(r'^profile/$', TemplateView.as_view(template_name='profiles/profile.html'), name='profile'),
    url(r'^login/$', LoginView.as_view(form_class=LoginForm), name='account_login'),
    url(r'^pending/$', views.PendingUsersView.as_view(), name='pending_users'),
    url(r'^approve/(?P<profile_id>\d+)/$', views.approve, name='approve'),
    url(r'^accounts/', include('allauth.urls')),
)