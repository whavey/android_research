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
        self.meta = dict(levenshtein_threshold=lev_threshold,sematic_threshold=sem_threshold)
        self.results = dict()
        self.reserved_word_similarity = {}
        self.food = food
        # Initialize the matcher with the shared vocab
        #self.matcher = Matcher(nlp.vocab)
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

        self.searchWords = ['username', 'name', 'email',
                   'passwd', 'password', 'pwd',
                   'phone_number', 'phone_num', 'twitter',
                   'social_media_url', 'wi_ssid', 'ssid',
                   'ftp', 'smtp', 'facebook',
                   'nq_account', 'gritsafe', 'exchange',
                   'adobe', 'username_or_email', 'twitter_passwd',
                   'wi_passwd', 'gmail_passwd', 'social_media_url',
                   'wi_ssid', 'ftp_passwd', 'smtp_passwd',
                   'facebook_passwd', 'nq_account_passwd', 'mint_passwd',
                   'gritsafe_passwd', 'exchange_passwd', 'adobe_passwd',
                   'person_name', 'date_of_birth', 'gender',
                   'company_name', 'person_age', 'person_weight',
                   'job_title', 'person_height', 'school_name',
                   'education_info', 'marital_status', 'demographic_info',
                   'native_language', 'citizenship', 'birth_place',
                   'marriage_date', 'religion', 'political_affiliation',
                   'credit_card_info', 'loan_info', 'bank_account_info',
                   'salary', 'bank_info', 'house_financial_info',
                   'vehicle_info', 'license_plate', 'vehicle_vin',
                   'insurance_policy_num', 'vehicle_registration', 'license_expiry_date',
                   'device_id', 'mac_address', 'serial_num',
                   'service_provider' ]

    @property
    def getResults(self):

        return self.results


    def worker(self, jsonFood, struct):

        searchWordTokens = nlp(' '.join(self.searchWords))
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
                        'SEMANTIC_SIMILARITY_SCORE': str(spacy),
                        'LEVENSHTEIN_SIMILARITY_SCORE': str(lev)
                        })

                    #if str(token) not in self.results[struct].keys():

                    #    self.results[struct] = {f"ANDROID_APP_TOKEN-{str(token)}": [{f"SIMILAR_PRIVACY_RELATED_TOKEN-{str(token2)}": {'semantic': str(spacy),'levenshtein': str(lev)}}]}

                    #else:

                    #    self.results[struct][f"ANDROID_APP_TOKEN-{str(token)}"].append({f"SIMILAR_PRIVACY_RELATED_TOKEN-{str(token2)}": {'semantic': str(spacy),'levenshtein': str(lev)}})

        if self.results:

            with open(f".struct-results-{struct}.json",'w') as tmpres:

                tmpres.write(json.dumps(self.results))


    def writeResults(self):

        results = list()

        for tmpfile in glob.glob('.struct-results*'):

            with open(tmpfile,'r') as structfile:

                results.append(json.load(structfile))

            os.remove(tmpfile)

        outdict = dict(meta=self.meta, results=results)

        with open(f"results{self.food.replace('structmappings','')}",'w') as resultsfile:

            resultsfile.write(json.dumps(outdict))

        print(convert(outdict,build_direction="TOP_TO_BOTTOM",table_attributes={"stle": "width:100%"}))


    def processForSimilarity(self):

        #searchWordTokens = nlp(' '.join(self.searchWords))
        #reservedWordTokens = nlp(' '.join(self.reservedWords))

        with open(self.food) as food:

            jsonFood = json.load(food)

            for struct in jsonFood.keys():
                p  = Process(target=self.worker, args=(jsonFood, struct,))
                p.start()
                p.join()

                #print(struct)
                #origWords = list(jsonFood[struct].keys())
                #words = origWords.copy()

                #for word in origWords:

                #    if word.lower() in self.reservedWords:

                #        words.remove(word)

                #string = ' '.join(words)
                #structTokens = nlp(string)

                #for token in structTokens:

                    #for token2 in searchWordTokens:

                    #    # Printing the following attributes of each token.  text: the word string, has_vector: if it contains 
                    #    # a vector representation in the model,  vector_norm: the algebraic norm of the vector, is_oov: if the word is out of vocabulary. 
                    #    #print(token1.text, token1.has_vector, token1.vector_norm, token1.is_oov)
                    #    #print(token2.text, token2.has_vector, token2.vector_norm, token2.is_oov)
                    #    spacy = token1.similarity(token2)
                    #    lev = ratio(str(token1),str(token2))

                    #    if spacy > .5 or lev > .75:

                    #        self.results[results][token1] = list()

                    #        #print(f"\n\t*Similar words: {token1} - {token2}\n\tSemantic:{spacy}\n\tLevenshtein:{lev}")
                    #        self.results[results][token1].append(dict(token2=dict(semantic=spacy,levenshtein=lev)))



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
    psim.processForSimilarity()
    psim.writeResults()

if __name__ == "__main__":

    parser = parser()
    args = parser.parse_args()
    main(args.path)
