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
    parser.add_argument('-o','--out', type=str, help='output to file')
    return parser.parse_args()

class LayoutScanner:
    def __init__(self):
        self.ui_keys = ['Button','EditText','CheckBox','RadioButton']
        self.all_elements = []
        self.scan_path = ''
        self.results = {}
        self.ns = {'res':'{http://schemas.android.com/apk/res/android}'}

    def setUIKeys(self, ui_keys):
        self.ui_keys = ui_keys

    def getUIKeys(self):
        return self.ui_keys

    def checkUIKeys(self,root):
        master_dict = {}
        for ui in self.ui_keys:
            ui_list = []
            for e in root.iter(ui):
                ui_list.append(e.get(f'{self.ns["res"]}onClick'))
            master_dict[ui] = ui_list
        return master_dict

    def checkTags(self,root):
        tags = []
        for e in root.iter():
            tags.append(e.tag)
        return set(tags)

    def getTree(self,xml):
        if magic.from_file(xml)[0:3] != 'XML':
            print("skipping:",xml," => NOT XML")
            return
        try:
           tree = ET.parse(xml)
           root = tree.getroot()
        except Exception as e:
            print("Error parsing xml for file:", xml, "\n", e, "\n")
            return
        return tree,root

    def iterateDir(self, path, scan_type):
        self.scan_path = path
        if os.path.isdir(path):
            for f in os.listdir(path):
                self.iterateDir(os.path.join(path,f), scan_type)
        else:
            res = self.getTree(path)
            if not res:
                return
            tree,root = res
            if scan_type == 'important':
                self.results[path] = self.checkUIKeys(root)
            elif scan_type == 'tags':
                self.results[path] = self.checkTags(root)

    def getAllTags(self, path):
        self.scan_path = path
        self.iterateDir(path, 'tags')

    def run(self, path):
        self.scan_path = path
        self.iterateDir(path, 'important')

    def printResults(self):
        for k in self.results.keys():
            if type(self.results[k]) == set:
                print(k)
                for t in self.results[k]:
                    print('\t',t)
            else:
                for key in self.ui_keys:
                    if len(self.results[k][key]) > 0:
                        print(f'{k}\n\t{key}s:')
                        for i in self.results[k][key]:
                            print(f'\t\t{i}')

if __name__ == '__main__':
    args = parse_args()
    scanner = LayoutScanner()
    path = args.path if args.path else os.getcwd()
    if args.scan_type == 'tags':
        scanner.getAllTags(path)
    else:
        scanner.run(path)

    scanner.printResults()

