# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'KartenUser.user_id'
        db.delete_column(u'Karten_kartenuser', 'user_id')

        # Adding field 'KartenUser.external_user_id'
        db.add_column(u'Karten_kartenuser', 'external_user_id',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True),
                      keep_default=False)

        # Adding field 'KartenUser.external_service'
        db.add_column(u'Karten_kartenuser', 'external_service',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True),
                      keep_default=False)


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'KartenUser.user_id'
        raise RuntimeError("Cannot reverse this migration. 'KartenUser.user_id' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'KartenUser.user_id'
        db.add_column(u'Karten_kartenuser', 'user_id',
                      self.gf('django.db.models.fields.CharField')(max_length=255),
                      keep_default=False)

        # Deleting field 'KartenUser.external_user_id'
        db.delete_column(u'Karten_kartenuser', 'external_user_id')

        # Deleting field 'KartenUser.external_service'
        db.delete_column(u'Karten_kartenuser', 'external_service')


    models = {
        u'Karten.kartencouchdb': {
            'Meta': {'object_name': 'KartenCouchDB'},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admin_of'", 'null': 'True', 'to': u"orm['Karten.KartenUser']"}),
            'allowed_users': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'databases'", 'null': 'True', 'to': u"orm['Karten.KartenUser']"}),
            'couchdb_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'Karten.kartenuser': {
            'Meta': {'object_name': 'KartenUser'},
            'external_service': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'external_user_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'friends': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['Karten.KartenUser']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['Karten']