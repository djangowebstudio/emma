#!/usr/bin/env python
# encoding: utf-8
"""
metadata.py

Created by Geert Dekkers on 2008-02-11.
Copyright (c) 2008, 2009 Geert Dekkers Web Studio, 2010, 2011, 2012 Django Web Studio. All rights reserved.
"""
import string
import sys
import os
import unittest
import subprocess
import re
import datetime
import time
from utes import *
try:
    import json
except:
    import simplejson as json

class Metadata(object):
    
    def __init__(self): pass
        
    
    
    
    def stat(self, path):
        """
        On OSX, st_birthtime is the only file time that accurately 
        reflects the original creation time of a file. Even
        st_ctime gets updated once in a while, for example
        when the metadata is updated.
        
        Sadly, st_birthtime is not exposed to python on all OSX versions.
        Notably not on 10.5, but it is on 10.7 (have not checked 10.6).
        
        Other platforms use st_ctime more correctly, but have no st_birthtime.
        
        This function is an alternative for os.stat(<path>).st_birthtime.
        It leaves testing the platform and/or the existence of the st_birthtime 
        method up to you.
        
        Returns a dict containing the response of stat -s <file>.
        The return value will be something like this:
        
        {'st_rdev': '0', 'st_ctime': '1339613207', 'st_mtime': '1339613207', 
        'st_blocks': '31432', 'st_nlink': '1', 'st_flags': '0', 'st_gid': '20', 
        'st_blksize': '4096', 'st_dev': '234881026', 'st_size': '16089528', 
        'st_mode': '0100667', 'st_uid': '501', 'st_birthtime': '1108716743', 
        'st_ino': '102959153', 'st_atime': '1339613537'}
        
        You will need to test for the exact response for your target 
        platform. 
        
        """
        r = subprocess.Popen(['stat', '-s', path], stdout=subprocess.PIPE).communicate()[0]
        d = dict([x.split('=') for x in r.rstrip().split(' ')])
        return d
    
    
    def exifGrepForCopyright(self, fileToCheck):
        """      gets metadata from a file
         takes a full path
         this function is very specific for the way the copyright info has been (wrongly) written to file
         uses shell grep, not python grep
         requests metadata using exiftool (http://www.sno.phy.queensu.ca/~phil/exiftool/)
         returns 1 or 0
"""

        grepStatement = 'grep -w -c "[cC]opyright[s]:[ ]ja"'

        proc = subprocess.Popen('exiftool' + ' -f -description ' + '\"' + fileToCheck + '\"' + ' | ' + grepStatement,
                                shell=True, 
                                stdout=subprocess.PIPE,
                                )
        return proc.communicate()[0]
        
    def exifGrepForCopyrightFromDescription(self, stringToGrep):
        
        yes = re.compile('copyrights*:\s*ja|yes|vrij', re.IGNORECASE)
        m = yes.search(stringToGrep)
        if m:
            return 1
        else:
            no = re.compile('copyrights*:\s*nee|no', re.IGNORECASE)
            n = no.search(stringToGrep)
            if n:
                return 0
            else:
                return 2
        
    def exifFromDescription(self, stringToGrep, t=0):
        """
        Migration script
        ----------------
        Try to populate standards-compliant metadata set from 1st generation metadata.
        
        This project has quite a history, and a web tool existed many years prior to the
        release of emma / beeldnet. By "1st generation" is meant metadata entered into the 
        predecessor application called Cumulus. Metadata was often incorrectly entered, so
        a migration script was necessary.
        
        At first release of emma / beeldnet, this migration script was used to migrate metadata
        from the older images.
        
        -title                                      (images_metadata.subject)*
        -keywords                                   (images_keyword.keywords, images_metadata.keywords)
        -description                                (images_metadata.description)
        -copyright                                  (images_keyword.cright)
        -instructions                               (images_metadata.instructions)
        -icc_profile:colorspacedata                 (images_keyword.profile)
        -creator                                    (images_metadata.creator)
        -urgency                                    (images_metadata.urgency)
        -captionwriter                              (images_metadata.captionwriter)
        -source                                     (images_metadata.source)
        -DateTimeOriginal                           (images_metadata.datetimeoriginal)
        -credit                                     (images_metadata.credit)
        -location                                   (images_metadata.location)
        
        (see exifAll)
        * Unavailable
        
        Todo: combine this function with exifAll
        
        """
        
        # Add a 'keywords' key if there is none
        if not re.compile('^Keywords:', re.IGNORECASE).match(stringToGrep): stringToGrep = 'Keywords: ' + stringToGrep      
        s = stringToGrep.splitlines()
        
        d = re.compile('(^.+?)(:)(.+$)', re.IGNORECASE) 
        
        rdict = {}
        cdict = {}
        for item in s:
            m = d.match(item)
            try:
                rdict[m.group(1).lower()] = m.group(3).strip()
            except:
                pass
        
        # Pass non-compliant instructions-related fieldnames to instructions key/value pair
        instructions = []
        for a in rdict.iterkeys():
            if re.compile(r'^toestemming').match(a):
                instructions.append(a)
                instructions.append(rdict[a])
        
        for b in rdict.iterkeys():
            if re.compile(r'voorbeeld').match(b):
                instructions.append(b)
                instructions.append(rdict[b])
        
        for c in rdict.iterkeys():
            if re.compile(r'naamsvermelding').match(c):
                instructions.append(c)
                instructions.append(rdict[c])
        
        cdict['instructions'] = ','.join(instructions)
        cdict['credit'] = rdict['fotobureau'] if rdict.has_key('fotobureau') == True else rdict['fotograaf'] if rdict.has_key('fotograaf') == True else ''
        cdict['creator'] = rdict['fotograaf'] if rdict.has_key('fotograaf') == True else ''
        cdict['keywords'] = rdict['keywords'] if rdict.has_key('keywords') == True else ''
        cdict['location'] = rdict['locatie'] if rdict.has_key('locatie') == True else ''
        cdict['softdate'] = rdict['datum'] if rdict.has_key('datum') == True else ''
        cdict['source'] = rdict['stocknummer'] if rdict.has_key('stocknummer') == True else ''
        
        
        # copyright is somewhat more complicated
        # sometimes the plural is used as key
        cdict['copyright'] = rdict['copyright'] if rdict.has_key('copyright') == True else rdict['copyrights'] if rdict.has_key('copyrights') == True else ''
        # and then users give a range of values...
        copyright = cdict['copyright']
        if copyright: cdict['copyright'] = self.copyright_case(copyright)
        if t == 1:
            return cdict, rdict
        else:
            return cdict
    
    def getInlineThumbnail(self, fileToCheck, out_path):
        """      gets inline thumbnail from a file's metadata
         takes an attribute to request and a full path
         returns requested metadata using exiftool (http://www.sno.phy.queensu.ca/~phil/exiftool/)
"""
        cmd = "exiftool -b " + " -thumbnailsimage " + "\"" + fileToCheck + "\" > " + out_path
        proc = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE,)
        return out_path
            
    def copyright_case(self, copyright):
        """Convert all known copyright values to numeric values"""
        c = copyright.lower().strip().replace('"','')
        for case in switch(c):
            if case('yes'):
                r = 1
                break
            if case('ja'):
                r = 1
                break
            if case('no'):
                r = 0
                break
            if case('nee'):
                r = 0
                break
            if case('vrij'):
                r = 0
                break
            if case():
                if c.find('ja') == 0:
                    r = 1
                elif c.find('nee') == 0:
                    r = 0
                else:
                    r = 2

        return r            
        
    def exif(self, attr, fileToCheck):
        """      gets metadata from a file
         takes an attribute to request and a full path
         returns requested metadata using exiftool (http://www.sno.phy.queensu.ca/~phil/exiftool/)
         """
        cmd = "exiftool -b " + " -" + attr + " " + "\"" + fileToCheck + "\""
        proc = subprocess.Popen(cmd,
                                shell=True, 
                                stdout=subprocess.PIPE,
                                )
        return proc.communicate()[0]
        
    def ex(self, attr, fileToCheck):
        """      gets metadata from a file
         takes an attribute to request and a full path
         returns requested metadata using exiftool (http://www.sno.phy.queensu.ca/~phil/exiftool/)"""

        cmd = "exiftool " + " -" + attr + " " + "\"" + fileToCheck + "\""
        proc = subprocess.Popen(cmd,
                                shell=True, 
                                stdout=subprocess.PIPE,
                                )
        return proc.communicate()[0]
    
        
    def exifWrite(self, attr, stringToWrite, writeToFile, concat=False ):
        """      writes metadata to a file
         Takes 1) an attribute (str) to write to, 2) a string to write, and 2) a full path.
         Optionally 4) a concat is done (boolean), adding to the attribute instead of wiping it clean and starting over.
         
         Hardcoded within this function:
         -P option set to ensure mtime is not altered
         -overwrite_original_in_place means that no backup will be made
         (Exiftool normally writes a backup file ((filename)._original))
         You should REALLY, REALLY make a copy of the tree you are processing first!
         returns requested metadata using exiftool (http://www.sno.phy.queensu.ca/~phil/exiftool/)
         """
        if not concat:
            cmd = ["exiftool", "-P", "-overwrite_original_in_place", "%s='%s" % (attr, stringToWrite), writeToFile]

        else:
            cmd = ''.join(['exiftool -P -overwrite_original_in_place ', '-', attr, '+="', stringToWrite, '" ', writeToFile])
        proc = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE,)
        return proc.communicate()[0]
    
    def exifWriteAll(self, cmdDict, writeToFile):
        """      writes metadata to a file
         takes a dict of attributes to write to and a full path
         -P option set to ensure mtime is not altered
        -overwrite_original_in_place leaves you with nothing at all if this action goes south.
        A better option would be to leave the _original backup files for a bit and clean them up at night.
         returns requested metadata using exiftool (http://www.sno.phy.queensu.ca/~phil/exiftool/)
        """
        cmdList = ["exiftool", "-P", "-overwrite_original_in_place",]  
        for a, b in cmdDict.iteritems():
            item = ''.join(['-',unicode(a), '=',unicode(b)])
            cmdList.append(item)
        cmdList.append(writeToFile)
        return subprocess.Popen(cmdList,stdout=subprocess.PIPE,).stdout.read()

    def description(self, fileToCheck):
        """
        # gets metadata from a file
        # takes an attribute to request and a full path
        # returns requested metadata using exiftool (http://www.sno.phy.queensu.ca/~phil/exiftool/)
        """
        
        cmd = "exiftool -b -description " + "\"" + fileToCheck + "\""
        proc = subprocess.Popen(cmd,
                                shell=True, 
                                stdout=subprocess.PIPE,
                                )
        results = proc.communicate()[0]
        if results == '':
            cmd = "exiftool -b -caption-abstract " + "\"" + fileToCheck + "\""
            proc = subprocess.Popen(cmd,
                                    shell=True, 
                                    stdout=subprocess.PIPE,
                                    )
            results = proc.communicate()[0]
        return results
    def exifRAW(self, path):
        """ Just a simple wrapper to exiftool -all (http://www.sno.phy.queensu.ca/~phil/exiftool/)"""
        cmd = ['exiftool', '-all', '-j', path]
        r = subprocess.Popen(cmd,stdout=subprocess.PIPE,).stdout.read()
        try:
            j = json.loads(r)[0]
            return j
        except:
            return None
        
    def exifJSON(self, path, key): 
        """ Wrapper to exiftool. Returns JSON for a single key """
        
        k = '-%s' % key
        
        cmd = ['exiftool', k, '-j', path]
        
        r = subprocess.Popen(cmd,stdout=subprocess.PIPE,).stdout.read()
        try:
            j = json.loads(r)[0]
            return j
        except:
            return None
        
        
            
    def exifAll(self, fileToCheck):
        """Extract tags from file using exiftool (http://www.sno.phy.queensu.ca/~phil/exiftool/).
        Takes: path
        The following tags are extracted:           (corresponding database table fields within parentheses)
        
        -title                                      (images_metadata.subject)
        -xmp:keywords                               (images_keyword.keywords, images_metadata.keywords)
        -description                                (images_metadata.description)
        -copyright                                  (images_keyword.cright)
        -instructions                               (images_metadata.instructions)
        -icc_profile:colorspacedata                 (images_keyword.profile)
        -creator                                    (images_metadata.creator)
        -creatortool                                (images_metadata.creator_tool)
        -urgency                                    (images_metadata.urgency)
        -captionwriter                              (images_metadata.caption_writer)
        -source                                     (images_metadata.source)
        -DateTimeOriginal                           (images_metadata.datetimeoriginal)
        -city                                       (images_metadata.city)
        -Province-State                             (images_metadata.province-state)
        -country                                    (images_metadata.country)
        -headline                                   (images_image.group_status)
        -credit                                     (images_metadata.credit) 1)
        -location                                   (images_metadata.location)
        -subject                                    (images_metadata.subject)
        -author                                     (images_metadata.author)
        -title                                      (images_metadata.title)
        -album                                      (images_metadata.album)
        -filetype                                   (images_metadata.file_type)
        -mimetype                                   (images_metadata.mime_type)
        -ManagedFromFilePath                        (images_metadata.document.path)
        -documentname                               (emma.interface.metadata.documentname) 2)
        -orientation#                               (images_metadata.orientation) 3)
        
        The results are returned as dict.
        UPDATE: We'll be writing all to json. 
        
        1) -credit changed to -xmp:credit because exiftool wasn't getting the part after the ":". Getting the xmp 
            explicitly might exclude older files though - as well as non-adobe files.
        2) Not to be confused with the previous "document.path" -- denotes the metadata field "Document Name "
        3) Orientation is grabbed as integer, changed the orientation field in the Metadata model to reflect this (20091122)
            Note that we need exiftool 8.00 for this feature
        
        To do: Find out if it's feasible to call the Perl lib directly from Python. One good reason? We have to fix 
        all spaces in all paths because we're using the ExifTool CLI!
        UPDATE: there's an API called pyperl but it's old, not maintained, and doesn't readily compile on macosx
        
        """
        d = re.compile('(^.+?)(:)(.+$)', re.IGNORECASE)
        cmd = ["exiftool","-m","-S","-f","-E","-documentname","-ManagedFromFilePath","-filetype","-mimetype",
                "-title","-subject", "-xmp:keywords", "-description","-copyright","-instructions","-xmp:credit",
                "-icc_profile:colorspacedata","-creator","-creatortool","-urgency","-captionwriter","-source",
                "-datetimeoriginal","-city","-province-state","-country","-headline","-location","-author",
                "-album","-orientation#",fileToCheck]
        results = subprocess.Popen(cmd,stdout=subprocess.PIPE).stdout.read()
        results_list =  results.splitlines()
        rdict = {}
        for item in results_list:
            m = d.match(item)
            try:
                rdict[m.group(1).lower()] = m.group(3).strip()
            except Exception, inst:
                pass
                        
        
        # post-process rdict: switch subject and keywords if keywords are empty   
        if rdict.has_key('keywords'):
            if not rdict['keywords'] or rdict['keywords'].strip() == '-':
                if rdict.has_key('subject'):
                    rdict['keywords'] = rdict['subject']
                
        # post-process rdict: set copyright to boolean int          
        copyright = rdict['copyright'] if rdict.has_key('copyright') else ''
        if copyright: rdict['copyright'] = self.copyright_case(copyright)

        # post-process rdict: set icc_profile:colorspacedata to boolean int
        if rdict.has_key('colorspacedata'):
            if rdict['colorspacedata'].lower().strip() == 'cmyk':
                rdict['colorspacedata'] = 1
            elif rdict['colorspacedata'].lower().strip() == 'rgb':
                rdict['colorspacedata'] = 0
            else:
                rdict['colorspacedata'] = 2
        else:
            rdict['colorspacedata'] = 2    
        
        # post-process rdict: format datetime   
        if rdict.has_key('datetimeoriginal'):
            rdict['datetimeoriginal'] = None if rdict['datetimeoriginal'].strip() == '-' else Utes().formatDateTime(rdict['datetimeoriginal'])
            
        # post-process rdict: format orientation
        if rdict.has_key('orientation'):
            rdict['orientation'] = 0 if rdict['orientation'].strip() == '-' else rdict['orientation']
            
        # post-process rdict: cut values = ' -'
        # The ExifTool -f option prints tags even if the value is not found. We need this because we're
        # mapping tags to dict keys to variables further along the line. But what we don't need is the 
        # ' -' ExifTool puts in. So we want to get rid of these.
        
        for a, b in rdict.iteritems():
            if b == '-':
                rdict[a] = ''
                
        return rdict

class DataTests:
        def __init__(self):
            pass
            
        def searchCopyright(self):
            """ Print copyright test"""
            m = Metadata()
            s = Keyword.objects.filter(cright=2)
            print "Copyright unknown: %s" % s.count()
            for i in s:
                p = os.path.join(settings.APP_CONTENT_ROOT, i.image_path)
                try:
                    a = int(i.image_LNID[0:5])
                    if a < settings.APP_NEW_DATA:

                        d = m.description(p)
                        print "old:", i.image_LNID, m.exifGrepForCopyrightFromDescription(d), "\n"
                        print "new:", i.image_LNID, m.exifFromDescription(d,1), "\n"

                    else:

                        d = m.exifAll(p)
                        print i.image_LNID, d
                except Exception, inst:
                    d = m.description(p)
                    print "other:", i.image_LNID, m.exifGrepForCopyrightFromDescription(d), "\n"

        
"""class Change:
    def __init__(self):
        pass
    
    def change(self,list):
        for item in list:
            try:
                if int(item[0:5]):
                    if int(item[0:5]) < 10000:
                        find
"""
                     

class MetadataTests(unittest.TestCase):
    def setUp(self):
        pass

if __name__ == '__main__': 
    m = Metadata()
    print m.exifAll('/Users/geert/Sites/doennet/content/Jubilea-DOEN/10-jaar-DOEN/1440510jaardoen.jpg')