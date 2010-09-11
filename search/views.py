from haystack.views import SearchView
from haystack.query import SearchQuerySet
from haystack.forms import SearchForm
from django.contrib.auth.decorators import login_required
from emma.interface.models import Metadata, Keyword
from django.http import Http404
import os, sys
from models import Exclude

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
        
        return sqs


@login_required
def search(req):
    return EmmaSearchView(template='search/search.html', form_class=SearchForm)(req)