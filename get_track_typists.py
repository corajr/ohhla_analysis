#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import traceback
import gzip
from utils import *

from django.core.management import setup_environ
from raplyrics import settings
setup_environ(settings)

from echonest_api_key import *
from pyechonest import song

from ohhla.models import *

with gzip.open('OHHLA-for-echonest.txt.gz') as f:
    ohhla = json.load(f)

def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

for row in ohhla['rows']:
    typist = row.get('typed by', None)
    if typist is not None:
        try:
            song = get_or_none(Song, filename=row.get('filename'))
            if song is not None:
                song.typist, _ = Typist.objects.get_or_create(email=typist)
                song.save()
        except:
            traceback.print_exc()