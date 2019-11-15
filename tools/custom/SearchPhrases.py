#!/usr/bin/python3
import os
import AndroidCodeFinder
import argparse
import json
from subprocess import Popen,PIPE

def parse_args():
    parser = argparse.ArgumentParser(description='Search for sensitive phrases.')
    parser.add_argument('-d','--debug', type=str, help='Turn on debug mode.')
    parser.add_argument('-p','--path', type=str, help='file to parse.')
    return parser.parse_args()

searchPhrases = {
    'Account/Contact': [
        'username',
        'email',
        'passwd',
        'password',
        'pwd',
        'phone_number',
        'phone',
        'phone_num',
        'twitter',
        'gmail',
        'social_media_url',
        'wi_ssid',
        'ssid',
        'ftp',
        'smtp',
        'facebook',
        'nq_account',
        'mint',
        'gritsafe',
        'exchange',
        'adobe' ],
    'Personal': [
        'full_name',
        'fullname',
        'last_name',
        'lastname',
        'first_name',
        'firstname',
        'person_name',
        'date_of_birth',
        'birthday',
        'birthdate',
        'gender',
        'sex',
        'orientation',
        'company',
        'person_age',
        'age',
        'person_weight',
        'weight',
        'job_title',
        'person_height',
        'height',
        'school_name',
        'education_info',
        'marital_status',
        'demographic_info',
        'nationality',
        'native_language',
        'education',
        'race',
        'citizenship',
        'birth_place',
        'marriage_date',
        'religion',
        'political_affiliation' ],
    'Financial': [
        'credit_card_info',
        'credit_card_number',
        'loan_info',
        'bank_account_info',
        'account_number',
        'salary',
        'bank_info',
        'house_financial_info' ],
    'Vehicle/Driver': [
        'vehicle_info',
        'license_plate',
        'vehicle_vin',
        'vin',
        'insurance_policy_num',
        'policy_num',
        'vehicle_registration',
        'license_expiry_date' ],
    'Device': [
            'ip_address',
            'ip',
            'device_id',
            'mac_address',
            'serial_num',
            'service_provider',
            'device_manufac_info',
            'sim_card' ],
    'Health': [
            'medication_name',
            'prescription_num',
            'drug_dosage',
            'blood_pressure',
            'blood_type',
            'heart_rate',
            'body_mass_index',
            'blood_glucose',
            'doctor_email_id' ],
    'Personal Id #': [
            'SSN',
            'driver_license_num',
            'id_num',
            'tax_id',
            'passport_num',
            'student_id',
            'medicaid_num' ],
    'Family Member': [
            'family_member_name',
            'family_member_phone',
            'guardian_email',
            'mother_birth_place' ],
    'Location/Travel': [
            'latitude',
            'longitude',
            'country',
            'location_info',
            'flight_num' ]
}

class AnGrep:
    def __init__(self, *args, **kwargs):
        self.results = {}
        self.path = args[0].path
        self.file_list = []
        self.file_count = 0
        self.searchPhrases = {}
        self.searchCategory = 'misc'

    def setSearchPhrases(self,searchPhrases):
        self.searchPhrases = searchPhrases

    def setCategory(self,category):
        self.searchCategory = category

    def doGrep(self,path=None):
        if path:
            self.path = path
        for phrase in self.searchPhrases:
            p = Popen(f'grep -r -i " {phrase}\|\.{phrase}" {self.path}',shell=True,stdout=PIPE)
            _lines = p.communicate()[0].decode("utf-8").split('\n')
            _file_list = [i.split(":")[0] for i in _lines]
            if _file_list != ['']:
                _file_count = len(_file_list)-1
                self.file_list += _file_list
                self.file_count += _file_count
            else:
                _file_count = 0
            self.results[phrase] = {_file_count:_file_list}

def run(target=None):
    for k in searchPhrases.keys():
        ag = AnGrep(args)
        ag.setCategory(k)
        ag.setSearchPhrases(searchPhrases[k])
        if target:
            ag.doGrep(f"../apps/source/{target}")
        else:
            ag.doGrep()
        print("\t",k,"Total Finds:",ag.file_count)
        for r in ag.results.keys():
            print("\t\t",r,[k for k in ag.results[r].keys()])

if __name__ == '__main__':
    args = parse_args()
    if not args.path:
        for i in os.listdir('../apps/source'):
            print("Searching:",i,"\n","="*(len(i)+10),)
            run(i)
    else:
        run()
