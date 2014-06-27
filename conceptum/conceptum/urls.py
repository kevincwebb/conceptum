from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from allauth.account.views import LoginView
from custom_auth.forms import LoginForm
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'conceptum.views.home', name='home'),

    url(r'^accounts/profile/$', TemplateView.as_view(template_name='profiles/profile.html'), name='profile'),
    url(r'^accounts/login/$', LoginView.as_view(form_class=LoginForm), name="account_login"),
    url(r'^accounts/', include('allauth.urls')),


    # This will likely move to an app later.  Prototyping for now.
    url(r'^landing/$', 'conceptum.views.landing', name='landing'),


    # Examples:
    # url(r'^conceptum/', include('conceptum.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^exams/', include('exam.urls')),
    

)

# Uncomment the next line to serve media files in dev.
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )
