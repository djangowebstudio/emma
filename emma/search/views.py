from haystack.views import SearchView
from haystack.query import SearchQuerySet
from haystack.forms import SearchForm
from django.contrib.auth.decorators import login_required
from emma.interface.models import Metadata, Keyword, User
from django.http import Http404
import os, sys
from models import Exclude
from django.core.paginator import Paginator, InvalidPage
import settings



replaces = ["(",")", "AND"]

class EmmaSearchView(SearchView):
    def __name__(self):
        return "EmmaSearchView"
    def extra_context(self):
        sqs = super(EmmaSearchView, self).extra_context()
        sqs['sqs'] = SearchQuerySet().auto_query(self.query).spelling_suggestion()
        suggestion = sqs['sqs']
        split, excludes = [], []
        try:
            for r in replaces: 
                suggestion = suggestion.replace(r, "")
            split = suggestion.replace("  ", " ").split(" ")
            for item in Exclude.objects.all(): excludes.append(item.exclude)
            for s in split: 
                if s in excludes: split.remove(s)
            sqs['partition'] = split
        except:    
            pass
        
        if self.query:
            try:
                sqs['mlt'] = Metadata.objects.filter(keywords__contains=self.query)[0]
            except:
                sqs['mlt'] = ''
                
        sqs['page_range'] = getattr(settings, 'APP_PAGE_RANGE', range(8,88,8))
        sqs['page_size'] = self.prefs(self.request)['page_size']
        
        return sqs
        
    def build_page(self):
        
        """
        Paginates the results appropriately.

        Overridden to include page_size
        """
        
        
        paginator = Paginator(self.results, self.prefs(self.request)['page_size'])

        try:
            page = paginator.page(self.request.GET.get('page', 1))
        except InvalidPage:
            raise Http404

        return (paginator, page)
        
        
    def prefs(self, request):
        """Get user prefs (pagesize,  order)"""
        prefs = {}
        try:
            u = User.objects.get(user=request.user.id)
            prefs['sortpref'] = int(u.order)
            prefs['page_size'] = int(u.pagesize)
        except Exception, inst: 
            prefs['sortpref'] = 1
            prefs['page_size'] = 8
        return prefs
    
    


@login_required
def search(req):
    return EmmaSearchView(template='search/search.html', form_class=SearchForm)(req)