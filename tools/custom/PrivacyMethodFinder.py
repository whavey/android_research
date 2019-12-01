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
        self.ignore_structs = ["BasicType","Literal","ForControl"]

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
        self.check_and_parse(e.expression)

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
        self.check_and_parse(e.expression)

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
            self.check_and_parse(element)

    def LocalVariableDeclaration(self,e):
        print("\nHandling LocalVariableDeclaration")
        print(f"\nname: {e.type.name}")
        return True

    def This(self,e):
        print("\nHandling This")
        selectors = e.selectors
        if len(selectors) > 0:
            for selector in selectors:
                self.check_and_parse(selector)

    def Cast(self,e):
        print("\nHandling Cast")
        self.check_and_parse(e.expression)

    def Assignment(self,e):
        print("\nHandling Assignment")
        print("\nAssignee:")
        self.check_and_parse(e.expressionl)
        print("\nValue:")
        self.check_and_parse(e.value)

    def SuperMethodInvocation(self,e):
        print("\nHandling Super Method Invocation")
        print(f"\nMember: {e.member}")
        return True

    def IfStatement(self,e):
        print("\nHandling If Statement")
        print("\nParsing Condition")
        self.check_and_parse(e.condition)
        print("\nChecking else statement")
        self.check_and_parse(e.else_statement)
        print("\nChecking then statement")
        self.check_and_parse(e.then_statement)

    def BlockStatement(self,e):
        print("\nHandling Block Statement")
        statements = e.statements
        if len(statements) > 0:
            for statement in statements:
                self.check_and_parse(statement)

    def BinaryOperation(self,e):
        print("\nHandling Binary Operation")
        print("\nleft operand:")
        self.check_and_parse(e.operandl)
        print("\nright operand:")
        self.check_and_parse(e.operandr)
        print("\nOperator:",e.operator)

    def TypeArgument(self,e):
        print("\nHandling Type Argument")
        self.check_and_parse(e.type)

    def VariableDeclaration(self,e):
        print("\nHandling Variable Declaration")
        declarators = e.declarators
        if len(declarators) > 0:
            for declarator in declarators:
                self.check_and_parse(declarator)

    def ForStatement(self,e):
        print("\nHandling For Statement")
        self.check_and_parse(e.body)

    def ConstructorDeclaration(self,e):
        print("\nHandling Constructor Declaration")
        print(f"\nName:{e.name}")

    def check_and_parse(self,structure):
        if structure is None:
            print("\nNo structure given")
            return False
        struct_type = str(type(structure)).split('.')[-1][0:-2]
        if struct_type in dir(self):
            getattr(self,struct_type)(structure)
        else:
            if struct_type in self.ignore_structs:
                return False
            print(f"Make Handler for: {structure}")
        return True

    def getMethodsFound(self):
        for i in self.tree.types:
            for j in i:
                for k in j:
                    if type(k) == tuple:
                        continue
                    print(">")
                    self.check_and_parse(k)
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
