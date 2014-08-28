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
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('email', self.gf('django.db.models.fields.EmailField')(db_index=True, max_length=255, unique=True, null=True, blank=True)),
            ('external_user_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('external_service', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('date_last_seen', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('is_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
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

        # Adding model 'KartenCouchServer'
        db.create_table(u'Karten_kartencouchserver', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('server_url', self.gf('django.db.models.fields.URLField')(max_length=255)),
        ))
        db.send_create_signal(u'Karten', ['KartenCouchServer'])

        # Adding model 'KartenStack'
        db.create_table(u'Karten_kartenstack', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('couchdb_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('couchdb_server', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stacks', to=orm['Karten.KartenCouchServer'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='admin_of', null=True, to=orm['Karten.KartenUser'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'Karten', ['KartenStack'])

        # Adding M2M table for field allowed_users on 'KartenStack'
        m2m_table_name = db.shorten_name(u'Karten_kartenstack_allowed_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('kartenstack', models.ForeignKey(orm[u'Karten.kartenstack'], null=False)),
            ('kartenuser', models.ForeignKey(orm[u'Karten.kartenuser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['kartenstack_id', 'kartenuser_id'])


    def backwards(self, orm):
        # Deleting model 'KartenUser'
        db.delete_table(u'Karten_kartenuser')

        # Removing M2M table for field friends on 'KartenUser'
        db.delete_table(db.shorten_name(u'Karten_kartenuser_friends'))

        # Deleting model 'KartenCouchServer'
        db.delete_table(u'Karten_kartencouchserver')

        # Deleting model 'KartenStack'
        db.delete_table(u'Karten_kartenstack')

        # Removing M2M table for field allowed_users on 'KartenStack'
        db.delete_table(db.shorten_name(u'Karten_kartenstack_allowed_users'))


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
            'Meta': {'ordering': "['username']", 'object_name': 'KartenUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'db_index': 'True', 'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'external_service': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'external_user_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'friends': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['Karten.KartenUser']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        }
    }

    complete_apps = ['Karten']