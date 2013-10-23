#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import re
import subprocess
import codecs
import csv
import json
from datetime import date

from django.core.management import setup_environ
from raplyrics import settings
setup_environ(settings)

from django.db.models import Avg, Max, Min
from ohhla.models import *
from utils import *

MALLET_OUT_DIR = 'lda'
TEXTS_FILE = os.path.join(MALLET_OUT_DIR, 'texts.txt')
DMAP_FILE = os.path.join(MALLET_OUT_DIR, 'dmap.txt')
METADATA_CSV = os.path.join(MALLET_OUT_DIR, 'metadata.csv')
INSTANCES_FILE = os.path.join(MALLET_OUT_DIR, 'instances.mallet')
PROGRESS_FILE = os.path.join(MALLET_OUT_DIR, 'progress.txt')
METADATA_FILE = os.path.join(MALLET_OUT_DIR, 'metadata.json')

metadata = {}
TOPICS = 50
MALLET = ['/Users/chrisjr/Applications/mallet-2.0.7/bin/mallet', 'run']

if not os.path.exists(MALLET_OUT_DIR):
    os.makedirs(MALLET_OUT_DIR)

metadata = {}
with file(METADATA_CSV, 'wb') as csv_file:
    writer = UnicodeCsvWriter(csv_file)
    writer.writerow(["doc", "year", "lon", "lat", "place", "artist", "typist"])
    with codecs.open(TEXTS_FILE, 'w', encoding='utf-8') as texts_file:
        with codecs.open(DMAP_FILE, 'w', encoding='utf-8') as dmap:
            for i, song in \
                enumerate(Song.objects.exclude(artist__place=None).exclude(album__date=None)):
                text = clean_text(song.content)

                texts_file.write(u'\t'.join([song.filename, 'ohhla', text]) + u'\n')
                dmap.write(song.filename + u'\n')
                song_metadata = {'itemID': song.id, 'title': unicode(song), 'date': song.album.date.isoformat()}
                place = song.artist.place
                typist = song.typist.email if song.typist is not None else u'unknown'
                artist = song.artist.name
                writer.writerow([unicode(x) for x in [i, song_metadata['date'][0:4], place.longitude, place.latitude, place.name, artist, typist]])
                metadata[song.filename] = song_metadata

with file(METADATA_FILE, 'w') as f:
    json.dump(metadata, f)


import_args = MALLET + [
    'cc.mallet.classify.tui.Csv2Vectors',
    '--encoding',
    'UTF-8',
    '--token-regex',
    "[\p{L}\p{M}]+",
    '--input',
    TEXTS_FILE,
    '--output',
    INSTANCES_FILE,
    '--line-regex',
    '^([^\\t]*)\\t([^\\t]*)\\t(.*)$',
    '--keep-sequence'
    ]

import_return = subprocess.call(import_args)

mallet_opts = {
    'input': INSTANCES_FILE,
    'num-topics': TOPICS,
    'num-iterations': 1000,
    'optimize-interval': 10,
    'optimize-burn-in': 200,
    'use-symmetric-alpha': 'false',
    'alpha': 50.0,
    'beta': 0.01,
    'output-state': os.path.join(MALLET_OUT_DIR, 'topic-state.gz'),
    'output-doc-topics': os.path.join(MALLET_OUT_DIR, 'doc-topics.txt'
            ),
    'output-topic-keys': os.path.join(MALLET_OUT_DIR, 'topic-keys.txt'
            ),
    'word-topic-counts-file': os.path.join(MALLET_OUT_DIR,
            'word-topics.txt'),
    'diagnostics-file': os.path.join(MALLET_OUT_DIR,
            'diagnostics-file.txt'),
    'xml-topic-phrase-report': os.path.join(MALLET_OUT_DIR,
            'topic-phrases.xml'),
    }

process_args = MALLET + ['cc.mallet.topics.tui.TopicTrainer']
for (k, v) in mallet_opts.iteritems():
    process_args.append(u'--' + k)
    process_args.append(unicode(v))

with codecs.open(PROGRESS_FILE, 'w', encoding='utf-8') as progress_file:
    lda_return = subprocess.call(process_args, stdout=progress_file, stderr=progress_file)
