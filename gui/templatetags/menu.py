from django import template
import settings
from django.template import Library
register = Library()
import os, sys, re, time, fnmatch



def has_request_as_parent(d, name, url):
    u = filter(lambda x: len(x) > 0, url.split('/'))
    # The path should match the current url and the ancestors
    # thereof.
    # Compile a nested list from u, where the items are grouped
    # by their position in the list.
    m = []  
    [m.append(u[0:u.index(i)+1]) for i in u]    
    
    # Join the items in this list so that it contains the current
    # url, and the ancestor urls.
    
    flattened = ['/'.join(item) for item in m]
    
    
    for k, v in d.iteritems():
        if d[name] in flattened:
            return True
    return False
            

def mknode(path, url=''):
    """    
    What the recursive function does:
    --------------------------------
    Takes a path, generates the list. Only the directories are processed. 
    Each directory is then passed into the recursive function, where it 
    in turn generates a new list. When allowed to run without check, the 
    recursive function will generate the complete tree.
    
    We need to stop the propagation of the recursion through all the 
    available nodes, based on certain conditions. 
    
    1) When the program starts, it should generate the first level of nodes.
    This is actually quite easy, as we can control the node level by splitting
    the path into a list (l). When the list enters its first level, the path (minus
    the base path) should have exactly one node. So then, other paths consisting
    of more than one node are not allowed to be generated, by stopping the propogation
    of the recursion.
    
    2) After that, the user should initiate the next action by choosing one
    first-level node. A request is then made, consisting of a single node url.
    This url should stop the propagation of the recursive function for all but the
    requested child nodes of the parent url.
    
    The notion of "parent" and "child" is key to solving the problem. Obviously, there
    is no intrinsic awareness of a parent-child concept when generating the next level 
    of nodes from a previous one, other than the action of the user. The url is in 
    effect the "memory" for the generated next level of nodes.
        
    The depth and the vector of the path matching the current url is taken into account.    
    Returns one node more than you asked for, and all others less than you asked for.
    
    Let's say you have this tree:
    
    a/b/c/
    a/b/d/
    a/b/e/    
        
    so if path_info = /a/b/
    
    you'd want 
    a/
    a/b/
    a/b/c/
    a/b/d/
    a/b/e/    
    
    Caveat: The request for the parent does not return the true parent, only a match. As a 
    consequence, when a tree contains duplicate directory names within a single branch, the 
    strategy employed here will fail in some way.
    
    It would be interesting to devise a way of obtaining the true parent, preferably short 
    of implementing something like mptt.
        
    """
    p = path.replace(settings.APP_CONTENT_ROOT + '/', '')
    if p:
        link_text = path.split('/').pop()
        
        if link_text.lower() in filter(lambda x: len(x) > 0, url.split('/')):
            menu_class = 'active'
        else:
            menu_class = 'passive'
            
        node = '<div class="menu-passive" id="%s" ><a class="%s" href="/folder/%s">%s</a>' % (p.replace('/', '_').lower(), menu_class, p.lower(), link_text)
    else:
        node = ''
        
        
    # Initiate a dict d and get the relative path in respect to the 
    # full path path   
    d = {}
    try:
        relpath = os.path.relpath(path, settings.APP_CONTENT_ROOT).lower()
    except ImportError:
        relpath = path.replace(settings.APP_CONTENT_ROOT, '').lower()
        
    for f in os.listdir(path):
        fullname = os.path.join(path, f)
        
        
        if os.path.isdir(fullname):
            
            # The path fullname will be used to generate the next listdir
            # We need the relative path rel to check against the request
            rel = os.path.relpath(fullname, settings.APP_CONTENT_ROOT).lower()            
            
            # The key rel is assigned a value relpath. All of the dirs in the current
            # listdir will now be recognisable as having the same parent relpath.
            
            d[rel] = relpath
            
            # The length of l is used for the first-level listdir
            l = filter(lambda x: len(x) > 0, rel.split('/'))
            
            # So now, if either the length l is 1 (first-level) or the
            # relative path rel has a parent matching one of the nodes
            # of the url, the path will be allowed to propagate.
            
            if has_request_as_parent(d, rel, url)  or len(l) == 1:
                node += mknode(fullname, url) 
                
    if p:
        node += '</div>'
    else:
        node += ''
    return node

@register.tag(name="emma_menu")
def build_menu(parser, token):
    return MenuNode()
    
    
class MenuNode(template.Node):
    
    def render(self, context):
        
        url = context['request'].META['PATH_INFO'].replace('/folder/','')
        path = settings.APP_CONTENT_ROOT + '/'
    
        return mknode(path, url)
    