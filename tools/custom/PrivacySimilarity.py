#!/usr/bin/python3

import spacy
import json
import argparse
from spacy.matcher import Matcher
from Levenshtein import *

# Loading a model and creating the NLP object
nlp = spacy.load('en_core_web_lg')

def parser():

    parser = argparse.ArgumentParser(description='Get Levenshtein and semantic simlarity scores.')
    parser.add_argument('-p','--path', type=str, help='path to json file(s) to process')
    parser.add_argument('-d','--debug', type=str, help='toggle debug mode.')

    return parser

class PrivacySimilarity:

    def __init__(self, food):

        if not food:
            print("Feed me a json file to process.")
            return

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

    def processForSimilarity(self):

        searchWordTokens = nlp(' '.join(self.searchWords))
        reservedWordTokens = nlp(' '.join(self.reservedWords))

        with open(self.food) as food:

            jsonFood = json.load(food)

            for struct in jsonFood.keys():

                print(struct)
                origWords = list(jsonFood[struct].keys())
                words = origWords.copy()

                for word in origWords:

                    if word.lower() in self.reservedWords:

                        words.remove(word)

                string = ' '.join(words)
                structTokens = nlp(string)

                for token1 in structTokens:

                    for token2 in searchWordTokens:

                        # Printing the following attributes of each token.  text: the word string, has_vector: if it contains 
                        # a vector representation in the model,  vector_norm: the algebraic norm of the vector, is_oov: if the word is out of vocabulary. 
                        #print(token1.text, token1.has_vector, token1.vector_norm, token1.is_oov)
                        #print(token2.text, token2.has_vector, token2.vector_norm, token2.is_oov)
                        spacy = token1.similarity(token2)
                        lev = ratio(str(token1),str(token2))

                        if spacy > .5 or lev > .75:

                            print(f"\n\t*Similar words: {token1} - {token2}\n\tSemantic:{spacy}\n\tLevenshtein:{lev}")


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

if __name__ == "__main__":

    parser = parser()
    args = parser.parse_args()
    main(args.path)
