'''
gunzip -c ../../data/poczatki_wikipediowe.txt.gz | head -n 10000 | python3 my_tokenize.py | python3 synonyms.py | sort -R | less -r

gunzip -c ../../data/poczatki_wikipediowe.txt.gz | pv -l -s 3024407 | python3 my_tokenize.py | python3 synonyms.py
'''

from sys import stdin
import unicodedata as ud
import re

def highlight(string):
    bold = '\033[1m'
    w  = '\033[0m'  # white (normal)
    r  = '\033[31m' # red
    g  = '\033[32m' # green
    o  = '\033[33m' # orange
    b  = '\033[34m' # blue
    p  = '\033[35m' # purple
    return bold+g+' '+string+' '+w

def replace_regex(string, regex_obj, replacement):
    m = regex_obj.search(string)
    while m:
        string = regex_obj.sub(replacement, string)
        m = regex_obj.search(string)
    return string

class Line:
    translate_dashes = unwanted_regexes = None
    def __init__(self):
        unicode_dashes = [ 173, 1418, 1470, 8208, 8209, 8210, 8211, 8212, 8213, 8722, 65123, 65293 ]
        Line.translate_dashes = dict.fromkeys(unicode_dashes, '-')
        
        unwanted_patterns = [   '! --((?!--).)*-- ',
                                '! --((?!--).)*$',
                                '= = =((?!= = =).)*= = = ',
                                '= = =((?!= = =).)*$',
                                '= =((?!= =).)*= = ',
                                '= =((?!= =).)*$' ]
        Line.unwanted_regexes = [ re.compile(p) for p in unwanted_patterns ]

    def prepare(line):
        line = line.translate(Line.translate_dashes).replace('& amp ; ndash ;', '-') # handle unicode dashes
        for r in Line.unwanted_regexes: # remove unwanted patterns
            line = replace_regex(line, r, '')
        line = line.replace('right ', '') # remove align specs
        return line.strip()
Line()

class Article:
    def suitable(title, body):
        conditions = [
            title.endswith('( ujednoznacznienie )'),  # strony ujednoznaczniajace
            body == '', # empty lines
            body.count('|') > 3, # infoboxes
            body.count('br /') > 3, # podobne dziwy
            body.startswith('/ > # redirect') ] # redirection pages
        return not any(conditions)

class Definition:
    regexes = None
    def __init__(self):
        # first occurence of a def_word outside paranthesis (nested * not working, so its an approximation)
        no_paran = '((?!{0})[^(])*'
        paran = '(\([^)]*\))*'
        pattern = '^' + no_paran + paran + no_paran + paran + no_paran + '(?P<word>{0})'
        keywords = [ ' - ', ' jest ', ' to ' ]
        Definition.regexes = [re.compile(pattern.format(w)) for w in keywords]

    def split(string):
        string = ' ' + string
        matches = [ m.span('word') for pattern in Definition.regexes for m in [pattern.search(string)] if m ]
        if matches:
            (start, end) = min(matches)
            #print(string[:start] + highlight(string[start:end]) + string[end:end+50])
            return (string[:start].strip(), string[end:].strip())
        else:
            return ('', string)
Definition()

class Synonym:
    syn_regexes = body_syn_regex = quoted_regex = None
    def __init__(self):
        # an intro_word followed by a series of ign_words indicate the beginning of interesting fragment from which the synonyms are to be extracted
        schema = "(?P<word>"+"'''*[^']*'''*" + "("+" *, *"+"'''*[^']*'''*"+")*"+")"
        syn_pattern = "{0}"+" *"+"("+"({1}) *"+")*"+schema
        body_syn_pattern = "^ *"+"(({0}) *"+"("+"({1}) *"+")*"+")?"+schema
        common_words = [ 'też', 'inaczej', 'właściwie', 'właść .', 'właśc .', 'oryginalnie', 'w oryginale', 'dawniej', 'dokładnie', 'dokładniej', 'zwyczajowo', 'zwycz .', 'potocznie', 'pot .', 'potocz .', 'syn.', 'synonimicznie', 'także', 'również', 'krótko', 'krócej', 'w skrócie', 'prościej', 'zwyczajnie', 'rzadziej', 'czasem', 'czasami', 'precyzyjnie', 'precyzyjniej', 'zwany', 'zwana', 'zwane', 'zwani', 'nazywany', 'nazywana', 'nazywane', 'nazywani', 'znany', 'znana', 'znane', 'tzw .', 'często', 'częściej', 'określany', 'określana', 'określane', 'określani']
        intro_words = [ ' lub ', ' albo ', ' skrót ', ' synonim ', ' synonimy ', ' czyli ', '^', '\( '] + [ ' '+w+' ' for w in common_words ]
        ign_words = [ 'jako ', 'nazwą ', 'pod nazwą ', 'mianem ', 'terminem ', 'określeniem ', 'pod określeniem ', ': ', '- ', 'po prostu ' ] + [ w+' ' for w in common_words ]
        ign_alternative = '|'.join(ign_words)
        Synonym.syn_regexes = [ re.compile(syn_pattern.format(w, ign_alternative)) for w in intro_words ]
        intro_alternative = '|'.join(intro_words)
        Synonym.body_syn_regex = re.compile(body_syn_pattern.format(intro_alternative, ign_alternative))
        Synonym.quoted_regex = re.compile("'''*[^']*'''*")

    def extract_all(term, description):
        description = ' '+description
        interesting_substrings = { m.group('word') for r in Synonym.syn_regexes for m in r.finditer(term) }
        interesting_substrings_in_body = { m.group('word') for m in Synonym.body_syn_regex.finditer(description) }
        interesting = interesting_substrings | interesting_substrings_in_body
        matches = { m for s in interesting for m in Synonym.quoted_regex.finditer(s) }
        synonyms = { inner for m in matches for inner in [m.group().strip().strip("'").strip()] if len(inner) > 0 and len(inner) < 64 }
        
        for separator in [',', '(', ')']:
            synonyms = { term.strip() for string in synonyms for term in string.split(separator) }

        return synonyms
Synonym()

if __name__ == "__main__":
    matched = unmatched = rejected = 0
    
    for line in stdin:
        line = Line.prepare(line)

        # classify the type of a line
        if not line: # empty line
            continue
        elif line[0:3] == '###': # title
            title = line[4:]
            continue
        else: # article body
            body = line
        
        # ignore garbage
        if not Article.suitable(title, body):
            rejected += 1
            continue
        
        # definition structure
        (term, description) = Definition.split(body)
        if term:
            matched += 1
        else:
            unmatched += 1
      
        # get the synonyms
        synonyms = Synonym.extract_all(term, description)
        synonyms.discard(title)
        if synonyms:
            print('{0} # {1}'.format(title, ' # '.join(sorted(synonyms))))


    print('matched:', matched)
    print('unmatched:', unmatched)
    print('rejected:', rejected)

