from django.contrib import admin
from emma.interface.models import *
from models import *
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin as FlatPageAdminOld

class FlatPageAdmin(FlatPageAdminOld):
    class Media:
        js = ('/s/js/tiny_mce/tiny_mce.js',
              '/s/js/tiny_mce/textareas.js',)

# We have to unregister it, and then reregister
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
	  	
class ImageAdmin(admin.ModelAdmin):
	list_display = ['image_LNID', 'image_category']
	search_fields = ['image_LNID', 'image_category']
	
admin.site.register(Image, ImageAdmin)
	
class OrderAdmin(admin.ModelAdmin):
	list_display = ('image_LNID', 'client', 'project', 'is_published', 'status', 'ts')
	search_fields = ['client']
	
admin.site.register(Order, OrderAdmin)
	
class KeywordAdmin(admin.ModelAdmin):
	list_display = ['image_LNID', 'subject', 'keywords', 'source']
	search_fields = ['image_LNID', 'subject', 'keywords', 'source']

admin.site.register(Keyword, KeywordAdmin)


class MetadataAdmin(admin.ModelAdmin):
	search_fields = ['image_LNID', 'subject', 'album', 'mime_type']
	fieldsets = (
	('About you', {'fields': ('caption_writer',)}),
	('Image information', {
							'classes': ('collapse',),
							'fields': ('subject', 'copyright', 'profile', 'keywords', 'description', 'instructions', 'source', 'location', 'city', 'provincestate', 'country', 'datetimeoriginal')}),
							
	('Attachments', { 'classes': ('collapse',),
						'fields': ('document',)}),
	('Author information', {
							'classes': ('collapse',),
							'fields':('author', 'creator', 'credit')}),
	('Album information', {
							'classes': ('collapse',),
							'fields':('album', 'headline')})
	)
	
	
	list_display = ('thumb','image_LNID','subject','copyright','profile','album', 'headline', 'has_attachment', 'keywords', 'mime_type')
	

admin.site.register(Metadata, MetadataAdmin)

class KeywordCountAdmin(admin.ModelAdmin):
	search_fields = ['keyword']
admin.site.register(KeywordCount, KeywordCountAdmin)
			
class ContractAdmin(admin.ModelAdmin):
	list_display = ('username', 'contract', 'date_signed')
	search_fields = ['username']
		
admin.site.register(Contract, ContractAdmin)
admin.site.register(Favorite)

class AlbumAdmin(admin.ModelAdmin):
	search_fields = ['album_name', 'album_identifier']
	fieldsets = (
	
	('Album information', {
			'fields': ('album_name',)}),
	('Attachments', {
			'fields': ('document', )},),
			
	('Items', {'classes': ('collapse',), 'fields': ('image',)})
	
	)
	
	filter_horizontal = ['image']
	list_display = ('album_name', 'album_identifier', 'document')
	
admin.site.register(Album, AlbumAdmin)
class UserAdmin(admin.ModelAdmin):
    exlude = ['setstr2']
admin.site.register(User, UserAdmin)
admin.site.register(Query)
class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ['name', 'active', 'is_complete',]
admin.site.register(Project, ProjectAdmin)