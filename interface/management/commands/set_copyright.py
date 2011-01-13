from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from emma.interface.models import *
import os, sys
from optparse import make_option

class Command(BaseCommand):
    help = """
    Set all copyrights to a certain value. Will optionally filter on category and / or directory. 
    """
    args = "copyright [yes|no], category [photo|illustration], directory, action"
    option_list = BaseCommand.option_list + (
           
            make_option('-r', '--for-real', 
                action='store_true', 
                dest='action',
                default=False, 
                help='Do the action.'),
                
            make_option('-c', '--copyright',
                action='store',
                dest='copyright',
                default='yes',
                help='Enter a string.'),
                
                
            make_option('-g', '--group',
                action='store',
                dest='category',
                default='illustration',
                type='string',
                help='Enter a category (called group here).'),
            
            make_option('-d', '--dir',
                action='store',
                dest='directory',
                default='',
                type='string',
                help='Enter a directory.'),
               
                )
                
                
    def handle(self, *args, **options):
        action = options.get('action', False)
        copyright = options.get('copyright', 'yes')       
        category = options.get('category', 'illustration')
        directory = options.get('directory', '')
        
        print 'acting on category %s' % category
        
        if not copyright:
            sys.stderr.write(self.style.ERROR('Please enter a copyright. (-c, --copyright [yes|no])' ) + '\n')
            exit()
        
        copyright = True if copyright == 'yes' else False
        
        if not category:
            sys.stderr.write(self.style.ERROR('Please enter a category ( -g --group ["photo|illustration"]).' ) + '\n')
            exit()
        
        if directory and category:
            m = Metadata.objects.filter(image__image_category=category, image__image_real_path__icontains=directory) 
        elif directory and not category:
            m = Metadata.objects.filter(image__image_real_path__icontains=directory)
        else:
            m = Metadata.objects.filter(image__image_category=category)         
        
        for item in m:
            print 'image: %s | copyright: %s | category: %s' % (item.image_LNID, item.copyright, item.image.image_category)
            if action:
                item.copyright = copyright
                try:
                    item.save()
                    print 'saved %s' % copyright
                    try:
                        k = Keyword.objects.get(image_LNID=item.image_LNID)
                        k.copyright = copyright
                        k.save()
                        print 'saved %s ' % copyright
                    except Exception, inst:
                        sys.stderr.write(self.style.ERROR(inst ) + '\n')
                except Exception, inst:
                    sys.stderr.write(self.style.ERROR(inst ) + '\n')
            
            