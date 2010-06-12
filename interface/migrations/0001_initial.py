# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Image'
        db.create_table('interface_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image_LNID', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
            ('image_path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('image_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('image_real_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('image_real_path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('date_entered', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('image_category', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('image_pages', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('group_status', self.gf('django.db.models.fields.CharField')(max_length=8, blank=True)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('interface', ['Image'])

        # Adding model 'Category'
        db.create_table('interface_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['interface.Image'])),
            ('image_LNID', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('image_cat', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('interface', ['Category'])

        # Adding model 'Group'
        db.create_table('interface_group', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image_LNID', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
            ('image_group', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('image_pages', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('interface', ['Group'])

        # Adding model 'AlbumClass'
        db.create_table('interface_albumclass', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('interface', ['AlbumClass'])

        # Adding model 'Album'
        db.create_table('interface_album', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('album_identifier', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
            ('album_name', self.gf('django.db.models.fields.CharField')(default='untitled album', max_length=255)),
            ('album_pages', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('document', self.gf('django.db.models.fields.files.FileField')(max_length=255, blank=True)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('interface', ['Album'])

        # Adding M2M table for field image on 'Album'
        db.create_table('interface_album_image', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('album', models.ForeignKey(orm['interface.album'], null=False)),
            ('image', models.ForeignKey(orm['interface.image'], null=False))
        ))
        db.create_unique('interface_album_image', ['album_id', 'image_id'])

        # Adding model 'MDAll'
        db.create_table('interface_mdall', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['interface.Image'])),
            ('image_LNID', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('MDall', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('interface', ['MDAll'])

        # Adding model 'Copyright'
        db.create_table('interface_copyright', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['interface.Image'])),
            ('image_LNID', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('copyright', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('copyright_terms', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('interface', ['Copyright'])

        # Adding model 'Order'
        db.create_table('interface_order', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['interface.Image'])),
            ('image_LNID', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('resolution', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('client', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('clientImage', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
            ('group_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('album_identifier', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(null=True)),
        ))
        db.send_create_signal('interface', ['Order'])

        # Adding model 'Keyword'
        db.create_table('interface_keyword', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['interface.Image'])),
            ('image_LNID', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
            ('image_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('keywords', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cright', self.gf('django.db.models.fields.NullBooleanField')(null=True)),
            ('profile', self.gf('django.db.models.fields.NullBooleanField')(null=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('image_path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('interface', ['Keyword'])

        # Adding model 'Metadata'
        db.create_table('interface_metadata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['interface.Image'])),
            ('keyword', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['interface.Keyword'])),
            ('image_LNID', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
            ('file_type', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('caption_writer', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('keywords', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('provincestate', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('instructions', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('creator_tool', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('creator', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('credit', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('datetimeoriginal', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('orientation', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('softdate', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('copyright', self.gf('django.db.models.fields.NullBooleanField')(null=True)),
            ('profile', self.gf('django.db.models.fields.NullBooleanField')(null=True)),
            ('headline', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('album', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('documentname', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('document', self.gf('django.db.models.fields.files.FileField')(max_length=255, blank=True)),
            ('MDall', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('interface', ['Metadata'])

        # Adding model 'Favorite'
        db.create_table('interface_favorite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['interface.Image'])),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('image_LNID', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('album_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('album_identifier', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('interface', ['Favorite'])

        # Adding model 'KeywordCount'
        db.create_table('interface_keywordcount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('keyword', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('interface', ['KeywordCount'])

        # Adding model 'Author'
        db.create_table('interface_author', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['interface.Image'])),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('interface', ['Author'])

        # Adding model 'ImageCount'
        db.create_table('interface_imagecount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('interface', ['ImageCount'])

        # Adding model 'User'
        db.create_table('interface_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('search', self.gf('django.db.models.fields.CharField')(default='simple', max_length=255)),
            ('pagesize', self.gf('django.db.models.fields.IntegerField')(default=8)),
            ('order', self.gf('django.db.models.fields.NullBooleanField')(null=True)),
            ('setting1', self.gf('django.db.models.fields.NullBooleanField')(null=True)),
            ('setting2', self.gf('django.db.models.fields.NullBooleanField')(null=True)),
            ('setting3', self.gf('django.db.models.fields.NullBooleanField')(null=True)),
            ('setting4', self.gf('django.db.models.fields.NullBooleanField')(null=True)),
            ('setting5', self.gf('django.db.models.fields.NullBooleanField')(null=True)),
            ('setting6', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('setting7', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('setting8', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('setting9', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('setting10', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('setstr1', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('setstr2', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('setstr3', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('setstr4', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('setstr5', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('interface', ['User'])

        # Adding model 'Contract'
        db.create_table('interface_contract', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('contract', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('interface', ['Contract'])

        # Adding model 'Query'
        db.create_table('interface_query', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('mode', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('query', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('interface', ['Query'])


    def backwards(self, orm):
        
        # Deleting model 'Image'
        db.delete_table('interface_image')

        # Deleting model 'Category'
        db.delete_table('interface_category')

        # Deleting model 'Group'
        db.delete_table('interface_group')

        # Deleting model 'AlbumClass'
        db.delete_table('interface_albumclass')

        # Deleting model 'Album'
        db.delete_table('interface_album')

        # Removing M2M table for field image on 'Album'
        db.delete_table('interface_album_image')

        # Deleting model 'MDAll'
        db.delete_table('interface_mdall')

        # Deleting model 'Copyright'
        db.delete_table('interface_copyright')

        # Deleting model 'Order'
        db.delete_table('interface_order')

        # Deleting model 'Keyword'
        db.delete_table('interface_keyword')

        # Deleting model 'Metadata'
        db.delete_table('interface_metadata')

        # Deleting model 'Favorite'
        db.delete_table('interface_favorite')

        # Deleting model 'KeywordCount'
        db.delete_table('interface_keywordcount')

        # Deleting model 'Author'
        db.delete_table('interface_author')

        # Deleting model 'ImageCount'
        db.delete_table('interface_imagecount')

        # Deleting model 'User'
        db.delete_table('interface_user')

        # Deleting model 'Contract'
        db.delete_table('interface_contract')

        # Deleting model 'Query'
        db.delete_table('interface_query')


    models = {
        'interface.album': {
            'Meta': {'object_name': 'Album'},
            'album_identifier': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True'}),
            'album_name': ('django.db.models.fields.CharField', [], {'default': "'untitled album'", 'max_length': '255'}),
            'album_pages': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'document': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['interface.Image']"}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'interface.albumclass': {
            'Meta': {'object_name': 'AlbumClass'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'interface.author': {
            'Meta': {'object_name': 'Author'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['interface.Image']"}),
            'notes': ('django.db.models.fields.TextField', [], {}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'interface.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['interface.Image']"}),
            'image_LNID': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'image_cat': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'interface.contract': {
            'Meta': {'object_name': 'Contract'},
            'contract': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'interface.copyright': {
            'Meta': {'object_name': 'Copyright'},
            'copyright': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'copyright_terms': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['interface.Image']"}),
            'image_LNID': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'interface.favorite': {
            'Meta': {'object_name': 'Favorite'},
            'album_identifier': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'album_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['interface.Image']"}),
            'image_LNID': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'interface.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_LNID': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True'}),
            'image_group': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'image_pages': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'interface.image': {
            'Meta': {'object_name': 'Image'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_entered': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'group_status': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_LNID': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True'}),
            'image_category': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'image_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'image_pages': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'image_path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'image_real_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'image_real_path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'interface.imagecount': {
            'Meta': {'object_name': 'ImageCount'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'interface.keyword': {
            'Meta': {'object_name': 'Keyword'},
            'cright': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['interface.Image']"}),
            'image_LNID': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True'}),
            'image_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'image_path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'profile': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'interface.keywordcount': {
            'Meta': {'object_name': 'KeywordCount'},
            'count': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'interface.mdall': {
            'MDall': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'Meta': {'object_name': 'MDAll'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['interface.Image']"}),
            'image_LNID': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'interface.metadata': {
            'MDall': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'Meta': {'object_name': 'Metadata'},
            'album': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'caption_writer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'copyright': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'creator': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'creator_tool': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'credit': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'datetimeoriginal': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'document': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'blank': 'True'}),
            'documentname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'file_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['interface.Image']"}),
            'image_LNID': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True'}),
            'instructions': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'keyword': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['interface.Keyword']"}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'orientation': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'profile': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'provincestate': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'softdate': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'interface.order': {
            'Meta': {'object_name': 'Order'},
            'album_identifier': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'client': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'clientImage': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True'}),
            'group_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['interface.Image']"}),
            'image_LNID': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'resolution': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'interface.query': {
            'Meta': {'object_name': 'Query'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'query': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'interface.user': {
            'Meta': {'object_name': 'User'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'pagesize': ('django.db.models.fields.IntegerField', [], {'default': '8'}),
            'search': ('django.db.models.fields.CharField', [], {'default': "'simple'", 'max_length': '255'}),
            'setstr1': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'setstr2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'setstr3': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'setstr4': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'setstr5': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'setting1': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'setting10': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'setting2': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'setting3': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'setting4': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'setting5': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'setting6': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'setting7': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'setting8': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'setting9': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['interface']
