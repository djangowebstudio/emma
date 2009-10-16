import os, sys, inspect
from django.db import models
import eam.core.metadata as metadata
from django.core.management import setup_environ
import settings
setup_environ(settings)
from django.core.files.storage import FileSystemStorage
fs = FileSystemStorage()
import logging
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import User as _u

# Create your models here.

def get_path(instance, filename):
	c = ContentType.objects.get_for_model(instance)
	ext = os.path.splitext(filename)[1]
	if c.name == 'album':
		if instance.album_identifier:
			return '%s/%s%s' % (c.name, instance.album_identifier, ext)
		else:
			return '%s/%s' % (c.name, filename)
	elif c.name == 'metadata':
		if instance.image_LNID:
			return '%s/%s%s' % (c.name, instance.image_LNID, ext)
		else:
			return '%s/%s' % (c.name, filename)
	else:
		return '%s/%s' % (c.name, filename)

class OverwriteStorage(FileSystemStorage):
    
    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

class Image(models.Model):
	""" Primary table."""
	id = models.AutoField(primary_key=True)
	image_LNID = models.CharField(max_length=255,unique=True)
	image_path = models.CharField(max_length=255)
	image_name = models.CharField(max_length=255)
	image_real_name = models.CharField(max_length=255)
	image_real_path = models.CharField(max_length=255)
	date_created = models.DateTimeField('Date Created',null=True)
	date_modified = models.DateTimeField('Date Modified',null=True)
	date_entered = models.DateTimeField('Date Entered',null=True)
	CATEGORY_CHOICES = (
		('photo', 'Photography'),
		('illustration', 'Illustrations and Art Work'),
	)
	image_category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
	image_pages = models.IntegerField(null=False, default=0)
	ALBUM_CHOICES = (
	    ('leader', 'In album and leader'),
	    ('follower', 'In album and follower'),
	)
	group_status = models.CharField(max_length=8, blank=True, choices=ALBUM_CHOICES)
	ts = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return self.image_LNID
		
		
class Category(models.Model):
	""" Unused. To hold information about the image category"""
	image = models.ForeignKey(Image)
	image_LNID = models.CharField(max_length=255)
	image_cat = models.CharField(max_length=255)
	
class Group(models.Model):
	""" Holds information about grouped images"""
	#image = models.ForeignKey(Image)
	image_LNID = models.CharField(max_length=255, unique=True)
	image_group = models.CharField(max_length=255)
	image_pages = models.IntegerField(null=False, default=0)
	
	def __unicode__(self):
		return self.image_group

class AlbumClass(models.Model):
	name = models.CharField(max_length=255)
	ts = models.DateTimeField(auto_now=True)
	def __unicode__(self):
	        return self.name

	class Meta:
		verbose_name = "Album category"
		verbose_name_plural = "Album categories"


class Album(models.Model):
	""" Holds information about grouped images"""
	image = models.ManyToManyField(Image)
	#kind = models.ForeignKey(AlbumClass, verbose_name="Unused at the moment", default=AlbumClass.objects.get(pk=1))
	album_identifier = models.CharField(max_length=255, unique=True)
	album_name = models.CharField(max_length=255, default="untitled album")
	album_pages = models.IntegerField(null=False, default=0)
	document = models.FileField(upload_to=get_path, max_length=255, blank=True, storage=OverwriteStorage())	
	ts = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return self.album_name

	
class MDAll(models.Model):
	"""Unused"""
	image = models.ForeignKey(Image)
	image_LNID = models.CharField(max_length=255)
	MDall = models.TextField(blank=True)

class Copyright(models.Model):
	"""Unused (for the moment)"""
	image = models.ForeignKey(Image)
	image_LNID = models.CharField(max_length=255)
	copyright = models.BooleanField()
	copyright_terms = models.TextField(blank=True)

class Order(models.Model):
	"""Holds cart items"""
	image = models.ForeignKey(Image)
	image_LNID = models.CharField(max_length=255)
	resolution = models.CharField(max_length=255, blank=True)
	client = models.CharField(max_length=255)
	clientImage = models.CharField(max_length=255, unique=True)
	group_name = models.CharField(max_length=255, blank=True)
	album_identifier = models.CharField(max_length=255, blank=True)
	notes = models.TextField(blank=True)
	ts = models.DateTimeField(auto_now=True)
	status = models.SmallIntegerField(null=True)
	
		

class Keyword(models.Model):
	"""Secondary table, most used for views."""
	image = models.ForeignKey(Image)
	image_LNID = models.CharField(max_length=255, unique=True)
	image_name = models.CharField(max_length=255)
	subject = models.CharField(max_length=255)
	keywords = models.TextField(blank=True)
	cright = models.NullBooleanField()
	profile = models.NullBooleanField()
	source = models.CharField(max_length=255)
	image_path = models.CharField(max_length=255)
	notes = models.TextField(blank=True)
	ts = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return self.image_LNID

class Metadata(models.Model):
	"""Holds image metadata. Creator_tool, creator and orientation are unused"""
	image = models.ForeignKey(Image)
	keyword = models.ForeignKey(Keyword)
	image_LNID = models.CharField(max_length=255, unique=True)	
	file_type = models.CharField(max_length=255, blank=True)
	mime_type = models.CharField(max_length=255, blank=True)
	source = models.CharField(max_length=255, blank=True)
	caption_writer = models.CharField(max_length=255, blank=True)
	subject = models.CharField(max_length=255, blank=True)
	keywords = models.TextField(blank=True)
	description = models.TextField(blank=True)	
	location = models.CharField(max_length=255, blank=True, help_text="Note that true GPS locationing is available as an add-on.")
	city = models.CharField(max_length=255, blank=True)
	provincestate = models.CharField(max_length=255, blank=True)
	country = models.CharField(max_length=255, blank=True)
	instructions = models.TextField(blank=True)
	title = models.CharField(max_length=255, blank=True)
	creator_tool = models.CharField(max_length=255, blank=True)
	creator = models.CharField(max_length=255, blank=True)
	author = models.CharField(max_length=255, blank=True)	
	credit = models.TextField(blank=True)
	datetimeoriginal = models.DateTimeField(null=True, blank=True)
	orientation = models.BooleanField(default=0)
	softdate = models.CharField(max_length=255, blank=True)
	copyright = models.NullBooleanField()
	profile = models.NullBooleanField()
	HEADLINE_CHOICES = (
	    ('leader', 'In album and leader'),
	    ('follower', 'In album and follower'),
	)
	
	headline = models.CharField(max_length=255, blank=True, choices=HEADLINE_CHOICES)
	album = models.CharField(max_length=255, blank=True)
	documentname = models.CharField(max_length=255, blank=True)
	document = models.FileField(upload_to=get_path, max_length=255, blank=True, storage=OverwriteStorage())	
	MDall = models.TextField(blank=True)
	ts = models.DateTimeField(auto_now=True)
	
	def __unicode__(self): return self.image_LNID
		
	def get_absolute_url(self): return '/media/%s' % self.document
		
	def get_document_path(self): return '%s/%s' % (settings.MEDIA_ROOT, self.document)
					
	def thumb(self): return '<img src="%s" />' % os.path.join('/gallery/miniThumbs/', self.image.image_name)
		
	thumb.allow_tags = True
	
	class Meta:
		permissions = (
		('can_edit_content', 'Can edit content')
		)
		
	
	def save(self):
		super(Metadata, self).save()
		# Execute only if the caller is not in watch. (See above)
		caller = inspect.getframeinfo(sys._getframe(1), context=0)[2]		
		try:
			if not caller == 'f':
				
				# Save overlapping Keyword / Metadata fields
				k = Keyword.objects.get(pk=self.image.pk)
				k.cright = self.copyright
				k.subject = self.subject
				k.source = self.source
				k.keywords = self.keywords
				k.save()
				
				# Save overlapping Image / Metadata fields
				i = Image.objects.get(pk=self.image.pk)
				i.group_status = self.headline
				i.save()
		
				m = metadata.Metadata()
				path = os.path.join(settings.APP_CONTENT_ROOT, i.image_real_path)
		
				cmdDict = {
				'source'				:	self.source,
				'captionwriter' 		:  	self.caption_writer,
				'subject'		    	:  	self.subject,
				'keywords'		    	:  	self.keywords,
				'description'	    	:  	self.description,
				'location'		    	:  	self.location,
				'city'			    	:  	self.city,
				'province-state'    	:  	self.provincestate,
				'country'		    	:  	self.country,
				'instructions'	    	:   self.instructions,
				'title'			    	:   self.title,
				'creatortool'	    	:   self.creator_tool,
				'creator'		    	:   self.creator,
				'author'		    	:   self.author,
				'credit'		    	:   self.credit,
				'headline'		    	:   self.headline,
				'album'			    	:	self.album,
				'documentname'			:	self.documentname,
				'copyright'				:   'yes' if self.copyright == 1 else 'no' if self.copyright == 0 else 'unknown',
				}
				
				if self.document:
					cmdDict['ManagedFromFilePath'] = self.document.path
		
				m.exifWriteAll(cmdDict, path)
				
			else:
				logging.info("Caller was %s so no models.Metadata super save()" % caller)
		
		
		finally:
			del caller

	
	class Meta:
		verbose_name_plural = "Image Metadata"

class Favorite(models.Model):
	"""User table for favorites admin."""
	image = models.ForeignKey(Image)
	user = models.CharField(max_length=255)
	image_LNID = models.CharField(max_length=255)
	album_name = models.CharField(max_length=255, blank=True)
	album_identifier = models.CharField(max_length=255, blank=True)
	tag = models.CharField(max_length=255)
	ts = models.DateTimeField(auto_now=True)
	notes = models.TextField(blank=True)
	
	def __unicode__(self):
		return self.user

class KeywordCount(models.Model):
	""" Filtered list of keywords generated from Keyword by generatekeywords.py."""
	keyword = models.CharField(max_length=255, unique=True)
	count = models.IntegerField(null=True)
	ts = models.DateTimeField(auto_now=True)
	notes = models.TextField(blank=True)
	
	def __unicode__(self):
		return self.keyword
	
	
class Author(models.Model):
	"""Unused (for the moment)"""
	image = models.ForeignKey(Image)
	author = models.CharField(max_length=255)
	ts = models.DateTimeField(auto_now=True)
	notes = models.TextField()
	
class ImageCount(models.Model):
	"""Represents the last EAM filename system number.
	Is retrieved and updated by fix.py"""
	count = models.IntegerField(default=0)


class User(models.Model):
	user = models.IntegerField(default=0)
	search = models.CharField(max_length=255, default='simple')
	pagesize = models.IntegerField(default=8)
	order = models.NullBooleanField()
	setting1 = models.NullBooleanField(help_text='Used to toggle the album view preference. Choose YES to view content as albums', verbose_name='View')
	setting2 = models.NullBooleanField(help_text='Used for Internet Explorer 6 settings. Choose NO to redirect to help page', verbose_name='Internet Explorer 6')
	setting3 = models.NullBooleanField()
	setting4 = models.NullBooleanField()
	setting5 = models.NullBooleanField()
	setting6 = models.BooleanField(help_text='Used for help text page', verbose_name='help page')
	setting7 = models.BooleanField()
	setting8 = models.BooleanField()
	setting9 = models.BooleanField()
	setting10 = models.BooleanField()
	setstr1 = models.CharField(max_length=255,blank=True)
	setstr2 = models.CharField(max_length=255,blank=True)
	setstr3 = models.CharField(max_length=255,blank=True)
	setstr4 = models.CharField(max_length=255,blank=True)
	setstr5 = models.CharField(max_length=255,blank=True)
	ts = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		try:
			u = _u.objects.get(id=self.user)
			username = u.username
		except:
			username = self.user
		return 'Settings for user %s' % username
		
	class Meta:
		verbose_name = "User settings"
		verbose_name_plural = "User settings"	

class Contract(models.Model):
	user = models.IntegerField(default=0)
	contract = models.IntegerField(default=0)
	username = models.CharField(max_length=255)
	
	def __unicode__(self):
		return self.username
		
	
class Query(models.Model):
	user = models.IntegerField(default=0)
	mode = models.CharField(max_length=50)		
	query = models.CharField(max_length=255)
	ts = models.DateTimeField(auto_now=True)
	
	def __unicode__(self): return self.query
	
	class Meta:
		verbose_name = "Search Query"
		verbose_name_plural = "Search Queries"