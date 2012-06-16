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
    
    Also removes iptc keywords. When -keywords is requested,
    by exiftool, only -xmp:keywords will be returned.
    
    """
    
    exiftool_args_path = os.path.join(settings.APP_ROOT, 
                            'project/script/exiftool/args/iptckw2xmpkw.arg')
    
    option_list = BaseCommand.option_list + (
           
            make_option('-r', '--for-real', 
                action='store_true', 
                dest='action',
                default=False, 
                help='Do the action.'),
                
            make_option('-p', '--path', 
                dest='path',
                help='Enter path'),
            
   
            )
    
    def handle(self, *args, **options):
        
        action = options.get('action', False)
        path = options.get('path', settings.APP_CONTENT_ROOT)
        
        if not action:
            print 'this is a dry run, only the subprocess command will be printed.'
            
        
        errors = []
        for root, dirs, files in os.walk(path):
            for f in files:
                p = os.path.join(root, f)
                
                arg = self.exiftool_args_path
                # enter keyowrds migration script, and remove iptc keywords
                cmd = ['exiftool', '-overwrite_original_in_place', '-@', arg, p]
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

        
        
        