from django.conf.urls import *
from mysky_visitor.views import *
from sky_visitor.urls import TOKEN_REGEX

urlpatterns = patterns('',
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'user/invitation/$', CustomInvitationStartView.as_view(), name='invitation_start'),
    url(r'user/invitation/%s/$' % TOKEN_REGEX, CustomInvitationCompleteView.as_view(), name='invitation_complete'),
    url(r'^', include('sky_visitor.urls')),
    )
