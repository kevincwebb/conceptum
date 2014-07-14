from django.conf.urls import patterns, url, include

from nodemanager import views

urlpatterns = patterns('',
            url(r'^(?P<node_id>\d+)/entry$', views.entry, name='free entry'),
            url(r'^(?P<node_id>\d+)/prune$', views.prune, name='prune'),
            url(r'^(?P<node_id>\d+)/rank$', views.rank, name='rank'),
            url(r'^(?P<node_id>\d+)/getentry', views.get_entry, name = 'get entry'),
                )
