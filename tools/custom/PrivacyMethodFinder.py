#!/usr/bin/python3

import os
import JavaTreeManager as jtm
import json
import argparse
import sys

def parser():
    parser = argparse.ArgumentParser(description='Print Private Info Collecting Methods.')
    parser.add_argument('-p','--path', type=str, help='path to file(s)')
    parser.add_argument('-d','--debug', type=str, help='toggle debug mode.')
    return parser

class PrivacyMethodFinder:
    def __init__(self, tree=None, *args, **kwargs):
        if not tree:
            if args:
                tree = jtm.JavaTreeManager(args[0].path).getTree()
                self.tree = tree
            else:
                print("Must pass a JavaTreeManager tree or a path to a java file(s)")
                print(args)
                return False
        else:
            self.tree = tree

        self.method_count = 0
        self.methods_found = {}

    def setPath(self,path):
        self.path = path

    def getMethodsFound(self):
        for i in self.tree.types:
            print(i,"\n")
        #for k,v in self.tree.types[0]:
        #    print("="*50,"\nK:\n",k,"\nV:\n",v,"\n")

    def getMethodsCount(self):
        return self.methods_found

    def findMethods(self):
        return


if __name__ == "__main__":
    parser = parser()
    args = parser.parse_args()
    if not args.path:
       print(parser.print_help())
       sys.exit()

    tree = jtm.JavaTreeManager(args).getTree()

    pmf = PrivacyMethodFinder(tree)
    methodsFound = pmf.getMethodsFound()

    print("Total:",pmf.getMethodsCount(),"\n")

    for k in methodsFound.keys():
        print("File:",k,"\n","="*len(k),methodsFound[k],"\n")
