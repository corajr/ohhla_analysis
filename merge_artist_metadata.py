#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils import *

METADATA_CSV = 'lda/metadata.csv'
ARTIST_CSV = 'lda/artist.csv'
METADATA_ALL_CSV = 'lda/metadata_all.csv'
rows = []

with file(METADATA_CSV, 'rb') as metadata:
    with file(ARTIST_CSV, 'rb') as artist:
        reader1 = unicode_csv_reader(metadata)
        reader2 = unicode_csv_reader(artist)
        try:
            while True:
                rows.append(reader1.next() + reader2.next()[1:])
        except StopIteration:
            pass

with file(METADATA_ALL_CSV, 'wb') as csv_file:
    writer = UnicodeCsvWriter(csv_file)
    for row in rows:
        writer.writerow(row)

