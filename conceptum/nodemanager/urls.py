from django.conf.urls import patterns, url, include

from nodemanager import views

urlpatterns = patterns('',

        # for free-entry of nodes. handles initial and consecutive entries
        url(r'^(?P<node_id>\d+)/entry$', views.entry, name='free entry'),
        url(r'^(?P<node_id>\d+)/reentry$', views.entry, {'redirected': True},
                name='redirected free entry',),
        url(r'^(?P<node_id>\d+)/getentry', views.get_entry, name = 'get entry'),

        url(r'^(?P<node_id>\d+)/finalsub$', views.add_finished_user, name='final sub'),

        url(r'^(?P<node_id>\d+)/merge$', views.merge, name='merge'),
        url(r'^(?P<node_id>\d+)/newmerge', views.get_merge,
            {'merge_type': 'add merge'}, name='add merge'),
        url(r'^(?P<node_id>\d+)/editmerge', views.get_merge,
            {'merge_type': 'subtract merge'}, name='subtract merge'),
        url(r'^(?P<node_id>\d+)/finalmerge$', views.finalize_merge, name='final merge'),

        url(r'^(?P<node_id>\d+)/rank/', include('ranking.urls')),
        )
