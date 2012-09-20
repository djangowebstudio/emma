from django import template
from django.template import Library
register = Library()
from django.utils.safestring import mark_safe
import os

@register.filter(name="to_queries")
def to_queries(value):
    """Compiles search queries from keywords"""
    
    li = []
    kws = value.split(',')
    for kw in kws:
        li.append('<a href="/search?q=%s">%s</a>' % (kw, kw))
    
    output = ', '.join(li)
    return mark_safe(output)
    
@register.filter(name="ext")
def ext(path):
    """ Returns the extension"""
    try:
        s = os.path.splitext(path)[1].replace('.','')
    except:
        s = None
        
    return s