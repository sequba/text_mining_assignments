'''
tokenize:
gunzip -c ../../data/cytaty.txt.gz | cut -c 3- | python3 my_tokenize.py | less


compare results:
gunzip -c ../../data/cytaty.txt.gz | wc 
gunzip -c ../../data/cytaty.txt.gz | pv -l -s 197570 | cut -c 3- | python3 my_tokenize.py | tr ' ' '\n' > /tmp/mine
gunzip -c ../../data/tokenized_quotes.txt.gz |tr ' ' '\n' > /tmp/theirs
diff /tmp/mine /tmp/theirs 

'''

import unicodedata as ud
from sys import stdin
from itertools import takewhile, dropwhile

def tokenize_word(w):
    word = w.casefold()
    while word:
        cat = ud.category(word[0])
        same_cat = lambda c: ud.category(c) == cat
        homocat = takewhile(same_cat, word)
        yield ''.join(homocat)
        word = list(dropwhile(same_cat, word))


for line in stdin:
    words = line.strip().split(' ')
    tokens = ( t for w in words for t in tokenize_word(w) )
    print(' '.join(tokens))


