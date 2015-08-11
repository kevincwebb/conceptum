from django.conf.urls import patterns, url, include

from cistage1 import views

urlpatterns = patterns('',
            #/stage1/
            url(r'^$', views.dispatch, name='stage1 dispatch'),

            #/stage1/setup/
            url(r'^setup$', views.setup, name='stage1 setup'),

            #/stage1/getsetup/
            url(r'^configure$', views.configure, name = 'stage1 configure'),

            url(r'^edit_tree', views.edit_tree, name='stage1 edit_tree'),

            url(r'^node/', include('nodemanager.urls')),
        )
