#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by Geert Dekkers on 2008-04-29.
Copyright (c) 2008 Geert Dekkers Web Studio. All rights reserved.
"""

import sys, os, re, subprocess, gc, inspect
import unittest
import MySQLdb
from django.core.management import setup_environ
import settings
setup_environ(settings)
from emma.interface.models import *
import logging
from datetime import datetime
from time import strptime, strftime
import unicodedata

class LNError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class Utes:
	def __init__(self):
		pass
	
	def _mkdir(self,newdir):
	    """works the way a good mkdir should :)
	        - already exists, silently complete
	        - regular file in the way, raise an exception
	        - parent directory(ies) does not exist, make them as well
	    """
	    if os.path.isdir(newdir):
	        pass
	    elif os.path.isfile(newdir):
	        raise OSError("a file with the same name as the desired " \
	                      "dir, '%s', already exists." % newdir)
	    else:
	        head, tail = os.path.split(newdir)
	        if head and not os.path.isdir(head):
	            self._mkdir(head)
	        logging.info( "_mkdir %s" % repr(newdir))
	        if tail:
	            os.mkdir(newdir)
	
	def merge(self,seq):
		#merges a list, deletes duplicates
		# takes a list
		# returns a list
	    d = {}
	    for s in seq:
	        for x in s:
	            d[x] = 1
	    return d.keys()

	def recount(self,x):
		# does some simple arithmetic on the input
		# takes an integer
		# returns an integer
		if x < 10:
			return 10
		elif 10 <= x < 50:
			return 20
		elif 50 <= x < 200:
			return 30
		elif 200 <= x < 500:
			return 40
		elif 500 <= x < 700:
			return 50
		else:
			return 60
	
	def formatDateTime(self, d_input):
		if d_input == '':
			return None
		else:

			try:
				dt =  datetime.strptime(d_input, "%Y:%m:%d %H:%M:%S+02:00")
				return dt.isoformat(' ')
			except:
				try:
					dt = datetime.strptime(d_input, "%Y:%m:%d %H:%M:%S")
					return dt.isoformat(' ')
				except:
					try:
						dt = datetime.strptime(d_input, "%d/%m/%y %H:%M AM")
						return dt.isoformat(' ')
					except:
						try:
							dt = datetime.strptime(d_input, "%d/%m/%y %H:%M PM")
							return dt.isoformat(' ')
						except:
							try:
								dt = datetime.strptime(d_input, "%d-%m-%Y %H:%M")
								return dt.isoformat(' ')
							except:
								try:
									dt =  datetime.strptime(d_input, "%Y:%m:%d %H:%M:%S+01:00")
									return dt.isoformat(' ')
								except ValueError, inst:
									logging.error( "None of the date formats at formatDateTime worked. Given up. %s" % inst)
									return None


		
		
	def chmodRecursive(self, p, mod):
		""" Correct permissions in the content tree. """
		for root, dirs, fnames in p:
			for f in fnames:
				try:
					os.chmod(os.path.join(root, f), mod)
				except Exception, inst:
					logging.error('Unable to set permissions %s for file %s,  error: %s' % (mod, f, inst))

	def tail_f(self, filepath, nol=10, read_size=1024):
	  """
		http://www.manugarg.com/2007/04/real-tailing-in-python.html
		(Note that the author calls his function "Tail")
	  This function returns the last line of a file.
	  Args:
	    filepath: path to file
	    nol: number of lines to print
	    read_size:  data is read in chunks of this size (optional, default=1024)
	  Raises:
	    IOError if file cannot be processed.


		You can call it in your program like this:
		tail_f('/var/log/syslog') or,
		tail_f('/etc/httpd/logs/access.log', 100)
	  """
	
	  f = open(filepath, 'rU')    # U is to open it with Universal newline support
	  offset = read_size
	  f.seek(0, 2)
	  file_size = f.tell()
	  while 1:
	    if file_size < offset:
	      offset = file_size
	    f.seek(-1*offset, 2)
	    read_str = f.read(offset)
	    # Remove newline at the end
	    if read_str[offset - 1] == '\n':
	      read_str = read_str[:-1]
	    lines = read_str.split('\n')
	    if len(lines) >= nol:  # Got nol lines
	      return "\n".join(lines[-nol:])
	    if offset == file_size:   # Reached the beginning
	      return read_str
	    offset += read_size
	  f.close()
	
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


	def check_status(self, item):
		""" checks the status of launchctl item"""
		search = '.'.join([settings.APP_COM_NAME,item])
		s = subprocess.Popen(["su","geert","launchctl", "list"], stdout=subprocess.PIPE).stdout.read()
		d = {} #Init a dict
		for i in s.splitlines():
			d[i.split('\t').pop()] = i.split('\t')[1]
		return '%s' % d[search] if d.has_key(search) else None
		
		
	def bad(self): return re.compile(settings.APP_FIX_BADCHARACTERS) # look for bad chars
	
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
	
		
	def dump_garbage(self):
	    # force collection
	    print "\nCollecting GARBAGE:"
	    gc.collect()
	    # prove they have been collected
	    print "\nCollecting GARBAGE:"
	    gc.collect()

	    print "\nGARBAGE OBJECTS:"
	    for x in gc.garbage:
	        s = str(x)
	        if len(s) > 80: s = "%s..." % s[:80]

	        print "::", s
	        print "        type:", type(x)
	        print "   referrers:", len(gc.get_referrers(x))
	        try:
	            print "    is class:", inspect.isclass(type(x))
	            print "      module:", inspect.getmodule(x)

	            lines, line_num = inspect.getsourcelines(type(x))
	            print "    line num:", line_num
	            for l in lines:
	                print "        line:", l.rstrip("\n")
	        except:
	            pass

	        print		

# http://code.activestate.com/recipes/410692/
# This class contains spaced indents; change to tabbed indents to edit
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False
	


class utesTests(unittest.TestCase):
	def setUp(self):
		pass


if __name__ == '__main__': pass
