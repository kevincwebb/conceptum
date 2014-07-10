from django.conf.urls import include, patterns, url
from django.views.generic.base import RedirectView

from allauth.account.views import LoginView

from . import views
from .forms import LoginForm

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(pattern_name='profile')),
    url(r'^login/$', LoginView.as_view(form_class=LoginForm), name='account_login'),
    url(r'^pending/$', views.PendingUsersView.as_view(), name='pending_users'),
    url(r'^pending/action/(?P<profile_id>\d+)/$', views.which_action, name='pending_action'),
    url(r'^inactive/$', views.AccountInactiveView.as_view(), name='account_inactive'),
    url(r'^confirm-email/$', views.EmailVerificationSentView.as_view(),
        name="account_email_verification_sent"),
    url(r'^profile/', include('profiles.urls')),
    url(r'^', include('allauth.urls')),
)