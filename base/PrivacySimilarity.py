#!/usr/bin/python3

import colorama
from colorama import Fore,Style
import spacy
import os
import re
import json
import argparse
from spacy.matcher import Matcher
from Levenshtein import *
from multiprocessing import Process
import glob
import shutil
from json2table import convert

# Loading a model and creating the NLP object
# Make sure this model is downloaded to the machine youre running on: from cmd line: python -m spacy download en_core_web_lg
nlp = spacy.load('en_core_web_lg')

def parser():
# Parse command line args

    parser = argparse.ArgumentParser(description='Get Levenshtein and semantic simlarity scores.')
    parser.add_argument('-p','--path', type=str, help='path to json file(s) to process')
    parser.add_argument('-d','--debug', type=str, help='toggle debug mode.')

    return parser

class PrivacySimilarity:

    # First full run thresholds were: lev prev .85 sem prev .6.
    def __init__(self, food, lev_threshold = .7, sem_threshold = .5):
    # Constructor

        if not food: # must be provided structmappings json file
            print("Feed me a json file to process.")
            return

        # Thresholds of similarity scores to check against to write a result
        self.lev_threshold = lev_threshold
        self.sem_threshold = sem_threshold
        self.separators = ['_', '-', '#']
        self.concat_phrases = {}

        # metadata to append to results file
        self.meta = dict(
                levenshtein_threshold=lev_threshold,
                sematic_threshold=sem_threshold,
                total_privacy_score=0,
                average_privacy_score=0,
                highest_sensitivity_score=0,
                highest_sensitivity_token=None,
                )

        self.results = dict()
        self.resultsFile = "_results"
        self.outputDir = "."
        self.reserved_word_similarity = {}
        self.food = food

        # ignore these identifiers 
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
                         'imagebutton', 'activityinfo', 'message']

        # These words are what were comparing the extracted identifiers against for privacy sensitivity with scores associated.
        self.searchWords = {
                # Using Schomakers 1-10, using ceiling (example: 9.01 -> 10)

                # High-privacy segment
                'passwd':10, 'password':10, 'pwd':10, 'twitter_passwd':10, 'wi_passwd':10, 'gmail_passwd':10,
                'ftp_passwd':10, 'smtp_passwd':10, 'facebook_passwd':10, 'nq_account_passwd':10, 'mint_passwd':10, 'gritsafe_passwd':10,
                'exchange_passwd':10, 'adobe_passwd':10, 'credit_card_number':10, 'loan_info':10, 'bank_account_number':10, 'bank_info':10,
                'house_financial_info':10, 'vehicle_info':8, # specifically the registration number
                'vehicle_vin':8, 'device_id':8, 'mac_address':8, # IP addr are considered 'high', MACs can't be changed as easily
                'serial_num':8, 'insurance_policy_num':9,

                # the following fields were not in our original list:
                'drivers_license':9, 'ip_address':8, 'social_security_number':10, 'credit_score':8, 'passport_number':9,

                # the following fields were listed in the paper but seem irrelevant here:
                'fingerprint':9, 'dna_profile':9, 'digital_signature':9,

                # Med-privacy segment
                'username':7, 'phone_number':7, 'phone_num':7, 'twitter':7, 'social_media_url':7, 'wi_ssid':7,
                'ssid':7, 'ftp':7, 'smtp':7, 'facebook':7, 'nq_account':7, 'gritsafe':7,
                'exchange':7, 'adobe':7, 'username': 7, 'email':7, # note that username is med while email is low
                'salary':7, 'income':7, 'vehicle_registration':7, 'license_expiry_date':7, 'license_plate':7, 'service_provider':7,

                # the following fields were listed in the papers but not in our original list:
                'maiden_name':8, 'address':7, 'gps':7, 'location':7, 'medication':9, 'sexual_preference':6,

                # the following fields were listed in the paper but seem irrelevant here:
                #handwriting sample, voice print, medical history (!), picture of face,
                #law enforcement files, grievance documentation, browsing history, online dating activities, and survey answers

                # Low-privacy segment
                'birth_place':6, 'demographic_info':5, 'religion':6, 'person_weight':5, 'person_height':5, 'email':7,
                'date_of_birth':6, 'person_age':6, # can be determined from date of birth 'zip_code':5,
                'number_of_children':5, 'political_affiliation':5, 'company_name':5, # occupation info
                'job_title':5, # occupation info 'person_name':5, 'gender':5, 'school_name':5,
                'education_info':5, 'marital_status':5, 'native_language':5, 'citizenship':5, 'marriage_date':5, 'pet_name':5, #only german data exists
                'hair_color':5, #only german data exists 'alcohol_consumption':5, #only german data exists 'signed_ petitions':5,
                }

    # Properties are functions that can be set or got without arguments to the function
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
    # This function does the similarity checking.

        searchWordTokens = nlp(' '.join(self.searchWords.keys())) # the nlp function converts the dictionary keys to nlp tokens
        origWords = list(jsonFood[struct].keys()) # Get the identifiers from the structmappings file
        words = origWords.copy() # copy for checking against reserved words

        # check against reserved words and remove cases where we dont want to check similarity
        for word in origWords:
            if word.lower() in self.reservedWords:
                words.remove(word)

        # de-concatenate phrases found that are camelcase or separated by 'separators'
        for word in words:
            sep_words = self.has_separator(word)
            if sep_words:
                words.remove(word)
                print("\n(separators) Phrase found:", word) 
                print("Adding Individual words:", sep_words)
                
                for ind_word in sep_words:
                    words.append(ind_word)
                    self.concat_phrases[word] = sep_words
        
            else:
        
                case_words = self.case_change(word)
                if case_words:
                    words.remove(word)
                    print("\n(case) Phrase found:", word) 
                    print("Adding Individual words:", case_words)
                    
                    for ind_word in case_words:
                        words.append(ind_word)
                        self.concat_phrases[word] = case_words

        string = ' '.join(words) # Get single string space separated of identifiers to check
        structTokens = nlp(string) # tokenify those identifiers

        # Check each identifier token
        for token in structTokens:
            # against each privacy similarity token
            for token2 in searchWordTokens:
                spacy = token.similarity(token2) # get the semantic (spacy nlp) similarity score
                lev = ratio(str(token),str(token2)) # get the levenshtein similarity score

                # check those scores against the thresholds
                if spacy > self.sem_threshold:

                    # check to make sure the semantic stucture type isnt already a key in the results dictionary
                    if struct not in self.results.keys():
                        self.results[struct] = list()

                    # append the result data under the semantic structure type key
                    self.results[struct].append({
                        "ANDROID_APP_TOKEN": str(token),
                        "SIMILAR_PRIVACY_RELATED_TOKEN": str(token2),
                        "SENSITIVITY_LEVEL": self.searchWords[str(token2)],
                        "SEMANTIC_SIMILARITY_SCORE": str(spacy),
                        "LEVENSHTEIN_SIMILARITY_SCORE": "N/A"
                        })

                elif lev > self.lev_threshold:

                    # check to make sure the semantic stucture type isnt already a key in the results dictionary
                    if struct not in self.results.keys():
                        self.results[struct] = list()

                    # append the result data under the semantic structure type key
                    self.results[struct].append({
                        "ANDROID_APP_TOKEN": str(token),
                        "SIMILAR_PRIVACY_RELATED_TOKEN": str(token2),
                        "SENSITIVITY_LEVEL": self.searchWords[str(token2)],
                        "SEMANTIC_SIMILARITY_SCORE": "N/A",
                        "LEVENSHTEIN_SIMILARITY_SCORE": str(lev)
                        })

        # Write the results to tempory hidden file for specific file in app if there are any
        if self.results:
            with open(f".struct-results-{struct}.json",'w') as tmpres:
                tmpres.write(json.dumps(self.results))

    def getSensitivityScores(self, results):
    # aggregate sensitivity scores for identifiers found to be privacy senstive in an app

        # Setup
        score_aggregate = 0 # total of all sensitivity scores
        count_total = 0 # total amount of entries

        # If there are results for this app check every entry and grab scores
        if len(results) > 0:
            for entry in results:
                for result in entry[list(entry.keys())[0]]:
                    count_total += 1 
                    score_aggregate += result["SENSITIVITY_LEVEL"]

                    # for checking what the highest sensitivity score was among the apps sensitive identifiers
                    if result["SENSITIVITY_LEVEL"] > self.meta["highest_sensitivity_score"]:
                        self.meta["highest_sensitivity_score"] = result["SENSITIVITY_LEVEL"]
                        self.meta["highest_sensitivity_token"] = result["ANDROID_APP_TOKEN"]

            try:
                print(Fore.BLUE + f"PrivacySimilarity: {self.food}: Entry total for :", count_total, "score aggregate:", score_aggregate, "average:", score_aggregate/count_total)

            except ZeroDivisionError:
                print(Fore.BLUE + "PrivacySimilarity: Division by zero for", self.food)

            self.meta['total_privacy_score'] = score_aggregate
            self.meta['average_privacy_score'] = score_aggregate / count_total


    def writeResults(self):
    # aggregate the results files for a single app into one file

        print(Fore.BLUE + f"PrivacySimilarity: {self.food}: Aggregating and writing results.")
        results = list()

        for tmpfile in glob.glob('.struct-results*'):
            with open(tmpfile,'r') as structfile:
                results.append(json.load(structfile))

            os.remove(tmpfile) # clean up temp hidden files that made up app results

        self.getSensitivityScores(results)
        outdict = dict(meta=self.meta, results=results)

        resfile = os.path.join(self.outputDir,self.resultsFile)
        with open(resfile, 'w') as resultsfile:
            resultsfile.write(json.dumps(outdict))

        # Create an html table of the results for if we ever make this more of an interactive web app
        with open(os.path.join(self.outputDir,self.resultsFile.replace('results','table')),'w') as table:
            print(convert(outdict,build_direction="TOP_TO_BOTTOM",table_attributes={"style": "width:100%"}), file=table)

        return resfile
    
    def case_change(self, word):
    # Splits out words detected from camel case

        _words = False
    
        words = re.findall('[a-z][^A-Z][a-z]*|[A-Z][a-z]*', word)
    
        if len(words) > 1:
            _words = words
    
        return _words
    
    def has_separator(word):
    # Splits out words separated by one of the self.separators. Checks cases changes after separators.
        for separator in separators:
            if separator in word:
                words = word.split(separator)
                _words = []
    
                for word in words:
                    cases = self.case_change(word)
    
                    if cases:
                        words.remove(word)
                        [_words.append(word) for word in cases]
    
                return words + _words


    def processForSimilarity(self):
    # Main function for processing

        print(Fore.BLUE + f"\n\tPrivacySimilarity: *START*:\n{self.food}")
        with open(self.food) as food:
            jsonFood = json.load(food) # load the structmappings json file

            # Initialize jobs
            jobs = []
            for struct in jsonFood.keys():
                p  = Process(target=self.worker, args=(jsonFood, struct,))
                p.start()
                jobs.append(p)

        print("\n")
        while len(jobs) > 0:

            yield "PrivacySimilarity processes still running.Yield." # Pause point

            # Remove finished jobs
            _jobs = jobs.copy()
            for job in _jobs:
                if not job.is_alive():
                    jobs.remove(job)
                    print(Fore.BLUE + f"PrivacySimilarity: {self.food} Subprocess finished. Remaining:", len(jobs), "<--", end='\r', flush=True)

                    yield # pause point, one apps identifiers processed

                    # For checking similarity to reserved words.
                    # TODO: make toggleable
                    # TODO: allow option to add finds to reservedWords ignore list
                    #for token2 in reservedWordTokens:
                    #    spacy = token1.similarity(token2)
                    #    lev = ratio(str(token1),str(token2))
                    #    if spacy > .5 or lev > .75:
                    #        print(f"\n\t#Similar to reserved words: \n\t{token1} - {token2}\n\tSemantic:{spacy}\n\tLevenshtein:{lev}")

        print("Concatenated phrases checked:", self.concat_phrases)
        resfile = self.writeResults()
        return resfile


# If running by itself
def main(path):

    psim = PrivacySimilarity(food=path)
    psim.setResultsFile(f"results{path.replace('structmappings','').split('/')[-1]}")
    psim.processForSimilarity()
    psim.writeResults()

if __name__ == "__main__":

    parser = parser()
    args = parser.parse_args()
    main(args.path)
