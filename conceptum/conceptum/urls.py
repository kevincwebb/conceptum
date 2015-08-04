
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

from .views import StaffView


urlpatterns = patterns('',
    url(r'^$', 'conceptum.views.home', name='home'),
    url(r'^ci_info$', 'conceptum.views.ci_info', name='ci_info'),
    url(r'^staff/$', StaffView.as_view(), name='staff_page'),
    
    url(r'^accounts/', include('custom_auth.urls')),

    url(r'^cidev/', include('cidev.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^exams/', include('exam.urls')),
    url(r'^stage1/', include('cistage1.urls')),
    url(r'^interviews/', include('interviews.urls')),
    
)

# Uncomment the next line to serve media files in dev.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )
