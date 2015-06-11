#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import csv
import subprocess
import codecs
import json
import math
from datetime import date

from django.core.management import setup_environ
from raplyrics import settings
setup_environ(settings)

from django.db.models import Avg, Max, Min
from ohhla.models import *

from utils import *

TEXTS_FILE = "texts.txt"
DMAP_FILE = "dmap.txt"
METADATA_CSV = 'metadata.csv'
METADATA_FILE = 'metadata.json'
FEATURES_FILE = "features.txt"
INSTANCES_FILE = "instances.mallet"
PROGRESS_FILE = "progress.txt"
TOPICS = 100
MALLET = ["/Users/chrisjr/Applications/mallet-2.0.7/bin/mallet", "run"]

date_extremes = Album.objects.aggregate(Min('date'), Max('date'))
year_min = date_extremes['date__min'].year
year_max = date_extremes['date__max'].year

bpm_extremes = Song.objects.aggregate(Min('bpm'), Max('bpm'))
bpm_min = bpm_extremes['bpm__min']
bpm_max = bpm_extremes['bpm__max']

def song_to_feature_string(song, features_used=('pd=', 'oneminuspd=','location', 'artist')):
    features = {}
    p = (song.album.date.year - year_min) / float(year_max - year_min)
    smooth = 0.01
    if p == 0.0:
        p += smooth
    elif p == 1.0:
        p -= smooth
    features[u'pd='] = math.log(p)
    features[u'oneminuspd='] = math.log(1.0-p)
    features[u'bpm='] = (song.bpm - bpm_min) / float(bpm_max - bpm_min)
    features[u'location'] = song.artist.place.id
    features[u'artist'] = song.artist.id
    return u' '.join([k + unicode(v) for k, v in features.iteritems() if k in features_used])

if not os.path.exists("dmr"):
    os.makedirs("dmr")
os.chdir("dmr")

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

import_args = MALLET + ["cc.mallet.topics.tui.DMRLoader", TEXTS_FILE, FEATURES_FILE, INSTANCES_FILE]
import_return = subprocess.call(import_args)

process_args = MALLET + ["cc.mallet.topics.DMRTopicModel", INSTANCES_FILE, str(TOPICS)]

with codecs.open(PROGRESS_FILE, 'w', encoding='utf-8') as progress_file:
    dmr_return = subprocess.call(process_args, stdout=progress_file)
