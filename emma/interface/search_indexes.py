from haystack import indexes
from haystack.sites import site
from models import Keyword, Metadata

class MetadataIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    image_LNID = indexes.CharField(model_attr='image_LNID')
    copyright = indexes.BooleanField(model_attr='copyright', null=True)
    subject = indexes.CharField(model_attr='subject')

site.register(Metadata, MetadataIndex)
        