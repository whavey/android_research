#!/usr/bin/python3

import spacy
import os
import json
import argparse
from spacy.matcher import Matcher
from Levenshtein import *
from multiprocessing import Process
import glob
import shutil
from json2table import convert

# Loading a model and creating the NLP object
nlp = spacy.load('en_core_web_lg')

def parser():

    parser = argparse.ArgumentParser(description='Get Levenshtein and semantic simlarity scores.')
    parser.add_argument('-p','--path', type=str, help='path to json file(s) to process')
    parser.add_argument('-d','--debug', type=str, help='toggle debug mode.')

    return parser

class PrivacySimilarity:

    def __init__(self, food, lev_threshold = .75, sem_threshold = .5):

        if not food:
            print("Feed me a json file to process.")
            return

        self.lev_threshold = lev_threshold
        self.sem_threshold = sem_threshold
        self.meta = dict(levenshtein_threshold=lev_threshold,sematic_threshold=sem_threshold,total_privacy_score=0,average_privacy_score=0)
        self.results = dict()
        self.resultsFile = "_results"
        self.outputDir = "."
        self.reserved_word_similarity = {}
        self.food = food
        self.reservedWords = ['abstract', 'assert', 'boolean',
                         'break', 'byte', 'case',
                         'catch', 'char', 'class',
                         'const', 'continue', 'default',
                         'double', 'do', 'else',
                         'enum', 'extends', 'false',
                         'final', 'finally', 'float',
                         'for', 'goto', 'if',
                         'implements', 'import', 'instanceof',
                         'int', 'interface', 'long',
                         'native', 'new', 'null',
                         'package', 'private', 'protected',
                         'public', 'return', 'short',
                         'static', 'strictfp', 'super',
                         'switch', 'synchronized', 'this',
                         'throw', 'throws', 'transient',
                         'true', 'try', 'void',
                         'volatile', 'while', 'synthetic',
                         'lambda', 'intent', 'thread',
                         'view', 'string', 'toast',
                         'mainactivity', 'com', 'object',
                         'alertdialog', 'linearlayout', 'seekbar',
                         'charsequence', 'onclick', 'oncreate',
                         'onfinish', 'ontick', 'onactivityresult',
                         'onbackpressed', 'onprogresschanged', 'ondestroy',
                         'packagename', 'bundle', 'gradientdrawable',
                         'dialoginterface', 'str', 'view', 'framelayout',
                         'object','windowmanager', 'componentname', 'iterator',
                         'imagebutton', 'activityinfo']

        self.searchWords = {
                'username':1, 'name':1, 'email':1,
                'passwd':1, 'password':1, 'pwd':1,
                'phone_number':1, 'phone_num':1, 'twitter':1,
                'social_media_url':2, 'wi_ssid':1, 'ssid':1,
                'ftp':1, 'smtp':1, 'facebook':1,
                'nq_account':1, 'gritsafe':1, 'exchange':1,
                'adobe':1, 'username_or_email':1, 'twitter_passwd':1,
                'wi_passwd':1, 'gmail_passwd':1, 'social_media_url':1,
                'wi_ssid':1, 'ftp_passwd':1, 'smtp_passwd':1,
                'facebook_passwd':1, 'nq_account_passwd':1, 'mint_passwd':1,
                'gritsafe_passwd':1, 'exchange_passwd':1, 'adobe_passwd':1,
                'person_name':1, 'date_of_birth':2, 'gender':2,
                'company_name':1, 'person_age':2, 'person_weight':3,
                'job_title':1, 'person_height':3, 'school_name':1,
                'education_info':1, 'marital_status':3, 'demographic_info':3,
                'native_language':3, 'citizenship':1, 'birth_place':2,
                'marriage_date':2, 'religion':3, 'political_affiliation':3,
                'credit_card_info':1, 'loan_info':1, 'bank_account_info':1,
                'salary':2, 'bank_info':1, 'house_financial_info':1,
                'vehicle_info':1, 'license_plate':3, 'vehicle_vin':3,
                'insurance_policy_num':2, 'vehicle_registration':2, 'license_expiry_date':2,
                'device_id':1, 'mac_address':2, 'serial_num':1,
                'service_provider':2
                }

    @property
    def getFoodFile(self):
        return self.food

    @property
    def getResults(self):
        return self.results

    @property
    def getResultsFile(self):
        return self.resultsFile

    @property
    def getOutputDir(self):
        return self.outputDir

    def setOutputDir(self,outputDir):
        self.outputDir = outputDir

    def setResultsFile(self,resultsFile):
        self.resultsFile = resultsFile

    def worker(self, jsonFood, struct):

        os.environ["SPACY_WARNING_IGNORE"] = "W008"

        searchWordTokens = nlp(' '.join(self.searchWords.keys()))
        origWords = list(jsonFood[struct].keys())
        words = origWords.copy()

        for word in origWords:
            if word.lower() in self.reservedWords:
                words.remove(word)

        string = ' '.join(words)
        structTokens = nlp(string)

        for token in structTokens:
            for token2 in searchWordTokens:
                spacy = token.similarity(token2)
                lev = ratio(str(token),str(token2))

                if spacy > self.sem_threshold or lev > self.lev_threshold:
                    if struct not in self.results.keys():
                        self.results[struct] = list()

                    self.results[struct].append({
                        "ANDROID_APP_TOKEN": str(token),
                        "SIMILAR_PRIVACY_RELATED_TOKEN": str(token2),
                        "SENSITIVITY_LEVEL": self.searchWords[str(token2)],
                        'SEMANTIC_SIMILARITY_SCORE': str(spacy),
                        'LEVENSHTEIN_SIMILARITY_SCORE': str(lev)
                        })

        if self.results:
            with open(f".struct-results-{struct}.json",'w') as tmpres:
                tmpres.write(json.dumps(self.results))


    def getSensitivityScores(self, results):

        print("Getting Sensitivity Scores.")

        score_aggregate = 0
        count_total = 0

        for entry in results:
            for result in entry[list(entry.keys())[0]]:
                count_total += 1
                score_aggregate += result["SENSITIVITY_LEVEL"]

        print("entry total:", count_total, "score aggregate:", score_aggregate, "average:", score_aggregate/count_total)
        self.meta['total_privacy_score'] = score_aggregate
        self.meta['average_privacy_score'] = score_aggregate / count_total


    def writeResults(self):

        print("Aggregating and writing results.")
        results = list()

        for tmpfile in glob.glob('.struct-results*'):
            with open(tmpfile,'r') as structfile:
                results.append(json.load(structfile))

            os.remove(tmpfile)

        self.getSensitivityScores(results)
        outdict = dict(meta=self.meta, results=results)

        with open(os.path.join(self.outputDir,self.resultsFile),'w') as resultsfile:
            resultsfile.write(json.dumps(outdict))

        with open(os.path.join(self.outputDir,self.resultsFile.replace('results','table')),'w') as table:
            print("Generating HTML Table:\n", )
            print(convert(outdict,build_direction="TOP_TO_BOTTOM",table_attributes={"style": "width:100%"}), file=table)


    def processForSimilarity(self):

        with open(self.food) as food:
            jsonFood = json.load(food)

            jobs = []
            for result in jsonFood["results"]:
                for struct in result.keys():
                    p  = Process(target=self.worker, args=(jsonFood["results"], struct,))
                    p.start()
                    jobs.append(p)

        print("Waiting for all sub processes to finish.")
        while len(jobs) > 0:
            _jobs = jobs.copy()
            for job in _jobs:
                if not job.is_alive():
                    jobs.remove(job)
                    print("Subprocess finished. Remaining:",len(jobs))

                    # For checking similarity to reserved words.
                    # TODO: make toggleable
                    # TODO: allow option to add finds to reservedWords ignore list
                    #for token2 in reservedWordTokens:
                    #    spacy = token1.similarity(token2)
                    #    lev = ratio(str(token1),str(token2))
                    #    if spacy > .5 or lev > .75:
                    #        print(f"\n\t#Similar to reserved words: \n\t{token1} - {token2}\n\tSemantic:{spacy}\n\tLevenshtein:{lev}")


def main(path):

    psim = PrivacySimilarity(food=path)
    psim.setResultsFile(f"results{psim.getFoodFile.replace('structmappings','')}")
    psim.processForSimilarity()
    psim.writeResults()

if __name__ == "__main__":

    parser = parser()
    args = parser.parse_args()
    main(args.path)
