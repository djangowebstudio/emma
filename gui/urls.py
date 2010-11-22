from django.conf.urls.defaults import *


urlpatterns = patterns('emma.gui.views',
    url(r'^$', 'index'),
    url(r'^menu/(?P<requestedDir>.*)/$', 'menu'),
)