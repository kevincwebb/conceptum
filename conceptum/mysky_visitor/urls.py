from django.conf.urls import *
from mysky_visitor.views import RegisterView, LoginView, ChangePasswordView, ForgotPasswordView
#from sky_visitor.urls import TOKEN_REGEX

urlpatterns = patterns('',
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^change_password/$', ChangePasswordView.as_view(), name='change_password'),
#    url(r'^forgot_password/$', ForgotPasswordView.as_view(), name='forgot_password'),


#    url(r'user/invitation/$', CustomInvitationStartView.as_view(), name='invitation_start'),
#    url(r'user/invitation/%s/$' % TOKEN_REGEX, CustomInvitationCompleteView.as_view(), name='invitation_complete'),
    url(r'^', include('sky_visitor.urls')),
)