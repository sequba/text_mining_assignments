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

class line_preparation:
    unicode_dashes = [ 173, 1418, 1470, 8208, 8209, 8210, 8211, 8212, 8213, 8722, 65123, 65293 ]
    translate_dashes = dict.fromkeys(unicode_dashes, '-')
    
    unwanted_patterns = [   '! --((?!--).)*-- ',
                            '! --((?!--).)*$',
                            '= = =((?!= = =).)*= = = ',
                            '= = =((?!= = =).)*$',
                            '= =((?!= =).)*= = ',
                            '= =((?!= =).)*$'
                        ]
    unwanted_regexes = [ re.compile(p) for p in unwanted_patterns ]

    def __call__(self, line):
        # handle unicode dashes
        line = line.translate(self.translate_dashes).replace('& amp ; ndash ;', '-')
        # remove unwanted patterns
        for r in self.unwanted_regexes:
            line = replace_regex(line, r, '')
        # remove align specs
        line = line.replace('right ', '')
        return line.strip()
prepare = line_preparation()

def suitable(title, definition):
    conditions = [
        # strony ujednoznaczniajace
        title.endswith('( ujednoznacznienie )'),
        # empty lines
        definition == '',
        # infoboxes
        definition.count('|') > 3,
        # podobne dziwy
        definition.count('br /') > 3,
        # redirection pages
        definition.startswith('/ > # redirect')
    ]

    if any(conditions):
        return False
    else:
        return True

# first occurence of a def_word outside paranthesis (nested * not working, so its an approximation)
def_pattern = '^'+'((?!{0})[^(])*'+'(\([^)]*\))*'+'((?!{0})[^(])*'+'(\([^)]*\))*'+'((?!{0})[^(])*'+'(?P<word>{0})'
def_words = [ ' - ', ' jest ', ' to ' ]
def_regexes = [re.compile(def_pattern.format(w)) for w in def_words]

def split_definition(string):
    string = ' ' + string
    matches = [ m.span('word') for pattern in def_regexes for m in [pattern.search(string)] if m ]
    if matches:
        (start, end) = min(matches)
        #print(string[:start] + highlight(string[start:end]) + string[end:end+50])
        return (string[:start].strip(), string[end:].strip())
    else:
        return ('', string)

# an intro_word followed by a series of ign_words indicate the beginning of interesting fragment from which the synonyms are to be extracted
schema = "(?P<word>"+"'''*[^']*'''*" + "("+" *, *"+"'''*[^']*'''*"+")*"+")"
syn_pattern = "{0}"+" *"+"("+"({1}) *"+")*"+schema
body_syn_pattern = "^ *"+"(({0}) *"+"("+"({1}) *"+")*"+")?"+schema
common_words = [ 'też', 'inaczej', 'właściwie', 'właść .', 'właśc .', 'oryginalnie', 'w oryginale', 'dawniej', 'dokładnie', 'dokładniej', 'zwyczajowo', 'zwycz .', 'potocznie', 'pot .', 'potocz .', 'syn.', 'synonimicznie', 'także', 'również', 'krótko', 'krócej', 'w skrócie', 'prościej', 'zwyczajnie', 'rzadziej', 'czasem', 'czasami', 'precyzyjnie', 'precyzyjniej', 'zwany', 'zwana', 'zwane', 'zwani', 'nazywany', 'nazywana', 'nazywane', 'nazywani', 'znany', 'znana', 'znane', 'tzw .', 'często', 'częściej', 'określany', 'określana', 'określane', 'określani']
intro_words = [ ' lub ', ' albo ', ' skrót ', ' synonim ', ' synonimy ', ' czyli ', '^', '\( '] + [ ' '+w+' ' for w in common_words ]
ign_words = [ 'jako ', 'nazwą ', 'pod nazwą ', 'mianem ', 'terminem ', 'określeniem ', 'pod określeniem ', ': ', '- ', 'po prostu ' ] + [ w+' ' for w in common_words ]
ign_alternative = '|'.join(ign_words)
syn_regexes = [ re.compile(syn_pattern.format(w, ign_alternative)) for w in intro_words ]
intro_alternative = '|'.join(intro_words)
body_syn_regex = re.compile(body_syn_pattern.format(intro_alternative, ign_alternative))

quoted_regex = re.compile("'''*[^']*'''*")

def extract_synonyms(head, body):
    interesting_substrings = { m.group('word') for r in syn_regexes for m in r.finditer(head) }
    interesting_substrings_in_body = { m.group('word') for m in body_syn_regex.finditer(' '+body) }
    interesting = interesting_substrings | interesting_substrings_in_body
    matches = { m for s in interesting for m in quoted_regex.finditer(s) }
    synonyms = { inner for m in matches for inner in [m.group().strip().strip("'").strip()] if len(inner) > 0 and len(inner) < 64 }
    
    for separator in [',', '(', ')']:
        synonyms = { term.strip() for string in synonyms for term in string.split(separator) }

    '''
    if interesting_substrings_in_body:
        string = head
        for m in interesting_substrings:
            string = string.replace(m, highlight(m))
        print('###', string)
        string = body
        for m in interesting_substrings_in_body:
            string = string.replace(m, highlight(m))
        print('$$$ ', string)
    '''
    return synonyms

matched = 0
unmatched = 0
rejected = 0
for line in stdin:
    line = prepare(line)

    if not line: # empty line
        continue
    elif line[0:3] == '###': # title line
        title = line[4:]
        continue
    else: # definition line
        definition = line
        if not suitable(title, definition) or title.endswith('( ujednoznacznienie )'): # garbage
            rejected += 1
            continue
   
    (head, body) = split_definition(line)
    if head:
        matched += 1
    else:
        unmatched += 1
  
    synonyms = extract_synonyms(head, body)
    synonyms.discard(title)
    if synonyms:
        print('{0} ## {1}'.format(title, ' # '.join(synonyms)))


# print('{0} vs {1} + {2}'.format(matched, unmatched, rejected))

