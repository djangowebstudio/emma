#!/usr/bin/env python
# encoding: utf-8
"""
metadata.py

Created by Geert Dekkers on 2008-02-11.
Copyright (c) 2008, 2009 Geert Dekkers Web Studio. All rights reserved.
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
# from django.core.management import setup_environ
# import settings
# setup_environ(settings)
# from eam.interface.models import *

class Metadata:
		
	def exifGrepForCopyright(self, fileToCheck):
		"""		 gets metadata from a file
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
		"""Try to populate standards-compliant metadata set from 1st generation metadata
		
		-title 										(images_metadata.subject)*
		-keywords 									(images_keyword.keywords, images_metadata.keywords)
		-description 								(images_metadata.description)
		-copyright 									(images_keyword.cright)
		-instructions 								(images_metadata.instructions)
		-icc_profile:colorspacedata 				(images_keyword.profile)
		-creator 									(images_metadata.creator)
		-urgency 									(images_metadata.urgency)
		-captionwriter								(images_metadata.captionwriter)
		-source										(images_metadata.source)
		-DateTimeOriginal							(images_metadata.datetimeoriginal)
		-credit										(images_metadata.credit)
		-location									(images_metadata.location)
		
		(see exifAll)
		* Unavailable
		
		Todo: combine this function with exifAll"""
		
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
		"""		 gets inline thumbnail from a file's metadata
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
		"""		 gets metadata from a file
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
		"""		 gets metadata from a file
		 takes an attribute to request and a full path
		 returns requested metadata using exiftool (http://www.sno.phy.queensu.ca/~phil/exiftool/)"""

		cmd = "exiftool " + " -" + attr + " " + "\"" + fileToCheck + "\""
		proc = subprocess.Popen(cmd,
		              			shell=True, 
		                        stdout=subprocess.PIPE,
		                        )
		return proc.communicate()[0]
	
		
	def exifWrite(self, attr, stringToWrite, writeToFile ):
		"""		 writes metadata to a file
		 takes an attribute to write to and a full path
		 -P option set to ensure mtime is not altered
		 -overwrite_original_in_place means that no backup will be made
		 (Exiftool normally writes a backup file ((filename)._original))
		 You should REALLY, REALLY make a copy of the tree you are processing first!
		 returns requested metadata using exiftool (http://www.sno.phy.queensu.ca/~phil/exiftool/)
"""
		cmd = ''.join(['exiftool -P -overwrite_original_in_place ', '-', attr, '="', stringToWrite, '" ', writeToFile])
		#cmd = "exiftool -P -overwrite_original_in_place" + " -" + attr + "=\"" + stringToWrite + "\" " + "\"" + writeToFile + "\""
		proc = subprocess.Popen(cmd,
		              			shell=True, 
		                        stdout=subprocess.PIPE,
		                        )
		return proc.communicate()[0]
	
	def exifWriteAll(self, cmdDict, writeToFile ):
		"""		 writes metadata to a file
		 takes a dict of attributes to write to and a full path
		 -P option set to ensure mtime is not altered
		-overwrite_original_in_place leaves you with nothing at all if this action goes south.
		A better option would be to leave the _original backup files for a bit and clean them up at night.
		 returns requested metadata using exiftool (http://www.sno.phy.queensu.ca/~phil/exiftool/)
		"""
		cmdList = ["exiftool", "-P", "-overwrite_original_in_place",]
		for a, b in cmdDict.iteritems():
			item = ''.join(['-',a, '=',b])
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
		cmdList = ['exiftool', '-all', path]
		return subprocess.Popen(cmdList,stdout=subprocess.PIPE,).stdout.read()
		
			
	def exifAll(self, fileToCheck):
		"""Extract tags from file using exiftool (http://www.sno.phy.queensu.ca/~phil/exiftool/).
		Takes: path
		The following tags are extracted: 			(corresponding database table fields within parentheses)
		
		-title 										(images_metadata.subject)
		-keywords 									(images_keyword.keywords, images_metadata.keywords)
		-description 								(images_metadata.description)
		-copyright 									(images_keyword.cright)
		-instructions 								(images_metadata.instructions)
		-icc_profile:colorspacedata 				(images_keyword.profile)
		-creator 									(images_metadata.creator)
		-creatortool								(images_metadata.creator_tool)
		-urgency 									(images_metadata.urgency)
		-captionwriter								(images_metadata.caption_writer)
		-source										(images_metadata.source)
		-DateTimeOriginal							(images_metadata.datetimeoriginal)
		-city										(images_metadata.city)
		-Province-State								(images_metadata.province-state)
		-country									(images_metadata.country)
		-headline 									(images_image.group_status)
		-credit										(images_metadata.credit) 1)
		-location									(images_metadata.location)
		-subject									(images_metadata.subject)
		-author										(images_metadata.author)
		-title										(images_metadata.title)
		-album										(images_metadata.album)
		-filetype									(images_metadata.file_type)
		-mimetype									(images_metadata.mime_type)
		-ManagedFromFilePath						(images_metadata.document.path)
		-documentname								(eam.interface.metadata.documentname) 2)
		
		The results are returned as dict.
		
		1) -credit changed to -xmp:credit because exiftool wasn't getting the part after the ":". Getting the xmp explicitly might exclude older files though - as well as non-adobe files
		2) Not to be confused with the previous "document.path" -- denotes the metadata field "Document Name "
		
		To do: Find out if it's feasible to call the Perl lib directly from Python. One good reason? We have to fix 
		all spaces in all paths because we're using the ExifTool CLI!
		UPDATE: there's an API called pyperl but it's old, not maintained, and doesn't readily compile on macosx
		"""
		d = re.compile('(^.+?)(:)(.+$)', re.IGNORECASE)
		cmd = "exiftool -m -S -f -E -documentname -ManagedFromFilePath -filetype -mimetype -title -subject -keywords -description -copyright -instructions -xmp:credit -icc_profile:colorspacedata -creator -creatortool -urgency -captionwriter -source -datetimeoriginal -city -province-state -country -headline -location -author -album " + "\"" + fileToCheck + "\""
		proc = subprocess.Popen(cmd,
		              			shell=True, 
		                        stdout=subprocess.PIPE,
		                        )
		results = proc.communicate()[0]
	
		results_list =  results.splitlines()
		
		
		rdict = {}
		for item in results_list:
			m = d.match(item)
			try:
				rdict[m.group(1).lower()] = m.group(3).strip()
			except Exception, inst:
				pass
		# post-process rdict: switch subject and keywords if ai and keywords are empty
		
		if fileToCheck.split('.').pop() == 'ai':
			if rdict.has_key('keywords'):
				if rdict['keywords'].strip() == '-':
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

if __name__ == '__main__': pass