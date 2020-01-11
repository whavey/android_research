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
      self.path = ""

  # Getter for this trees package name.
  def getPackage(self):
      print(self.tree.package.name)

  def _checkViews(self,tree,parent):
      try:
          if tree.member == 'findViewById':
              print("\nFinding UI element:\n\t",tree,tree.arguments[0].member) #"\n\tParent:\n\t\t",parent)
          #if tree.member == 'setOnClickListener':
          #    print("\nSetting click listener for:\n\t",tree)
      except:
          #print("\n *Messed up on:\n\t",tree)
          pass


  # Getter for method declarations or invocations
  def getMethods(self,path):
      self.path = path
      for k,v in self.tree.types[0]:
          self._checkViews(v,k)
          for ck,cv in v:
              self._checkViews(cv,ck)
              for sk,sv in cv:
                  self._checkViews(sv,sk)
                  for vk,vv in sv:
                      self._checkViews(vv,vk)


# Class for managing all trees found in a searched directory of java files.
class JavaTreeManager:
    # Initialize object with args.
    def __init__(self, path=None, debug=False):
        if path:
            self.path = path
        else:
            self.path = os.getcwd()

    # Recursively make JavaTreeParser objects for each java tree made.
    # Should be careful with this class as Im not sure how making JavaCodeParser objects for each tree will scale without memory management.
    def parseAllTrees(self,path=None):
      if path is None:
          path = self.path
      if os.path.isdir(path):
          for f in os.listdir(path):
                self.parseAllTrees(os.path.join(path,f))
      else:
          if path.split('.')[-1] == 'java':
            tree = self.getTree(path)
            if tree:
                JavaTreeParser(tree).getMethods(path)
          else:
            print('skipping:',path)

    # Getter for java.compilationUnit treelike object
    def getTree(self, target=None):
        if not target:
            target = self.path
        try:
            with open(target,'r') as _target:
                tree = javalang.parse.parse(_target.read())
        except Exception as e:
            #print("Error with target",target)
            tree = False
        return tree

if __name__ == "__main__":
    # Parse args and initialize object with args.
    args = parse_args()
    jl = JavaTreeManager(path=args.path,debug=args.debug)
    lp = LineParser(args)
    lp.parseLine()
