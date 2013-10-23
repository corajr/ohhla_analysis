#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import re
from collections import defaultdict

PARAM_FILE = 'dmr/dmr.parameters'

topic_features = defaultdict(dict)
with file(PARAM_FILE) as f:
    topic = 0
    for line in f:
        new_topic = re.match('FEATURES FOR CLASS topic([0-9]+)', line)
        if new_topic is not None:
            topic = int(new_topic.group(1))
        else:
            this_line = line.split(' ')
            feature = this_line[1]
            topic_features[topic][feature] = float(this_line[2])

with file("dmr_features.csv", 'w') as f:
    writer = csv.writer(f)
    writer.writerow(["topic", "feature", "value"])
    for topic, feature_dict in topic_features.iteritems():
        for feature, value in feature_dict.iteritems():
            writer.writerow([topic, feature, value])