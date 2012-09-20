from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, Template
from django.shortcuts import render_to_response, get_list_or_404
import emma.core.utes as utes
import time, os, sys, shutil, re
from django.core.management import setup_environ
from django.contrib.auth.decorators import login_required
import settings
setup_environ(settings)
import subprocess

@login_required
def controller(request):
	return render_to_response('controller.html')

def plist(item): 
	"""Compile plist names and paths."""
	name = '.'.join(['com', settings.APP_ROOT.split('/').pop(), item, 'plist'])
	source = os.path.join(settings.APP_ROOT, 'launchd', name)
	target = os.path.join(settings.APP_PLIST_ROOT, name)
	
	return {'name': name, 'source': source, 'target': target}


def copy(request, item):
	"""Copy a plist to target."""
	try:
		shutil.copy(plist(item)['source'], plist(item)['target'])
		return HttpResponse("%s copied" % plist(item)['name'])
	except Exception, inst:
		return HttpResponse("Error: %s" % inst)
		
def check_status(request, item):
	""" checks the status of launchctl item, returns an HttpResponse"""
	u = utes.Utes()
	return HttpResponse(0 if u.check_status(item) == None else 1)
				
def launchctl(request, action, item):
	"""
	Invoke a launchctl command for an item
	takes: action (str), item (str)
	returns: a response by calling emma.utes.Utes().check_status()
	"""
	# Initiate a dict containing launchctl commands
	actions = {'load': 'load', 'unload': 'unload'}
	p = subprocess.Popen(["su","geert","launchctl", actions[action], "-w", plist(item)['target']],stdout=subprocess.PIPE).stdout.read()
	u = utes.Utes()
	r = u.check_status(item)
	response = '%s loaded with status %s' % (item, r) if r else '%s not loaded with response %s' % (item, p)
	return HttpResponse(response)


def tail_f(request, item):
	u = utes.Utes()
	log = '.'.join([item, 'log'])
	path = os.path.join(settings.APP_LOGS_ROOT, log)
	if os.path.exists(path):
		if os.path.getsize(path) > 0:
			r = u.tail_f(path)
			return HttpResponse('<pre>%s</pre>' % r)
		else:
			return HttpResponse('The requested log is empty.')
	else:
		return HttpResponse("The requested log doesn't appear to exist.")