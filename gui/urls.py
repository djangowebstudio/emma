from django.conf.urls.defaults import *

urlpatterns = patterns('emma.gui.views',
    url(r'^$', 'index'),
    url(r'^(?P<p>\d+)/$', 'index'),
    url(r'^folder/(?P<path>.*)/(?P<p>\d+)/$', 'folder'),     
    url(r'^folder/(?P<path>.*)/$', 'folder'),   
    url(r'^toggle/sorting/$', 'sorting'),
    url(r'^change/pagesize/(?P<page_size>[0-9]+)/$', 'page_size'),   
    url(r'^show_costs/(?P<item>.*)/$', 'show_costs', name='show_costs'),

)