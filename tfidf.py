#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import cPickle as pickle
from utils import *

from django.core.management import setup_environ
from raplyrics import settings
setup_environ(settings)

from ohhla.models import *

VOCAB_FILE = 'vocab'
if not os.path.exists(VOCAB_FILE):
    vocab = Vocab()
    for song in Song.objects.exclude(artist__place=None).exclude(album__date=None):
        vocab.add_doc(song.filename, get_cleaned_words(song.content))
    with file(VOCAB_FILE, 'w') as f:
        pickle.dump(vocab, f)
else:
    with file(VOCAB_FILE) as f:
        vocab = pickle.load(f)

tfidf = vocab.tfidf()
# removed = vocab.remove_hapax(3)
removed = vocab.tfidf_filter(min_df=5)
with codecs.open('stopwords.txt', 'w', encoding='utf-8') as f:
    for word in removed:
        f.write(word + u'\n')
    with codecs.open('stoplists_en.txt', encoding='utf-8') as g:
        for word in [x.strip() for x in g.readlines() if x.strip() != u'']:
            f.write(word + u'\n')

tf = vocab.getall()
words = sorted(((word, value) for word, value in tf.iteritems()), key=lambda x: x[0])
with codecs.open('vocab.txt', 'w', encoding='utf-8') as f:
    for word, value in words:
        f.write(word + u',' + unicode(value) + u'\n')


# tfidf = vocab.tfidf()
# terms = argsort(tfidf)
# with codecs.open('tfidf.csv', 'w', encoding='utf-8') as f:
#     for term in terms:
#         f.write(term + u',' + unicode(tfidf[term]))