# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Song'
        db.create_table(u'ohhla_song', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(related_name='songs', to=orm['ohhla.Artist'])),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('echonest_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tracks', to=orm['ohhla.Album'])),
            ('key', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('mode', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('bpm', self.gf('django.db.models.fields.FloatField')()),
            ('whosampled_id', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('spotify_id', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('sevendigital_id', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'ohhla', ['Song'])

        # Adding model 'Artist'
        db.create_table(u'ohhla_artist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('echonest_id', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('place', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ohhla.Place'], null=True, blank=True)),
            ('familiarity', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('hotness', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'ohhla', ['Artist'])

        # Adding model 'Album'
        db.create_table(u'ohhla_album', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'ohhla', ['Album'])

        # Adding M2M table for field artists on 'Album'
        m2m_table_name = db.shorten_name(u'ohhla_album_artists')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('album', models.ForeignKey(orm[u'ohhla.album'], null=False)),
            ('artist', models.ForeignKey(orm[u'ohhla.artist'], null=False))
        ))
        db.create_unique(m2m_table_name, ['album_id', 'artist_id'])

        # Adding model 'Place'
        db.create_table(u'ohhla_place', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'ohhla', ['Place'])


    def backwards(self, orm):
        # Deleting model 'Song'
        db.delete_table(u'ohhla_song')

        # Deleting model 'Artist'
        db.delete_table(u'ohhla_artist')

        # Deleting model 'Album'
        db.delete_table(u'ohhla_album')

        # Removing M2M table for field artists on 'Album'
        db.delete_table(db.shorten_name(u'ohhla_album_artists'))

        # Deleting model 'Place'
        db.delete_table(u'ohhla_place')


    models = {
        u'ohhla.album': {
            'Meta': {'object_name': 'Album'},
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'albums'", 'symmetrical': 'False', 'to': u"orm['ohhla.Artist']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
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
            'whosampled_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['ohhla']