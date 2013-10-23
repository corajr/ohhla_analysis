<<<<<<< HEAD
#!/usr/bin/env python
=======
>>>>>>> 6e82b0c9e29ac53f971598f0f0c0ed125b640792
import re
import sys
import struct
import json
import os
import gzip
import codecs
import xml.etree.ElementTree as et
import logging
import traceback
import base64
from itertools import izip

from django.core.management import setup_environ
from raplyrics import settings
setup_environ(settings)

from ohhla.models import *

from collections import Counter, defaultdict


logging.basicConfig()


MALLET_OUT_DIR = "lda"
mallet_opts = {
    'num-topics': 50,
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


metadata_filename = os.path.join(MALLET_OUT_DIR, 'metadata.json')
if os.path.exists(metadata_filename):
    with file(metadata_filename) as f:
        metadata = json.load(f)
else:
    metadata = {}
    for song in Song.objects.exclude(artist__place=None).exclude(album__date=None):
        obj = {'itemID': song.id, 'title': unicode(song)}
        obj['date'] = song.album.date.isoformat()
        metadata[song.filename] = obj
    with file(metadata_filename, 'w') as f:
        json.dump(metadata, f)

def format_date(date):
    return date + u'T00:00:00'

def group_by_n(seq, n=2):
    ''' Return seq in chunks of length n (omitting any leftover elements) '''
    return izip(*(iter(seq), ) * n)

coherence = {}
wordProbs = {}
phrases = {}
allocationRatios = {}
with codecs.open(os.path.join(MALLET_OUT_DIR, 'dmap.txt'), 'r', encoding='utf-8') as dmap:
    docs = [x.strip() for x in dmap.readlines()]

with codecs.open(mallet_opts['diagnostics-file'], 'r', 
                 encoding='utf-8', errors='ignore') as diagnostics:
    try:
        tree = et.parse(diagnostics)
        for elem in tree.getiterator("topic"):
            topic = elem.get("id")
            coherence[topic] = float(elem.get("coherence"))
            allocationRatios[topic] = float(
                                        elem.get("allocation_ratio"))
            wordProbs[topic] = []
            for word in elem.getiterator("word"):
                wordProbs[topic].append({'text': word.text, 
                                         'prob': word.get("prob")})
    except:
        logging.error("The diagnostics file could not be parsed!")
        logging.error("The error is reproduced below.")
        logging.error(traceback.format_exc())

with file(mallet_opts['xml-topic-phrase-report'], 'rb') as phrase_file:
    try:
        tree = et.parse(phrase_file)
        for elem in tree.getiterator("topic"):
            topic = elem.get("id")
            titles = elem.get("titles")
            phrases[topic] = titles.split(', ')
    except:
        logging.error("The topic phrase report could not be parsed!")
        logging.error("The error is reproduced below.")
        logging.error(traceback.format_exc())

labels = {x[0]: {"words": wordProbs[x[0]],
                 "allocation_ratio": allocationRatios[x[0]],
                 "phrases": phrases[x[0]]
                } 
          for x in [y.split() for y in 
                    codecs.open(mallet_opts['output-topic-keys'],
                                'r', encoding='utf-8').readlines()
                    ]
        }

<<<<<<< HEAD
topics_fmt = '<' + str(len(wordProbs)) + 'f'
=======
topics_fmt = '<' + str(mallet_opts['num-topics']) + 'f'
>>>>>>> 6e82b0c9e29ac53f971598f0f0c0ed125b640792

doc_topics = {}

for line in codecs.open(mallet_opts['output-doc-topics'], 'r', 
                        encoding='utf-8'):
    try:
        values = line.split('\t')

        docid = values.pop(0)
        if docid.startswith("#doc"):
            continue
        filename = docs[int(docid)]

        itemid = metadata[filename]["itemID"]
        topics = [float(y[1]) for y in sorted(group_by_n(values[1:]), 
                                              key=lambda x: int(x[0]))]
        doc_topics[filename] = topics
        topics_str = base64.b64encode(struct.pack(topics_fmt, *topics))
        metadata[filename]["topics"] = topics_str
    except KeyboardInterrupt, SystemExit:
        sys.exit(1)
    except:
        logging.error(traceback.format_exc())

for filename in docs:
    metadata[filename]['date'] = format_date(metadata[filename]['date'])

top_words = defaultdict(Counter)
doc_words_topics = defaultdict(lambda: defaultdict(Counter))
with gzip.open(mallet_opts['output-state'], 'rb') as f:
    for line in f:
        if line.startswith('#'):
            continue
        parts = line.split(' ')
        docid = parts[0]
        word = parts[4]
        topic = int(parts[5])
        filename = docs[int(docid)]
        top_words[filename][word] += 1
        doc_words_topics[filename][word][topic] += 1

for filename, word_counts in top_words.iteritems():
    my_top_words = []
    for k, v in word_counts.most_common(50):
        my_top_words.append({'text': k, 'topic': doc_words_topics[filename][k].most_common(1)[0][0], 'prob': v})
    metadata[filename]["topWords"] = my_top_words

params = {"TOPIC_LABELS": labels,
          "TOPIC_COHERENCE": coherence,
          'DOC_METADATA': dict((v['itemID'], v)
                           for (k, v) in metadata.iteritems())
}

with file("viz/topics/js/ohhla_lda.js", 'w') as f:
    f.write('var data=')
    f.write(json.dumps(params))
    f.write(';')
