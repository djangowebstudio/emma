from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, Template, RequestContext
from django.shortcuts import render_to_response, get_list_or_404
from emma.interface.models import *
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.management import setup_environ
import settings
setup_environ(settings)

def index(request):
    """Returns index template"""
    k = Keyword.objects.all()
    nums = []
    for i in k: 
        n = len(i.keywords.split(','))
        nums.append(n)
    nums.sort()
    longest = nums[len(nums)-1]
        
    return render_to_response('columnview/index.html', {'range': longest},context_instance=RequestContext(request) )


def get(request, key=0, search=None):
    """Returns column"""
    k = Keyword.objects.all() if not search else Keyword.objects.filter(keywords__icontains=search)
    first, f, d = [], [], {}
    for i in k: 
        try: first.append( i.keywords.split(',')[int(key)] )  
        except: pass    
    #     remove duplicates
    for w in first: d[w] = w
    for k, v in d.iteritems(): f.append(v)
    f.sort()
          
    return render_to_response('columnview/base.html', {
                                'first': f, 
                                'search': search,
                                'key': int(key) + 1,
                                }, context_instance=RequestContext(request))
    
    