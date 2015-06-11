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
    lda_return = subprocess.call(process_args, stdout=progress_file,
                                 stderr=progress_file)
