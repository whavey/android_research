#!/usr/bin/python3

import colorama
from colorama import Fore,Style
import os
import JavaTreeManager as jtm
import json
import argparse
import javalang
import sys
import inspect
import glob
import pandas
import multiprocessing
import hashlib
from multiprocessing import Process

def parser():

    parser = argparse.ArgumentParser(description='Get Java Structure to code mappings.')
    parser.add_argument('-p','--path', type=str, help='path to file(s)')
    parser.add_argument('-d','--debug', type=str, help='toggle debug mode.')
    parser.add_argument('-o','--output', default='.', type=str, help='output directory')

    return parser

class CodeExtractor:

    def __init__(self, *args, **kwargs):

        self.tree = False
        self.max_processes = 1019# multiprocessing.cpu_count()*8
        self.output_directory = '.'
        self.tree_errors = []
        self.processed_files = []
        self.master_dict = {}
        self.ignore_structs = ["BasicType","Literal","ForControl","ArraySelector"]
        self.make_handlers_for = []
        self.skipdirs = [
                'me', 'androidx', 'kotlin', 'javax', 'io', 'bolts',
                'android', 'fi', 'okhttp3', 'okio', 'defpackage', 'bitter',
                'cpro', 'retrofit2', 'van', 'developers', 'universal', 'cn',
                'cz', 'a', 'paperparcel', 'b', 'rx', 'p008do',
                'p003for', 'p004if', 'kotlinx', 'dagger', 'de', 'jp',
                'shared', 'plugin', 'network', 'CoronaProvider', 'missing', 'j$',
                'watevra', 'ca', 'w', 'p', 's', 'h',
                'timber', 'u', 'x', 'j', 't', 'n',
                'i', 'q', 'firebase', 'k', 'butterknife', 'v',
                'o', 'r', 'm', 'l', 'ffimageloading',
                'xamarin', 'mono',  
                'opentk', 'opentk_1_0', 
                'c', 'e', 'd', 'f', 'pub', 'p010if', 'p009for',
                'p003do', 'g', 'ru', 'hu', 'tv', 'twitter4j',
                'uk', 'zendesk', 'proguard', 'at', 'bo', 'pl',
                'retrofit', 'junit', 'freemarker', 'oauth', 'ch', 'name',
                'cordova', 'nl', 'fr', 'br', 'lib', 'roboguice',
                'leakcanary', 'se', 'oooooo', 'nnnnnn', 'social', 'googledata',
                'gen_binder', 'logs', 'siftscience', 'nucleus', 'permissions', 'chirpconnect',
                'go', 'by', 'scratch', 'in', 'im', 'info',
                'icepick', 'it', 'z', 'no', 'teads', 'carbon',
                'eu', 'aa', 'ubermedia', 'main', 'app', 'repackaged',
                'drinkless', 'avro', 'autovalue', 'video', 'audio', 'haymaker',
                'kotterknife', 'auto', 'companion', 'blur', 'J', 'tvo',
                'secondary', 'java', 'eightbitlab', 'mobileads', 'unitydirectionkit', 'okhttp3copy',
                'spacemadness', 'au', 'retrofit2copy', 'squareup', 'okiocopy', 'p010for',
                'p000do', 'p011if', 'air', 'Microsoft', 'Ms', 'ly',
                'microsoft', 'b0', 'g0', 'c0', 'f0', 'a0',
                'd0', 'h0', 'e0', 'fm', 'y', 'okreplay',
                'xyz', 'moe', 'xmlwise', 'rx_activity_result2', 'afu', 'libcore',
                'comms', 'bigo', 'sg', 'es', 'mbanje', 'test',
                'inshot', 'us', 'mobi', 'arch', 'project', 'flipboard',
                'ie', 'tdt', 'vdgk', 'pwz', 'qmm', 'snapchat',
                'sns', 'X', 'v2signature', 'cat', 'beancopy', 'dmt',
                'gen', 'conan', 'demo', 'toothpick', 'brut', 'theoremreach',
                'lombok', 'amazon', 'coreplaybackplugin', 'jumio', 'jcifs', 'collections',
                'cl', 'bb', 'gs', 'be', 'ff', 'ai', 'db', 
                'md52784b6b6564df579ab09ba8bad5c54dd', 
                'md56aabda7acd4abaa2b1d1169cd8c7c6ee',
                'md58432a647068b097f9637064b8985a5e0', 
                'md51558244f76c53b6aeda52c8a337f2c37', 
                'md5adcd58131f4046b9abfeb77bd8cc5019',
                'md583c97a0310bc1a6b1fc391803d3b5925', 
                'md5dab4f5c7853fd57f3a9c9a523364ac69', 
                'md513d0258903c37fed2a3d17a14e8551a2', 
                'md5dcb6eccdc824e0677ffae8ccdde42930', 
                'md513074be467e0034b6ca192c1689af813',
                'md52514e982df737db6cefaf8b770e7bf9c', 
                'md51ced204a8584c6428455006baf22546f', 
                'md51a661c430a2ff996e6df44cb033f322b', 
                'md5a649762eb5f39d42f149c3b708a371fd', 
                'md5bdef51b5d55b03f73ceb6e3f875ee94c',
                'md55759adc3208eb42caa6ddcbd3000b15e',
                'md5d630c3d3bfb5f5558520331566132d97',
                'md5d06a077489831141efe6f537ac3ef2f5',
                'md5bb098716dd46c8e113564e6b42b7cde9',
                'md508a116ab629a9168c5f121b9962d8ce6',
                'md5ee831aaa9224fb6bebbc261c6e557baa',
                'md5fe8996628db2722b2645843f91097c26', 
                'md5f92e0daf340890c9667469657ee2ece8', 
                'md5a0a6d252fe95a949244d2744b3db206e', 
                'java9', 'kankan', 'gnu', 'rrrrrr', 'android_src', 
                'generated_rootmodule', 'dalvik', 'hardlight', 'sdk', 'we', 
                'id', 'hirondelle', 'pb', 'dagger1', 'google', 
                'hotchemi', 'colorlights',  'mehdi', 'j0', 'i0',  
                'theme_engine', 'mystickers', 'kin', 'photo']

    def getTreeErrors(self):
        return self.tree_errors

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

    def getResName(self,path):

        potential_names = path.split('/')
        resName = False
    
        for pn in potential_names:
            if pn[0:3] == ('com' or 'org' or 'net' or 'edu'):
                resName = pn
                break
    
        if not resName:
            resName = path.replace('/','_')
            resName = hashlib.md5(str.encode(resName)).hexdigest()

        self.setProcessedFile(path)

        return resName

    def processFile(self,javaFile):

        resName = self.getResName(javaFile)
    
        ext = javaFile.split('.')[-1] #type: {magic.from_file(path)[0:3]}")
    
        if ext == 'java':
            tree = jtm.JavaTreeManager(path=javaFile).getTree()
    
            if not tree:
                self.tree_errors.append(javaFile)
                return
    
            self.setTree(tree)
            nlpCandidates = self.getNlpCandidates()
            
        results = self.getResults()

        if results:
            thisFile = javaFile.split("/")[-1]

            with open(f"{self.output_directory}/.structmappings-{resName}-{thisFile}",'w+') as fhandle:
                fhandle.write(json.dumps(results))

    def jobCheck(self,jobs):

        deadJobs = 0
        while deadJobs < multiprocessing.cpu_count():
            _jobs = jobs.copy()

            for job in _jobs:
                if not job.is_alive():
                    jobs.remove(job)
                    deadJobs += 1
                    yield
                    if deadJobs >= multiprocessing.cpu_count():
                        return

    def run(self,path,output_directory='.'):
    
        self.output_directory = output_directory

        if not os.path.isdir(output_directory):
            os.mkdir(self.output_directory)

        print(Fore.GREEN + f"\nCodeExtractor: *START*:\n{path}")
        if os.path.isfile(path):
            self.processFile(path)
    
        else:
            jobs = []

            for thisDir, subdirList, fileList in os.walk(path):
                for _file in fileList:
                    p  = Process(target=self.processFile, args=(os.path.join(thisDir,_file),))
                    p.start()
                    jobs.append(p)

                    if len(jobs) >= self.max_processes:
                        yield
                        self.jobCheck(jobs)

        print("\n")
        while len(jobs) > 0:
            _jobs = jobs.copy()

            for job in _jobs:
                if not job.is_alive():
                    jobs.remove(job)
                    print(Fore.GREEN + f"CodeExtractor: Subprocess finished. Remaining: ",len(jobs),"<--",end='\r',flush=True)

        print(Fore.GREEN + f"\nCodeExtractor: {path}: Aggregating and writing results.")
        results = list()

        resName = self.getResName(path)
        for tmpfile in glob.glob(f"{self.output_directory}/.structmappings-{resName}*"):
            with open(tmpfile,'r') as structfile:
                try:
                    results.append(json.load(structfile))
                except:
                    print("\nProblem appending json results to final structmappings file",tmpfile)

            os.remove(tmpfile)

        outdict = {}
        for _dict in results:
            for k in _dict.keys():
                if k in outdict.keys():
                    outdict[k].update(_dict[k])

                else:
                    outdict.update(_dict)

        resFile = os.path.join(self.output_directory,f"structmappings-{resName}")

        with open(resFile,'w') as resultsfile:
            resultsfile.write(json.dumps(outdict))

        yield resFile

    def getStats(self):
        
        processed = self.getProcessedFiles()
        treeErrors = self.getTreeErrors()
        unhandled = self.getUnhandled()
        print(f"\nProcessed {len(processed)} files.")
        print(f"\nError getting javalang tree for {len(treeErrors)} files.")
        print(f"\nCodeExtractor handler not made for {len(unhandled)} java code structures.")


if __name__ == "__main__":

    parser = parser()
    args = parser.parse_args()

    if not args.path:

       print(parser.print_help())
       sys.exit()

    ceObject = CodeExtractor()
    ceObject.run(args.path,args.output)
