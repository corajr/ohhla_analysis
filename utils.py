import time
import re
import math
import codecs
import os
from collections import Counter, defaultdict

# from https://gist.github.com/gregburek/1441055
def RateLimited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rateLimitedFunction(*args,**kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rateLimitedFunction
    return decorate

STOPLIST = 'stopwords.txt'
if STOPLIST is not None and os.path.exists(STOPLIST):
    with codecs.open(STOPLIST, 'r', encoding='utf-8') as f:
        stopwords = set([x.strip().lower() for x in f.readlines()])
else:
    stopwords = set()


def clean_text(text):
    text = re.sub(r"\[[^]]+?\]", u'', text.lower(), flags=re.UNICODE)
    text = re.sub(r"[^\w_]+", u' ', text, flags=re.UNICODE)
    words = text.split(u' ')
    text = u' '.join([x for x in words if x not in stopwords and len(x)
                     > 3])
    return text

def argmax(obj):
    if hasattr(obj, 'index'):
        return obj.index(max(obj))
    elif hasattr(obj, 'iteritems'):
        return max(obj.iteritems(), key=operator.itemgetter(1))[0]


def argsort(seq, reverse=False):
    '''Sort indexes/keys from least to greatest'''
    if hasattr(seq, 'index'):
        return sorted(range(len(seq)), key=seq.__getitem__,
                      reverse=reverse)
    elif hasattr(seq, 'iteritems'):
        return sorted(seq.keys(), key=seq.__getitem__, reverse=reverse)

class Vocab:
    def __init__(self):
        self.docs = {}
    def add_doc(self, url, doc):
        self.docs[url] = Counter(doc)
    def getall(self):
        tf = Counter()
        for url, doc in self.docs.iteritems():
            tf.update(doc)
        return tf
    def remove_hapax(self):
        tf = self.getall()
        removed = set()
        for url in self.docs.keys():
            for word in self.docs[url].keys():
                if tf[word] == 1:
                    removed.add(word)
                    del self.docs[url][word]
        return removed
    def tfidf(self):
        self.tf = defaultdict(float)
        self.df = Counter()
        self.tfidf_dict = {}
        for url, doc_counter in self.docs.iteritems():
            total = sum(doc_counter.values())
            for word, count in doc_counter.iteritems():
                c = float(count)/total
                if c > self.tf[word]:
                    self.tf[word] = c
            self.df.update(doc_counter.keys())
        for word, count in self.df.iteritems():
            self.tfidf_dict[word] = self.tf[word] * math.log10(len(self.docs)/count)
        return self.tfidf_dict
    def tfidf_filter(self, min_df = 3, top_words = 5000):
        removed = set()
        tfidf = self.tfidf()
        below_minimum = set([word for word,count in self.df.iteritems() if count < min_df])
        tfidf_top = [x for x in argsort(tfidf, reverse=True) if x not in below_minimum]
        allowed = set(tfidf_top[0:top_words])
        for url in self.docs.keys():
            for word in self.docs[url].keys():
                if word not in allowed:
                    removed.add(word)
                    del self.docs[url][word]
        return removed