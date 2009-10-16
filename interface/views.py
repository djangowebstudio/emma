#**************************************************************************************************
# Geert Dekkers Web Studio 2008, 2009
# nznl.com | nznl.net | nznl.org INTERNET PRODUCTIONS
# views.py - django views for eam.interface
#
#**************************************************************************************************
import zipfile
from cStringIO import StringIO
import os, sys, pwd
import sets
import time
import datetime
from time import strftime
from operator import itemgetter
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, Template
from django.shortcuts import render_to_response, get_list_or_404
from eam.interface.models import *
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.core.paginator import Paginator, InvalidPage
from django.core.mail import send_mail
from django.views.decorators.cache import never_cache   # are we using this???
from django.core.management import setup_environ
import settings
setup_environ(settings)
import eam.core.utes as utes
import re
import subprocess
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

#--------------------------------------------------------------------------------------------------
# Statics for use in zip functions
prefix_HR = settings.APP_CONTENT_ROOT
prefix_LR = settings.GALLERY_ROOT + "/images/"

#--------------------------------------------------------------------------------------------------
@login_required
def index(request):
    """ Redirects user to first page """
    # Redirect IE6 users to help page (todo: a browser detection class)
    if request.META['HTTP_USER_AGENT'].find('MSIE 6.0') > -1: 
        try:
            r = User.objects.get(user=request.user.id)
        
            if r.setting2 == 1: 
                return render_to_response('index.html', {'username': request.user.username, 'title': settings.APP_PUBLIC_NAME})
            else:
                r.setting2 = 0
                r.save()
                return render_to_response('ie6.html')
        except: return render_to_response('ie6.html')
    
        
    # Check the contract
    if settings.USERS_USE_CONTRACT == 1:
        try:
            c = Contract.objects.get(user=request.user.id)
            if c.contract == 1: 
                return render_to_response('index.html', {'username': request.user.username, 'title': settings.APP_PUBLIC_NAME})     
            else:
                return render_to_response('contract.html', {'user': request.user})
        except Contract.DoesNotExist:
            return render_to_response('contract.html', {'user': request.user})
            
    else: return render_to_response('index.html', {'username': request.user.username, 'title': settings.APP_PUBLIC_NAME})

def ie6(request, action=None): 
    """ Returns a page for internet explorer 6"""
    # IE6 users can choose to visit EAM regardless of their antiquated browser (but they'll regret it)
    if action == None:
        return render_to_response('ie6.html')
    else:
        try:
            r = User.objects.get(user=request.user.id)
            r.setting2 = 1
            r.save()
            return render_to_response('index.html', {'username': request.user.username, 'title': settings.APP_PUBLIC_NAME})
        except Exception, inst:
            return HttpResponse(_('An error has occurred saving your Internet Explorer preferences %s') % inst)
    
def stock(request):
    """ Returns an information page on stock photography"""
    return render_to_response('stock.html')

def buildZippedFolder(username, itemObj, zip_filename, album):
    """Builds a zip file from a Folder, updates orders table. Note that you'll need to be able to write to the packages folder. See settings.APP_PACKAGES_ROOT"""
    clientImage = '.'.join([username,album.album_identifier])
    zip_path = settings.APP_PACKAGES_ROOT + "/" + zip_filename
    try:
    
        zip = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)

        # If the album has an attachment, add it to the zip     
        album_attachment = attachment_search(album.album_identifier, 'album')
        if album_attachment: 
            f = ''.join(['README-', utes.Utes().bad().sub('-', album.album_name), os.path.splitext(album_attachment[1])[1]])
            zip.write(album_attachment[0], str(f))
        
        # Iterate through the items in the album, attaching path and filename to the zip
        for a in album.image.all():     

            # Consider the resolution when determining the path         
            if itemObj.resolution == 'HR':
                item = os.path.join(prefix_HR, a.image_real_path).encode('utf-8')
                fname = a.image_real_name.encode('utf-8')
            else:
                item = os.path.join(prefix_LR, a.image_name).encode('utf-8')
                fname = a.image_name.encode('utf-8')
            zip.write(item, fname)
            
            # Add attachment for the item if it exists
            attachment = attachment_search(a.image_LNID, 'metadata')
            if attachment: zip.write(attachment[0], ''.join(['README-', attachment[1]]))

        zip.close()
        #
        # Update Order to reflect the status of the download.
        # This is just once per album, accepting that future changes in the album
        # may distort the reality of this piece of data. 
        #
        
        try:
            o = Order.objects.get(clientImage=clientImage)
            o.status = 1
            o.group_name=album.album_name
            o.album_identifier = album.album_identifier
            o.save()
            #print ('Saving found order object %s' % o)
        except Order.DoesNotExist:
            try: 
                i = Order(
                image=a,
                image_LNID=a.image_LNID,
                resolution=itemObj.resolution,
                group_name=album.album_name,
                client=muser.username,
                clientImage=clientImage,
                status=1)
                i.save()
                #print( 'made new order obj')
            except Exception, inst: pass
                #print( 'error saving order object %s' % inst)
                
        # Get information for later rendering as text
        group = album.image.all()
        for g in group: 
            try:
                b = Keyword.objects.get(image_LNID=g.image_LNID)
                g.cright = b.cright
                g.profile = b.profile
                g.resolution = itemObj.resolution
            except Exception, inst: pass
                #print ('Error compiling group information %s' % inst)
        return zip_path, group
        
            
    except Exception, inst:
        #print('Error %s ' % inst)
        return None

def attachment_search(item_id, folder): 
    """ Search the attachments folder for matching file """
    
    for root, dirs, files in os.walk(os.path.join(settings.MEDIA_ROOT, folder)):
        for f in files:
            if os.path.splitext(f)[0] == item_id:
                return os.path.join(root, f), f
    
    
@login_required
def doBuildZIP(request):
    """Builds zipfile, sends email"""
    muser = request.user
    buffer = StringIO()
    zip = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)

    groupList = []
    imageList = []
    itemList = Order.objects.select_related().filter(client__exact=muser.username, status=0)
    for i in itemList:
        # Get the related albums if they exist. Then call doBuildZippedFolder to generate 
        # a zip which is to be added to the zip above. Additionally, an object is added
        # to groupList initiated above.
        
        if i.album_identifier: 
            try:
                album = Album.objects.get(album_identifier=i.album_identifier)
                zipfilename = utes.Utes().bad().sub('-', i.group_name).replace('/','-') + '.zip'.encode('utf-8')            
                z = buildZippedFolder(muser.username, i, zipfilename, album)
                zip.write(z[0], zipfilename.encode('utf-8'))
                groupList.append(z[1])
                # To do: Get rid of the saved zip now....
            except Exception, inst: pass
                #print ('error occurred at buildZippedFolder %s'  % inst)
            
        else:
            a = i.image
            i.image_real_path = a.image_real_path
            i.image_name = a.image_name
            i.image_real_name = a.image_real_name
                
            
            
            # Add the properties we need for the email from Keyword
            
            try:
                b = Keyword.objects.get(image_LNID=i.image_LNID)
                i.cright = b.cright
                i.profile = b.profile
            except Keyword.DoesNotExist:
                pass
        
            # Append the properties to the imageList
            imageList.append(i)
            
            # Get the path to the file on disk. HR/LR download checked? 
            # Also, get the filename of the zipped file in fname
            
            if i.resolution == 'HR':
                item = os.path.join(prefix_HR, i.image_real_path).encode('utf-8')
                fname = i.image_real_name.encode('utf-8')
            else:
                item = os.path.join(prefix_LR, i.image_name).encode('utf-8')
                fname = i.image_name.encode('utf-8')
            
            # Write the item to the zip
            zip.write(item,fname)
            # Now, if the item includes an attached document, write it. 
            attachment = attachment_search(i.image_LNID, 'metadata')
            if attachment: zip.write(attachment[0], ''.join(['README-', attachment[1]]))
                        
            
            
    zip.close()
    buffer.flush
    
    t = loader.get_template('emailtemplates/downloads.txt')
    c = Context({'name': muser.first_name,'imageList': imageList, 'groupList': groupList })
    
    settings.APP_EMAIL_RECIPIENTS.append(muser.email)
    send_mail('%s download' % settings.APP_PUBLIC_NAME, t.render(c), settings.APP_EMAIL_SENDER, settings.APP_EMAIL_RECIPIENTS, fail_silently=False )
    # delete the downloaded items in the cart
    downloadList = Order.objects.filter(client=muser.username, status=0)
    
    for item in downloadList:
        item.status = 1
        item.save()

    response = HttpResponse(buffer.getvalue(),mimetype = 'application/zip')
    response['Content-Disposition'] = 'attachment; filename='+strftime("%Y%m%d%H%M%S")+'-'+settings.APP_PUBLIC_NAME+'-download.zip'
    buffer.close()
    return response

@login_required
def doEmptyBasket(request):
    muser = request.user
    try:
        Order.objects.filter(client=muser, status=0).delete()
        return HttpResponse(_('Your basket is empty.'))
    except Exception, inst:
        return HttpResponse(_('An error occurred while emptying you basket.'))

@login_required
def doRemoveFromBasket(request,item):
    """Removes item from basket"""
    try:
        Order.objects.filter(pk=item).delete()
        msg = _('The item has been removed')
    except:
        msg = _('An error occurred. The item was not removed')
    
    return HttpResponse(msg)
    
def doUpdateBasket(request,item):
    
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
def doCreateEntryForAlbum(request, album):
    
    a = Album.objects.get(album_identifier=album)
    try:
        leaders = a.image.filter(group_status='leader')
        for leader in leaders:
            clientImage = '.'.join([request.user.username, album])
        #print clientImage
        try:
            o, c = Order.objects.get_or_create(image=leader, image_LNID=leader.image_LNID, client=request.user.username, clientImage=clientImage, group_name=a.album_name, album_identifier=a.album_identifier, status=0, resolution='HR')
            r = _('%s is in your basket') % a.album_name if c else _('%s is already in there!') % a.album_name
        except Exception, inst:
            try:
                i = Order.objects.get(clientImage=clientImage, status=1)
                i.status = 0
                i.save()
                r = _('%s has already been downloaded') % a.album_name
            except Exception, inst:
                r = _('%(album)s is already selected %(inst)s') % { 'album': a.album_name,'inst': inst }                
    except Exception, inst:
        return HttpResponse(_("An error has occurred -- unable to get album leader %(inst)s %(leader)s") % {'inst':inst,'leader': leader})  
    return HttpResponse(r)



@login_required
def doCreateEntry(request, item, album=None):
    """Creates entry in basket"""
    muser = request.user
    currentItem = Image.objects.get(image_LNID=item)
    
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
        obj, created = Order.objects.get_or_create(image=currentItem,image_LNID=currentItem.image_LNID, client=muser.username, clientImage=clientImage, group_name=currentItem.group_name, album_identifier=currentItem.album_identifier,status=0, resolution='HR')
        if created == True:
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
            i.save()
            resp = _('%(item)s had been downloaded (more than) once already.') % {'item': i.image_LNID if len(currentItem.group_name) == 0 else currentItem.group_name }
        except Exception, inst:
            resp = _('%(item)s already selected') % {'item':item}
        
    
    return HttpResponse(resp)

@login_required 
def doShowData(request, item, t):
    """
    Shows metadata in DOM element.
    Presents both old-style, i.e. presenting only the description field,
    and new style, whereby multiple metadata field are presented.
    dict
    To do: Have the template translate the field names
    """
    template = 'parts/doShowLayout.html' if int(t) == 1 else 'parts/doShowData.html' # Use a different template if t has a value
    dataDict = {}  # Initiate a dict
    
    try:
        dataDict = Metadata.objects.filter(image_LNID=item).values('subject', 'description', 'location', 'source', 'datetimeoriginal', 'softdate', 'keywords', 'credit', 'creator', 'instructions')
        
        for d in dataDict:
            for k, v in d.iteritems():
                if v == '-':
                    d[k] = ''
        
        try:
            image_LNID_prefix = int(item[0:5])
            i = 0 if image_LNID_prefix < settings.APP_NEW_DATA else 1
        except Exception, inst:
            i = 1
            
        return render_to_response(template, {'dataDict' : dataDict, 'i': i, 'item': item})
    except Exception, inst:
        
        dataDict = {_('Exception'): _('no information')}
        return render_to_response(template, {'dataDict' : dataDict, 'item': item})


    

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
    
        
@login_required
def doShowBasket(request, time):
    muser = request.user
    itemList = Order.objects.select_related().filter(client=muser.username, status=0).order_by('-ts')
    count = itemList.count()
    for i in itemList:
        a = i.image
        i.image_name = a.image_name
        i.image_category = a.image_category
        if get_album(a,i): i = get_album(a,i)
        
        
    return render_to_response('parts/doShowBasket.html', { 'itemList' : itemList, 'count': count, 'appendix': strftime("%Y%m%d%H%M%S") })


@login_required 
def doShowTags(request, format, search='all', page=1):
    """Shows tags in list or cloud"""
    u = utes.Utes()
        
    if search == 'all':
        search = ''
        
    itemListObj = KeywordCount.objects.filter(keyword__startswith=search).order_by('keyword')
    count = KeywordCount.objects.all().count()
    
    itemList = []
    for i in itemListObj:
        i = i.keyword.replace(" ", " +"), i.keyword, i.count, u.recount(i.count)
        itemList.append(i)
    
    if format == 'cloud':
        template = 'parts/doShowCloud.html'
    else:
        template = 'parts/doShowTags.html'
    
    if search == '':
        search = 'all'

    paginator = Paginator(itemList, 30).page(page)
    return render_to_response(template, {'count': count, 
                                         'search': search, 
                                         'paginator':paginator.object_list,
                                         'has_next':paginator.has_next(),
                                         'has_prev':paginator.has_previous(),
                                         'next_page': paginator.next_page_number(),
                                         'prev_page': paginator.previous_page_number(),
                                        })

@login_required
def doShowThumbs(request,match,cat,weeks=0,page=1,groups=1):
    
    """Shows thumbs
    Takes: match (str or int), cat (str), weeks (int), page (int) groups (int)
    
    """
    # Override groups user pref if groups arg is set
    try:
        int(groups) # Test groups arg: is it an int?
        override_user_grp_prefs = int(groups)
    except:
        groups = 1
        override_user_grp_prefs = None
        

    # Get user prefs (pagesize, album visibility, order) if groups arg is unchanged
    try:
        u = User.objects.get(user=request.user.id)
        sortpref = u.order
        pageSize = u.pagesize
        if not override_user_grp_prefs == 0: 
            if not u.setting1 == None:
                groups = u.setting1
            else:
                groups = 1
        else:
            groups = override_user_grp_prefs
    except Exception, inst: 
        #print 'error %s' % inst
        sortpref = 1
        pageSize = 8
        groups = 1
        

    order = 'interface_image.date_modified' if sortpref == 1 else '-interface_image.date_modified'
    
    # Replace the _SLASH_ delimiters
    cat = cat.replace("_SLASH_","/")
    
    # Initiate date variables   
    today = datetime.datetime.today()
    
    difference = datetime.timedelta(weeks=-int(weeks))
    start_date = today + difference
    if match == '_ALL_':
        if cat == '_ALL_':
            cat = ''
        if groups == 0:
            itemListObj = Keyword.objects.select_related().filter(image__image_real_path__istartswith=cat.replace('/','',1), image__date_modified__range=(start_date, today)).order_by(order)
        else:           
            itemListObj = Keyword.objects.select_related().filter(image__image_real_path__istartswith=cat.replace('/','',1), image__date_modified__range=(start_date, today)).exclude(image__group_status__icontains='follower').order_by(order)
    else:
        if cat == '_SOURCE_':
            try:
                itemListObj = Metadata.objects.select_related().filter(source__contains=match)
                
            except Exception, inst:
                pass
        
        elif cat == '_ALL_':
            cat = ''
            try:
                fnMatch = int(match[0:5])
                itemListObj = Keyword.objects.select_related().filter(image_LNID=match)
            except:
                if groups == 0:
                    itemListObj = Keyword.objects.select_related().filter(keywords__search='+' + match, image__image_real_path__istartswith=cat).filter(image__date_modified__range=(start_date, today)).order_by(order)
                else:
                    itemListObj = Keyword.objects.select_related().filter(keywords__search='+' + match, image__image_real_path__istartswith=cat).filter(image__date_modified__range=(start_date, today)).exclude(image__group_status__icontains='follower').order_by(order)
        else:
            if groups == 0:
                itemListObj = Keyword.objects.select_related().filter(keywords__search='+' + match, image__image_real_path__istartswith=cat).filter(image__date_modified__range=(start_date, today)).order_by(order)
            else:
                itemListObj = Keyword.objects.select_related().filter(keywords__search='+' + match, image__image_real_path__istartswith=cat).filter(image__date_modified__range=(start_date, today)).exclude(image__group_status__icontains='follower').order_by(order)
    
    # Get the number of occurrences here, before adding count to the object...
    count = itemListObj.count()
    for i in itemListObj:
    
        a = i.image
        i.image_category = a.image_category
        i.image_pages = a.image_pages
        i.image_name = a.image_name
        if groups == 1:
            if get_album(a,i): i = get_album(a,i)
        else:
            try:
                i.document = Metadata.objects.get(image=i).document
            except: pass
            
    

    # Render pages
    paginator = Paginator(itemListObj, int(pageSize))
    
    try:
        p = paginator.page(page)
    except InvalidPage:
        p = paginator.page(1)

    if cat == '':
        cat = '_ALL_'
    if match == '':
        match = '_ALL_'
    return render_to_response('parts/doShowThumbs.html', {
    'count': count, 
    'pageSize': pageSize, 
    'pages': p,
    'match': match, 
    'cat': cat.replace("/","_SLASH_"), 
    'weeks': weeks, 
    'paginator':p.object_list,
    'has_next':p.has_next(),
    'has_prev':p.has_previous(),
    'next_page': p.next_page_number(),
    'prev_page': p.previous_page_number(),
    'last_page': paginator.num_pages,
    'first_page': 1,
    'appendix':strftime("%Y%m%d%H%M%S"),
    'sortpref' : sortpref,
    'groups': groups,
    'albumpref' : _('item view') if groups == 1 else _('album view'),
    'order': _('show newest first') if sortpref == 1 else _('show oldest first'),
    'div': 'content',
    },context_instance=RequestContext(request))




def doShowAlbumContents(request, album, div):
    """Presents the album content into a template. 
    Takes album, and a div argument which is passed to the template unchanged"""
    
    try:
        a = Album.objects.get(album_identifier=album)
        content = a.image.all()
        for item in content:
            m = Metadata.objects.get(image=item)
            item.copyright = m.copyright
            item.profile = m.profile
            item.document = m.document
        a.content = content
    
        return render_to_response('parts/doShowAlbumContents.html', {'album': a, 'div': div},context_instance=RequestContext(request))
    except Exception, inst:
        return render_to_response('parts/doShowAlbumContents.html', {'debug': inst})
    
    
    
def doShowGroup(request,container,item, page=1):
    """Deprecated"""
    try:
        r = Group.objects.get(image_LNID=container)
        subject = r.image_group
        group = Metadata.objects.filter(subject=subject).order_by('image_LNID')
        for i in group:
            a = i.keyword
            i.cright = a.cright
            i.profile = a.profile
            
        paginator = Paginator(group, 1)

        try:
            p = paginator.page(page)
        except InvalidPage:
            p = paginator.page(1)

        return render_to_response('parts/doShowGroup.html', {
        'container': container,
        'page': page,
        'pages': p,
        'paginator':p.object_list,
        'has_next':p.has_next(),
        'has_prev':p.has_previous(),
        'next_page': p.next_page_number(),
        'prev_page': p.previous_page_number(),
        'last_page': paginator.num_pages,
        'first_page': 1,
        'complete_group': group,
        'group_name': subject,
        })
    
    except Exception, inst:
        return HttpResponse(_('De requested album does not exist'))
    
    

@login_required
def doCheckCart(request, item):
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
def updateSearchSelect(request, mode):
    """Updates search mode in User (eam.interface.models) """
    u = request.user.id
    
    try:
        s = User.objects.get(user=u)
        s.search = mode
        s.save()
    except User.DoesNotExist:
        s = User(user=u, search=mode)
        s.save()
        
    return HttpResponse('')
    
def doSearch(request):
        """Generates a clickable tag list, multiple templates possible.     
        1. Return gives a straight search in doShowThumbs
        The search term is included in the resultant query to
        2. Additionally, if the user enters three integers, a simple filename
        search is initiated."""
    
        u = utes.Utes()                                                                                                 # Initiate the utes class
        match = request.POST.copy()
        
            
        
        itemList = []
        itemListMerged = []
        itemListFinal = []
        
        try:
            mode = User.objects.get(user=request.user.id).search
        except:
            mode = 'simple'
            
        # Keep the search query for analysis

        try:
            q = Query(user=request.user.id, mode=mode, query=match['s'])
            q.save()
        except Exception, inst: pass
        
        
        if mode == 'image':                                                                                             # Initiate a list to hold results
            try:
                filename = match['s']                                                                                   # Can we change the request to integer?
                itemListObj = Image.objects.filter(image_LNID__startswith=filename).order_by('image_LNID')[:30]         # If so, we can search for a file beginning with the requested characters
                for i in itemListObj:
                    m = i.image_LNID, i.image_LNID
                    itemListFinal.append(m)
                return render_to_response('parts/doShowSearch.html', {'itemList': itemListFinal })
            except Exception, inst:
                return render_to_response('parts/doShowSearch.html', {'itemList': [_('No results')]})
        elif mode == 'advanced':                                                                                        # If changing the request to integers doesn't work, we are apparently searching for keywords
            searchterm = match['s'].replace(" ", " +") + "*"
            itemListObj = Keyword.objects.filter(keywords__search=searchterm)[:30]
        
            for i in itemListObj:
                i = i.keywords.replace("."," ").strip().split(",")
                itemList.append(i)
            itemListMerged = u.merge(itemList)  
            for i in itemListMerged:
                m = ' +' + match['s'] + ' +' + i.strip().replace(" "," +")
                i = i, m
                itemListFinal.append(i)
            return render_to_response('parts/doShowSearch.html', {'itemList': itemListFinal,'mode': mode })
        elif mode == 'simple':
            searchterm = match['s'].replace(" ", " +") + "*"
            itemListObj = KeywordCount.objects.filter(keyword__search=searchterm)[:40]
        
            for i in itemListObj:
                m = i.keyword.replace("."," ").strip()
                n = ' +' + m.replace(" ", " +")
                x = m, n
                itemList.append(x)
            
                
                            
            return render_to_response('parts/doShowSearch.html', {'itemList': itemList, 'mode': mode})
            
        elif mode == 'source':
            searchterm = match['s']
            itemListObj = Metadata.objects.filter(source__startswith=searchterm).order_by('source')[:40]
            for i in itemListObj:
                m = i.source, i.source
                itemListFinal.append(m)
            return render_to_response('parts/doShowSearchSource.html', {'itemList': itemListFinal })
        else:
            return render_to_response('parts/doShowSearch.html', {'itemList': [_('No results')]})
                
        
@login_required
def doEnterFavorite(request, item, value=''):
    """Enters favorites"""
    
    this_user  = request.user
    if item.startswith('album'):
        album = Album.objects.get(album_identifier=item)
        for a in album.image.all():
            if a.group_status == 'leader': imageObj = a
            
        #print 'imageObj %s' % imageObj
    else:
        imageObj = Image.objects.get(image_LNID=item)
                                                                                        
    try:
        obj = Favorite.objects.get(user=this_user.username, image=imageObj, image_LNID=item)
        try:
            album_identifier = album.album_identifier
            album_name = album.album_name
        except:
            album_identifier = ''
            album_name = ''
        
        try:
            obj.tag=value
            obj.album_identifier=album_identifier
            obj.album_name=album_name
            obj.save()
            resp = _(' added to an existing favorite')  
        except Exception, inst:
            resp = 'update',inst
        
    
    except Favorite.DoesNotExist:
        
        try:
            album_identifier = album.album_identifier
            album_name = album.album_name
        except:
            album_identifier = ''
            album_name = ''
        
        try:
            obj = Favorite(user=this_user.username,image=imageObj,image_LNID=item,album_identifier=album_identifier,album_name=album_name,tag=value)
            obj.save()
            resp = _(' added new favorite')
        except Exception, inst:
            resp = 'new', inst
                        
    #return a result
    
    return HttpResponse(resp)
    
@login_required 
def doCallFavorite(request,item):
    """ Returns the favorite tag. """
    this_user  = request.user
    resp = ''
    try:
        obj = Favorite.objects.get(user=this_user.username,image_LNID=item)
        resp = obj.tag
    except:
        pass
    return HttpResponse(resp)
        
    
@login_required
def doShowFavorites(request, requestTemplate,  pageSize, page):
    """Shows favorite in the requested template"""
    this_user  = request.user
        
    itemList = Favorite.objects.select_related().filter(user=this_user.username).order_by('-ts')
    for i in itemList:
        a = i.image
        i.image_category = a.image_category
        i.image_pages = a.image_pages
        i.image_name = a.image_name
        m = Metadata.objects.get(image=a)
        i.cright = m.copyright
        i.profile = m.profile
        i.document = m.document
        if a.group_status == 'leader':
            try:
                i.album = Album.objects.get(album_identifier=m.album)
                content = i.album.image.all()
                for item in content:
                    m = Metadata.objects.get(image=item)
                    item.copyright = m.copyright
                    item.profile = m.profile
                    item.document = m.document
                i.album.content = content
            except:
                pass
        
    
    count = itemList.count()
    itemsPerPage = int(pageSize)
    paginator = Paginator(itemList, itemsPerPage)
    page_info = paginator.page(page)
    if requestTemplate == 'dock':
        template = 'parts/doShowFavorites.html'
    elif requestTemplate == 'edit':
        template = 'parts/doShowFavoritesLarge.html'
        
    
    return render_to_response(template,     
        {'page': page,
        'pages' : page_info,
        'count': count, 
        'paginator' : page_info.object_list,
        'prev' : page_info.has_previous(),
        'previous_page' : page_info.previous_page_number(),
        'next' : page_info.has_next(),
        'next_page' : page_info.next_page_number(), 
        'first_page': 1,
        'last_page': paginator.num_pages,
        'user': this_user,
        })
    
    
@login_required
def doRemoveFavorite(request,item):
    """Removes favorite"""
    Favorite.objects.get(pk=item).delete()
    
    return HttpResponse(_('removed'))

@login_required
def doStartPage(request,pageSize,cat,page):
    """Generates start page content."""
    itemList = Keyword.objects.filter(image__image_category=cat).exclude(image__group_status__icontains='follower').order_by('-interface_image.date_modified')[:50]
        
    for i in itemList:
    
        a = i.image
        i.image_category = a.image_category
        i.image_pages = a.image_pages
        i.image_name = a.image_name
        if get_album(a,i): i = get_album(a,i)
    
    paginator = Paginator(itemList, int(pageSize))
    
    try:
        p = paginator.page(page)
    except InvalidPage:
        p = paginator.page(1)
    return render_to_response('parts/doShowStartPage.html', 
        {'page': page,
        'pages' : p,
        'cat': cat, 
        'paginator' : p.object_list,
        'has_prev' : p.has_previous(),
        'previous_page' : p.previous_page_number(),
        'has_next' : p.has_next(),
        'next_page' : p.next_page_number(), 
        'first_page': 1,
        'last_page': paginator.num_pages,
        'appendix' : strftime("%Y%m%d%H%M%S"),
        'div': ''.join([cat,'_main_dl'])
        },context_instance=RequestContext(request))
        
@login_required
def doShowMenu(request,requestedDir=''):
    """ 
    Shows a menu node, using os.listdir. 
    Takes requestedDir
    Returns a menu node in a DOM element created on the fly."""
    # Apache doesn't seem to like empty url nodes so we fill them...
    
    requestedDir = requestedDir.replace('_SLASH_','/').replace('_ALL_','')
    crumbs = requestedDir
    
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
    
    return render_to_response('parts/doShowMenu.html', {'dirlist': dirlist, 'mList': requestedDir.replace('/', '_SLASH_') + "_SLASH_", 'crumbs': crumbs, 'user': request.user})
    

@login_required 
def doShowHelp(request):
    """Static help page"""
    return render_to_response('help.html')
        
@login_required
def signContract(request):
    """Digital contract. When user ticks the checkbox, this function is called. Template is only to be shown when user hasn't yet signed."""
    
    try:
        c = Contract.objects.get(user=request.user.id)
        if c.contract == 1:
            pass
        else:
            c.contract = 1
            c.username = request.user.username
            c.save()
    except Contract.DoesNotExist:
        c = Contract(user=request.user.id,contract=1,username=request.user.username)
        c.save()
    
    # Check it!
    try:
        chk = Contract.objects.get(user=request.user.id)
        if chk.contract == 1: 
            return HttpResponse('Je contract is getekend, %s. <a href="/">Ga naar beeldnet<a/>' % request.user.first_name)
        else:
            return HttpResponse('Er is iets misgegaan met het tekenen van het contract. Neem contact op met beeldnetsupport@schepper.nl of bel 020-3058800')
    except Contract.DoesNotExist:
        return HttpResponse('Het lukt niet om het contract te tekenen. Neem contact op met beeldnetsupport@schepper.nl of bel 020-3058800')


def doChangePageSize(request, pageSize):
    """ Changes page size in user preferences"""    
    
    try:
        u = User.objects.get(user=request.user.id)
        u.pagesize = pageSize
        u.save()
        return HttpResponse(_('saved pagesize %s') % pageSize)
    except Exception, inst:
        return HttpResponse(_('Sorry, something went wrong %s') % inst)
        
                        
def doChangeSortingOrder(request, order):
    """ Change sorting order in User Preferences"""

    u = User.objects.get(user=request.user.id)
    u.order = int(order)
    u.save()
    return HttpResponse(_('Order by date set to descending (oldest first)') if order == 0 else _('Order by date set to ascending (newest first)'))



def doChangeAlbumVisibility(request, visibility):
    
    u = User.objects.get(user=request.user.id)
    u.setting1 = int(visibility)
    u.save()
    return HttpResponse(_('Album visibility set to %s') % u.setting1) 
    
def doAddAlbum(request, album):
    """Add Album"""
    a = Album(album_identifier=album)
    a.save()
    return HttpResponse(_('new album generated'))   
    
def doAddToAlbum(request,album,item):
    """Add item to album"""
    
    # Get the Image object corresponding to the item. Note that the naming protocol forbids duplicate item names.
    # We'll therefore get an error back if the get() returns for than one result.
    try:
        i = Image.objects.select_related().get(image_LNID=item)
    except Exception, inst:
        return HttpResponse(_('An error getting the Image object %(inst)s for argument %(item)s') % {'inst': inst, 'item': item})
        
        
    # Get the Album associated with the album identifier. This most probably exists; actually no need to wrap it in a try
    try:    
        a = Album.objects.get(album_identifier=album)
        count = a.image.count()
        i.group_status = 'leader' if count == 0 else 'follower'
        m = Metadata.objects.get(image=i)
        i.copyright = m.copyright
        i.profile = m.profile
        # Add the image object to the album
        a.image.add(i)
        a.save()

        m.album = a.album_identifier
        m.headline = i.group_status
        m.documentname = a.album_name
        m.save()    

        
        return HttpResponse(_('%(item)s entered into album %(album)s') % {'item': item, 'album': a.album_name})
    except Exception, inst:
        return HttpResponse(_('An error occurred %s') % inst)
        

def doEditAlbum(request, album, text):
    """ Edit album name"""
    try:
        a = Album.objects.get(album_identifier=album)
        a.album_name = text
        a.save()
        return HttpResponse(_('Saved %s') % a.album_name)
    except Exception, inst:
        return HttpResponse(_('An error occurred %s') % inst)
        
def doRemoveFromAlbum(request, album, item):
    """Remove item from album, if possible"""
    try:
        i = Image.objects.get(image_LNID=item) 
        # As the naming protocol forbids duplicate image_LNID's we can go for this.
        # If there is a duplicate anyway, this function will immediately return the error. 
        
    except Exception, inst:
        return HttpResponse(_('An error occurred %s') % inst)
    
    try:
        a = Album.objects.get(album_identifier=album)
        count = a.image.count()
        if count > 0: # Of course this is always so; just leaving it in to catch any stragglers left from the dev process
            if not i.group_status == 'leader':
                i.group_status = ''
                a.image.remove(i)
                # If removed from an album, then the headline and document name in the item metadata will also have to go.
                try:
                    m = Metadata.objects.get(image_LNID=i.image_LNID)
                    m.documentname = ''
                    m.album = ''
                    m.headline = ''
                    m.save()
                    return HttpResponse(_('%(item)s removed from album %(album)s.') % {'item': item, 'album': a.album_name})
                except Exception, inst:
                    return HttpResponse( _("Error saving Metadata object for Album follower %s") % inst)
                                
                
            else: # it's a leader, choose another
                try:
                    new_leader = Image.objects.get(image_LNID=a.image.filter(group_status='follower')[0])
                    new_leader.group_status = 'leader'
                    new_leader.save()
                    i.group_status = ''
                    a.image.remove(i)
                    try:
                        m = Metadata.objects.get(image_LNID=i.image_LNID)
                        m.documentname = ''
                        m.album = ''
                        m.headline = ''
                        m.save()
                        return HttpResponse(_('%(item)s removed from this album. As this was the leader, %(new)s has now been made leader') % {'item': item, 'new': new_leader.image_LNID})
                    except Exception, inst:
                        return HttpResponse( "Error saving Metadata object for Album leader %s" % inst)
                    
                except Exception, inst:
                    try:
                        if count == 1: # It's probable that this is the case, as, apparently, there are no others to make leader
                            i.group_status = '' # NOTE: this means that the item can't be a leader and a follower at one time; 
                                                # this also means that the album concept within a file system trigger concept is fundamentally flawed.
                                                # To be left for the moment -- but anyway, why would the leader, contemplated as the REASON for the existence
                                                # of the album, be used to lead ANOTHER album?
                            i.image_pages = (count - 1)
                            i.save()
                            try:
                                m = Metadata.objects.get(image_LNID=i.image_LNID)
                                m.documentname = ''
                                m.album = ''
                                m.headline = ''
                                m.save()
                            except Exception, inst: pass
                                #print( "Error saving Metadata object for Album leader as last man standing %s" % inst)
                            
                            a.delete()  # Delete this album, because it will be invisible without an item to trigger its visibility.
                            return HttpResponse(_('The last item has been removed, and consequently the album %s has been deleted.') % a.album_name)
                    except Exception, inst:
                        return HttpResponse(_('An error occurred removing the last item. %s') % item)
                        
            
    except Exception, inst:
        return HttpResponse(_('An error occurred %s') % inst)
            
@login_required
def rotate(request, item, rotation):
    """ Rotate image """
    
    try:
        r = int(rotation)
    except Exception, inst:
        return HttpResponse('An error occurred %s' % inst)
                
    from PIL import Image as _i
    try:
        i = Image.objects.get(image_LNID=item)
        path = os.path.join(settings.APP_CONTENT_ROOT, i.image_real_path)
        img = _i.open(path)
        img.rotate(r).save(path)
        return HttpResponse('%s rotated %s degrees. Effects will be visible within %s seconds.' % (i, r, settings.APP_WATCH_DELAY))
    except Exception, inst:
        return HttpResponse('An error occurred processing %s %s' % (item, inst))