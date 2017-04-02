# gunzip -c ../../data/2grams.gz | pv -l -s 75395184 | python3 super_ngrams.py

# head -n 100000 ../../data/polimorfologik-2.1.txt > /tmp/polimorfologik-2.1.txt
# head -n 100000 ../../data/superbase.txt > /tmp/superbase.txt


from sys import stdin
from collections import defaultdict
from lemat_search import Lematizer

class UniqueLematizer(Lematizer):
    def __getitem__(self, word):
        lemats = self.mapping[word]
        if lemats:
            for l in lemats:
                break
            return l
        else:
            return word

# classify ngrams into buckats depending on its super- form
buckets = defaultdict(list)

if __name__ == "__main__":
    lemats_file = '../../data/polimorfologik-2.1.txt'
    #lemats_file = '/tmp/polimorfologik-2.1.txt'
    superbase_file = '../../data/superbase.txt'
    #superbase_file = '/tmp/superbase.txt'
    superbase = UniqueLematizer(superbase_file)

    for line in stdin:
        words = line.strip().split()
        if words:
            count = words[0]
            super_ngram = tuple( superbase[w] for w in words[1:] )
            buckets[super_ngram].append(tuple(words))
    
    # no need to keep both dictionaries in memory
    del superbase
    lemats = Lematizer(lemats_file)
    
    for (super_ngram, ngrams) in buckets.items():
        positions = tuple(zip(*ngrams))
        
        bucket_count = sum(int(s) for s in positions[0])
        for (p, words) in enumerate(positions[1:]):
            if words:
                common_lems = lemats[ words[0] ]
                for (i,w) in enumerate(words[1:]):
                    common_lems &= lemats[w]
                if not common_lems:
                    print(bucket_count, super_ngram, 'pos: {0}'.format(p+1))

