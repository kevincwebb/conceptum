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
            {'merge type': 'new merge'}, name='new merge'),
        url(r'^(?P<node_id>\d+)/newmerge', views.get_merge,
            {'merge type': 'edit merge'}, name='edit merge'),
        url(r'^(?P<node_id>\d+)/rank$', views.rank, name='rank'),
        )
