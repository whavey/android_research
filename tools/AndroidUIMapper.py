#!/usr/bin/python3

import argparse
import javalang
import AndroidCodeFinder
import LineParser
import json

def parse_args():
    parser = argparse.ArgumentParser(description='Parse Layout Files')
    parser.add_argument('-d','--debug', type=str, help='Turn on debug mode.')
    parser.add_argument('-l','--line', type=str, help='line to parse.')
    parser.add_argument('-p','--path', type=str, help='file to parse.')
    parser.add_argument('-s','--search_string', default='setOnClickListener', type=str, help='String to search methods for.')
    return parser.parse_args()

args = parse_args()
finder = AndroidCodeFinder.AndroidCodeFinder(args)
finder.setSearchString('findViewById')

lp = LineParser.LineParser(args)

methodList = finder.getMethodList()

# Print out json-ified results if exists. 
if methodList != []:
    for m in methodList:
        for target in m.keys():
            print("begin","="*60,'\n',target)
            for line in m[target]:
                for l in line.values():
                    lp.parseUIAssignment(l)
            print("end","="*60)
else:
    print("No Lines found for: 'findViewById'")
