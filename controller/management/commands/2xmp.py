from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from progressbar import ProgressBar, SimpleProgress
import os, sys, subprocess
from django.conf import settings
from emma.core.metadata import Metadata

class Command(BaseCommand):
    """
    Migrates keywords from the IPTC framework to the
    XMP framework.
    
    """
    
    path = settings.APP_CONTENT_ROOT
    
    option_list = BaseCommand.option_list + (
           
            make_option('-r', '--for-real', 
                action='store_true', 
                dest='action',
                default=False, 
                help='Do the action.'),
            
   
            )
    
    def handle(self, *args, **options):
        
        action = options.get('action', False)
        
        if not action:
            print 'this is a dry run, only the subprocess command will be printed.'
        
        errors = []
        for root, dirs, files in os.walk(self.path):
            for f in files:
                p = os.path.join(root, f)
                # get original keywords
                keywords = Metadata().exif("iptc:keywords", p)
                
                # some older files contain linebreaks in their 
                # keywords, we will remove these
                
                keywords = keywords.replace('\n', ', ')
                
                # use subprocess directly for the write call
                c = '-xmp:keywords=%s' % keywords
                cmd = ['exiftool', '-P', '-overwrite_original_in_place', c, p]
                if action:
                    r = subprocess.call(cmd)
                    # the call should return 0, if not write to errors list.
                    if r: 
                        errors.append(p)
                        print 'error for file %s' % p
                    else:
                        print 'successfully migrated keywords for %s' % p
                else:
                    print cmd
                    
        if errors:
            print errors
            return 'process complete, but with errors'
        else:
            return 'complete'

        
        
        