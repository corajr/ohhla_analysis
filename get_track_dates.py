#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shelve
import spotimeta
from datetime import date
from utils import *

from contextlib import closing

@RateLimited(5)
def get_date_from_spotify(spotimetadata, song):
    track_id = song.spotify_id.replace('spotify-WW', 'spotify')
    song_data = spotimetadata.lookup(track_id)
    if song_data is not None:
        album_id = song_data['result']['album']['href']
        song.album.spotify_id = album_id
        song.album.save()
        album_data = spotimetadata.lookup(album_id)
        if album_data is not None:
            if 'released' in album_data['result']:
                song.album.date = date(album_data['result']['released'],1,1)
                song.album.save()

if __name__ == '__main__':
    from django.core.management import setup_environ
    from raplyrics import settings
    setup_environ(settings)

    from ohhla.models import *

    with closing(shelve.open('spotifycache')) as spotifycache:
        spotimetadata = spotimeta.Metadata(cache=spotifycache)

        for song in Song.objects.exclude(spotify_id = None).filter(pk__gt=806):
            if song.album.date is None:
                print song.id
                get_date_from_spotify(spotimetadata, song)
