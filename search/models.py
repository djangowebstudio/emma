from django.db import models

class Exclude(models.Model):
    exclude = models.CharField(max_length=50, default='', unique=True)
    
    def __unicode__(self):
        return self.exclude
