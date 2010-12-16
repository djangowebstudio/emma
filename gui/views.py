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
from django.utils.translation import ugettext_lazy as _



@login_required
def index(request, p=1):
    """Returns the last xx items"""
    
    # get no. of items & page_range from settings    
    number = getattr(settings, 'APP_NO_ITEMS', 100)
    page_range = getattr(settings, 'APP_PAGE_RANGE', range(8, 88, 8))
    # get sorting order & page_size
    preferences = prefs(request)
    sortpref, page_size = preferences['sortpref'], preferences['page_size']

    order = 'image__date_modified' if sortpref == 1 else '-image__date_modified'
    m = Metadata.objects.all().order_by(order)
    m = m[:number] if number else m
    page = get_page(request, m, p)    
    
    # Check the contract FIXME: abstract & move to middleware
    if getattr(settings,'USERS_USE_CONTRACT', 1) == 1:
        try:
            c = Contract.objects.get(user=request.user.id)
            if c.contract == 1: 
                return render_to_response('gui/main.html', locals(), context_instance=RequestContext(request))   
            else:
                return render_to_response('contract.html', {'user': request.user}, context_instance=RequestContext(request))
        except Contract.DoesNotExist:
            return render_to_response('contract.html', {'user': request.user}, context_instance=RequestContext(request))
            
    else: return render_to_response('gui/main.html', locals(), context_instance=RequestContext(request))
    

@login_required                                                            
def folder(request, path='', p=1):
    """
    Queries for path
    """
    url = 'folder/%s/' % path
    if path.startswith('/'):
        path = path[1:]
        
    preferences = prefs(request)
    sortpref, page_size = preferences['sortpref'], preferences['page_size']
    
    # get page range from settings
    page_range = getattr(settings, 'APP_PAGE_RANGE', range(8, 88, 8))
    order = 'image__date_modified' if sortpref == 1 else '-image__date_modified'
    m = Metadata.objects.filter(image__image_real_path__istartswith=path).order_by(order)
    
    page = get_page(request, m, p)
        
    # Check the contract
    if getattr(settings,'USERS_USE_CONTRACT', 1) == 1:
        try:
            c = Contract.objects.get(user=request.user.id)
            if c.contract == 1: 
                return render_to_response('gui/main.html', locals(), context_instance=RequestContext(request))   
            else:
                return render_to_response('contract.html', {'user': request.user}, context_instance=RequestContext(request))
        except Contract.DoesNotExist:
            return render_to_response('contract.html', {'user': request.user}, context_instance=RequestContext(request))
            
    else: return render_to_response('gui/main.html', locals(), context_instance=RequestContext(request))
    
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
        u, created = User.objects.get_or_create(user=request.user.id)
        prefs['sortpref'] = int(u.order)
        prefs['page_size'] = int(u.pagesize)
    except Exception, inst: 
        prefs['sortpref'] = 1
        prefs['page_size'] = 8
    return prefs


def sorting(request):
    """ Change sorting order in User Preferences"""
    u, created = User.objects.get_or_create(user=request.user.id)
    u.order = 1 if u.order == 0 else 0
    u.save()
    return HttpResponse(_('Order by date set to descending (oldest first)') if u.order == 0 else _('Order by date set to ascending (newest first)'))
    
def page_size(request, page_size):
    """ Changes page size in user preferences"""    
    try:
        u, created = User.objects.get_or_create(user=request.user.id)
        u.pagesize = page_size
        u.save()
        return HttpResponse('saved pagesize %s' % page_size)
    except Exception, inst:
        return HttpResponse('Sorry, something went wrong %s' % inst)
        

