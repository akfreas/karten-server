# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'KartenUser'
        db.create_table(u'Karten_kartenuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'Karten', ['KartenUser'])

        # Adding M2M table for field friends on 'KartenUser'
        m2m_table_name = db.shorten_name(u'Karten_kartenuser_friends')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_kartenuser', models.ForeignKey(orm[u'Karten.kartenuser'], null=False)),
            ('to_kartenuser', models.ForeignKey(orm[u'Karten.kartenuser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_kartenuser_id', 'to_kartenuser_id'])

        # Adding model 'KartenCouchDB'
        db.create_table(u'Karten_kartencouchdb', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('couchdb_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('admin', self.gf('django.db.models.fields.related.ForeignKey')(related_name='admin_of', null=True, to=orm['Karten.KartenUser'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('allowed_users', self.gf('django.db.models.fields.related.ForeignKey')(related_name='databases', null=True, to=orm['Karten.KartenUser'])),
        ))
        db.send_create_signal(u'Karten', ['KartenCouchDB'])


    def backwards(self, orm):
        # Deleting model 'KartenUser'
        db.delete_table(u'Karten_kartenuser')

        # Removing M2M table for field friends on 'KartenUser'
        db.delete_table(db.shorten_name(u'Karten_kartenuser_friends'))

        # Deleting model 'KartenCouchDB'
        db.delete_table(u'Karten_kartencouchdb')


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
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'friends': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['Karten.KartenUser']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['Karten']