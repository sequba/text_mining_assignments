from sys import stdin
from collections import defaultdict
from cli_colours import coloured

class Index:
    index = None
    documents = None

    def __init__(self, documents_file):
        self.index = defaultdict(set)
        self.documents = defaultdict(str)
        for (i,line) in enumerate(open(documents_file)):
            line = line.strip()
            self.documents[i] = line
            for w in line.split():
                self.index[w].add(i)

    def search(self, word_list):
        hit = self.index[ word_list[0] ]
        for w in word_list[1:]:
            hit &= self.index[w]
        return sorted( self.documents[i] for i in hit )

class Lematizer:
    mapping = None # word -> lemats
    reversed_mapping = None # lemat -> words

    def __init__(self, lemat_dict_file):
        # build mapping 
        self.mapping = defaultdict(set)
        for line in open(lemat_dict_file):
            fields = line.strip().split(';')
            self.mapping[ fields[1] ].add(fields[0])
        
        # build reversed_mapping
        self.reversed_mapping = defaultdict(set)
        for (w, lemats) in self.mapping.items():
            for l in lemats:
                self.reversed_mapping[l].add(w)

    def __getitem__(self, word):
        lemats = self.mapping[word]
        if lemats:
            return lemats
        else:
            return { word }

    def all_forms(self, word):
        word_lemats = self[word]
        result = { word }
        for l in word_lemats:
            result |= self.reversed_mapping[l]
        return result

class LematIndex(Index):
    lemats = None

    def __init__(self, documents_file, lemat_dict_file):
        self.index = defaultdict(set)
        self.documents = defaultdict(str)
        self.lemats = Lematizer(lemat_dict_file)

        for (i,line) in enumerate(open(documents_file)):
            line = line.strip()
            self.documents[i] = line
            for w in line.split():
                for l in self.lemats[w]:
                    self.index[l].add(i)

    def search(self, word_list):
        hit = self.index[ word_list[0] ]
        for w in word_list[1:]:
            hit &= self.index[w]
        return sorted( self.documents[i] for i in hit )

def prompt():
    print(coloured('?> ', 'r'), end='', flush=True)

if __name__ == "__main__":
    docs = '../../data/wikicytaty_stokenizowane_nltk.txt'
    lemats = '../../data/polimorfologik-2.1.txt'
    index = LematIndex(docs, lemats)

    prompt()
    for line in stdin:
        line = line.strip()
        if len(line) > 0:
            words = line.split()
            result = index.search(words)
            for doc in result:
                to_be_printed = doc
                for w in words:
                    for form in index.lemats.all_forms(w):
                        form = ' '+form+' '
                        to_be_printed = to_be_printed.replace(form, coloured(form, 'g'))
                print(to_be_printed)
        prompt()
