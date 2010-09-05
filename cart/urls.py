from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('emma.cart.views',
            url(r'^add/item/(?P<item>.*)/$', 'add', name='add_item'),
            url(r'^show/$', 'show', name="show_cart"),
            url(r'^show/(?P<time>.*)/$', 'show', name="show_cart_with_timestring"),
            url(r'^check/(?P<item>.*)/$', 'check', name="check_cart"),	
            url(r'^remove/(?P<item>\d+)/$', 'remove', name="remove_item"),
            url(r'^update/(?P<item>\d+)/$', 'update', name="update_item"),
            url(r'^empty/', 'empty', name="empty_cart"),
            url(r'^add/project/(?P<name>.*)/$', 'add_project', name="add_project"),
            url(r'^update/name/(?P<project_id>\d+)/$', 'update_name', name="update_name"),
        )



