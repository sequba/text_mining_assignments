# Wyszukiwarka synonimów - opis

## Input
Wyszukiwarka oczekuje tekstu stokenizowanego. Przykładowe wywołanie:
```
$ cat poczatki_wikipediowe.txt | python3 my_tokenize.py | python3 synonyms.py > /synonimy.txt
```

## Przygotowanie

Dla ułatwienia późniejszych operacji, w stokenizowanym tekście wyszukiwane są pewne ciągi znaków i zamieniane na inne. Najważniejszą zmianą jest translacja wszystkich symboli z unicode'u, które przypominają znak `'-'`, na ten właśnie znak, gdyż jest on istotny na jednym z kolejnych etapów przetwarzania tekstu.

## Filtrowanie

Na wstępie odrzucane są artykuły, które spełniają któreś z poniższych kryterów:
- tytuł zaczyna się jednym ze słów `['szablon', 'kategoria', 'wikipedia', 'plik', 'portal', 'mediawiki', 'wikiprojekt', 'pomoc']` ("meta-artykuły")
- tytuł kończy się na `'( ujednoznacznienie )'`
- zawierają ponad trzy wystąpienia znaku `'|'` (infoboxy)
- zawierają ponad trzy wystąpienia `''br /'` (jakieś tabelki)
- zaczynaja sie od frazy `'/ > # redirect'` (przekierowania)

## Identyfikacja struktury definicji

Ten etap opiera się na założeniu, że początkowy fragment artykułu zawiera definicję pojęcia, która w większości przypadków ma dosyć szczególną strukturę:
```
<głowa definicji> <fraza definiująca> <ciało definicji>
```
Głowa definicji w najprostszym przypadku zawiera jedynie definiowane pojącie, frazą definiującą może być słowo 'to', a ciało to mniej lub bardziej ścisły opis charakteryzujący definiowane pojęcie.

Przykład definicji z Wikipedii z wyróżnionymi częściami:
```'< '''Aksjomat''' ('''postulat''', '''pewnik'''; gr. αξιωμα ''aksíoma'' – godność, pewność, oczywistość) > < - > < jedno z podstawowych pojęć logiki matematycznej. Od czasów Euklidesa uznawano, że aksjomaty [...] >'
```

Można zauważyć, że zdecydowana większość synonimów występuje w głowie definicji. Wyszukiwarka ogranicza się tylko do tej części, co pozwala jest znacząco ograniczyć liczbę trafień "false-positive" przy stosowaniu agresywnych (prostych, powszechnych) wzorców. W artykułach, w których nie udało się wyróżnić struktury definicji, wzorce synonimów są wyszukiwane tylko na początku.

Wyszukiwarka klasyfikuję frazę jako frazę definiującą, jeśli znajdzie poza nawiasami i poza cudzysłowami jeden z ciągów znaków:`[ ' - ', ' jest to ', ' jest ', ' to ' ]`

## Wzorce synonimów

Synonimy są wskazywane na podstawie słów, które je poprzedzają. Stosowany wzorzec:
```
<intro> <ign>* ''+<syn>''+ (, ''+<syn>''+)*
```
Jako synonimy brane pod uwagę są jedynie frazy ujęte w podwójne lub potrójne apostrofy. Wyszukiwane są ciągi takich fraz (oddzielonych przecinkami), przed którymi występuje fraza `<intro>` i byćmoże kilka fraz `<ign>`.

Dokładne frazy, brane pod uwagę są wylistowane w poniższym fragmencie kodu:
```
common_words = [ 'też', 'inaczej', 'właściwie', 'właść .', 'właśc .', 'oryginalnie', 'w oryginale', 'dawniej', 'dokładnie', 'dokładniej', 'zwyczajowo', 'zwycz .', 'potocznie', 'pot .', 'potocz .', 'syn.', 'synonimicznie', 'także', 'również', 'krótko', 'krócej', 'w skrócie', 'prościej', 'zwyczajnie', 'rzadziej', 'czasem', 'czasami', 'precyzyjnie', 'precyzyjniej', 'zwany', 'zwana', 'zwane', 'zwani', 'nazywany', 'nazywana', 'nazywane', 'nazywani', 'znany', 'znana', 'znane', 'tzw .', 'często', 'częściej', 'określany', 'określana', 'określane', 'określani']
intro_words = [ ' lub ', ' albo ', ' skrót ', ' synonim ', ' synonimy ', ' czyli ', '^', '\( '] + [ ' '+w+' ' for w in common_words ]
ign_words = [ 'jako ', 'nazwą ', 'pod nazwą ', 'mianem ', 'terminem ', 'określeniem ', 'pod określeniem ', ': ', '- ', 'po prostu ' ] + [ w+' ' for w in common_words ]

```
