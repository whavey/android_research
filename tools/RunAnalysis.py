#!/usr/bin/python3
import os
import argparse
import PrivacySimilarity
import CodeExtractor

def parser():
    parser = argparse.ArgumentParser(description='Run full analysis.')
    parser.add_argument('-p','--path', type=str, help='path to all apps organized by category')
    parser.add_argument('-d','--debug', type=str, help='toggle debug mode.')
    parser.add_argument('-o','--output', type=str, help='directory to save results in.')

    return parser

args = parser().parse_args()


def runCodeExtractor(path,output):

    ceObject = CodeExtractor.CodeExtractor()
    results = ceObject.run(path,output)
    return results

def runPrivacySimilarity(path,output):

    for _file in os.listdir(path):
    
        food = os.path.join(path,_file)
        psim = PrivacySimilarity.PrivacySimilarity(food=food)
        psim.setOutputDir(output)
        psim.setResultsFile(f"results{food.replace('structmappings','').split('/')[1]}")
        output = os.path.join(psim.getOutputDir, psim.getResultsFile)
        print(f"Output will be {output}")
        psim.processForSimilarity()
        psim.writeResults()


def main(path,output):

    for category in os.listdir(path):

        os.mkdir(f"full_results/{category}")
        extracted = runCodeExtractor(os.path.join(path,category,"sources"),output)
        runPrivacySimilarity(extracted,output)

if __name__ == "__main__":
    os.mkdir("full_results") if not os.isdir("full_results")
    main(args.path,args.output)

