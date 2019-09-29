#!/usr/bin/python3

import javalang
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Parse Layout Files')
    parser.add_argument('-d','--debug', type=str, help='Turn on debug mode.')
    parser.add_argument('-p','--path', type=str, help='file to parse.')
    return parser.parse_args()

class JavaLanger:
    def __init__(self, *args, **kwargs):
        self.debug = args[0].debug

    def getTree(self, target):
        try:
            tree = javalang.parse.parse(target)
        except Exception as e:
            print("Error with target",target)
            if self.debug:
                print(e,'\n====')
            tree = False
        return tree



args = parse_args()
jl = JavaLanger(args)
with open(args.path,'r') as jfile:
        tree = jl.getTree(jfile.read())
        if tree:
            print("Package:",tree.package.name)
            for k,v in tree.types[0]:
                if type(v) == javalang.tree.ClassDeclaration:
                    print("\tClass:",v.name)
                for ck,cv in v:
                  #if type(cv) == javalang.tree.MethodDeclaration:
                  #    print("\t\tMethod Declaration:",cv.name)
                  if type(cv) == javalang.tree.MethodInvocation:
                      print("\t\tMethod Invocation:",cv.member)
