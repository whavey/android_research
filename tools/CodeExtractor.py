#!/usr/bin/python3

import os
import JavaTreeManager as jtm
import json
import argparse
import javalang
import sys
import inspect

def parser():

    parser = argparse.ArgumentParser(description='Get Java Structure to code mappings.')
    parser.add_argument('-p','--path', type=str, help='path to file(s)')
    parser.add_argument('-d','--debug', type=str, help='toggle debug mode.')
    parser.add_argument('-o','--output', default='.', type=str, help='output directory')

    return parser

class CodeExtractor:

    def __init__(self, *args, **kwargs):

        self.tree = False
        self.processed_files = []
        self.master_dict = {}
        self.ignore_structs = ["BasicType","Literal","ForControl","ArraySelector"]
        self.make_handlers_for = []


    def setProcessedFile(self,f):

        self.processed_files.append(f)


    def getProcessedFiles(self):

        return self.processed_files


    def setIgnoreStructs(self,ignore_structs):

        self.ignore_structs = list(ignore_structs)


    def getUnhandled(self):

        return self.make_handlers_for


    def getResults(self):

        return self.master_dict


    def setPath(self,path):

        self.path = path


    def setTree(self,tree):

        self.tree = tree


    def uniqueAdd(self,jstruct,word):

        if jstruct in self.master_dict.keys():

            if word not in self.master_dict[jstruct].keys():

                self.master_dict[jstruct].append(word)

        else:

            self.master_dict[jstruct] = [word]


    def countAdd(self,jstruct,word):

        if len(word) == 1:
            return

        if jstruct in self.master_dict.keys():

            if word in self.master_dict[jstruct].keys():

                self.master_dict[jstruct][word] += 1

            else:

                self.master_dict[jstruct][word] = 1

        else:

            self.master_dict[jstruct] = {word:1}


    def ClassDeclaration(self,e):

        #print("\nHandling Class")
        #print("\tName:",e.name)
        self.countAdd(inspect.stack()[0][3],e.name)

        #for elem in e.body:

        #    self.check_and_parse(elem)


    def ClassCreator(self,e):

        #print("\nHandling Class Creator")
        #print(f"\tname: {e.type.name}")
        self.countAdd(inspect.stack()[0][3],e.type.name)


    def FieldDeclaration(self,e):

        #print("\nHandling Field Declaration")

        for declarator in e.declarators:

            #print("\tName:",declarator.name)
            self.countAdd(inspect.stack()[0][3],declarator.name)

        #print("\tField Type:",e.type.name)
        #self.countAdd("Field Declaration Field Type",e.type.name)

        #if e.type.sub_type is not None:

            #print("\tSubtype:",e.type.sub_type.name)
            #self.countAdd("Field Declaration Sub Type",e.type.sub_type.name)


    def ReferenceType(self,e):

        #print("\nHandling Reference Type")
        #print(f"\tName: {e.name}")
        self.countAdd(inspect.stack()[0][3],e.name)

        if e.sub_type is not None:

            #print(f"\tSubtype Name: {e.sub_type.name}")
            self.countAdd("Reference Type Sub Type",e.sub_type.name)


    def VariableDeclarator(self,e):

        #print("\nHandling Variable Declarator")
        #print(f"\tname: {e.name}")
        self.countAdd(inspect.stack()[0][3],e.name)


    def ReturnStatement(self,e):

        #print("\nHandling Return Statement")
        self.check_and_parse(e.expression)


    def MethodInvocation(self,e):

        #print("\nHandling Method Invocation")
        #print(f"\tname: {e.member}")
        self.countAdd(inspect.stack()[0][3],e.member)


    def MethodDeclaration(self,e):

        #print("\nHandling Method Declaration")
        #print(f"\tname: {e.name}")
        self.countAdd(inspect.stack()[0][3],e.name)

        #for elem in e.body:

        #    self.check_and_parse(elem)


    def FormalParameter(self,e):

        #print("\nHandling FormalParameter")
        #print(f"\tname: {e.name}")
        self.countAdd(inspect.stack()[0][3],e.name)


    def StatementExpression(self,e):

        #print("\nHandling Statement Expression")
        self.check_and_parse(e.expression)


    def MemberReference(self,e):

        #print("\nHandling MemberReference")
        #print(f"\tname: {e.member}")
        self.countAdd(inspect.stack()[0][3],e.member)


    def ArrayCreator(self,e):

        #print("\nHandling ArrayCreator")
        #print(f"\nname: {e.type.name}")
        self.countAdd(inspect.stack()[0][3],e.type.name)


    def ArrayInitializer(self,e):

        #print("\nHandling ArrayInitializer")
        for element in e.initializers:

            self.check_and_parse(element)


    def LocalVariableDeclaration(self,e):

        #print("\nHandling LocalVariableDeclaration")
        #print(f"\nname: {e.type.name}")
        self.countAdd(inspect.stack()[0][3],e.type.name)


    def This(self,e):

        #print("\nHandling This")
        selectors = e.selectors

        if len(selectors) > 0:

            for selector in selectors:

                self.check_and_parse(selector)


    def Cast(self,e):

        #print("\nHandling Cast")
        self.check_and_parse(e.expression)


    def Assignment(self,e):

        #print("\nHandling Assignment")
        #print("\nAssignee:")
        self.check_and_parse(e.expressionl)
        #print("\nValue:")
        self.check_and_parse(e.value)


    def SuperMethodInvocation(self,e):

        #print("\nHandling Super Method Invocation")
        #print(f"\nMember: {e.member}")
        self.countAdd(inspect.stack()[0][3],e.member)


    def IfStatement(self,e):

        #print("\nHandling If Statement")
        #print("\nParsing Condition")
        self.check_and_parse(e.condition)
        #print("\nChecking else statement")
        self.check_and_parse(e.else_statement)
        #print("\nChecking then statement")
        self.check_and_parse(e.then_statement)


    def BlockStatement(self,e):

        #print("\nHandling Block Statement")
        statements = e.statements

        if len(statements) > 0:

            for statement in statements:

                self.check_and_parse(statement)


    def BinaryOperation(self,e):

        #print("\nHandling Binary Operation")
        #print("\nleft operand:")
        self.check_and_parse(e.operandl)
        #print("\nright operand:")
        self.check_and_parse(e.operandr)
        #print("\nOperator:",e.operator)


    def TypeArgument(self,e):

        #print("\nHandling Type Argument")
        self.check_and_parse(e.type)


    def VariableDeclaration(self,e):

        #print("\nHandling Variable Declaration")
        declarators = e.declarators

        if len(declarators) > 0:

            for declarator in declarators:

                self.check_and_parse(declarator)


    def ForStatement(self,e):

        #print("\nHandling For Statement")
        self.check_and_parse(e.body)


    def ConstructorDeclaration(self,e):

        #print("\nHandling Constructor Declaration")
        #print(f"\nName:{e.name}")
        self.countAdd(inspect.stack()[0][3],e.name)


    def ThrowStatement(self,e):

        self.check_and_parse(e.expression)


    def Annotation(self,e):

        self.countAdd(inspect.stack()[0][3],e.name)


    def SwitchStatement(self,e):

        for case in e.cases:

            self.check_and_parse(case)


    def SwitchStatementCase(self,e):

        for statement in e.statements:

            self.check_and_parse(statement)


    def check_and_parse(self,structure):

        if structure is None:

            #print("\nNo structure given")
            return False

        if type(structure) is list:

            for struct in structure:

                self.check_and_parse(struct)

        struct_type = str(type(structure)).split('.')[-1][0:-2]

        if struct_type in dir(self):

            getattr(self,struct_type)(structure)

        else:

            if struct_type in self.ignore_structs:

                return False

            self.make_handlers_for.append(structure)


    def getNlpCandidates(self):

        # I think this would be the proper way to do it and then call each child element
        # from the class handler down.
        #self.check_and_parse(self.tree.types[0])

        # This is the way Im doing it for now because its quicker.
        for classChild in self.tree.types:

            for elemChild in classChild:

                for child in elemChild:

                    if type(child) == tuple:

                        continue

                    self.check_and_parse(child)


# Heather: TODO: Needs Threading 
# Process Single File
def processFile(javaFile,ceObject):

    ext = javaFile.split('.')[-1] #type: {magic.from_file(path)[0:3]}")

    if ext == 'java':

        tree = jtm.JavaTreeManager(path=javaFile).getTree()

        if not tree:

            print("Error getting javalang tree for:", javaFile)
            return

        ceObject.setTree(tree)
        nlpCandidates = ceObject.getNlpCandidates()


def main(path,ceObject=None,output_directory='.'):

    if not ceObject:

        ceObject = CodeExtractor()

    if not os.path.isdir(path):

        print("File Processing:",path)
        processFile(path,ceObject)

    else:

        for dirName, subdirList, fileList in os.walk(path):

            currCount = 0
            totalFiles = len(fileList)

            for fname in fileList:

                if fname == "R.java":

                    continue

                f = os.path.join(dirName,fname)
                processFile(f,ceObject)
                ceObject.setProcessedFile(f)

                results = ceObject.getResults()
                processed = ceObject.getProcessedFiles()

                if results:

                    potential_names = path.split('/')
                    resName = False

                    for pn in potential_names:

                        if pn[0:3] == ('com' or 'org'):

                            resName = pn
                            break

                    if not resName:

                        resName = path.replace('/','_')


                    with open(f"{output_directory}/structmappings-{resName}",'w') as fhandle:

                        fhandle.write(json.dumps(results))

                    currCount += 1
                    print(f"\tProcessing files: {currCount} / {totalFiles}",end="\r",flush=True )

    #print(f"\nProcessed:\n{'='*len('Processed')}")

    #for f in processed:

    #    print(f)


if __name__ == "__main__":

    parser = parser()
    args = parser.parse_args()

    if not args.path:

       print(parser.print_help())
       sys.exit()

    main(args.path,None,args.output)
