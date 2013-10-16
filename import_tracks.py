#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Import tracks from OpenRefine output'''

import json
import gzip
import shelve
import time
import spotimeta

from contextlib import closing

from utils import *

from django.core.management import setup_environ
from raplyrics import settings
setup_environ(settings)

from echonest_api_key import *
from pyechonest import song

from get_track_dates import *
from ohhla.models import *

with gzip.open('OHHLA-for-echonest.txt.gz') as f:
    ohhla = json.load(f)

tracks = list(enumerate(ohhla['rows']))

start_at = 29000
end_at = None

with closing(shelve.open('backup')) as backup:
    with closing(shelve.open('spotifycache')) as spotifycache:
        spotimetadata = spotimeta.Metadata(cache=spotifycache)

        @RateLimited(60.0/60.0)
        def process_track(track):
            filename = track['filename']
            artist = track['artist']
            title = track['song']
            if not filename in backup and track.get('album', None) is not None:
                results = song.search(artist=artist, title=title, buckets=['id:whosampled',
                                                                           'id:7digital-US',
                                                                           'id:spotify-WW',
                                                                           'tracks',
                                                                           'audio_summary',
                                                                           'artist_location',
                                                                           'artist_familiarity',
                                                                           'artist_hotttnesss'])
                if len(results) > 0:
                    result = results[0]        
                    backup[filename] = result
                    song_obj = Song()
                    song_obj.title = result.title
                    song_obj.filename = filename
                    artist, new_artist = Artist.objects.get_or_create(echonest_id=result.artist_id,
                                                              defaults= {'name': result.artist_name,
                                                                         'familiarity':result.artist_familiarity,
                                                                         'hotness': result.artist_hotttnesss}
                                                         )
                    song_obj.artist = artist

                    artist_location = result.artist_location
                    lat = artist_location['latitude']
                    lng = artist_location['longitude']
                    place_name = artist_location['location']
                    if lat is not None and lng is not None and place_name is not None and new_artist:
                        artist.place = Place.objects.get_or_create(name=place_name, 
                                                                   defaults={'latitude': lat, 'longitude': lng})[0]
                        artist.save()
                    album = Album.objects.get_or_create(name=track['album'])[0]
                    song_obj.album = album
                    album.artists.add(artist)

                    audio_summary = result.audio_summary        
                    song_obj.key = audio_summary['key']
                    song_obj.mode = audio_summary['mode']
                    song_obj.bpm = audio_summary['tempo']
                    song_obj.echonest_id = result.id
                    song_obj.content = track['lyrics']
                    whosampled = result.get_tracks('whosampled')
                    sevendigital = result.get_tracks('7digital-US')
                    spotify = result.get_tracks('spotify-WW')
                    if len(whosampled) > 0:
                        song_obj.whosampled_id = whosampled[0]['foreign_id']
                    if len(sevendigital) > 0:
                        song_obj.sevendigital_id = sevendigital[0]['foreign_id']
                    if len(spotify) > 0:
                        song_obj.spotify_id = spotify[0]['foreign_id']
                    song_obj.save()
                    if song_obj.spotify_id is not None:
                        get_date_from_spotify(spotimetadata, song_obj)


        for i, track in tracks[start_at:end_at]:
            print i
            process_track(track)