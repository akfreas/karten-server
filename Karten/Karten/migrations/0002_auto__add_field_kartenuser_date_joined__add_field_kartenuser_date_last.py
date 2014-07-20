# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'KartenUser.date_joined'
        db.add_column(u'Karten_kartenuser', 'date_joined',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 7, 20, 0, 0)),
                      keep_default=False)

        # Adding field 'KartenUser.date_last_seen'
        db.add_column(u'Karten_kartenuser', 'date_last_seen',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 7, 20, 0, 0)),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'KartenUser.date_joined'
        db.delete_column(u'Karten_kartenuser', 'date_joined')

        # Deleting field 'KartenUser.date_last_seen'
        db.delete_column(u'Karten_kartenuser', 'date_last_seen')


    models = {
        u'Karten.kartencouchserver': {
            'Meta': {'object_name': 'KartenCouchServer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'server_url': ('django.db.models.fields.URLField', [], {'max_length': '255'})
        },
        u'Karten.kartenstack': {
            'Meta': {'object_name': 'KartenStack'},
            'allowed_users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'stacks'", 'symmetrical': 'False', 'to': u"orm['Karten.KartenUser']"}),
            'couchdb_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'couchdb_server': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stacks'", 'to': u"orm['Karten.KartenCouchServer']"}),
            'creation_date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admin_of'", 'null': 'True', 'to': u"orm['Karten.KartenUser']"})
        },
        u'Karten.kartenuser': {
            'Meta': {'object_name': 'KartenUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {}),
            'date_last_seen': ('django.db.models.fields.DateTimeField', [], {}),
            'external_service': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'external_user_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'friends': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['Karten.KartenUser']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['Karten']