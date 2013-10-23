#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import re
from django.core.management import setup_environ
from raplyrics import settings
setup_environ(settings)

from ohhla.models import *

def color_text(text, assignments):
    text = text.replace(u'\n', u' </> \n')
    words = text.split(u' ') #re.split('\s+', text, flags=re.UNICODE)
    all_assigned = set(x[0] for x in assignments)
    output = []
    for word in words:
        stripped = re.sub(r'<[^>]+?>', '', re.sub(r"[^\w_]+", u'', word.lower(), flags=re.UNICODE))
        if len(assignments) > 0 and stripped == assignments[0][0]:
            assignment = assignments.pop(0)
            if assignment[1] == '4':
                output.append(u"\\textbf{" + word.strip() + u"}")
            else:
                output.append(word)
            # output.append(u"<span class='topic{}'>{}</span>".format(assignment[1], word))
        else:
            output.append(word)
    return u' '.join(output)

text = Song.objects.get(title='Dear Mama').content

assignments = []
words_assigned = []
with file("dearmama.csv") as f:
    reader = csv.reader(f)
    reader.next()
    for row in reader:
        assignments.append((row[0], row[1]))
        words_assigned.append(row[0])

colored = color_text(text, assignments)

print colored.replace("</>", " \\\\ ")
# with file("dearmama.html", 'w') as f:
#     f.write("<html><head><style> .topic4 { color: red; }</style></head><body>\n")
#     f.write(colored)
#     f.write("</body></html>\n")