#!/usr/bin/env python

#This file is part of text2ldac.

#text2ldac is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#text2ldac is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with text2ldac. If not, see <http://www.gnu.org/licenses/>.



import argparse
import codecs
import os
import operator
import string
import sys
import traceback

from collections import defaultdict, Counter
import itertools

from django.core.management import setup_environ
from raplyrics import settings
setup_environ(settings)

from utils import *
from ohhla.models import *

__doc = \
'''
This is a program to convert documents into the file format used by David
Blei's dtm implementation. It generates the .dat, .vocab and
.dmap files from .txt files in a given directory.

cf. http://www.cs.princeton.edu/~blei/lda-c/readme.txt
'''
__author__ = 'Johannes Knopp <johannes@informatik.uni-mannheim.de>'

def init_parser():
	'''
	Returns an argument parser configured with options for this program
	'''
	parser = argparse.ArgumentParser(
			description='A program to convert documents to .dat, .vocab and .dmap files'
			)

	#options
	parser.add_argument('-o', '--output', action='store', dest='outdir', default = 'dtm_release',
			help='directory to store the resulting files')
	#stopwords
	parser.add_argument('--stopwords', action='store', dest='stopword_file',
			help='Remove the stopwords given in the stopword file (one line per stopword).')

	return parser.parse_args()


def get_pks_and_years_dict():
	'''Returns a list of zotero keys and a dict mapping them to the years they belong in.'''
	pks = []
	years_dict = {}
	
	pk_query = Song.objects.exclude(artist__place = None).exclude(album__date = None).order_by('album__date')
	
	key_values = list(pk_query.values_list("id", flat = True))
	date_values = [d.year for d in pk_query.values_list("album__date", flat = True)]

	years_dict = dict(zip(key_values, date_values))
	
	return key_values, years_dict
	
def clean_word(word):
	'''
	returns the word in lowercase without punctuation at the start or end
	'''
	return word.rstrip(string.punctuation).lstrip(string.punctuation).lower()

def load_stopwords(stopword_filename):
	'''
	returns a set of stopwords found line by line in the stopwords file
	'''
	stopwords = set()

	with codecs.open(stopword_filename, 'r', 'utf-8') as sf:
		for line in sf:
			if len(line.split()) != 1:
				print('ignoring line with more than one stopword:\n"{0}"'.format(
					line))
				continue
			stopwords.add(line.strip())

	return stopwords

def write_document_map_file(pks, dmap_fname):
	"""
	Save document's names in the order they were processed
	"""
	with codecs.open(dmap_fname,'w','utf-8') as d_file:
		for title in pks:
			try:
				d_file.write(str(title) + '\n')
			except:
				traceback.print_exc()

def write_document_seq_file(years, seq_fname):
	"""
	Save number of years for each document
	"""
	with codecs.open(seq_fname,'w','utf-8') as s_file:
		s_file.write(str(len(years.keys())) + '\n')
		for year in sorted(years.keys()):
			try:
				s_file.write(str(years[year]) + '\n')
			except:
				traceback.print_exc()

def generate_dat_lines_and_word_ids(pks, config, years_dict):
	dat_lines = [] #.dat file output
	word_id_dict = defaultdict(itertools.count().next) 
	used_docs = [] #needed to generate .dmap file
	years_docs = {x : 0 for x in set(years_dict.values())}

	for i, key in enumerate(pks):
		freq_dict = None

		if i % 1000 == 0:
			print i
		
		try:
			doc = get_cleaned_words(Song.objects.get(pk = key).content)
			freq_dict = Counter(doc)
			for word in freq_dict.keys():
				next_id = word_id_dict[word]
		except UnicodeDecodeError as u_error:
			print('Document "{0}" has encoding errors and is ignored!\n{1}'.format(key, u_error))
		except:
			traceback.print_exc()

		if freq_dict is None or len(freq_dict)==0: #did the document contribute anything?
			print('Document "{0}" (#{1}) seems to be empty and is ignored!'.format(key,pks.index(key)))
			continue
		else:
			used_docs.append(key)
			years_docs[years_dict[key]] += 1

		dat_line =	'' #line for the .dat file

		for word in freq_dict.iterkeys():
			dat_line += str(word_id_dict[word]) + ':' + str(freq_dict[word]) + ' '

		#last blank in dat_line is removed
		dat_lines.append(str(len(freq_dict)) + ' ' + dat_line[:-1] + '\n')

	write_document_map_file(used_docs, config['dmapname'])
	write_document_seq_file(years_docs, config['seqname'])

	return dat_lines, word_id_dict


def generate_dat_and_vocab_files(pks, config, years_dict):

	with codecs.open(config['datname'], 'w', 'utf-8') as datfile:
		dat_lines, word_id_dict = generate_dat_lines_and_word_ids(pks,
				config, years_dict)
		datfile.writelines(dat_lines)

	#sort word_id_dict ascending by value und write the words in that
	#order to a .vocab file
	with codecs.open(config['vocabname'], 'w', 'utf-8') as vocabfile:
		for item in sorted(word_id_dict.iteritems(), key=operator.itemgetter(1)):
			vocabfile.write(item[0]+'\n')

	print('Found {0} unique words in {1} files.'.format(
		len(word_id_dict), len(pks)))
	print('Results can be found in "{0}" and "{1}"'.format(
		config['datname'], config['vocabname']))


if __name__=='__main__':

	parser = init_parser()

	#directory with document files
#	 dirname = parser.dirname
#	 dirname = dirname + os.sep if not dirname.endswith(os.sep) else dirname
	#directory for results
	outdir_name = parser.outdir if parser.outdir else settings.LOCAL_PREFIX+"/dtm_release/"
	outdir_name = outdir_name + os.sep if not outdir_name.endswith(os.sep) else outdir_name
	#prefix of the .dat and .vocab files
	basename = "texts" #os.path.dirname(dirname).split('/')[-1]

	if not os.path.exists(outdir_name):
		os.mkdir(outdir_name)

	#store configuration
	config = dict()
	config['datname'] = outdir_name + basename + '-mult.dat'
	config['vocabname'] = outdir_name + basename + '.vocab'
	config['dmapname'] = outdir_name + basename + '.dmap'
	config['seqname'] = outdir_name + basename + '-seq.dat'
	if parser.stopword_file:
		config['stopwords'] = load_stopwords(parser.stopword_file)
	else:
		config['stopwords'] = set()

	pks, years_dict = get_pks_and_years_dict()
	
	try:
		generate_dat_and_vocab_files(pks, config, years_dict)
	except IOError as ioe:
		print(ioe)
		sys.exit(1)
