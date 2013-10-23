#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
<<<<<<< HEAD
import csv
import subprocess
import codecs
import json
=======
import subprocess
import codecs
>>>>>>> 6e82b0c9e29ac53f971598f0f0c0ed125b640792
from datetime import date

from django.core.management import setup_environ
from raplyrics import settings
setup_environ(settings)

from django.db.models import Avg, Max, Min
from ohhla.models import *

from utils import *

TEXTS_FILE = "texts.txt"
DMAP_FILE = "dmap.txt"
<<<<<<< HEAD
METADATA_CSV = 'metadata.csv'
METADATA_FILE = 'metadata.json'
=======
>>>>>>> 6e82b0c9e29ac53f971598f0f0c0ed125b640792
FEATURES_FILE = "features.txt"
INSTANCES_FILE = "instances.mallet"
PROGRESS_FILE = "progress.txt"
TOPICS = 50
MALLET = ["/Users/chrisjr/Applications/mallet-2.0.7/bin/mallet", "run"]

<<<<<<< HEAD
=======

if STOPLIST:
    with codecs.open(STOPLIST, 'r', encoding='utf-8') as f:
        stopwords = set([x.strip().lower() for x in f.readlines()])
else:
    stopwords = set()

>>>>>>> 6e82b0c9e29ac53f971598f0f0c0ed125b640792
date_extremes = Album.objects.aggregate(Min('date'), Max('date'))
year_min = date_extremes['date__min'].year
year_max = date_extremes['date__max'].year

bpm_extremes = Song.objects.aggregate(Min('bpm'), Max('bpm'))
bpm_min = bpm_extremes['bpm__min']
bpm_max = bpm_extremes['bpm__max']

<<<<<<< HEAD
def song_to_feature_string(song, features_used=('year=','location', 'artist')):
=======
def song_to_feature_string(song, features_used=('year=','bpm=','location')):
>>>>>>> 6e82b0c9e29ac53f971598f0f0c0ed125b640792
    features = {}
    features[u'year='] = (song.album.date.year - year_min) / float(year_max - year_min)
    features[u'bpm='] = (song.bpm - bpm_min) / float(bpm_max - bpm_min)
    features[u'location'] = song.artist.place.id
<<<<<<< HEAD
    features[u'artist'] = song.artist.id
=======
>>>>>>> 6e82b0c9e29ac53f971598f0f0c0ed125b640792
    return u' '.join([k + unicode(v) for k, v in features.iteritems() if k in features_used])

if not os.path.exists("dmr"):
    os.makedirs("dmr")
os.chdir("dmr")

<<<<<<< HEAD
metadata = {}
with file(METADATA_CSV, 'wb') as csv_file:
    writer = UnicodeCsvWriter(csv_file)
    writer.writerow(["doc", "year", "lon", "lat", "place", "artist", "typist"])
    with codecs.open(TEXTS_FILE, 'w', encoding='utf-8') as texts_file:
        with codecs.open(FEATURES_FILE, 'w', encoding='utf-8') as features_file:
            with codecs.open(DMAP_FILE, 'w', encoding='utf-8') as dmap:
                for i, song in enumerate(Song.objects.exclude(artist__place = None).exclude(album__date = None)):
                    text = clean_text(song.content)

                    texts_file.write(text + u'\n')
                    song_metadata = {'itemID': song.id, 'title': unicode(song), 'date': song.album.date.isoformat()}
                    place = song.artist.place
                    typist = song.typist.email if song.typist is not None else u'unknown'
                    artist = song.artist.name
                    writer.writerow([unicode(x) for x in [i, song_metadata['date'][0:4], place.longitude, place.latitude, place.name, artist, typist]])
                    metadata[song.filename] = song_metadata
                    features_file.write(song_to_feature_string(song) + u'\n')
                    dmap.write(song.filename + u'\n')

with file(METADATA_FILE, 'w') as f:
    json.dump(metadata, f)
=======
with codecs.open(TEXTS_FILE, 'w', encoding='utf-8') as texts_file:
    with codecs.open(FEATURES_FILE, 'w', encoding='utf-8') as features_file:
        with codecs.open(DMAP_FILE, 'w', encoding='utf-8') as dmap:
            for song in Song.objects.exclude(artist__place = None).exclude(album__date = None):
                text = clean_text(song.content)

                texts_file.write(text + u'\n')
                features_file.write(song_to_feature_string(song) + u'\n')
                dmap.write(song.filename + u'\n')
>>>>>>> 6e82b0c9e29ac53f971598f0f0c0ed125b640792

import_args = MALLET + ["cc.mallet.topics.tui.DMRLoader", TEXTS_FILE, FEATURES_FILE, INSTANCES_FILE]
import_return = subprocess.call(import_args)

process_args = MALLET + ["cc.mallet.topics.DMRTopicModel", INSTANCES_FILE, str(TOPICS)]

with codecs.open(PROGRESS_FILE, 'w', encoding='utf-8') as progress_file:
    dmr_return = subprocess.call(process_args, stdout=progress_file)
