from django.conf.urls import include, patterns, url
from django.views.generic import TemplateView

from allauth.account.views import LoginView

from . import views
from .forms import LoginForm

urlpatterns = patterns('',
    url(r'^profile/$', TemplateView.as_view(template_name='profiles/profile.html'), name='profile'),
    url(r'^login/$', LoginView.as_view(form_class=LoginForm), name='account_login'),
    url(r'^pending/$', views.PendingUsersView.as_view(), name='pending_users'),
    url(r'^pending/action/(?P<profile_id>\d+)/$', views.which_action, name='pending_action'),
    url(r'^inactive/$', views.AccountInactiveView.as_view(), name='account_inactive'),
#url(r'^approve/$', views.approve, name='approve'),
    url(r'^', include('allauth.urls')),
)