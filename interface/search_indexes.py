from haystack import indexes
from haystack.sites import site
from models import Keyword, Metadata

class MetadataIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    image_LNID = indexes.CharField(model_attr='image_LNID')

site.register(Metadata, MetadataIndex)

class KeywordIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    image_LNID = indexes.CharField(model_attr='image_LNID')
site.register(Keyword, KeywordIndex)
        