#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
from django.core.management import setup_environ
from raplyrics import settings
setup_environ(settings)

from ohhla.models import *

from utils import *

import csv

features = set()
with file("dmr_features.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        features.add(row[1])
        if row[0] == '1':
            break

features.remove('year')

with file("dmr_feature_labels.csv", 'wb') as f:
    writer = UnicodeCsvWriter(f)
    writer.writerow([u'feature', u'label'])
    for feature in features:
        if feature.startswith('location'):
            place_id = int(feature.replace('location', ''))
            name = Place.objects.get(id=place_id).name
        elif feature.startswith('artist'):
            artist_id = int(feature.replace('artist', ''))
            name = Artist.objects.get(id=artist_id).name
        writer.writerow([feature, name])


