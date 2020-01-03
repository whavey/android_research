#!/usr/bin/python3

import argparse
import string
import json
import os
import magic
import re
import LineParser as lp
import JavaTreeManager as jtm

def parse_args():
    parser = argparse.ArgumentParser(description='Parse Layout Files')
    parser.add_argument('-p','--path', default='.', type=str, help='Path to code files.')
    parser.add_argument('-d','--debug', type=str, help='Turn on debug mode.')
    parser.add_argument('-o','--output', type=str, help='File to write to.')
    return parser.parse_args()

class NlpFeeder:
    def __init__(self, *args, **kwargs):
        if args[0].output:
            self.output = args[0].output
        else:
            self.output = "food.json"
        self.debug = args[0].debug
        self.food = {}
        self.search_path = args[0].path
        self.parsers = [line.replace('\n','') for line in open('parsers.txt','r')]

    def getPath(self):
        return self.search_path
    def setSearchString(self,search_string):
        self.search_string = search_string
    def getSearchString(self):
        return self.search_string

    def _parse(self,parserObj,parserType):
        p = parserObj.getParser()
        try:
            return getattr(p,parserType)()
        except:
            return False

    def _runParsers(self,parserObj):
        for p in self.parsers:
            res = self._parse(parserObj,p)
            if res:
                return res

    def parseLine(self,target):
        with open(target,'r') as searchme:
            self.food[target] = []
            if self.debug:
                print('Running parser against:',target)
            for line in searchme:
                _res = False
                words = re.findall(r"[\w]+",line )
                if not words:
                    continue

                checkComment = line.lstrip()[0:2]
                if  checkComment == "//" or checkComment == "/*":
                    _type = "comment"
                else:
                    parser = lp.LineParser(line=line)
                    validParsers = parser.getValidParsers()
                    _res = self._runParsers(parser)
                    _type = str(type(_res)).split('.')[-1].replace('\'>','')
                if not _res:
                    _type = 'unknown'
                out = {"file":target, "type": _type,"words": words,"line":line.lstrip().replace('\n','')}
                self.food[target].append(out)
                print(json.dumps(out),file=open(self.output,'a+'))

    def genFeeder(self,path=None):
        if not self.search_path and not path:
            print("No Path Given")
            return

        if path:
          self.search_path = path
        else:
          path = self.search_path

        if os.path.isdir(path):
            for f in os.listdir(path):
                self.genFeeder(os.path.join(path,f))
        else:
            self.parseLine(path)
        return self.food

if __name__ == '__main__':
    # Parse args and create object
    args = parse_args()
    feeder = NlpFeeder(args)

    # Do the search
    food = feeder.genFeeder()
    print(json.dumps(food))
