from django.conf.urls import *
from mysky_visitor.views import *

urlpatterns = patterns('',
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^', include('sky_visitor.urls')),
    )
