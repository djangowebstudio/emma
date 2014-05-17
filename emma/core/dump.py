#!/usr/bin/env python
# encoding: utf-8
"""
dump.py

Created by Geert Dekkers on 2008-06-07.
Copyright (c) 2008 Geert Dekkers Web Studio, 2009, 2010, 2011, 2012, 2013 
Django Web Studio. All rights reserved.

Dumps the app mysql database. Preferably to be triggered by a cron job, or launchd on macosx.
Could also be triggered by Scheduler on Windows, but we're not using Windows, are we?

Produces a timestamped dump which could be used for rollback.
Takes app specific settings, to be found in settings.py

To do: build a database-agnostic dump tool

"""
import sys
import os
import datetime
import subprocess
import tarfile
import utes
from django.conf import settings

#--------------------------------------------------------------------------------------------------
# Logging
#
# A "logs" directory will be created the first time this file is run.
#--------------------------------------------------------------------------------------------------
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=settings.APP_LOGS_ROOT + '/dump.log',
                    filemode='w')
#--------------------------------------------------------------------------------------------------

def main():
	
	"""Dumps the app database to disk, tar gzips the dump and deletes the original.
	Then ends by deleting the oldest dumps from the dumps directory."""
	
	# Check for the existence of a dumps dir in the path
	
	check_dir = utes.Utes()
	check_dir._mkdir(settings.APP_DUMP_PATH)
	
	# Compile the dump filename and path
	dump_name = ''.join((datetime.datetime.today().isoformat('-').replace(":","-").replace("-","").replace(".","-"), ".sql"))
	dump_path = settings.APP_DUMP_PATH + "/" + dump_name
	
	# Initiate a gzipped tar file object
	tar = tarfile.open(settings.APP_DUMP_PATH + "/" + dump_name.replace(".sql", ".tar.gz"), 'w:gz')
	
	# Compile the command. Use the complete path, because the script will probably be running as root.
	cmd = "%(mysqldump_path)s/mysqldump --user=%(user)s --password=%(password)s %(database)s" % {'mysqldump_path': settings.APP_MYSQLDUMP_PATH, 'user':settings.DATABASE_USER,'password': settings.DATABASE_PASSWORD,'database': settings.DATABASE_NAME,'path': settings.APP_DUMP_PATH }
	
	# Execute the cammand and get the output	
	try:
		proc = subprocess.Popen(cmd.encode('utf-8'),shell=True, stdout=subprocess.PIPE,)
		r = proc.communicate()[0]
		try:
			# Open a file and write the output to it.
			f = open(dump_path, 'w')
			f.write(r)
			try:
				# Tar the file from disk, remove the dump file
				tar.add(dump_path)
				tar.close()
				logging.info('Dumped database %s as %s' % (settings.DATABASE_NAME, dump_name))
				try:
					os.remove(dump_path)
				except Exception, inst:
					logging.error("Error removing file after gzipping %s" % inst)
			except Exception, inst:
				logging.error("Error tar.gzipping the file %s" % inst)
		except Exception, inst:
			logging.error("Error writing file %s" % inst)
		
				
	except Exception, inst:
		logging.error("An error occurred dumping the database %s" % inst)
	
	# End by removing the last file from the dumps dir.
	# Set number of dumps to keep in the app specific last segment of settings.py
	
	files = os.listdir(settings.APP_DUMP_PATH)
	
	if len(files) > settings.APP_DB_ROLLBACKS:
		oldest_file = files.pop(0)
		try:
			os.remove(settings.APP_DUMP_PATH + "/" + oldest_file)
		except Exception, inst:
			logging.error("Error removing oldest file %s" % inst)

if __name__ == '__main__':
	main()

