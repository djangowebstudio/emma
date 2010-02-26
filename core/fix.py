#!/usr/bin/env python
# encoding: utf-8
#**************************************************************************************************
"""
fix.py

Created by Geert Dekkers on 2008-01-18.
Copyright (c) 2008, 2009 Geert Dekkers Web Studio. All rights reserved.

unzips, fixes and formats filenames

"""
#**************************************************************************************************
import sys, re, os, time
import unicodedata
import subprocess
import zipfile
import utes
import datetime
from django.core.management import setup_environ
import settings
setup_environ(settings)
from emma.interface.models import *
import utes
from emma.core.metadata import *
#--------------------------------------------------------------------------------------------------
# Logging
#--------------------------------------------------------------------------------------------------
import logging

u = utes.Utes()
u._mkdir(settings.APP_LOGS_ROOT)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=settings.APP_LOGS_ROOT + '/fix.log',
                    filemode='w')
#--------------------------------------------------------------------------------------------------



class Fix:
    def __init__(self): pass
    def settings(self): return settings # Get the settings for reuse as imported class
    def increment(self, input): return input + 1
    def percent2f_n_bad(self): return re.compile(settings.APP_FIX_BADCHARACTERS) # look for bad chars
    def generateFN(self):
        """Gets the last file prefix number"""
        try:
            obj = ImageCount.objects.get(pk=1)
            return obj.count
        except Exception, inst:
            logging.error("Error extracting next number from database. %(inst)s" % {'inst': inst})
                    
    def unzip(self):
        """Unzips and converts files according to rules"""
        ute = utes.Utes()
        for root, dirs, files in os.walk(settings.APP_CONTENT_ROOT):
            for f in files:
                c = self.excludes(f, settings.APP_PACKAGES_ID)
                if True in c:   # the "excludes" function returns a Boolean, ? tuple
                    try:
                        oldpath = os.path.join(root, f)
                        newpath = os.path.join(settings.APP_PACKAGES_ROOT, f.replace(c[1].split('.')[0],'')) # remove the package identifier
                        os.rename(oldpath, newpath )    # rename the file
                        os.remove(oldpath) # remove the renamed file
                    except Exception, inst:
                        logging.error('Error renaming package %s'  % inst)
                elif f[len(f)-4:len(f)] == '.zip':
                    try:
                        os.chmod(os.path.join(root, f), 0755)
                        logging.info('Chmodded %s ' % f)
                    except Exception, inst:
                        logging.error('Couldn\'t chmod %(f)s %(inst)s' % {'f': f, 'inst': inst})
                    if zipfile.is_zipfile(os.path.join(root, f)):
                        try:
                            z = zipfile.ZipFile(os.path.join(root, f))
                            for filename in z.namelist():
                                if filename[0:2] != '__':   # exclude dirnames beginning with '__'
                                    if filename[len(filename)-1:len(filename)] == '/':
                                        dirname = os.path.join(root, self.percent2f_n_bad().sub('-',filename))
                                        ute._mkdir(dirname)
                                        try:
                                            os.chmod(dirname, 0755)
                                        except Exception, inst:
                                            logging.error('Couldn\'t chmod %(f)s %(inst)s' % {'f': dirname, 'inst': inst})
                                    else:
                                        if False in self.excludes(filename, settings.APP_FIX_EXCLUDES):
                                            fname = os.path.join(root,self.percent2f_n_bad().sub('-',filename))
                                        else:
                                            fname = os.path.join(root,filename)
                                        outfile = file(fname, "w")
                                        outfile.write(z.read(filename))
                                        if filename[0:1] != '.':  #exclude filenames begining with a dot (ie .DS_Store and such)
                                            try:
                                                os.chmod(fname, 0755)
                                            except Exception, inst:
                                                logging.error('Couldn\'t chmod %(f)s %(inst)s' % {'f': fname, 'inst': inst})
                                        outfile.close()
                            os.remove(os.path.join(root, f))
                            return f, "unzipped"
                        except Exception, inst:
                            logging.error( "Error opening zipfile %(inst)s" % {'inst': inst})
                    else:
                        logging.warning( "%(f)s doesn't seem to be a valid zipfile, or perhaps it just isn't all there yet..." % {'f': f})
        return "...done."

    
    def fix(self, delay=60):
        """Calls all other functions in Fix"""
        logging.info( "Fix calling in for %s..." % settings.APP_CONTENT_ROOT)
        logging.info( "...checking for zipped files...")
        unzip_results = self.unzip()
        logging.info( "%(results)s" % {'results' : unzip_results})
        logging.info( "...checking files and folders...")
        for root, dirs, files in os.walk(settings.APP_CONTENT_ROOT):
            self.convertDirs(root,dirs)
            self.convertFiles(root,files)
        logging.info( "...done checking files and folders")
        time.sleep(delay)
        self.fix()

        
    def excludes(self, f, excludes):
        """ 
        Excludes files based on regex list in settings. 
        Returns a tuple (Boolean, match found) if True, 
        otherwise a single Boolean, False.
        """

        for e in excludes:
            d = re.compile(e)
            r = d.search(f)
            # If a match is found, return True, if nothing is found, return False
            if r: return True, r.group()
        
        return False,   
    

        
                                                        
    def convertDirs(self, root, dirs):
        """Renames directories if necessary"""

        for f in dirs:
            if False in self.excludes(f, settings.APP_FIX_EXCLUDES):
                newfile = self.percent2f_n_bad().sub('-', f)                                        # strip the bad chars 
                newfile = newfile.strip()                                                           # strip the spaces from the directories
                newfile = newfile.replace(' ', '-')                                                 # replace spaces with hyphens (sometimes fix misses a space)
                newfile = newfile.replace('\'', '-')                                                # explicitly remove apostrophes
                newfile = newfile.replace('-_-', '')                                                # remove any -_- signs (see settings) in folders
                newfile = newfile.replace('-_--','')                                                # see above
                newfile = newfile.replace('--','-')                                                 # remove double hyphens
                newfile = newfile.replace('---','-')                                                # remove triple hyphens
                if newfile.startswith('-week') == True: newfile = newfile.replace('-week', 'week')  # very specific, i know...
                newfile = self.convertText(newfile, 'ignore')                                       # get rid of the latin-1 chars
                if newfile != f: 
                    newpath = os.path.join(root,newfile)
                    oldpath = os.path.join(root,f)
                    try:
                        os.rename(oldpath, newpath)
                        logging.info( "%(f)s changed to %(newfile)s" % {'f': f, 'newfile':newfile})
                    except Exception, inst:
                        logging.error( "Error renaming %(oldpath)s %(inst)s" % {'oldpath': oldpath, 'inst':inst})
        
    def updateImageCount(self, number):
        """Updates images_imagecount in database"""
        try:
            obj = ImageCount.objects.get(pk=1)
            obj.count = number
            obj.save()
        except Exception, inst:
            logging.error( "Error updating ImageCount %(inst)s" % {'inst':inst})
    
    
    def pairFlashComponents(self, flashDict, root, flashComponent, correct=True):
        """ Processes .fla /.swf pairs - renames both, copies the swf to gallery """
        u = utes.Utes()
        if flashComponent[len(flashComponent)-4:len(flashComponent)] == '.fla':
            
            component_key = self.percent2f_n_bad().sub('-', flashComponent).replace('.fla', '')
            
            if component_key not in flashDict:
                
                
                number = str(self.generateFN())
                flashDict[component_key] = root, number + component_key + '.fla', number + component_key + '.swf'
                    
                oldpath_FLA = os.path.join(root, flashComponent)
                oldpath_SWF = os.path.join(root, flashComponent.replace('.fla','.swf'))
                newpath_FLA = os.path.join(root, flashDict[component_key][1])
                newpath_images_SWF = os.path.join(settings.STATIC_ROOT + '/gallery/images', flashDict[component_key][2])
                newpath_thumbs_SWF = os.path.join(settings.STATIC_ROOT + '/gallery/thumbs', flashDict[component_key][2])
                
                try:
                    os.rename(oldpath_FLA, newpath_FLA)
                    flashDict[number + component_key] = root, flashDict[component_key][1], ''
                    self.updateImageCount(number)
                except Exception, inst:
                    logging.error('Error renaming %(fla)s %(inst)s' % {'fla': flashComponent, 'inst': inst})
                    
                try: 
                    u.pcopy(oldpath_SWF, newpath_thumbs_SWF)  # First copy the swf to the thumbs dir in gallery, set chmod"
                    try: 
                        os.chmod(newpath_thumbs_SWF, 0755)
                    except Exception, inst:
                        logging.warning("Chmod to 755 for swf in thumbs didn't work out %s" % inst)
                    os.rename(oldpath_SWF, newpath_images_SWF) # Then move the swf to the images dir, chmod.
                    try: 
                        os.chmod(newpath_thumbs_SWF, 0755)
                    except Exception, inst:
                        logging.warning("Chmod to 755 for swf in images didn't work out %s" % inst)
                    
                    flashDict[number + component_key] = root, flashDict[component_key][1], flashDict[component_key][2]
                    del flashDict[component_key]
                except Exception, inst:
                    logging.error('Error renaming %(swf)s %(inst)s' % {'swf': flashComponent.replace('.fla', '.swf'), 'inst': inst})
            else:
                logging.warning('%s already exists' % component_key )
                

    def convertFiles(self, root, files):
        """Does most of the renaming, processes files without extension, pairs fla/swf for further processing."""
        # Init Dict for pairFlashComponents()
        flashDict = {}
        for f in files:
            if False in self.excludes(f, settings.APP_FIX_EXCLUDES):
                # If the filename starts with five integers, it's probably ok
                try:
                    i = int(f[0:5])
                    # Everything should be lower case anyway
                    newfile = f.lower()                                                             
                except: 
                    # Now we can prepare to change the filenames. However, in some cases it would be prudent to capture any existing information, and often
                    # that would be the filename. So the first step is to load some data from the *old* name for later reuse.
                    keywords =  ','.join([root.replace(settings.APP_CONTENT_ROOT,'').replace('/',',').replace('-', ',').replace('_',','), os.path.splitext(f)[0].replace('-',',').replace('_',',').replace(' ', ',')]) 
                    k = keywords[1:len(keywords)] # clip off the leading comma
                    keywords = k.split(',')
                    for word in keywords:
                        if len(word) < 2 or word in settings.APP_FIX_EXCLUDEKEYWORDS:
                            keywords.remove(word)
                    keywords = ', '.join(keywords)
                            
                    if f[len(f)-4:len(f)] == '.fla':
                        # Flash files are to be entered into APP_CONTENT_ROOT as .fla / .swf pairs
                        # If either the .fla is present without an .swf, or vv, then they should be treated
                        # as any other file
                        self.pairFlashComponents(flashDict, root, f)
                    else:
                        # Since we've made it this far, we'll be needing a number prefix
                        number = self.generateFN()                                          
                        if f[(len(f)-4):(len(f)-3)] != "." and f[(len(f)-5):(len(f)-4)] != "." and f[(len(f)-3):(len(f)-2)] != ".": # wow, how about just popping the ext?
                        
                            # This file probably doesn't have an extension. 
                            # We'll use exiftool to look up the filetype in the metadata
                        
                            logging.warning( "%(f)s doesn't seem to have an extension...we'll go look for the file type..." % {'f': f})
                            extension = self.exif('filetype', os.path.join(root,f)).lower()
                            newfile = f + "." + extension
                            if f[0:3] == '-_-':
                                newfile = str(number) + f.replace('-_-','') + "." + extension
                            else:
                                newfile = str(number) + root.split("/").pop().lower() + "." + extension                                     
                            newfile = self.percent2f_n_bad().sub('-', newfile)
                            newfile = newfile.strip().lower().replace("-","")
                            newfile = self.convertText(newfile, 'ignore')
                            number += 1
                        else:
                            if f[0:3] == '-_-':
                                newfile = str(number) + f.replace('-_-','')
                            elif f[0:1] == '*':
                                newfile = self.percent2f_n_bad().sub('-', newfile)                                      
                            else:
                                newfile = str(number) + root.split("/").pop().lower() + "." + f.split(".").pop() # add the old extension to the new name                                                
                            newfile = self.percent2f_n_bad().sub('-', newfile)
                            newfile = newfile.strip().lower().replace("-","")
                            newfile = self.convertText(newfile, 'ignore')
                            number += 1
                        if newfile != f:
                            newpath = os.path.join(root,newfile)
                            oldpath = os.path.join(root,f)
                            try:
                                os.rename(oldpath, newpath)
                                logging.info( "%(f)s changed to %(newfile)s " % {'f': f, 'newfile': newfile})
                                self.updateImageCount(number)
                                if 'APP_FIX_ADDKEYWORDS' in dir(settings) and settings.APP_FIX_ADDKEYWORDS:
                                    # Write the saved keywords data
                                    metadata.Metadata().exifWrite('keywords', keywords, newpath, True) 
                                    logging.info("Added %s to %s" % (keywords, newpath))
                                logging.info( "Count updated to %(number)s" % {'number':number})
                            except Exception, inst:
                                logging.error ("Error renaming %(oldpath)s" % {'oldpath':oldpath, 'inst': inst})
                        else:
                            return None
        
    def convertText(self, text, action):
        """ 
        http://techxplorer.com/2006/07/18/converting-unicode-to-ascii-using-python/
        References to XML in comments removed, apart from that, used as-is.
        Converts a string with embedded unicode characters
            - text, the text to convert
            - action, what to do with the unicode
        """
        try:
            temp = unicode(text, "utf-8")
            fixed = unicodedata.normalize('NFKD', temp).encode('ASCII', action)
            return fixed
        except Exception, errorInfo:
            logging.error ("Unable to convert the Unicode characters %(inst)s" % {'inst' : errorInfo})

    def exif(self, attr, fileToCheck):
        """ Gets metadata from a file
            Takes an attribute to request and a full path
            Returns requested metadata using exiftool (http://www.sno.phy.queensu.ca/~phil/exiftool/)"""
        cmd = "exiftool -b " + " -" + attr + " " + "\"" + fileToCheck + "\""
        proc = subprocess.Popen(cmd,
                                shell=True, 
                                stdout=subprocess.PIPE,
                                )
        result = proc.communicate()[0]
        if result != None:
            return result
                
if __name__ == '__main__':
    logging.info ("Starting fix() for %(settings)s" % {'settings' : settings.APP_CONTENT_ROOT})
    
    f = Fix()
    f.fix()
