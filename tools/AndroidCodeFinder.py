#!/usr/bin/python3

import argparse
import os
import magic
import re
#import layout_parser as lp

def parse_args():
    parser = argparse.ArgumentParser(description='Parse Layout Files')
    parser.add_argument('-p','--path', default='.', type=str, help='Path to code files.')
    parser.add_argument('-s','--search_string', default='setOnClickListener', type=str, help='String to search methods for.')
    parser.add_argument('-d','--debug', type=str, help='Turn on debug mode.')
    return parser.parse_args()

class OnClickFinder:
    def __init__(self, *args, **kwargs):
        self.debug = True if args[0].debug else False
        self.method_list = []
        self.search_path = args[0].path
        self.search_string = args[0].search_string

    def getPath(self):
        return self.search_path

    def getSearchString(self):
        return self.search_string

    def getMethodList(self):
        self.searchForMethods(self.search_path)
        return self.method_list

    def runRegex(self,target):
        with open(target,'r') as searchme:
            for line_index, line in enumerate(searchme,1):
                try:
                    results = re.findall(f'.*{self.search_string}.*',line)
                    if self.debug:
                        print('Ran regex against:',target)
                    if results:
                        return [f"{line_index}: {x.replace(' ','')}" for x in results]

                except Exception as e:
                    if self.debug:
                        print('Exception trying to parse:',target,'\nReason:\n',e)

    def searchForMethods(self, path):
        self.search_path = path
        if os.path.isdir(path):
            for f in os.listdir(path):
                self.searchForMethods(os.path.join(path,f))
        else:
            ext = path.split('.')[-1] #type: {magic.from_file(path)[0:3]}")
            if ext == 'java':
                results = self.runRegex(path)
                if results:
                    results = [result.replace(' ','') for result in results]
                    self.method_list.append({path: results})

args = parse_args()
finder = OnClickFinder(args)

searchPath = finder.getPath()
searchString = finder.getSearchString()
print(f'searchPath: {searchPath}\nsearchString: {searchString}\nResults:\n========')
methodList = finder.getMethodList()

if methodList != []:
    for m in methodList:
        print('-',m)
else:
    print("No methods found for:",searchString)
