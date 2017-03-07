import unicodedata as ud
from collections import defaultdict as dd 

txt = ".,‹›«»~{}⟨⟩…©§€£„”-–¿αξłAa갢½∞⩽123Ω$%"
cat = dd(lambda:[])

for r in txt:
    print(r+':',' ', ud.name(r), ', ', ud.category(r), ', ', ud.bidirectional(r))
    #cat[unicodedata.category(r)].append(r)

#for c in cat:
#    print (c+':', ' '.join(cat[c]))
