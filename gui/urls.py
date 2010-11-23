from django.conf.urls.defaults import *


urlpatterns = patterns('emma.gui.views',
    url(r'^$', 'index'),
    url(r'^(?P<p>\d+)/$', 'index'),
    url(r'^thumbs/(?P<requestedDir>.*)/(?P<p>\d+)/$', 'thumbs'),     
    url(r'^thumbs/(?P<requestedDir>.*)/$', 'thumbs'),   
    
    url(r'^menu/(?P<requestedDir>.*)/$', 'menu'),

)