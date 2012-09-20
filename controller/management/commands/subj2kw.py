from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import os, sys, subprocess
from django.conf import settings
from emma.interface.models import Metadata, Keyword

import logging
#--------------------------------------------------------------------------------------------------
# Logging
# A directory will be created the first time watch is run.
#--------------------------------------------------------------------------------------------------

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=os.path.join(settings.APP_ROOT, 'subj2kw.log'),
                    filemode='w')





class Command(BaseCommand):
    """
    Writes subject to keywords if keywords is empty.
    
    """
    
    option_list = BaseCommand.option_list + (

             make_option('-r', '--for-real', 
                 action='store_true', 
                 dest='action',
                 default=False, 
                 help='Do the action.'),


             )
    
    
    
    
    
    
    
    
    
    def handle(self, *args, **options):
        action = options.get('action', False)
        
        print """
        Looking for empty keywords fields in Metadata model.
        Empty fields will be reported.
        
        Add the -r flag to save to the Metadata & the Keyword 
        model.
        
        """
        
        m = Metadata.objects.all()
        for i in m:
            if not i.keywords and i.subject:
                print '---> keywords empty for %s but we have %s in subject' % (i.image_LNID, i.subject)
                
                if action:
                    i.keywords = i.subject
                    i.save()
                    print 'saved to Metadata model'
                    # also save to the Keyword model
                    k = Keyword.objects.get(image_LNID=i.image_LNID)
                    k.keywords = i.subject
                    k.save()
                    print 'saved to Keyword model'
                    
                else:
                    print 'add the -r flag to save....'
                    
                
            if not i.keywords and not i.subject:
                logging.warn('%s has neither keywords nor subject' % i.image_LNID)
                
                
        print "done"                
        