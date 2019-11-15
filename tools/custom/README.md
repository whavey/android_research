# Scripts for analyzing java code and xml files from decompiled android apps.

TODO: threading and general performance tuning

## AndroidCodeFinder.py*
### Essentially a fancy grepper to find specific lines of note like "onClickListener".
usage: AndroidCodeFinder.py [-h] [-p PATH] [-s SEARCH_STRING] [-d DEBUG]

Parse Layout Files

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to code files.
  -s SEARCH_STRING, --search_string SEARCH_STRING 
                        String to search methods for.
  -d DEBUG, --debug DEBUG 
                        Turn on debug mode.

## AndroidUIMapper.py*
### Find lines in java code that are UI related
usage: AndroidUIMapper.py [-h] [-d DEBUG] [-l LINE] [-p PATH]
                          [-s SEARCH_STRING]

optional arguments:
  -h, --help            show this help message and exit
  -d DEBUG, --debug DEBUG
                        Turn on debug mode.
  -l LINE, --line LINE  line to parse.
  -p PATH, --path PATH  file to parse.
  -s SEARCH_STRING, --search_string SEARCH_STRING
                        String to search methods for.
## JavaTreeManager.py*
### Get JavaLang tree structure
usage: JavaTreeManager.py [-h] [-d DEBUG] [-p PATH]

optional arguments:
  -h, --help            show this help message and exit
  -d DEBUG, --debug DEBUG
                        Turn on debug mode.
  -p PATH, --path PATH  file to parse.

## LayoutParser.py*
### Parse Layout XML Files
usage: LayoutParser.py [-h] [-p PATH] [-s SCAN_TYPE] [-d DEBUG]

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  path to layout files
  -s SCAN_TYPE, --scan_type SCAN_TYPE
                        print all xml tags per file
  -d DEBUG, --debug DEBUG
                        toggle debug mode.

## PrivacySimilarity.py
### Uses NLP to find words similar (semantic and Levenshtein) to a set of privacy related keywords

## LineParser.py*
### Use JavaLang to tokenize and parse a single line of java code
usage: LineParser.py [-h] [-d DEBUG] [-l LINE]

optional arguments:
  -h, --help            show this help message and exit
  -d DEBUG, --debug DEBUG
                        Turn on debug mode.
  -l LINE, --line LINE  line to parse.

## NlpFeeder.py
### Generate json file of java lines for processing. Includes lines, individual words without syntax bloat, and the file the line was found in.
usage: NlpFeeder.py [-h] [-d DEBUG] [-p PATH]

optional arguments:
  -h, --help            show this help message and exit
  -d DEBUG, --debug DEBUG
                        Turn on debug mode.
  -p PATH, --path PATH  file to parse.

## SearchPhrases.py*
### Search for sensitive phrases.
usage: SearchPhrases.py [-h] [-d DEBUG] [-p PATH]

optional arguments:
  -h, --help            show this help message and exit
  -d DEBUG, --debug DEBUG
                        Turn on debug mode.
  -p PATH, --path PATH  file to parse.
