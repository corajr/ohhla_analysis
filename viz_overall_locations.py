#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
import csv
from collections import Counter, defaultdict
from django.core.management import setup_environ
from raplyrics import settings
setup_environ(settings)

from ohhla.models import *

places = defaultdict(Counter)
place_id_to_coords = {}

for song in Song.objects.exclude(artist__place=None).exclude(album__date=None):
    place = song.artist.place
    if place.id not in place_id_to_coords:
        place_id_to_coords[place.id] = {'lat': place.latitude,
                'lon': place.longitude}
    places[place.id][song.album.date.year] += 1

data = []

for (place_id, coords) in place_id_to_coords.iteritems():
    coords['counts'] = dict(places[place_id])
    data.append(coords)

with file("all_places.csv", 'w') as f:
    writer = csv.writer(f) #lon, lat, count
    for coords in data:
        writer.writerow([unicode(x) for x in [coords['lon'], coords['lat'], sum(coords['counts'].values())]])
# heatmap_filename = os.path.join('viz', 'heatmap', 'heatmap_data.js')
# with file(heatmap_filename, 'w') as f:
#     f.write('var data=')
#     f.write(json.dumps(data))
#     f.write(';')
