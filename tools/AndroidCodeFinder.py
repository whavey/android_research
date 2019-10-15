#!/usr/bin/python3

import argparse
import json
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

class AndroidCodeFinder:
    # Initialize with search string and search path from args. Main return value is method list.
    def __init__(self, *args, **kwargs):
        self.debug = True if args[0].debug else False
        self.method_list = []
        self.search_path = args[0].path
        self.search_string = args[0].search_string

    # Getter for path.
    def getPath(self):
        return self.search_path

    def setSearchString(self,search_string):
        self.search_string = search_string

    # Getter for search string.
    def getSearchString(self):
        return self.search_string

    # Getter for files containing search string.
    def getMethodList(self):
        self._searchForMethods(self.search_path)
        return self.method_list

    # Internal Method for use by _searchForMethods.
    # Does the actual searching 
    def _runRegex(self,target):
        with open(target,'r') as searchme:
            if self.debug:
                print('Running regex against:',target)
            results = [] # local result list initialize

            # Search the file one line at a time. Maybe could thread this.
            for line_index, line in enumerate(searchme,1):
                try:
                    _results = re.findall(f'.*{self.search_string}.*',line)
                    if _results:
                        # return dict of line number in file as key and actual line minus leading whitespace as value.
                        results.append({line_index: x.lstrip() for x in _results})

                except Exception as e:
                    if self.debug:
                        print('Exception trying to parse:',target,'\nReason:\n',e)
            if results:
                return results

    # Internal method for use by getMethodList. Recursively search files and call _runRegex on them.
    def _searchForMethods(self, path):
        self.search_path = path

        # Recursively search for files
        if os.path.isdir(path):
            for f in os.listdir(path):
                self._searchForMethods(os.path.join(path,f))
        else:
            # Check file extension to not waste time on non-java files.
            # magic was unreliable in this case, returning more than one type for java files.
            # just looking at the extension seems easier that trying to maintain a list of potential magic types returned.
            ext = path.split('.')[-1] #type: {magic.from_file(path)[0:3]}")
            if ext == 'java':
                results = self._runRegex(path)

                # append each files results to master return list as a dict.
                if results:
                    if self.debug:
                        print('Found specified lines in:',path)
                    self.method_list.append({path: results})

if __name__ == '__main__':
    # Parse args and create object
    args = parse_args()
    finder = AndroidCodeFinder(args)

    # Get current path and strings for display
    # TODO: probably want to format output to a real format like yaml.
    searchPath = finder.getPath()
    searchString = finder.getSearchString()
    print(f'searchPath: {searchPath}\nsearchString: {searchString}\nResults:\n========')

    # Do the search
    methodList = finder.getMethodList()

    # Print out json-ified results if exists. 
    if methodList != []:
        for m in methodList:
            print(json.dumps(m))
    else:
        print("No methods found for:",searchString)
