from time import strftime
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
from django.utils.translation import ugettext_lazy as _


@login_required
def empty(request):
    muser = request.user
    try:
        Order.objects.filter(client=muser, status=0).delete()
        return HttpResponse(_('Your basket is empty.'))
    except Exception, inst:
        return HttpResponse(_('An error occurred while emptying you basket.'))

@login_required
def remove(request,item):
    """Removes item from basket"""
    try:
        Order.objects.filter(pk=item).delete()
        msg = _('The item has been removed')
    except:
        msg = _('An error occurred. The item was not removed')
    
    return HttpResponse(msg)

@login_required   
def update(request,item):
    
    try:
        i = Order.objects.get(pk=item)
        if i.resolution == 'HR':
            i.resolution = 'LR'
        else:
            i.resolution = 'HR'
        i.save()
    except:
        pass    
    return HttpResponse('')
    
@login_required
def add(request, item, album=None):
    """Creates entry in basket"""
    muser = request.user
    currentItem = Image.objects.get(image_LNID=item)
    current_project = User.objects.get(user=muser.id).current_project

    if album:
        a = Album.objects.get(album_identifier=album)   
        currentItem.group_name = a.album_name
        currentItem.album_identifier = a.album_identifier
    else:
        currentItem.group_name = ''
        currentItem.album_identifier = ''

    # Compile unique id from client username and image_LNID
    clientImage = muser.username + "." + item

    try:
        obj, created = Order.objects.get_or_create(
                                                    image=currentItem,
                                                    image_LNID=currentItem.image_LNID, 
                                                    client=muser.username, 
                                                    clientImage=clientImage, 
                                                    group_name=currentItem.group_name, 
                                                    album_identifier=currentItem.album_identifier,
                                                    status=0, 
                                                    resolution='HR',
                                                    project=current_project
                                                    )
        if created:
            resp = _('%(item)s is in your basket') % {'item' : item if len(currentItem.group_name) == 0 else currentItem.group_name }   
        else:
            resp = _('%(item)s already here!') % {'item':item if len(currentItem.group_name) == 0 else currentItem.group_name }
    except Exception, inst:
        try: 
            i = Order.objects.get(clientImage=clientImage, status=1)            
            i.clientImage = clientImage
            i.status = 0
            i.image = currentItem
            i.image_LNID = currentItem.image_LNID
            i.group_name = currentItem.group_name
            i.album_identifier = currentItem.album_identifier
            i.resolution = 'HR'
            i.project = current_project
            i.save()
            resp = _('%(item)s had been downloaded (more than) once already.') % {'item': i.image_LNID if len(currentItem.group_name) == 0 else currentItem.group_name }
        except Exception, inst:
            resp = _('%(item)s already selected') % {'item':item}


    return HttpResponse(resp)
    
@login_required
def show(request, time=None):
    muser = request.user
    # Get basket name
    try:
        prefs = User.objects.get(user=request.user.id)
        current_project = prefs.current_project
    except:
        current_project = None

    itemList = Order.objects.select_related().filter(client=muser.username, status=0).order_by('-ts')
    count = itemList.count()
    for i in itemList:
        a = i.image
        i.image_name = a.image_name
        i.image_category = a.image_category
        if get_album(a,i): i = get_album(a,i)


    return render_to_response('cart/base.html', { 
                                                            'itemList' : itemList, 
                                                            'count': count, 
                                                            'appendix': strftime("%Y%m%d%H%M%S"), 
                                                            'current_project': current_project,
                                                            'projects': Project.objects.all() },
                                                             context_instance=RequestContext(request))
 
@login_required
def check(request, item):
     """
     Check for the existence of the item in the user cart.
     If something goes wrong while checking, just return a zero count, 
     so the add to cart button gets displayed regardless.
     Takes: item (image_LNID)
     Returns: integer
     """
     try:
         r =  Order.objects.filter(image_LNID=item, client=request.user, status=0).count()
     except:
         r = 0
     return HttpResponse(r)
     
@login_required
def update_name(request, project_id):
     """Updates project name"""
     p = Project.objects.get(id=project_id)
     try:
         u = User.objects.get(user=request.user.id)
         u.current_project = p
         u.save()
         orders = Order.objects.filter(client=request.user.username, status=0)
         for order in orders:
             order.project = p
             order.save()

         return HttpResponse(_("successfully entered project"))
     except Exception, inst:
         return HttpResponse(inst)
         
         
@login_required   
def add_project(request, name):
     """Adds a new project"""
     p, created = Project.objects.get_or_create(name=name)
     if created:
         p.slug = name.replace(' ', '-').lower()
         p.save()
     message = "successfully created new project" if created else "project with this name already exists"
     return HttpResponse(_(message))

def get_album(a,i):
     try:
         m = Metadata.objects.get(image=i)
         i.document = m.document
         if a.group_status == 'leader':
             try:
                 i.album = Album.objects.get(album_identifier=m.album)
                 return i
             except Exception, inst:
                 return (_("The item seemed to be part of an album, but no album found - %s") % inst)
         else: return None
     except: return None


