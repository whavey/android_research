#!/usr/bin/python3

import os
import JavaTreeManager as jtm
import json
import argparse
import javalang
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
        self.master_dict = {}
        self.ignore_structs = ["BasicType","Literal"]

    def setPath(self,path):
        self.path = path

    def ClassDeclaration(self,e):
        print("\nHandling Class")
        print("\tName:",e.name)
        return True

    def ClassCreator(self,e):
        print("\nHandling Class Creator")
        print(f"\tname: {e.type.name}")
        return True

    def FieldDeclaration(self,e):
        print("\nHandling Field Declaration")
        for declarator in e.declarators:
            print("\tName:",declarator.name)
        print("\tField Type:",e.type.name)
        if e.type.sub_type is not None:
            print("\tSubtype:",e.type.sub_type.name)
        return True

    def ReferenceType(self,e):
        print("\nHandling Reference Type")
        print(f"\tName: {e.name}")
        if e.sub_type is not None:
            print(f"\tSubtype Name: {e.sub_type.name}")
        return True

    def VariableDeclarator(self,e):
        print("\nHandling Variable Declarator")
        print(f"\tname: {e.name}")
        return True

    def ReturnStatement(self,e):
        print("\nHandling Return Statement")
        exp = str(type(e.expression)).split('.')[-1][0:-2]
        if exp in dir(self):
            getattr(self,exp)(e.expression)
        else:
            print(f"Make Handler for: {exp}")
        return True

    def MethodInvocation(self,e):
        print("\nHandling Method Invocation")
        print(f"\tname: {e.member}")
        return True

    def MethodDeclaration(self,e):
        print("\nHandling Method Declaration")
        print(f"\tname: {e.name}")
        return True

    def FormalParameter(self,e):
        print("\nHandling FormalParameter")
        print(f"\tname: {e.name}")
        return True

    def StatementExpression(self,e):
        print("\nHandling Statement Expression")
        exp = str(type(e.expression)).split('.')[-1][0:-2]
        if exp in dir(self):
            getattr(self,exp)(e.expression)
        else:
            print(f"Make Handler for: {exp}")

    def MemberReference(self,e):
        print("\nHandling MemberReference")
        print(f"\tname: {e.member}")
        return True

    def ArrayCreator(self,e):
        print("\nHandling ArrayCreator")
        print(f"\nname: {e.type.name}")
        return True

    def ArrayInitializer(self,e):
        print("\nHandling ArrayInitializer")
        for element in e.initializers:
            jstruct = str(type(element)).split('.')[-1][0:-2]
            if jstruct in dir(self):
                getattr(self,jstruct)(element)
            else:
                print(f"Make Handler for: {exp}")
        return True

    def LocalVariableDeclaration(self,e):
        print("\nHandling LocalVariableDeclaration")
        print(f"\nname: {e.type.name}")
        return True

    def This(self,e):
        print("\nHandling This")
        selectors = e.selectors
        if len(selectors) > 0:
            exp = str(type(selectors[0])).split('.')[-1][0:-2]
            if exp in dir(self):
                getattr(self,exp)(selectors[0])
            else:
                print(f"Make Handler for: {exp}")
        return True

    def Cast(self,e):
        print("\nHandling Cast")
        exp = str(type(e.expression)).split('.')[-1][0:-2]
        if exp in dir(self):
            getattr(self,exp)(e.expression)
        else:
            print(f"Make Handler for: {exp}")
        return True

    def getMethodsFound(self):
        for i in self.tree.types:
            for j in i:
                for k in j:
                    if type(k) == tuple:
                        continue
                    javastruct = str(type(k)).split('.')[-1][0:-2]
                    print(">")
                    if javastruct in dir(self):
                        getattr(self,javastruct)(k)
                    else:
                        if javastruct in self.ignore_structs:
                            continue
                        print(f"Make Handler for: {k}")
                    print("<")

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

    #print("Total:",pmf.getMethodsCount(),"\n")

    #for k in methodsFound.keys():
    #    print("File:",k,"\n","="*len(k),methodsFound[k],"\n")
