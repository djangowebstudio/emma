#!/usr/bin/env python
# encoding: utf-8
"""
generatekeywords.py

Created by Geert Dekkers on 2008-03-27.
Copyright (c) 2008 Geert Dekkers Web Studio. All rights reserved.

Generates a keyword list from Keyword (images_keyword)
This script should be triggered by launchd on macosx. It could,
of course, also be triggered by a cron tab on a unix-like platform, or by
Scheduler on Windows.

"""

import sys
import os
from django.core.management import setup_environ
import settings
setup_environ(settings)
from eam.interface.models import *

#--------------------------------------------------------------------------------------------------
# Logging
#--------------------------------------------------------------------------------------------------
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=settings.APP_LOGS_ROOT + '/generatekeywords.log',
                    filemode='w')

#--------------------------------------------------------------------------------------------------

class GenerateKeywords:
	def main(self):
		pass


	def generateKeywordsTableContent(self):
		itemListObj = Keyword.objects.exclude(keywords='').order_by('keywords')
		itemList = []
		m = GenerateKeywords()
		for i in itemListObj:
			if i != "":
				item = i.keywords.lower().strip().replace("\n", " ")
				if item[len(item)-1:len(item)] == '.':
					item = item.replace(".","")
				item = item.replace("\r", " ")
				item = item.replace("datum opname", "")
				itemList.append(item.split(","))
				
	
		mergedList = []	
		mergedList = m.merge(itemList)		

		for a in mergedList:
			a = a.strip()
			s = '+%(item)s' % {'item': a.replace(" ", " +")}
			try:
				c = Keyword.objects.filter(keywords__search=s).count()
			except Exception, inst:
				logging.warning ("error during search for item in keyword %(s)s %(inst)s" & {'s': s, 'inst':inst})
			
			try:
				obj = KeywordCount.objects.get(keyword__exact=a)
				obj.count = c
				obj.save()
			except KeywordCount.DoesNotExist:
				
				obj = KeywordCount(keyword=a, count=c)
				try:
					obj.save()
				except Exception, inst:
					logging.warning("error saving new keywordcount item %(s)s %(inst)s" % {'s': a, 'inst':inst})

			except Exception, inst:
				logging.warning("error creating keywordcount entry %(s)s %(inst)s" % {'s': a, 'inst':inst})
				
		try:
			obj = KeywordCount.objects.filter(keyword=None).delete()
		except Exception, inst:
			logging.error( "error deleting empties %(inst)s" % {'inst':inst})
			
	def merge(self, seq):
		#merges a list, deletes duplicates
		# takes a list
		# returns a list
	    d = {}
	    for s in seq:
	        for x in s:
	            d[x] = 1
	    return d.keys()	

if __name__ == '__main__':
	g = GenerateKeywords()
	g.generateKeywordsTableContent()
	#pass

