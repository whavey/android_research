#!/usr/bin/python36

import xml.etree.ElementTree as ET
import sys
import os
import shutil
import argparse
import re
import magic

def parse_args():
    parser = argparse.ArgumentParser(description='Parse Layout Files')
    parser.add_argument('-p','--path', type=str, help='path to layout files')
    parser.add_argument('-s','--scan_type', type=str, help='print all xml tags per file')
    parser.add_argument('-d','--debug', type=str, help='toggle debug mode.')
    return parser.parse_args()

class LayoutScanner:
    # Initializer.
    # UI_keys are the specific xml tags to look for.
    # Main return object is a dict.
    # names space string used to help parse xml.
    def __init__(self, *args, **kwargs):
        self.ui_keys = ['Button','EditText','CheckBox','RadioButton']
        self.all_elements = []
        self.scan_path = ''
        self.results = {}
        self.ns = {'res':'{http://schemas.android.com/apk/res/android}'}
        self.debug = args[0].debug


    # Setter and Getter for the UI keys to look for
    def setUIKeys(self, ui_keys):
        self.ui_keys = ui_keys
    def getUIKeys(self):
        return self.ui_keys

    # Method to check just UI keys. Gets onClick tag and id tag. (onClick doesnt always exist).
    def checkUIKeys(self,root):
        master_dict = {} # local dict to append to and return.
        # Check each import UI element type specified.
        for ui in self.ui_keys:
            ui_list = [] # Local list of tags found to set as value for UI element type key.
            for e in root.iter(ui):
                ui_list.append(e.get(f'{self.ns["res"]}onClick'))
                ui_list.append(e.get(f'{self.ns["res"]}id'))
            master_dict[ui] = ui_list
        return master_dict

    # Method to tree xml tree and tree-root.
    def getTree(self,xml):
        # use magic to check if XML file first to not waste time.
        if magic.from_file(xml)[0:3] != 'XML':
            if self.debug:
                print("skipping:",xml," => NOT XML")
            return
        # Try to get the xml tree and root.
        try:
           tree = ET.parse(xml)
           root = tree.getroot()
        except Exception as e:
            print("Error parsing xml for file:", xml, "\n", e, "\n")
            return
        return tree,root

    # Recursively check for files to parse. 
    def iterateDir(self, path, scan_type):
        self.scan_path = path
        if os.path.isdir(path):
            for f in os.listdir(path):
                self.iterateDir(os.path.join(path,f), scan_type)
        else:
            # Run parser
            res = self.getTree(path)
            if not res:
                return
            tree,root = res
            # Check if only parsing for UI elements or for all tags.
            if scan_type == 'important':
                self.results[path] = self.checkUIKeys(root)
            elif scan_type == 'tags':
                tags = []
                for e in root.iter():
                    tags.append(e.tag)
                self.results[path] = set(tags)

    # getter for all xml tags
    def getAllTags(self, path):
        self.scan_path = path
        self.iterateDir(path, 'tags')

    # getter for important UI xml tags 
    def getUITags(self, path):
        self.scan_path = path
        self.iterateDir(path, 'important')

    # Outputter
    def printResults(self):
        for k in self.results.keys():
            # If printing all xml tags just print them.
            if type(self.results[k]) == set:
                print(k)
                for t in self.results[k]:
                    print('\t',t)

            # if printing important UI tags format a little better.
            else:
                for key in self.ui_keys:
                    # Only print results for a specific UI type if results were found.
                    if len(self.results[k][key]) > 0:
                        print(f'{k}\n\t{key}s:')
                        for i in self.results[k][key]:
                            print(f'\t\t{i}')

def main():
    # Parse args and initialize object.
    args = parse_args()
    scanner = LayoutScanner(args)

    # if no path specified then use current working directory as default.
    path = args.path if args.path else os.getcwd()

    # Can grab all the tags instead of just the UI keys if specified.
    if args.scan_type == 'tags':
        scanner.getAllTags(path)
    else:
        scanner.run(path)

    # Call outputter for resutls
    scanner.printResults()

if __name__ == '__main__':
    main()
