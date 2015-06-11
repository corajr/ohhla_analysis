#!/usr/bin/python

import os
import codecs
import subprocess

def format_process_args(process_location, process_name, options):
    process_args = [process_location, process_name]
    for (k, v) in options.iteritems():
        process_args.append(u'--' + k)
        process_args.append(unicode(v))
    return process_args

def run_process(args, progress_filename):
    with codecs.open(progress_filename, 'w', encoding='utf-8') as progress_file:
        retval = subprocess.call(args, stdout=progress_file,
                                     stderr=progress_file)
    return retval


MALLET_OUT_DIR = 'lda_anchor'
INSTANCES_FILE = os.path.join(MALLET_OUT_DIR, 'instances.mallet')
METADATA_FILE = os.path.join(MALLET_OUT_DIR, 'metadata.json')

ANCHOR = '/Users/chrisjr/Downloads/anchor-master/bin/anchor'

def do_test(min_docs = 20, topics = 100):
    md = str(min_docs)
    TOPICS_FILE = os.path.join(MALLET_OUT_DIR, 'tests', md + 'topics.txt')
    DOC_TOPICS_FILE = os.path.join(MALLET_OUT_DIR, 'tests', md + 'doc-topics.txt')
    PROGRESS_FILE = os.path.join(MALLET_OUT_DIR, 'tests', md + 'progress.txt')
    DOC_PROGRESS_FILE = os.path.join(MALLET_OUT_DIR, 'tests', md +'doc-progress.txt')
    TOPICS = topics

    anchor_opts = {
        'input': INSTANCES_FILE,
        'num-topics': TOPICS,
        'num-random-projections': 1000,
        'projection-density': 0.01,
        'min-docs': min_docs,
        'topics-file': TOPICS_FILE
    }


    lda_args = format_process_args(ANCHOR, 'train-anchor', anchor_opts)
    lda_return = run_process(lda_args, PROGRESS_FILE)

    anchor_doc_opts = {
        'input': INSTANCES_FILE,
        'num-topics': TOPICS,
        'topics-file': TOPICS_FILE,
        'doc-topics': DOC_TOPICS_FILE
    }

    # doc_args = format_process_args(ANCHOR, 'doc-topics', anchor_doc_opts)
    # doc_topic_return = run_process(doc_args, DOC_PROGRESS_FILE)

for i in [150,200,300]:
    do_test(i)