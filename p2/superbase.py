# cat ../../data/polimorfologik-2.1.txt | head -n 100000 > ../../data/poli_mini_test
# python3 superbase.py | pv -l -s 4811853 | sort > ../../data/superbase.txt

from lemat_search import Lematizer
from unionfind import UnionFind

class SuperBase:
    superbase = None
    lematizer = None

    def __init__(self, lemat_dict_file):
        self.lematizer = Lematizer(lemat_dict_file)
        self.superbase = UnionFind()
        
        lemats = self.lematizer.all_lemats()
        for l in lemats:
            self.superbase.make_set(l)

        for (_, lems) in self.lematizer.items():
            sofar = None
            for l in lems:
                if sofar:
                    self.superbase.union(sofar, l)
                sofar = self.superbase.find(l)

    def __getitem__(self, word):
        try:
            # trick
            for lem in self.lematizer[word]:
                break
            # confused?
            # above code is the best way I know to extract an element from the set
            return self.superbase.find(lem)
        except KeyError:
            return word

    def items(self):
        return ( (w, self[w]) for (w,_) in self.lematizer.items() )

if __name__ == "__main__":
    #lemats_file = '../../data/poli_mini_test'
    lemats_file = '../../data/polimorfologik-2.1.txt'
    superbase = SuperBase(lemats_file)

    for (w, base) in superbase.items():
        print(base, w, sep=';')

'''
$ wc ../../data/polimorfologik-2.1.txt
4811853   4811922 332890031 ../../data/polimorfologik-2.1.txt

$ cat ../../data/polimorfologik-2.1.txt | cut -d ';' -f 1-2 | sort | uniq | wc
4811854 4811922 126501094

$ cat ../../data/polimorfologik-2.1.txt | cut -d ';' -f 2 | sort | uniq | wc
4668625 4668625 66366777

$ wc ../../data/superbase.txt 
4668776   4668973 123248288 ../../data/superbase.txt
'''
