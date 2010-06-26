from haystack.views import SearchView
from haystack.query import SearchQuerySet
from django.contrib.auth.decorators import login_required


class EmmaSearchView(SearchView):
    def __init__(self):
        self.req = req
    def extra_context(self):
        c = SearchQuerySet().filter(content=self.req).count()
        return c

@login_required
def search(req):
    return SearchView(template='search/search.html')(req)
