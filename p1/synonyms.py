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

comment_regex = re.compile('! --((?!--).)*-- ')
open_comment_regex = re.compile('! --((?!--).)*$')
category_regex = re.compile('= = =((?!= = =).)*= = = ')
open_category_regex = re.compile('= = =((?!= = =).)*$')
subcategory_regex = re.compile('= =((?!= =).)*= = ')
open_subcategory_regex = re.compile('= =((?!= =).)*$')

def remove_occurences(regex_object, string):
    m = regex_object.search(string)
    while m:
        string = regex_object.sub('', string)
        m = regex_object.search(string)
    return string

unicode_dashes = {173, 1418, 1470, 8208, 8209, 8210, 8211, 8212, 8213, 8722, 65123, 65293}
translation_table = dict.fromkeys(unicode_dashes, '-')

def prepare(line):
    line = line.strip()
    line = line.translate(translation_table).replace('& amp ; ndash ;', '-')
    line = remove_occurences(comment_regex, line)
    line = remove_occurences(open_comment_regex, line)
    line = remove_occurences(category_regex, line)
    line = remove_occurences(open_category_regex, line)
    line = remove_occurences(subcategory_regex, line)
    line = remove_occurences(open_subcategory_regex, line)
    line = line.replace('right ', '')

    return line

def suitable(string):
    conditions = [
        # empty lines
        string == '',
        # infoboxes
        string.count('|') > 3,
        # podobne dziwy
        string.count('br /') > 3,
        # redirection pages
        string.startswith('/ > # redirect')
    ]

    if any(conditions):
        return False
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

    synonyms = set()
    for s in interesting:
        quoted = quoted_regex.finditer(s)
        synonyms = { inner for q in quoted for inner in [q.group().strip().strip("'").strip()] if len(inner) < 64 }
    
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

    if line[0:3] == '###': # title line
        title = line[4:]
        continue
    elif not suitable(line) or title.endswith('( ujednoznacznienie )'): # garbage
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

