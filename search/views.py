from haystack.views import SearchView
from haystack.query import SearchQuerySet
from django.contrib.auth.decorators import login_required

class EmmaSearchView(SearchView):
    def __name__(self):
        return "EmmaSearchView"
    def extra_context(self):
        sqs = super(EmmaSearchView, self).extra_context()
        sqs['sqs'] = SearchQuerySet().auto_query(self.query).spelling_suggestion()
        return sqs


@login_required
def search(req):
    return EmmaSearchView(template='search/search.html')(req)
