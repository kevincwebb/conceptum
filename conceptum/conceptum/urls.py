from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'conceptum.views.home', name='home'),

   
    url(r'^user/', include('sky_visitor.urls')),
    #url(r'^accounts/', include('registration.backends.default.urls')),
    #url(r'^accounts/profile/', TemplateView.as_view(template_name='registration/profile.html'), name = 'registration_profile'),
    


    # This will likely move to an app later.  Prototyping for now.
    url(r'^landing/$', 'conceptum.views.landing', name='landing'),

    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/profile/', TemplateView.as_view(template_name='registration/profile.html'), name = 'registration_profile'),


    # Examples:
    # url(r'^conceptum/', include('conceptum.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^exams/', include('exam.urls')),

    #It may be important that django.contrib.auth.urls come
    #       before registration.backends.default.urls, because
    #       there is some overlap
    
   
    #url(r'^accounts/', include('django.contrib.auth.urls')),
    #url(r'^accounts/', include('registration.backends.default.urls')),
    

)

# Uncomment the next line to serve media files in dev.
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )
