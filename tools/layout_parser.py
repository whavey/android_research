#!/usr/bin/python36

import xml.etree.ElementTree as ET
import os
import shutil
import argparse
import re

def parse_args():
    parser = argparse.ArgumentParser(description='Parse Layout Files')
    parser.add_argument('-p','--path', type=str, help='path to layout files')
    parser.add_argument('-o','--out', type=str, help='output to file')
    return parser.parse_args()

args = parse_args()

class LayoutScanner:
    def __init__(self,path):
        self.ui_keys = ['Button','EditText','CheckBox']
        self.results = {}
        self.scan_path = path
        self.ns = {'res':'{http://schemas.android.com/apk/res/android}'}

    def setUIKeys(self, ui_keys):
        self.ui_keys = ui_keys

    def getUIKeys(self):
        return self.ui_keys

    def walkTree(self,root):
        master_dict = {}
        for ui in self.ui_keys:
            ui_list = []
            for e in root.iter(ui):
                ui_list.append(e.get(f'{self.ns["res"]}id'))
            master_dict[ui] = ui_list
        return master_dict

    def getTree(self,xml):
        try:
           tree = ET.parse(os.path.join(self.scan_path,xml))
           root = tree.getroot()
           self.results[xml] = self.walkTree(root)
        except Exception as e:
            print("Error parsing xml for file:", xml, "\n", e, "\n")

    def iteratePath(self):
        if os.path.isdir(self.scan_path):
            for f in os.listdir(self.scan_path):
                self.getTree(f)
        else:
            self.getTree(self.scan_path)
        return self.results

def main():
    path = args.path if args.path else os.getcwd()
    scanner = LayoutScanner(path)
    results = scanner.iteratePath()
    for k in results.keys():
        for key in scanner.getUIKeys():
            if len(results[k][key]) > 0:
                print(f'{k}\n\t{key}s:')
                for i in results[k][key]:
                    print(f'\t\t{i}')




main()
