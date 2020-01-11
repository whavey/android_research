#!/usr/bin/python3
import os
import argparse
import PrivacySimilarity
import CodeExtractor
import queue
import time

smapqueue = queue.Queue() 

def parser():
    parser = argparse.ArgumentParser(description='Run full analysis.')
    parser.add_argument('-p','--path', type=str, help='path to all apps organized by category')
    parser.add_argument('-d','--debug', type=str, help='toggle debug mode.')
    parser.add_argument('-n','--number_of_apps', type=int, help='the number of apps to analyze per category')

    return parser

args = parser().parse_args()

def runCodeExtractor(path,output):

    ceObject = CodeExtractor.CodeExtractor()
    results = ceObject.run(path,output)
    return results

def runPrivacySimilarity(path,output):

    food = path
    psim = PrivacySimilarity.PrivacySimilarity(food=food)
    psim.setOutputDir(output)
    psim.setResultsFile(f"results{food.replace('structmappings','').split('/')[-1]}")

    return psim.processForSimilarity()
    #psim.writeResults()

def main(path,appcount):

    master_dict = {}
    categories = (category for category in os.listdir(path))

    for cat in categories:
        apps = (app for app in os.listdir(os.path.join(path,cat)))
        master_dict[cat] = apps

    categories = (category for category in os.listdir(path))
    rceGen = None
    rpsGen = None
    count = 0
    cat = next(categories)
    app = next(master_dict[cat])

    while True:
            resultpath = os.path.join("full_results", cat)

            if not rceGen:
                mainpath = "/".join(app.replace(".","/").split("/")[0:-1])
                target = os.path.join(path, cat, app, "sources", mainpath)
                rceGen = runCodeExtractor(target, resultpath)

            try:
                extracted = next(rceGen)

            except StopIteration:
                smapqueue.put((extracted,resultpath))
                try:
                    cat = next(categories)

                except StopIteration:
                    if count > appcount:
                        break
                    else:
                        categories = (category for category in os.listdir(path))
                        count += 1
                        print(f"\nCycling Categories for next iteration of processing: {count}/{appcount}")

                app = next(master_dict[cat])
                rceGen = None 

            if rpsGen:
                try:
                    next(rpsGen)

                except StopIteration:
                    rpsGen = None

            else:
                if not smapqueue.empty():
                    structmapfile, resultpath = smapqueue.get()
                    rpsGen = runPrivacySimilarity(structmapfile, resultpath)
                    try:
                        next(rpsGen)
                    except StopIteration:
                        print("\nGot stop iteration immediately processing:", structmapfile)

if __name__ == "__main__":
    if not os.path.isdir("full_results"):
        os.mkdir("full_results")

    main(args.path,args.number_of_apps)
    print("Analysis Completed")

