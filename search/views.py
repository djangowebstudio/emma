from haystack.views import SearchView
from haystack.query import SearchQuerySet
from haystack.forms import SearchForm
from django.contrib.auth.decorators import login_required
from emma.interface.models import Metadata, Keyword
from django.http import Http404

class EmmaSearchView(SearchView):
    def __name__(self):
        return "EmmaSearchView"
    def extra_context(self):
        sqs = super(EmmaSearchView, self).extra_context()
        sqs['sqs'] = SearchQuerySet().auto_query(self.query).spelling_suggestion()
        try:
            sqs['mlt'] = Metadata.objects.filter(keywords__contains=self.query)[0]
        except:
            sqs['mlt'] = ''
        
        return sqs


@login_required
def search(req):
    try:
        return EmmaSearchView(template='search/search.html', form_class=SearchForm)(req)
    except Exception, inst:
        raise Http404
