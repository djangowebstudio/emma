#!/usr/bin/env python
# encoding: utf-8
#**************************************************************************************************
# Geert Dekkers Web Studio 2008, 2009, Django Web Studio 2010, info@djangowebstudio.nl
# 
# watch.py for EMMA
#**************************************************************************************************
"""
EMMA (Easy Media Management Application)
Administer your image sharing webapp through a fileserver share on your macosx 10.5 client or server.

Watches over the content - updates, inserts, deletes, and more. Sees to it that the database
accurately reflects the content directory tree at settings.APP_CONTENT_ROOT.
Watch works in concurrence with fix and generatekeywords.

1.  Fixes spaces in filenames and directories
2.  Converts PDF, EPS, AI, PNG, PSD to JPG
3.  Resizes JPG's for use as thumbs and minithumbs
4.  Converts avi, mpg, mov, wmv and more to flv
5.  From paired .fla / .swf files, moves .swf to gallery.

--------------
DEPLOYING EMMA
--------------

1.  EMMA is a set of django apps. It needs to be deployed to a project to work (at all!). So the first
    step is to start a project and add stub files for watch, generatekeywords, fix and converter. You'll
    also need to add a urls.py. (sorry, no installer yet!)

2.  In settings, change APP_CONTENT_ROOT to reflect the living quarters of your content. Or
    move your content to where APP_CONTENT_ROOT points to. Configure your template & static paths.
    Override templates & statics locally if you wish.

3.  From within the django project root, run script/load -f, and leave it running. (you will need admin 
    permissions for this).
    Refer to fix's log at /Library/Logs/[project name]/fix.log to check the progress. Wait for files to 
    be processed before going on to the next step.
    Fix will fix filenames, renaming as needed to comply with workflow policy. And does heaps
    of other useful stuff. Please refer to the programmer's notes in Fix's header.
    Set interval at in app settings. IMPORTANT NOTE: Before running, the fixture will set
    images_imagecount.count to a five digit  number, i.e. 10000.

4.  Run "script/load -l". Your site will now be filled. This could take quite long, depending on your content.
    Make sure script/load is running at all times. While running, watch.py will watch over your content
    as described above. It is set to rescan settings.APP_ROOT_CONTENT at an interval as set in settings.py.
    This may be freely altered, but restart using script/load -r to apply changes.

"""

from __future__ import nested_scopes

import os, sys, time
from time import strftime
from django.core.management import setup_environ
import settings
setup_environ(settings)
from emma.interface.models import *
import metadata
import converter
import datetime
import utes
import logging
#--------------------------------------------------------------------------------------------------
# Logging
# A directory will be created the first time watch is run.
#--------------------------------------------------------------------------------------------------

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=os.path.join(settings.APP_LOGS_ROOT, 'watch.log'),
                    filemode='w')
#--------------------------------------------------------------------------------------------------
# Configuration
#--------------------------------------------------------------------------------------------------

gallery_images = settings.GALLERY_ROOT + '/images/'
gallery_thumbs = settings.GALLERY_ROOT + '/thumbs/'
gallery_minithumbs = settings.GALLERY_ROOT + '/miniThumbs/'
gallery_albums = settings.GALLERY_ROOT + '/albums/'


# Get a value for the tmp variable    
tmp = getattr(settings, 'APP_CONTENT_TMP', False)

#--------------------------------------------------------------------------------------------------

class Watch:
    
    def convertImages(self,item,file_type='', mime_type='', rotate=''):
            """ Calls the appropriate functions in Converter
            This function does no actual conversion itself."""
            
            
            c = converter.Convert()
            m = metadata.Metadata()
            
            # assign the full path to a var
            current_path = item
            
            # get the filename
            fname = os.path.split(item)[1]
            
            # sort files by extension and initiate the appropriate converter function
            
            # Set default values for the return variables
            image_id = ''
            image_path = ''
            image_name = ''
            image_category = ''
            image_pages = 0
            
            # Go through our files, looking at their extensions to route them to the appropriate converters
            # At the moment, fix.py is handling files without extensions by extracting file format
            # information from the metadata and then appending the appropriate extension.
            
            # Todo: sort extensions using os.path.split. This will be less costly and improve code readability.
            # Todo: Look into magic file definition -- API? Speed issues?
            
            # NOTE: We're going to extract the file type using exiftool for the moment. This is quite costly, but
            # as we're getting a whole heap of metadata anyway, this one bit of extra data won't slow us down much.
            
            
            if file_type:
                if mime_type and not mime_type == 'image/vnd.fpx':# Exclude Windows Thumbs.db if it happens to appear under another name
                    print 'file: %s, file_type: %s, mime_type: %s' % (current_path, file_type, mime_type)
                    logging.info('Converting fname: %s, file_type: %s, mime_type: %s' % (fname, file_type, mime_type))
                    mime_type = mime_type.lower() # Just to make sure...
                    
                    if mime_type.find('video') == 0:
                        print 'foutput: %s' % gallery_images + fname.replace(os.path.splitext(fname)[1], '.flv')
                        image_path = c.ffmpeg(current_path, gallery_images + fname.replace(os.path.splitext(fname)[1], '.flv'),'large')
                        c.ffmpeg(current_path, gallery_thumbs, 'small', 148, 'jpg')
                        image_category = 'video'
                    
                    elif mime_type.find('audio') == 0:
                        image_path = c.ffmpeg(current_path, gallery_images + fname.replace(os.path.splitext(fname)[1], '.flv'),'large')
                        c.pcopy(gallery_thumbs + 'sound-thumb.jpg', gallery_thumbs + fname.replace(os.path.splitext(fname)[1]) + '.jpg')
                        image_category = 'audio'
                    
                    elif mime_type.find('image') == 0:
                        image_path = c.resize (current_path, gallery_images + fname.replace(os.path.splitext(fname)[1], '.jpg'), settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH)
                        image_category = 'photo'
                    
                    elif mime_type == 'application/pdf':
                        image_path, image_pages = c.convertPDF (current_path, gallery_images)
                        image_category = 'illustration'
                        
                    elif mime_type == 'application/vnd.adobe.illustrator':
                        image_path, image_pages = c.convertPDF (current_path, gallery_images)
                        image_category = 'illustration'
                    
                    elif mime_type == 'application/vnd.adobe.photoshop':
                        image_path = c.resize (current_path, gallery_images + fname.replace(os.path.splitext(fname)[1], '.jpg'), settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH)
                        image_category = 'illustration'
                    
                    
                    elif mime_type == 'application/postscript':
                        newpath = gallery_images + fname.replace(os.path.splitext(fname)[1], '.jpg') # convertToBitmap needs to know the extension
                        try:
                            image_path =  c.convertToBitmap (current_path, newpath )
                            c.resize(newpath, newpath, settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH) # resize the image immediately afterwards
                        except Exception, inst:
                            logging.warning("%(fname)s %(inst)s" % {'fname': fname, 'inst':inst})
                        image_category = 'illustration'
                    
                    elif mime_type == 'application/photoshop':
                        image_path = c.resize (current_path, gallery_images + fname.replace(os.path.splitext(fname)[1], '.jpg'), settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH)
                        image_category = 'illustration'
                    
                    elif mime_type == 'application/msword':
                        # We might consider storing the pdf instead of the word doc.
                        try:
                            document_path = c.convertDocument(current_path, tmp)
                            if document_path:
                                image_path, image_pages = c.convertPDF(document_path, gallery_images)
                                image_category = 'document'
                            else:
                                return None
                        except Exception, inst:
                            logging.warning('Tried converting %s but gave up with error %s' % (fname,inst))
                    
                    else:
                        logging.warning('This mime type %s is not supported right now, skipping %s' % (mime_type, item))
                        return None
                        
                
                else:
                    
                    file_type = file_type.lower()
                    print 'No mime type; file: %s, file_type: %s' % (current_path, file_type)
                    logging.info('Converting items using file_type %s' % file_type)
                    
                    if file_type == "eps":
                        newpath = gallery_images + fname.replace('.eps', '.jpg') # convertToBitmap needs to know the extension
                        try:
                            image_path =  c.convertToBitmap (current_path, newpath )
                            c.resize(newpath, newpath, settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH) # resize the image immediately afterwards
                        except Exception, inst:
                            logging.warning("%(fname)s %(inst)s" % { 'fname': fname, 'inst':inst})
                        image_category = 'illustration'
                    
                    elif file_type == "pdf":
                        image_path, image_pages = c.convertPDF (current_path, gallery_images)
                        image_category = 'illustration'
                    
                    elif file_type == "jpeg":
                        image_path = c.resize (current_path, gallery_images + fname, settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH)
                        image_category = 'photo'
            
                    
                    elif file_type == "gif":
                        image_path = c.resize (current_path, gallery_images + fname.replace('.gif', '.jpg'), settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH)
                        image_category = 'illustration'
            
                    
                    elif file_type == "psd":
                        image_path = c.resize (current_path, gallery_images + fname.replace('.psd', '.jpg'), settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH)
                        image_category = 'illustration'
                    
                    elif file_type == "png":
                        image_path = c.resize (current_path, gallery_images + fname.replace('.png', '.jpg'), settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH)
                        image_category = 'photo'
                    
                    elif file_type == "tiff":
                        image_path = c.resize (current_path, gallery_images + fname.replace('.tif', '.jpg'), settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH)
                        image_category = 'photo'
                    
                    elif file_type == "au":
                        image_path = c.ffmpeg(current_path, gallery_images + fname.replace(os.path.splitext(fname)[1], '.flv'),'large')
                        c.ffmpeg(current_path, gallery_thumbs + fname.replace(file_type, '.flv'),'cropped')
                        image_category = 'audio'
                    
                    elif file_type == "mp3":
                        image_path = c.ffmpeg(current_path, gallery_images + fname.replace(os.path.splitext(fname)[1], '.flv'),'large')
                        c.ffmpeg(current_path, gallery_thumbs + fname.replace(file_type, '.flv'),'cropped')
                        image_category = 'audio'
                    
                    elif file_type == "aiff":
                        image_path = c.ffmpeg(current_path, gallery_images + fname.replace(os.path.splitext(fname)[1], '.flv'),'large')
                        c.ffmpeg(current_path, gallery_thumbs + fname.replace(file_type, '.flv'),'cropped')
                        image_category = 'audio'
                    
                    elif file_type == "m4v":
                        image_path = c.ffmpeg(current_path, gallery_images + fname.replace(os.path.splitext(fname)[1], '.flv'),'large')
                        c.ffmpeg(current_path, gallery_thumbs + fname.replace(file_type, '.flv'),'small')
                        image_category = 'video'
                    
                    elif file_type == "mp4":
                        image_path = c.ffmpeg(current_path, gallery_images + fname.replace(os.path.splitext(fname)[1], '.flv'),'large')
                        c.ffmpeg(current_path, gallery_thumbs + fname.replace(file_type, '.flv'),'small')
                        image_category = 'video'
                    
                    elif file_type == "mov":
                        image_path = c.ffmpeg(current_path, gallery_images + fname.replace(os.path.splitext(fname)[1], '.flv'),'large')
                        c.ffmpeg(current_path, gallery_thumbs + fname.replace(file_type, '.flv'),'small')
                        image_category = 'video'
                    
                    elif file_type == "mpg":
                        image_path = c.ffmpeg(current_path, gallery_images + fname.replace(os.path.splitext(fname)[1], '.flv'),'large')
                        c.ffmpeg(current_path, gallery_thumbs + fname.replace(file_type, '.flv'),'small')
                        image_category = 'video'
                    
                    elif file_type == "avi":
                        image_path = c.ffmpeg(current_path, gallery_images + fname.replace(os.path.splitext(fname)[1], '.flv'),'large')
                        c.ffmpeg(current_path, gallery_thumbs + fname.replace(file_type, '.flv'),'small')
                        image_category = 'video'
                    
                    elif file_type == "wmv":
                        image_path = c.ffmpeg(current_path, gallery_images + fname.replace(os.path.splitext(fname)[1], '.flv'),'large')
                        c.ffmpeg(current_path, gallery_thumbs + fname.replace(file_type, '.flv'),'small')
                        image_category = 'video'
                    
                    elif file_type == "flv":
                        image_path = c.ffmpeg(current_path, gallery_images + fname, 'large')
                        c.ffmpeg(current_path, gallery_thumbs + fname,'small')
                        image_category = 'video'
                    
                    elif file_type == "fla":
                        image_path = gallery_images + fname
                        #c.pcopy(current_path, gallery_thumbs + fname.replace('.fla', '.swf')) Moving and copying is now being done in fix.
                        image_category = 'flash'
                    
                    elif file_type == "swf":
                        image_path = c.pcopy(current_path, gallery_images + fname)
                        c.pcopy(current_path, gallery_thumbs + fname) # The only swf files you should be seeing here are standalone files (as opposed to paired fla/swf)
                        image_category = 'flash'
                
                    
                    # Looking for one of txt, doc, htm, xml
                    
                    else:
                        logging.warning( "%(file)s doesn't seem to belong to our favourite formats. We'll try to treat it as a text doc, otherwise leave it." % {'file':current_path})
                        
                        try:
                            document_path = c.convertDocument(current_path, tmp)
                            if document_path:
                                image_path, image_pages = c.convertPDF(document_path, gallery_images)
                                image_category = 'document'
                            else:
                                return None
                        except Exception, inst:
                            logging.warning('Tried converting %s but gave up with error %s' % (fname,inst))
                
        
            
            elif fname[(len(fname)-4):(len(fname)-3)] == ".":
                
                
                print 'No file type, no mime type; file: %s' % (current_path)
                image_id = fname[0:(len(fname)-4)]
                
                if fname[(len(fname)-4):len(fname)] == ".eps":
                    newpath = gallery_images + fname.replace('.eps', '.jpg') # convertToBitmap needs to know the extension
                    try:
                        image_path =  c.convertToBitmap (current_path, newpath )
                        c.resize(newpath, newpath, settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH) # resize the image immediately afterwards
                    except Exception, inst:
                        logging.warning("%(fname)s %(inst)s" % { 'fname': fname, 'inst':inst})
                    image_category = 'illustration'
                
                elif fname[(len(fname)-4):len(fname)] == ".pdf":
                    image_path, image_pages = c.convertPDF (current_path, gallery_images)
                    image_category = 'illustration'
                
                elif fname[(len(fname)-4):len(fname)] == ".jpg":
                    image_path = c.resize (current_path, gallery_images + fname, settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH)
                    image_category = 'photo'
            
                
                elif fname[(len(fname)-4):len(fname)] == ".gif":
                    image_path = c.resize (current_path, gallery_images + fname.replace('.gif', '.jpg'), settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH)
                    image_category = 'illustration'
            
                
                elif fname[(len(fname)-4):len(fname)] == ".psd":
                    image_path = c.resize (current_path, gallery_images + fname.replace('.psd', '.jpg'), settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH)
                    image_category = 'illustration'
                
                elif fname[(len(fname)-4):len(fname)] == ".png":
                    image_path = c.resize (current_path, gallery_images + fname.replace('.png', '.jpg'), settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH)
                    image_category = 'photo'
                
                elif fname[(len(fname)-4):len(fname)] == ".tif":
                    image_path = c.resize (current_path, gallery_images + fname.replace('.tif', '.jpg'), settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH)
                    image_category = 'photo'
                
                elif fname[(len(fname)-4):len(fname)] == ".mp4":
                    image_path = c.ffmpeg(current_path, gallery_images + fname.replace(fname[(len(fname)-4):len(fname)], '.flv'),'large')
                    c.ffmpeg(current_path, gallery_thumbs + fname.replace(fname[(len(fname)-4):len(fname)], '.flv'),'small')
                    image_category = 'video'
                
                elif fname[(len(fname)-4):len(fname)] == ".m4v":
                    image_path = c.ffmpeg(current_path, gallery_images + fname.replace(fname[(len(fname)-4):len(fname)], '.flv'),'large')
                    c.ffmpeg(current_path, gallery_thumbs + fname.replace(fname[(len(fname)-4):len(fname)], '.flv'),'small')
                    image_category = 'video'
                
                elif fname[(len(fname)-4):len(fname)] == ".mov":
                    image_path = c.ffmpeg(current_path, gallery_images + fname.replace(fname[(len(fname)-4):len(fname)], '.flv'),'large')
                    c.ffmpeg(current_path, gallery_thumbs + fname.replace(fname[(len(fname)-4):len(fname)], '.flv'),'small')
                    image_category = 'video'
                
                elif fname[(len(fname)-4):len(fname)] == ".mpg":
                    image_path = c.ffmpeg(current_path, gallery_images + fname.replace(fname[(len(fname)-4):len(fname)], '.flv'),'large')
                    c.ffmpeg(current_path, gallery_thumbs + fname.replace(fname[(len(fname)-4):len(fname)], '.flv'),'small')
                    image_category = 'video'
                
                elif fname[(len(fname)-4):len(fname)] == ".avi":
                    image_path = c.ffmpeg(current_path, gallery_images + fname.replace(fname[(len(fname)-4):len(fname)], '.flv'),'large')
                    c.ffmpeg(current_path, gallery_thumbs + fname.replace(fname[(len(fname)-4):len(fname)], '.flv'),'small')
                    image_category = 'video'
                
                elif fname[(len(fname)-4):len(fname)] == ".wmv":
                    image_path = c.ffmpeg(current_path, gallery_images + fname.replace(fname[(len(fname)-4):len(fname)], '.flv'),'large')
                    c.ffmpeg(current_path, gallery_thumbs + fname.replace(fname[(len(fname)-4):len(fname)], '.flv'),'small')
                    image_category = 'video'
                
                elif fname[(len(fname)-4):len(fname)] == ".flv":
                    image_path = c.ffmpeg(current_path, gallery_images + fname, 'large')
                    c.ffmpeg(current_path, gallery_thumbs + fname,'small')
                    image_category = 'video'
                
                elif fname[(len(fname)-4):len(fname)] == ".fla":
                    image_path = gallery_images + fname
                    #c.pcopy(current_path, gallery_thumbs + fname.replace('.fla', '.swf')) Moving and copying is now being done in fix.
                    image_category = 'flash'
                
                elif fname[(len(fname)-4):len(fname)] == ".swf":
                    image_path = c.pcopy(current_path, gallery_images + fname)
                    c.pcopy(current_path, gallery_thumbs + fname) # The only swf files you should be seeing here are standalone files (as opposed to paired fla/swf)
                    image_category = 'flash'
                
                # Looking for one of txt, doc, htm, xml
                
                else:
                    logging.warning( "%(file)s doesn't seem to belong to our favourite formats. We'll try to treat it as a text doc, otherwise leave it." % {'file':current_path})
                    try:
                        document_path = c.convertDocument(current_path, tmp)
                        if document_path:
                            image_path, image_pages = c.convertPDF(document_path, gallery_images)
                            image_category = 'document'
                        else:
                            return None
                    except Exception, inst:
                        logging.warning('Tried converting %s but gave up with error %s' % (fname,inst))
                
            
            elif fname[(len(fname)-3):(len(fname)-2)] == ".":
                
                if  fname[(len(fname)-3):len(fname)] == ".ai":
                    try:
                        image_path =  c.convertPDF (current_path, gallery_images)[0] # Just get the first item of the tuple. Note that we're using convertPDF, which retrns a tuple.
                        image_category = 'illustration'
                    except:
                        pass
                else:
                    logging.warning( "%(file)s doesn't seem to belong to our favourite formats. We'll try to treat it as a text doc, otherwise leave it" % {'file':current_path})
                    image_path, image_pages = c.convertPDF(c.convertDocument(current_path), gallery_images)
                    image_category = 'document'
        
            
            elif fname[(len(fname)-5):(len(fname)-4)] == ".":
                
                if fname[(len(fname)-5):len(fname)] == ".jpeg":
                    image_path = c.resize (current_path, gallery_images + fname.replace('.jpeg','.jpg'), settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH)
                    image_category = 'photo'
                
                elif fname[(len(fname)-5):len(fname)] == ".tiff":
                    image_path = c.resize (current_path, gallery_images + fname.replace('.tiff','.jpg'), settings.GALLERY_IMAGE_WIDTH, settings.GALLERY_IMAGE_WIDTH)
                    image_category = 'photo'
                else:
                    logging.warning( "%(file)s doesn't seem to belong to our favourite formats. We'll try to treat it as a text doc, otherwise leave it" % {'file':current_path})
                    try:
                        document_path = c.convertDocument(current_path, tmp)
                        if document_path:
                            image_path, image_pages = c.convertPDF(document_path, gallery_images)
                            image_category = 'document'
                        else:
                            return None
                    except Exception, inst:
                        logging.warning('Tried converting %s but gave up with error %s' % (fname,inst))

        

            
            else:
                print 'Everything else failed for %s' % current_path
                image_id = fname
                image_path = gallery_images + fname + ".jpg"
                image_category = 'photo'
                logging.warning( "%(file)s doesn't seem to belong to our favourite formats. We're not doing anything with it at the moment." % {'file':current_path})
            
            try:
                image_name = os.path.basename(image_path)
            except Exception, inst:
                logging.warning( "Error while generating image_name variable %(inst)s" % {'inst':inst})
                image_name = fname
            
            #create interface images from the resultant image ------------------------------------
            if image_name[len(image_name)-4:len(image_name)] == '.jpg':
                try:
                    c.resize(image_path, gallery_thumbs + image_name, settings.GALLERY_THUMBS_WIDTH, settings.GALLERY_THUMBS_WIDTH )
                except:
                    logging.warning( " tried building thumbs from %(image)s , but it didn't work out." % {'image': current_path})
                    
                    # Copy and resize the image to an absolute square for the album cover and miniThumbs
                try:
                    source = os.path.join(settings.GALLERY_ROOT,'images',image_name)
                    target = os.path.join(settings.GALLERY_ROOT,'albums',image_name)
                    c.resize_with_sips(source, target, settings.GALLERY_THUMBS_WIDTH, settings.GALLERY_THUMBS_WIDTH)
                    c.resize(target, gallery_minithumbs + image_name, settings.GALLERY_MINITHUMBS_WIDTH, settings.GALLERY_MINITHUMBS_WIDTH )
                except Exception, inst:
                    return logging.error('An error occurred processing the album image %s' % inst)
        
            
            return image_id, image_path, image_name, fname, image_category, image_pages

    
    def extractImage_LNID(self,filename):
        """Get what appears to be the name of the file minus extension.
        We use this as image identifier all through the application.
        Accommodates for dotted filenames (i.e. Marketing codes used as filenames)"""
        
        f = os.path.split(filename)[1]
        return f.replace('.' + f.split('.').pop(),'')


    
    def renderItem(self,filename):
            d = metadata.Metadata()
            description = d.exif('b -description', filename).split(':')[0].replace("\n"," ").lower()
            for i in wordlist:
                description = description.replace(i,'')
            return description
    
    wordlist = ['fotobureau', 'let op'] # This list is to moved to some sensible location when it gets too big.
    def renderKeywordsFromDescription(description):
        results = description.split(':')[0].replace("\n"," ").lower()
        for i in wordlist:
            results = results.replace(i,'')
        return results
    
    def update_obj(obj, image_LNID, **kwargs):
        """Shorthand for repetitive object updates"""
        try:
            o = obj.objects.get(image_LNID=image_LNID)
            for key in kwargs:
                o.key = kwargs[key]
            o.save()
            logging.info( "Saved %s" % image_LNID)
        except Exception, inst:
            logging.error( "Error saving %s %s " % (obj, image_LNID))

    
    def get_stats(obj):
        if sys.platform == 'darwin':
            return datetime.datetime(obj.st_mtime), datetime.datetime(obj.st_birthtime)
        else:
            return datetime.datetime(obj.st_mtime), datetime.datetime(obj.st_ctime)
            
    
    
    def watch_directories (self, paths, func, delay=1.0):
        
        # Create gallery folders if they don't already exist
        
        makeDirs = utes.Utes()
        makeDirs._mkdir(gallery_images)
        makeDirs._mkdir(gallery_thumbs)
        makeDirs._mkdir(gallery_minithumbs)
        makeDirs._mkdir(gallery_albums)
        if tmp: makeDirs._mkdir(tmp)
        
        # So, once we've done all that, start watching...
        
        """(paths:[str], func:callable, delay:float)
        Continuously monitors the paths and their subdirectories
        for changes.  If any files or directories are modified,
        the callable 'func' is called with a list of the modified paths of both
        files and directories.  'func' can return a Boolean value
        for rescanning; if it returns True, the directory tree will be
        rescanned without calling func() for any found changes.
        (This is so func() can write changes into the tree and prevent itself
        from being immediately called again.)
        """
        
        # Basic principle: all_files is a dictionary mapping paths to
        # modification times.  We repeatedly crawl through the directory
        # tree rooted at 'path', doing a stat() on each file and comparing
        # the modification time.
        
        all_files = {}
        def f (self, dirname, files):
            # Traversal function for directories
            for filename in files:
                if not filename == '.DS_Store' or not filename == 'Thumbs.db':
                    path = os.path.join(dirname, filename)
                    
                    try:
                        t = os.stat(path)

                    
                    except os.error:
                    # If a file has been deleted between os.path.walk()
                    # scanning the directory and now, we'll get an
                    # os.error here.  Just ignore it -- we'll report
                    # the deletion on the next pass through the main loop.
                        continue
            
                    
                    mtime = remaining_files.get(path)
                    if mtime is not None:
                        # If we are on darwin, we must use st_birthtime to get
                        # the true creation date of the file.
                        
                        # Record this file as having been seen
                        del remaining_files[path]
                        # File's mtime has been changed since we last looked at it.
                        if t.st_mtime > mtime:
                            appendix = path, self.get_stats(t)
                            changed_list.append(appendix)
                    else:
                        # No recorded modification time, so it must be
                        # a brand new file.
                        #today = datetime.datetime.now()
                        appendix = path, datetime.datetime.fromtimestamp(t.st_mtime), datetime.datetime.fromtimestamp(t.st_birthtime)
                        changed_list.append(appendix)
                    # Record current mtime of file.
                    all_files[path] = t.st_mtime
        
        # Main loop
        rescan = False
        while True:
            changed_list = []
            remaining_files = all_files.copy()
            all_files = {}
            
            for path in paths:
                os.path.walk(path, f, None)
            removed_list = remaining_files.keys()
            if rescan:
                rescan = False
            elif changed_list or removed_list:
                rescan = func(changed_list, removed_list)
            
            time.sleep(delay)
    
    
    def __init__(self):
        def f (changed_files, removed_files):
            c = converter.Convert()
            m = metadata.Metadata()
            u = utes.Utes()
            for item, item_mtime, item_ctime in changed_files:
                # Only files WITH extensions!
                if item[(len(item)-5):(len(item)-4)] == "." or item[(len(item)-4):(len(item)-3)] == "." or item[(len(item)-3):(len(item)-2)] == ".": 
                
            
                    
                    createdate = item_ctime
                    modifydate = item_mtime
            
                    
                    # Query the database first, and THEN call convertImages
                    # Do a query on image_LNID, image_real_path and date_modified;
                    # if all three are OK you wouldn't want to call convertImages at all.
                    #
                    # Note that you can only call convertImages if date_modified has changed for
                    # the image corresponding to a particular image_LNID. A change in image_LNID or
                    # image_real_path alone will NOT get you in this loop at all!
                    
                    # Init vars to hold metadata info
                    
                    description = ''
                    keywords = ''
                    subject = ''
                    creator = ''
                    creator_tool = ''
                    caption = ''
                    caption_writer = ''
                    instructions = ''
                    credit = ''
                    source = ''
                    location = ''
                    city = ''
                    provincestate = ''
                    country = ''
                    headline = ''
                    datetimeoriginal = item_ctime
                    softdate = ''
                    copyright = ''
                    profile = ''
                    title = ''
                    author = ''
                    album = ''
                    orientation = 0
                    group_status = ''
                    file_type = ''
                    mime_type= ''
                    managedfromfilepath = ''
                    documentname = ''
                    
                    # other vars
                    mdObj_album = ''
                    m_album = ''
            
                    
                    image_LNID = self.extractImage_LNID(item)                               # Extract the image_LNID from the filename
                    
                    image_real_path = item.replace(settings.APP_CONTENT_ROOT + "/",'')      # Get the image path minus the path-to-content, no leading slash
                    if image_LNID != '':
                        
                        # We want to get an exact match on image_LNID, image path, and date modified. If any one of the three properties has
                        # changed, we need to update. However, the trigger for watch is always date modified. So if that doesn't change, nothing is changed.
                
                        # Excluding things like Thumbs.db. See the appropriate settings entry.
                        if 'APP_WATCH_EXCLUDES' in dir(settings) and settings.APP_WATCH_EXCLUDES:
                            if True in u.excludes(os.path.basename(item), settings.APP_WATCH_EXCLUDES):
                                logging.info('%s is in the excludes list, skipping...' % item)
                                continue

                        try:
                            imageObj = Image.objects.get(image_LNID__exact=image_LNID, image_real_path__exact=image_real_path, date_modified=modifydate)
                        
                        except Image.DoesNotExist: # Because one of the three above tests failed, we're going to process the image again
                            
                            # Do the conversions, get the info for the item if the image_LNID - date_modified combination doesn't exist
                            logging.info("Starting sequence -----------------------------------------------------")
                            logging.info("Doing image conversion and picking up info for %(item)s" % {'item':item})
                            
                            try:
                                
                                
                                item_dict = m.exifAll(item)
                                # Write the dict to variables - we'll be using these over and over...
                                description = item_dict['description'].strip()
                                keywords = item_dict['keywords'].lower().strip()
                                copyright = item_dict['copyright']
                                location = item_dict['location'].strip()
                                subject = item_dict['title'].strip()
                                creator = item_dict['creator'].strip()
                                try:
                                    author = item_dict['author'].strip() if item_dict.has_key('author') else creator
                                except Exception, inst:
                                    logging.warning("item_dict['author']" % inst)
                                creator_tool = item_dict['creatortool'].strip()
                                caption_writer = item_dict['captionwriter'].strip()
                                instructions = item_dict['instructions'].strip()
                                credit = item_dict['credit'].strip()
                                profile = item_dict['colorspacedata']
                                source = item_dict['source'].strip()
                                city = item_dict['city'].strip()
                                provincestate = item_dict['province-state'].strip()
                                country = item_dict['country'].strip()
                                datetimeoriginal = item_dict['datetimeoriginal']
                                album = item_dict['album']
                                softdate = ''
                                # Get the group_status from the headline
                                if item_dict['headline']:
                                    hl = item_dict['headline'].strip()
                                    if not hl == '-':
                                        if hl.lower() == 'leader' or hl.lower() == 'follower':
                                            group_status = hl.lower()
                                
                                file_type = item_dict['filetype']
                                mime_type = item_dict['mimetype']
                                managedfromfilepath = item_dict['managedfromfilepath']
                                documentname = subject if subject else item_dict['documentname']
                                orientation = item_dict['orientation']
                                
                                results = self.convertImages(item, file_type, mime_type) # image conversions based on file type
                            except Exception, inst:
                                logging.error("Error executing exifAll with item %s %s, doing convertImages without metadata" % (item, inst))
                                results = self.convertImages(item) # image conversions based on file extension
                            
                                    
                            
                            if results and results[1] != '':  # Test for a value for convertImages, i.e. image_path
                                try:
                                    imageObj = Image.objects.get(image_LNID=image_LNID)  # If we get a match here, we're updating existing file data
                                    imageObj.image_path=results[1]
                                    imageObj.image_name=results[2]
                                    imageObj.image_real_name=results[3]
                                    imageObj.image_real_path=item.replace(settings.APP_CONTENT_ROOT + "/",'')
                                    imageObj.group_status=group_status
                                    imageObj.date_created=createdate
                                    imageObj.date_modified=modifydate
                                    imageObj.date_entered=datetime.datetime.now()
                                    imageObj.image_category=results[4]
                                    imageObj.image_pages=results[5]
                                    try:
                                        imageObj.save()
                                        logging.info( "Image updated successfully %(image)s" % {'image':image_LNID})
                                    except Exception, inst:
                                        logging.error("Image update failed %s" % inst)
                                        continue
                                    try:    # Keyword for uupdate existing data
                                        obj = Keyword.objects.get(image_LNID=image_LNID)
                                        obj.image_name = results[2]
                                        obj.keywords = keywords
                                        obj.cright = copyright
                                        obj.profile = profile
                                        obj.save()
                                        logging.info( "Keyword updated successfully %(image)s" % {'image':image_LNID})
                                    except Keyword.DoesNotExist:
                                        try:
                                            obj = Keyword(image=imageObj,
                                            image_LNID=image_LNID,
                                            keywords=keywords,
                                            image_name=results[2],
                                            cright=copyright,
                                            profile=profile,
                                            image_path=item.replace(settings.APP_CONTENT_ROOT + "/",''))
                                            obj.save()
                                            logging.info( "new Keyword saved from existing data %(image)s" % {'image':image_LNID})
                                        except Exception, inst:
                                            logging.error( "Keyword error saving existing data %(inst)s" % {'inst':inst})
                                    
                                    try: #Metadata update for existing data
                                        mdObj = Metadata.objects.get(image_LNID=image_LNID)
                                        mdObj.description = description
                                        mdObj.keywords = keywords
                                        mdObj.subject = subject
                                        mdObj.creator = creator
                                        mdObj.creator_tool = creator_tool
                                        mdObj.caption_writer = caption_writer
                                        mdObj.instructions = instructions
                                        mdObj.credit = credit
                                        mdObj.source = source
                                        mdObj.location = location
                                        mdObj.city = city
                                        mdObj.provincestate = provincestate
                                        mdObj.country = country
                                        mdObj.headline = group_status
                                        mdObj.datetimeoriginal = datetimeoriginal
                                        mdObj.softdate = softdate
                                        mdObj.copyright = copyright
                                        mdObj.profile = profile
                                        mdObj.title = title
                                        mdObj.author = author
                                        mdObj.album = album
                                        mdObj.orientation = orientation
                                        mdObj.file_type = file_type
                                        mdObj.mime_type = mime_type
                                        mdObj.document = managedfromfilepath
                                        mdObj.documentname = documentname
                                        try:
                                            mdObj.save()
                                            logging.info( "Metadata updated successfully from existing data  %(image)s" % {'image':image_LNID})
                                        except Exception, inst:
                                            logging.error("Metadata update error from existing data %(d)s %(inst)s" % {'d': datetimeoriginal, 'inst': inst})
                                    
                                    except Metadata.DoesNotExist:
                                        try:
                                            mdObj = Metadata(
                                            image=imageObj,
                                            image_LNID=image_LNID,
                                            keyword=obj,
                                            description=description,
                                            keywords=keywords,
                                            subject=subject,
                                            creator=creator,
                                            creator_tool=creator_tool,
                                            caption_writer=caption_writer,
                                            instructions=instructions,
                                            credit=credit,
                                            source=source,
                                            location=location,
                                            city=city,
                                            provincestate=provincestate,
                                            country=country,
                                            headline=group_status,
                                            datetimeoriginal=datetimeoriginal,
                                            softdate=softdate,
                                            copyright=copyright,
                                            profile=profile,
                                            title=title,
                                            author=author,
                                            album=album,
                                            orientation=orientation,
                                            file_type=file_type,
                                            mime_type=mime_type,
                                            document=managedfromfilepath,
                                            documentname=documentname)
                                            mdObj.save()
                                            logging.info( "new Metadata saved from existing data %(image)s" % {'image':image_LNID})
                                        except Exception, inst:
                                            logging.error( "Metadata save error form existing data (1) %(inst)s" % {'inst':inst})
                                
                                    
                                    try: # Album update for existing data (case: content manager adds the file to an Album through the host's file system)
                                        logging.info("Checking for the existence of album data...")
                                        if group_status:
                                            if documentname:
                                                a = Album.objects.filter(image=imageObj) # Check if the image is already in an Album
                                                if not a:
                                                    logging.info("This item %s doesn't seem to be part of an Album" % item)
                                                    new_album = Album.objects.filter(album_name=documentname)
                                                    if new_album:
                                                        albumObj = Album.objects.filter(album_name=documentname)[0]
                                                        logging.info("At least one Album with this documentname already exists, adding the item %s to it..." % item)
                                                        albumObj.image.add(imageObj)
                                                        mdObj.album = albumObj.album_identifier
                                                        mdObj.save()
                                                    else:
                                                        logging.info("Contructing a new Album for %s" % item)
                                                        album_identifier = ''.join(['album-',strftime("%Y%m%d%H%M%S")]) # Build an album_identifier string
                                                        albumObj, created = Album.objects.get_or_create(album_identifier=album_identifier, album_name=documentname)
                                                        albumObj.save()
                                                        albumObj.image.add(imageObj)
                                                        mdObj.album=albumObj.album_identifier
                                                        mdObj.save()
                                                        logging.info("Album %s constructed for item %s" % (albumObj.album_identifier, item)) if created else logging.info("Existing album %s updated with %s" % (albumObj.album_identifier, item))
                                                else: logging.info("This item is already part of an album")
                                            else: logging.warning("No documentname value, checking for album data aborted")
                                        else: logging.warning("No group_status value, checking for album data aborted")
                                        
                                    
                                    except Exception, inst:
                                        logging.error("Error trying to construct an Album from item %s %s" % (image_LNID, inst))
                                                        
                          
                            
                                
                                except Image.DoesNotExist: # No matching image_LNID, so we must be dealing with a completely new file
                                    imageObj = Image(
                                    image_LNID=image_LNID,
                                    image_path=results[1],
                                    image_name=results[2],
                                    image_real_name=results[3],
                                    image_real_path=item.replace(settings.APP_CONTENT_ROOT + "/",''),
                                    group_status=group_status,
                                    date_created=createdate,
                                    date_modified=modifydate,
                                    date_entered=datetime.datetime.now(),
                                    image_category=results[4],
                                    image_pages=results[5] )
                                    try:
                                        imageObj.save()
                                        logging.info( "new Image saved %(image)s" % {'image':image_LNID})
                                    except Exception, inst:
                                        logging.error( "error saving new Image %(inst)s" % {'inst':inst})
                                        continue
                                    
                                    try: # Album update for new image (case: content manager adds the file to an Album through the host's file system)
                                        logging.info("Checking for the existence of album data for new item...")
                                        if group_status:
                                            if documentname:
                                                a = Album.objects.filter(image=imageObj) # Check if the image is already in an Album
                                                if not a:
                                                    logging.info("The item %s isn't part of an album" % item)
                                                    new_album = Album.objects.filter(album_name=documentname) # now get an album with the same documentname
                                                    if new_album:
                                                        albumObj = Album.objects.filter(album_name=documentname)[0]
                                                        logging.info("At least one Album with this documentname already exists, adding the item %s to it..." % item)
                                                        albumObj.image.add(imageObj)
                                                        mdObj_album = albumObj.album_identifier # save this to a var in order to assign to metadata obj later
                                                    else:
                                                        logging.info("Contructing a new Album for %s" % item)
                                                        album_identifier = ''.join(['album-',strftime("%Y%m%d%H%M%S")]) # Build an album_identifier string
                                                        albumObj, created = Album.objects.get_or_create(album_identifier=album_identifier, album_name=documentname)
                                                        albumObj.save()
                                                        albumObj.image.add(imageObj)
                                                        mdObj_album=albumObj.album_identifier # save this to a var in order to assign to metadata obj later
                                                        logging.info("Album %s constructed for item %s" % (albumObj.album_identifier, item)) if created else logging.info("Existing album %s updated with %s" % (albumObj.album_identifier, item))
                                                else: logging.info("Is this NEW item already part of an album?")
                                            else: logging.warning("No documentname value, checking for album data aborted")
                                        else: logging.warning("No group_status value, checking for album data aborted")
                                    
                                    except Exception, inst:
                                        logging.error("Error trying to construct an Album for new item %s %s" % (image_LNID, inst))
                                    
                                    
                                    try:    # Is this file known to Keyword?
                                        obj = Keyword.objects.get(image_LNID=image_LNID)
                                        obj.image_name = results[2]
                                        obj.keywords = keywords
                                        obj.cright = copyright
                                        obj.profile = profile
                                        obj.save()
                                        logging.info( "Keyword saved %(image)s" % {'image':image_LNID})
                                    except Keyword.DoesNotExist:
                                        try:
                                            obj = Keyword(image=imageObj,
                                            image_LNID=image_LNID,
                                            keywords=keywords,
                                            image_name=results[2],
                                            cright=copyright,
                                            profile=profile,
                                            image_path=item.replace(settings.APP_CONTENT_ROOT + "/",''))
                                            obj.save()
                                            logging.info( "new Keyword saved %(image)s" % {'image':image_LNID})
                                        except Exception, inst:
                                            logging.error( "Keyword edit error %(inst)s" % {'inst':inst})
                                    
                                    try: # Is this file known to Metadata?
                                        mdObj = Metadata.objects.get(image_LNID=image_LNID)
                                        mdObj.description = description
                                        mdObj.keywords = keywords
                                        mdObj.subject = subject
                                        mdObj.creator = creator
                                        mdObj.creator_tool = creator_tool
                                        mdObj.caption_writer = caption_writer
                                        mdObj.instructions = instructions
                                        mdObj.credit = credit
                                        mdObj.source = source
                                        mdObj.location = location
                                        mdObj.city = city
                                        mdObj.provincestate = provincestate
                                        mdObj.country = country
                                        mdObj.headline = group_status
                                        mdObj.datetimeoriginal = datetimeoriginal
                                        mdObj.softdate = softdate
                                        mdObj.copyright = copyright
                                        mdObj.profile = profile
                                        mdObj.title = title
                                        mdObj.author = author
                                        mdObj.album = mdObj_album if mdObj_album else album if album else ''
                                        mdObj.orientation = orientation
                                        mdObj.file_type = file_type
                                        mdObj.mime_type = mime_type
                                        mdObj.document = managedfromfilepath
                                        mdObj.documentname = documentname
                                        try:
                                            mdObj.save()
                                            logging.info( "Metadata saved %(image)s" % {'image':image_LNID})
                                        except Exception, inst:
                                            logging.error("Metadata edit error %(d)s %(inst)s" % {'d': datetimeoriginal, 'inst': inst})
                                    except Metadata.DoesNotExist:
                                        m_album = mdObj_album if mdObj_album else album if album else '' # get album info if it exists
                                        try:
                                            mdObj = Metadata(
                                            image=imageObj,
                                            image_LNID=image_LNID,
                                            keyword=obj,
                                            description=description,
                                            keywords=keywords,
                                            subject=subject,
                                            creator=creator,
                                            creator_tool=creator_tool,
                                            caption_writer=caption_writer,
                                            instructions=instructions,
                                            credit=credit,
                                            source=source,
                                            location=location,
                                            city=city,
                                            provincestate=provincestate,
                                            country=country,
                                            headline=group_status,
                                            datetimeoriginal=datetimeoriginal,
                                            softdate=softdate,
                                            copyright=copyright,
                                            profile=profile,
                                            title=title,
                                            author=author,
                                            album=m_album,
                                            orientation=orientation,
                                            file_type=file_type,
                                            mime_type=mime_type,
                                            document=managedfromfilepath,
                                            documentname=documentname)
                                            mdObj.save()
                                            logging.info( "new Metadata saved %(image)s" % {'image':image_LNID})
                                        except Exception, inst:
                                            logging.error( "Metadata edit error (2) %(inst)s" % {'inst':inst})
            
            
            
            
            for item in removed_files:
                if item[(len(item)-4):(len(item)-3)] == "." or item[(len(item)-3):(len(item)-2)] == ".":
                    
                    # Deletes image data, and also the generated files...
                    
                    image_LNID = self.extractImage_LNID(item)
                    
                    try:
                        Image.objects.get(image_LNID__exact=image_LNID).delete()
                        logging.info( "Image deleted %(item)s" % {'item':item})
                        try:
                            os.remove(gallery_images + image_LNID + ".jpg")
                            logging.info( "removed from %(path)s" % { 'path':gallery_images})
                        except Exception, inst:
                            logging.warning( "Error removing %(path)s %(inst)s" % { 'path': gallery_images + image_LNID + ".jpg", 'inst' :inst})
                        try:
                            os.remove(gallery_thumbs + image_LNID + ".jpg")
                            logging.info( "removed from %(path)s" % { 'path':gallery_thumbs})
                        except Exception, inst:
                            logging.warning( "Error removing %(path)s %(inst)s" % { 'path': gallery_thumbs + image_LNID + ".jpg", 'inst' :inst})
                        try:
                            os.remove(gallery_minithumbs + image_LNID + ".jpg")
                            logging.info( "removed from %(path)s" % { 'path':gallery_minithumbs})
                        except Exception, inst:
                            logging.warning( "Error removing %(path)s %(inst)s" % { 'path': gallery_minithumbs + image_LNID + ".jpg", 'inst' :inst})
                    
                    except Exception, inst: logging.warning( "Image delete %(image)s %(inst)s" % {'image':image_LNID, 'inst': inst } )
                    
                    try:
                        Keyword.objects.get(image_LNID__exact=image_LNID).delete()
                        logging.info( "Keyword deleted %(item)s" % {'item':item})
                    except Exception, inst: logging.warning( "Keyword delete %(image)s %(inst)s" % {'image':image_LNID, 'inst': inst } )
                    
                    try:
                        Metadata.objects.get(image_LNID__exact=image_LNID).delete()
                        logging.info( "Metadata deleted %(item)s" % {'item':item})
                    except Exception, inst: logging.warning( "Metadata delete %(image)s %(inst)s" % {'image':image_LNID, 'inst': inst } )
            
            
            # correct permissions
            u = utes.Utes()
            u.chmodRecursive(os.walk(settings.APP_CONTENT_ROOT), 0667)
            logging.info('Permissions %s set.' % settings.APP_CONTENT_ROOT)
            logging.info( 'WATCHING %(path)s ***************************************************************************' % {'path':settings.APP_CONTENT_ROOT})
        
        self.watch_directories([settings.APP_CONTENT_ROOT], f, settings.APP_WATCH_DELAY) 