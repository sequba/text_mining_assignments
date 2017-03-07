# usage:
# cat ../../data/znaki_wikipedii.txt | python3 char_classes.py | less

from sys import stdin
import unicodedata
from collections import defaultdict

def classify(collection, classifier):
    classes = defaultdict(set)
    for item in collection:
        classes[classifier(item)].add(item)
    return classes

sep = ' '

# read input
chars = {c for line in stdin for c in line}

# use categories
categories = classify(chars, unicodedata.category)

# for letters use names
for (cat, chars) in categories.items():
    if cat[0] == 'L':
        categories[cat] = classify(chars, lambda c: unicodedata.name(c, '???').split(' ')[0])

# print
for (cat, value) in sorted(categories.items()):
    if hasattr(value, 'items'):
        for (subcat, chars) in sorted(value.items()):
            print('{0}.{1}:\n{2}\n'.format(cat, subcat, sep.join(sorted(chars))))
    else:
        print('{0}:\n{1}\n'.format(cat, sep.join(sorted(value))))

