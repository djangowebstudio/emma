from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, Template, RequestContext
from django.shortcuts import render_to_response, get_list_or_404
from emma.interface.models import *
from django.http import Http404
from django.contrib.auth.decorators import login_required
from emma.core.metadata import Metadata
from emma.interface.models import Image
from django.core.management import setup_environ
import settings
setup_environ(settings)
import os, sys

content_root = getattr(settings, 'APP_CONTENT_ROOT', None)

def postcode(request, item):
    """Renders image metadata"""
    
    try:
        i = Image.objects.get(image_LNID=item)
        path =  os.path.join(content_root, i.image_real_path)
    except ObjectDoesNotExist:
        raise Http404
    
    try:
        postcode = Metadata().exifJSON(path, 'creatorpostalcode')['CreatorPostalCode']
    except:
        postcode = None
    
    google_api_key = getattr(settings, 'GOOGLE_API_KEY', None)
    return render_to_response('metadata/postcodemap.html', locals(), context_instance=RequestContext(request))
    
    
