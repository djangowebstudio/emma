from django import template
import settings
from django.template import Library
register = Library()
import os, sys

def mknode(path):
    "Return HTML for the entire tree"
    p = path.replace(settings.APP_CONTENT_ROOT + '/', '')
    if p:
        node = '<div id="%s" class="menu-passive"><a href="/gui/folder/%s">%s</a>' % (p.replace('/', '_').lower(), p.lower(), path.split('/').pop())
    else:
        node = ''
    for f in os.listdir(path):
        fullname = os.path.join(path, f)
        if os.path.isdir(fullname):
            el = mknode(fullname)
            node += el
    if p:
        node += '</div>'
    else:
        node += ''
    return node

@register.tag(name="emma_menu")
def build_menu(parser, token):
    menu = mknode(settings.APP_CONTENT_ROOT + '/')
    return MenuNode(menu)
    
    
class MenuNode(template.Node):
    def __init__(self, menu):
        self.menu = menu
    def render(self, context):
        return self.menu
    