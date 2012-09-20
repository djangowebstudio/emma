# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'Order', fields ['clientImage']
        db.delete_unique('interface_order', ['clientImage'])

        # Changing field 'User.setting4'
        db.alter_column('interface_user', 'setting4', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True))

        # Changing field 'User.setting5'
        db.alter_column('interface_user', 'setting5', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True))

        # Changing field 'User.setting1'
        db.alter_column('interface_user', 'setting1', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True))

        # Changing field 'User.setting2'
        db.alter_column('interface_user', 'setting2', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True))

        # Changing field 'User.setting3'
        db.alter_column('interface_user', 'setting3', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True))

        # Changing field 'User.order'
        db.alter_column('interface_user', 'order', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True))

        # Changing field 'Metadata.copyright'
        db.alter_column('interface_metadata', 'copyright', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True))

        # Changing field 'Metadata.profile'
        db.alter_column('interface_metadata', 'profile', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True))

        # Changing field 'Keyword.profile'
        db.alter_column('interface_keyword', 'profile', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True))

        # Changing field 'Keyword.cright'
        db.alter_column('interface_keyword', 'cright', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True))


    def backwards(self, orm):
        
        # Adding unique constraint on 'Order', fields ['clientImage']
        db.create_unique('interface_order', ['clientImage'])

        # Changing field 'User.setting4'
        db.alter_column('interface_user', 'setting4', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'User.setting5'
        db.alter_column('interface_user', 'setting5', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'User.setting1'
        db.alter_column('interface_user', 'setting1', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'User.setting2'
        db.alter_column('interface_user', 'setting2', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'User.setting3'
        db.alter_column('interface_user', 'setting3', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'User.order'
        db.alter_column('interface_user', 'order', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Metadata.copyright'
        db.alter_column('interface_metadata', 'copyright', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Metadata.profile'
        db.alter_column('interface_metadata', 'profile', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Keyword.profile'
        db.alter_column('interface_keyword', 'profile', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Keyword.cright'
        db.alter_column('interface_keyword', 'cright', self.gf('django.db.models.fields.NullBooleanField')(null=True))


    models = {
        'interface.album': {
            'Meta': {'object_name': 'Album'},
            'album_identifier': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'album_name': ('django.db.models.fields.CharField', [], {'default': "'untitled album'", 'max_length': '255'}),
            'album_pages': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'document': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['interface.Image']", 'symmetrical': 'False'}),
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
            'date_signed': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
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
            'image_LNID': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
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
            'image_LNID': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
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
            'cright': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['interface.Image']"}),
            'image_LNID': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'image_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'image_path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'profile': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'interface.keywordcount': {
            'Meta': {'object_name': 'KeywordCount'},
            'count': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
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
            'copyright': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
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
            'image_LNID': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'instructions': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'keyword': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['interface.Keyword']"}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'orientation': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'profile': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
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
            'clientImage': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'group_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['interface.Image']"}),
            'image_LNID': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['interface.Project']", 'null': 'True', 'blank': 'True'}),
            'resolution': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'interface.project': {
            'Meta': {'object_name': 'Project'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '50', 'db_index': 'True'}),
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
            'current_project': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['interface.Project']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'pagesize': ('django.db.models.fields.IntegerField', [], {'default': '8'}),
            'search': ('django.db.models.fields.CharField', [], {'default': "'simple'", 'max_length': '255'}),
            'setstr1': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'setstr2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'setstr3': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'setstr4': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'setstr5': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'setting1': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'setting10': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'setting2': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'setting3': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'setting4': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'setting5': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'setting6': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'setting7': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'setting8': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'setting9': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['interface']
