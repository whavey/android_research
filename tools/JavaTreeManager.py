#!/usr/bin/python3

# Wayne Havey
# 2019

import javalang
import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser(description='Parse Layout Files')
    parser.add_argument('-d','--debug', type=str, help='Turn on debug mode.')
    parser.add_argument('-p','--path', type=str, help='file to parse.')
    return parser.parse_args()

# Class for parsing a single java code tree
class JavaTreeParser:
  # Initializer for this tree parser object
  def __init__(self, tree):
      self.tree = tree
      self.classDeclarations = []
      self.methodDeclarations = []
      self.methodInvocations = []
      self.fieldDeclarations = []

  # Getter for this trees package name.
  def getPackage(self):
      print(self.tree.package.name)

  # Getter for method declarations or invocations
  def getMethods(self):
      for k,v in self.tree.types[0]:
          #print("Type:", v, '\n')
          if type(v) == javalang.tree.ClassDeclaration:
              #print("\tClass:",v.name)
              for ck,cv in v:
                  if type(cv) == javalang.tree.StatementExpression:
                      for sk,sv in cv:
                          if type(sv) == javalang.tree.MethodInvocation:
                              if sv.member == 'setOnClickListener':
                                  print("Setting click listener for:",cv.expression.selectors[0].member)
                          if type(sv) == javalang.tree.Assignment:
                              for vk,vv in sv.value:
                                  #print(vv,'\n')
                                  if type(vv) == javalang.tree.MethodInvocation:
                                    if vv.member == 'findViewById':
                                          print("Assigning",vv.arguments[0].member,"UI element to variable:", sv.expressionl.selectors[0].member)

                  #if type(cv) == javalang.tree.MethodInvocation:
                  #    if cv.member == "findViewById":
                  #        if cv.arguments[0].member == 'sendButton':
                  #            print(ck)
          #        if type(cv) == javalang.tree.MethodDeclaration:
          #            print("\t\tMethod Declaration:",cv.name)
          #        if type(cv) == javalang.tree.MethodInvocation:
          #            print("\t\tMethod Invocation:",cv.member)

# Class for managing all trees found in a searched directory of java files.
class JavaTreeManager:
    # Initialize object with args.
    def __init__(self, *args, **kwargs):
        self.debug = args[0].debug
        self.path = args[0].path

    # Recursively make JavaTreeParser objects for each java tree made.
    # Should be careful with this class as Im not sure how making JavaCodeParser objects for each tree will scale without memory management.
    def parseAllTrees(self,path=None):
      if path is None:
          path = self.path
      if os.path.isdir(path):
          for f in os.listdir(path):
              self.parseAllTrees(os.path.join(path,f))
      else:
          tree = self.getTree(path)
          if tree:
              print("\nResults for:", path, '\n'+'='*len("results for: "+path))
              JavaTreeParser(tree).getMethods()

    # Getter for java.compilationUnit treelike object
    def getTree(self, target):
        try:
            with open(target,'r') as _target:
                tree = javalang.parse.parse(_target.read())
        except Exception as e:
            print("Error with target",target)
            if self.debug:
                print(e,'\n====')
            tree = False
        return tree

# Parse args and initialize object with args.
args = parse_args()
jl = JavaTreeManager(args)
jl.parseAllTrees()

