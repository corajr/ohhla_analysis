#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utils import *

from django.core.management import setup_environ
from raplyrics import settings
setup_environ(settings)
from ohhla.models import *

DMAP_FILE = 'lda/dmap.txt'
ARTIST_CSV = 'lda/artist.csv'

with codecs.open(DMAP_FILE, 'r', encoding='utf-8') as dmap:
    filenames = [x.strip() for x in dmap.readlines()]

with file(ARTIST_CSV, 'wb') as csv_file:
    writer = UnicodeCsvWriter(csv_file)
    writer.writerow(["doc", "artist"])
    for i, filename in enumerate(filenames):
        name = Song.objects.get(filename=filename).artist.name
        writer.writerow([str(i), name])

