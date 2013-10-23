from django.db import models

class Song(models.Model):
    KEYS = tuple(enumerate(('C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B')))
    MODES = tuple(enumerate(['minor', 'major']))
    title = models.CharField(max_length=256)
    artist = models.ForeignKey('Artist', related_name='songs')
    filename = models.CharField(max_length=256)
    typist = models.ForeignKey('Typist', blank=True, null=True)
    echonest_id = models.CharField(max_length=32)
    album = models.ForeignKey('Album', related_name='tracks')
    key = models.SmallIntegerField(choices=KEYS)
    mode = models.SmallIntegerField(choices=MODES)
    bpm = models.FloatField()
    whosampled_id = models.CharField(max_length=64, blank=True, null=True)
    spotify_id = models.CharField(max_length=64, blank=True, null=True)
    sevendigital_id = models.CharField(max_length=64, blank=True, null=True)
    content = models.TextField()

    def __unicode__(self):
        return self.artist.name + u' - ' + self.title

class Artist(models.Model):
    name = models.CharField(max_length=256)
    echonest_id = models.CharField(max_length=256)
    place = models.ForeignKey('Place', blank=True, null=True)
    familiarity = models.FloatField(blank=True, null=True)
    hotness = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        return self.name

class Typist(models.Model):
    email = models.CharField(max_length=256)

    def __unicode__(self):
        return self.email

class Album(models.Model):
    name = models.CharField(max_length=256)
    date = models.DateField(blank=True, null=True)
    spotify_id = models.CharField(max_length=64, blank=True, null=True)
    artists = models.ManyToManyField(Artist, related_name='albums')

    def __unicode__(self):
        return self.name


class Place(models.Model):
    name = models.CharField(max_length=256)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __unicode__(self):
        return self.name