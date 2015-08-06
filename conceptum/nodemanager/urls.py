from django.conf.urls import patterns, url, include

from nodemanager import views

urlpatterns = patterns('',

        url(r'^(?P<node_id>\d+)/$', views.display, name='nodemanager display'),
        url(r'^(?P<node_id>\d+)/submit_entry', views.submit_entry, name = 'nodemanager submit_entry'),
        url(r'^(?P<node_id>\d+)/finalize', views.finalize, name='nodemanager finalize'),

        url(r'^(?P<node_id>\d+)/advance', views.advance, name='nodemanager advance'),


        # TODO: replace these with a submit merge? or submit/finalize_merge, renaming finalize above?
#        url(r'^(?P<node_id>\d+)/newmerge', views.get_merge,
#            {'merge_type': 'add merge'}, name='add merge'),
#        url(r'^(?P<node_id>\d+)/editmerge', views.get_merge,
#            {'merge_type': 'subtract merge'}, name='subtract merge'),
#        url(r'^(?P<node_id>\d+)/finalmerge$', views.finalize_merge, name='final merge'),

        url(r'^(?P<node_id>\d+)/rank/', include('ranking.urls')),
        )
