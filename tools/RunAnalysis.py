#!/usr/bin/python3
import os
import argparse
import PrivacySimilarity

def parser():
    parser = argparse.ArgumentParser(description='Run Privacy Similary Tests.')
    parser.add_argument('-p','--path', type=str, help='path to json file(s) to process')
    parser.add_argument('-d','--debug', type=str, help='toggle debug mode.')
    parser.add_argument('-o','--output', type=str, help='directory to save results in.')

    return parser

args = parser().parse_args()
for _file in os.listdir(args.path):

    food = os.path.join(args.path,_file)
    psim = PrivacySimilarity.PrivacySimilarity(food=food)
    psim.setOutputDir(args.output)
    psim.setResultsFile(f"results{food.replace('structmappings','').split('/')[1]}")
    output = os.path.join(psim.getOutputDir, psim.getResultsFile)
    print(f"Output will be {output}")
    psim.processForSimilarity()
    psim.writeResults()
