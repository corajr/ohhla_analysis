#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import subprocess
import codecs
from datetime import date

from django.core.management import setup_environ
from raplyrics import settings
setup_environ(settings)

from django.db.models import Avg, Max, Min
from ohhla.models import *

from utils import *

TEXTS_FILE = "texts.txt"
DMAP_FILE = "dmap.txt"
FEATURES_FILE = "features.txt"
INSTANCES_FILE = "instances.mallet"
PROGRESS_FILE = "progress.txt"
TOPICS = 50
MALLET = ["/Users/chrisjr/Applications/mallet-2.0.7/bin/mallet", "run"]


if STOPLIST:
    with codecs.open(STOPLIST, 'r', encoding='utf-8') as f:
        stopwords = set([x.strip().lower() for x in f.readlines()])
else:
    stopwords = set()

date_extremes = Album.objects.aggregate(Min('date'), Max('date'))
year_min = date_extremes['date__min'].year
year_max = date_extremes['date__max'].year

bpm_extremes = Song.objects.aggregate(Min('bpm'), Max('bpm'))
bpm_min = bpm_extremes['bpm__min']
bpm_max = bpm_extremes['bpm__max']

def song_to_feature_string(song, features_used=('year=','bpm=','location')):
    features = {}
    features[u'year='] = (song.album.date.year - year_min) / float(year_max - year_min)
    features[u'bpm='] = (song.bpm - bpm_min) / float(bpm_max - bpm_min)
    features[u'location'] = song.artist.place.id
    return u' '.join([k + unicode(v) for k, v in features.iteritems() if k in features_used])

if not os.path.exists("dmr"):
    os.makedirs("dmr")
os.chdir("dmr")

with codecs.open(TEXTS_FILE, 'w', encoding='utf-8') as texts_file:
    with codecs.open(FEATURES_FILE, 'w', encoding='utf-8') as features_file:
        with codecs.open(DMAP_FILE, 'w', encoding='utf-8') as dmap:
            for song in Song.objects.exclude(artist__place = None).exclude(album__date = None):
                text = clean_text(song.content)

                texts_file.write(text + u'\n')
                features_file.write(song_to_feature_string(song) + u'\n')
                dmap.write(song.filename + u'\n')

import_args = MALLET + ["cc.mallet.topics.tui.DMRLoader", TEXTS_FILE, FEATURES_FILE, INSTANCES_FILE]
import_return = subprocess.call(import_args)

process_args = MALLET + ["cc.mallet.topics.DMRTopicModel", INSTANCES_FILE, str(TOPICS)]

with codecs.open(PROGRESS_FILE, 'w', encoding='utf-8') as progress_file:
    dmr_return = subprocess.call(process_args, stdout=progress_file)
