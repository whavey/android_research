#!/usr/bin/python3

import spacy
import json

# importing the Matcher
from spacy.matcher import Matcher
from Levenshtein import *

# Loading a model and creating the NLP object
nlp = spacy.load('en_core_web_lg')

# Initialize the matcher with the shared vocab
matcher = Matcher(nlp.vocab)
reservedWords = ['abstract', 'assert', 'boolean',
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
                 'lambda' ]

searchWords = ['username', 'name', 'email',
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

print(" Similarity",'\n','='*10)
# Data object is in the form of a list of dictionaries
with open("food.json", "r") as food:
    searchWordTokens = nlp(' '.join(searchWords))
    for line in food:
        jline = json.loads(line)
        rawLine = jline['line']
        if rawLine[0:2] == '/*':
            continue
        words = jline['words'].copy()
        for word in words:
            if word in reservedWords:
                jline['words'].remove(word)
        words = jline['words']
        string = ' '.join(words)
        lineTokens = nlp(string)
        for token1 in lineTokens:
            for token2 in searchWordTokens:
                # Printing the following attributes of each token.  text: the word string, has_vector: if it contains 
                # a vector representation in the model,  vector_norm: the algebraic norm of the vector, is_oov: if the word is out of vocabulary. 
                #print(token1.text, token1.has_vector, token1.vector_norm, token1.is_oov)
                #print(token2.text, token2.has_vector, token2.vector_norm, token2.is_oov)
                spacy = token1.similarity(token2)
                lev = ratio(str(token1),str(token2))
                if spacy > .5 or lev > .75:
                    print(f"Similar words: {token1} - {token2}\nLine:{rawLine}\nFile:{jline['file']}\nSemantic:{spacy}\nLevenshtein:{lev}\n========\n")
                #print(f"{token1} <> {token2}: semantic:{token1.similarity(token2)} | levenshtein:{ratio(str(token1),str(token2))}\n")
