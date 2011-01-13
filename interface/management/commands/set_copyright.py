from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from emma.interface.models import *
import os, sys
from optparse import make_option

class Command(BaseCommand):
    help = """
    Set all copyrights to a certain value. Will optionally filter on category. 
    """
    args = "copyright, category, action"
    option_list = BaseCommand.option_list + (
           
            make_option('-r', '--for-real', 
                action='store_true', 
                dest='action',
                default=False, 
                help='Do the action.'),
                
            make_option('-c', '--copyright',
                action='store',
                dest='copyright',
                type='string',
                help='Enter a string.'),
                
                
            make_option('-g', '--group',
                action='store',
                dest='category',
                type='string',
                help='Enter a category (called group here).'),
                
                )
                
                
    def handle(self, *args, **options):
        action = options.get('action', False)
        copyright = options.get('copyright', '')
        category = options.get('category', 'illustration')
        
        print 'acting on category %s' % category
        
        if not copyright:
            sys.stderr.write(self.style.ERROR('Please enter a copyright string.' ) + '\n')
            exit()
            
        if not category:
            sys.stderr.write(self.style.ERROR('Please enter a category (string, illustration or photo).' ) + '\n')
            exit()
        
        m = Metadata.objects.filter(image__image_category=category)    
        
        
        for item in m:
            print 'image: %s | copyright: %s | category: %s' % (item.image_LNID, item.copyright, item.image.image_category)
            if action:
                item.copyright = 'no'
                try:
                    item.save()
                    try:
                        k = Keyword.objects.get(image_LNID=item.image_LNID)
                        k.copyright = 'no'
                        k.save()
                    except Exception, inst:
                        sys.stderr.write(self.style.ERROR(inst ) + '\n')
                except Exception, inst:
                    sys.stderr.write(self.style.ERROR(inst ) + '\n')
            
            