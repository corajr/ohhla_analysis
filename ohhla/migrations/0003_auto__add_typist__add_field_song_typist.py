# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Typist'
        db.create_table(u'ohhla_typist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'ohhla', ['Typist'])

        # Adding field 'Song.typist'
        db.add_column(u'ohhla_song', 'typist',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ohhla.Typist'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Typist'
        db.delete_table(u'ohhla_typist')

        # Deleting field 'Song.typist'
        db.delete_column(u'ohhla_song', 'typist_id')


    models = {
        u'ohhla.album': {
            'Meta': {'object_name': 'Album'},
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'albums'", 'symmetrical': 'False', 'to': u"orm['ohhla.Artist']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'spotify_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        u'ohhla.artist': {
            'Meta': {'object_name': 'Artist'},
            'echonest_id': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'familiarity': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'hotness': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ohhla.Place']", 'null': 'True', 'blank': 'True'})
        },
        u'ohhla.place': {
            'Meta': {'object_name': 'Place'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'ohhla.song': {
            'Meta': {'object_name': 'Song'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tracks'", 'to': u"orm['ohhla.Album']"}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'songs'", 'to': u"orm['ohhla.Artist']"}),
            'bpm': ('django.db.models.fields.FloatField', [], {}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'echonest_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SmallIntegerField', [], {}),
            'mode': ('django.db.models.fields.SmallIntegerField', [], {}),
            'sevendigital_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'spotify_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'typist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ohhla.Typist']", 'null': 'True', 'blank': 'True'}),
            'whosampled_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        u'ohhla.typist': {
            'Meta': {'object_name': 'Typist'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['ohhla']