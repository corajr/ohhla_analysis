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
        vocab.add_doc(song.filename, clean_text(song.content).split(u' '))
    with file(VOCAB_FILE, 'w') as f:
        pickle.dump(vocab, f)
else:
    with file(VOCAB_FILE) as f:
        vocab = pickle.load(f)

tfidf = vocab.tfidf()
<<<<<<< HEAD
# removed = vocab.remove_hapax(3)
removed = vocab.tfidf_filter()
with codecs.open('stopwords.txt', 'w', encoding='utf-8') as f:
    for word in removed:
        f.write(word + u'\n')
    with codecs.open('stoplists_en.txt', encoding='utf-8') as g:
        for word in [x.strip() for x in g.readlines() if x.strip() != u'']:
            f.write(word + u'\n')
=======
removed = vocab.remove_hapax()
removed.update(vocab.tfidf_filter())
with codecs.open('stopwords.txt', 'w', encoding='utf-8') as f:
    for word in removed:
        f.write(word + u'\n')
>>>>>>> 6e82b0c9e29ac53f971598f0f0c0ed125b640792

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