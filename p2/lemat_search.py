from sys import stdin
from collections import defaultdict
from cli_colours import coloured

class Index:
    word_index = None
    documents = None

    def __init__(self, documents_file):
        self.word_index = defaultdict(set)
        self.documents = defaultdict(str)
        for (i,line) in enumerate(open(documents_file)):
            line = line.strip()
            self.documents[i] = line
            for w in line.split():
                self.word_index[w].add(i)

    def search(self, word_list):
        hit = self.word_index[ word_list[0] ]
        for w in word_list[1:]:
            hit &= self.word_index[w]
        return sorted( self.documents[i] for i in hit )

def prompt():
    print(coloured('?> ', 'r'), end='', flush=True)

if __name__ == "__main__":
    docs = '../../data/wikicytaty_stokenizowane_nltk.txt'
    index = Index(docs)

    prompt()
    for line in stdin:
        line = line.strip()
        if len(line) > 0:
            words = line.split()
            result = index.search(words)
            for doc in result:
                to_be_printed = doc
                for w in words:
                    w = ' '+w+' '
                    to_be_printed = to_be_printed.replace(w, coloured(w, 'g'))
                print(to_be_printed)
        prompt()
