# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ModpackCache.description'
        db.add_column('api_modpackcache', 'description',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)


        # Changing field 'ModpackCache.url'
        db.alter_column('api_modpackcache', 'url', self.gf('django.db.models.fields.CharField')(max_length=255))

    def backwards(self, orm):
        # Deleting field 'ModpackCache.description'
        db.delete_column('api_modpackcache', 'description')


        # Changing field 'ModpackCache.url'
        db.alter_column('api_modpackcache', 'url', self.gf('django.db.models.fields.URLField')(max_length=200))

    models = {
        'api.apikey': {
            'Meta': {'object_name': 'ApiKey'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'api.modcache': {
            'Meta': {'object_name': 'ModCache'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'localpath': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'md5': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'modInfo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api.ModInfoCache']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'api.modinfocache': {
            'Meta': {'object_name': 'ModInfoCache'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pretty_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'api.modpackcache': {
            'Meta': {'object_name': 'ModpackCache'},
            'background_md5': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'icon_md5': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo_md5': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'api.versioncache': {
            'Meta': {'object_name': 'VersionCache'},
            'forgever': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest': ('django.db.models.fields.BooleanField', [], {}),
            'mcversion': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'mcversion_checksum': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'modpack': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api.ModpackCache']"}),
            'mods': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['api.ModCache']", 'symmetrical': 'False'}),
            'recommended': ('django.db.models.fields.BooleanField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['api']