from django.conf.urls.defaults import *
urlpatterns = patterns('',	
	(r'^$', 'emma.columnview.views.index'),
	(r'^get/(?P<key>\d+)/(?P<search>.*)/$', 'emma.columnview.views.get'),
	
	)