from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, Template, RequestContext
from django.shortcuts import render_to_response, get_list_or_404
from emma.interface.models import *
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, InvalidPage
from django.core.management import setup_environ
import settings
setup_environ(settings)
from emma.search.views import EmmaSearchView
import emma.core.utes as utes

def index(request, p=1):
    """Returns the last xx items"""
    number = getattr(settings, 'APP_NO_ITEMS', 100)
    m = Metadata.objects.all().order_by('-ts')[:number]
    
    page = get_page(request, m, p)    
    return render_to_response('gui/main.html', locals(), context_instance=RequestContext(request))
    
def menu(request,requestedDir=''):
    """ 
    Shows a menu node, using os.listdir. 
    Takes requestedDir
    Returns a menu node in a DOM element created on the fly."""
    # Apache doesn't seem to like empty url nodes so we fill them...
    requestedDir = requestedDir.replace('_SLASH_','/').replace('_ALL_','')
    crumbs = requestedDir
    mList = requestedDir.replace('/', '_SLASH_') + "_SLASH_"

    # Init utes 
    e = utes.Utes()

    # We'll be needing a list to hold the results
    dirlist = []
    results = os.listdir(settings.APP_CONTENT_ROOT + requestedDir)
    for d in results:
        if d[0:1] != '.':
            if d[0:2] != '--':
                if d[(len(d)-5):(len(d)-4)] != ".":
                    if d[(len(d)-4):(len(d)-3)] != ".":
                        if d[(len(d)-3):(len(d)-2)] != ".":
                            if d.lower()[0:4] != 'icon':
                                if not d.endswith('_original'):
                                # excludes returns a tuple, so...
                                    if False in e.excludes(d,settings.APP_MENU_EXCLUDES):
                                        dirlist.append(d.encode('utf-8'))

    return render_to_response('includes/menu-item.html', locals(), context_instance=RequestContext(request))
                                                            
def thumbs(request, requestedDir='', p=1):
    """
    Takes an encoded path, queries for path
    """
    url = 'thumbs/%s/' % requestedDir
    path = requestedDir.replace('_SLASH_', '/')
    if path.startswith('/'):
        path = path[1:]
    sortpref = prefs(request)['sortpref']
    order = 'interface_image.date_modified' if sortpref == 1 else '-interface_image.date_modified'
    m = Metadata.objects.filter(image__image_real_path__startswith=path).order_by(order)
    
    page = get_page(request, m, p)
        
    return render_to_response('gui/main.html', locals(), context_instance=RequestContext(request))
    
def get_page(request, obj, p=1):
    """Returns page for object"""
    paginator = Paginator(obj, prefs(request)['page_size']) 
    try:
        page = paginator.page(p)
    except InvalidPage:
        page = paginator.page(1)
    return page
            
def prefs(request):
    """Get user prefs (pagesize,  order)"""
    prefs = {}
    try:
        u = User.objects.get(user=request.user.id)
        prefs['sortpref'] = int(u.order)
        prefs['page_size'] = int(u.pagesize)
    except Exception, inst: 
        print inst
        prefs['sortpref'] = 1
        prefs['page_size'] = 8
    return prefs
    
    
