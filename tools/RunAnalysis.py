#!/usr/bin/python3
import shutil
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

def runCodeExtractor(path, app, output):

    ceObject = CodeExtractor.CodeExtractor()
    results = ceObject.run(path, app, output)
    return results

def runPrivacySimilarity(path,output):

    food = path
    psim = PrivacySimilarity.PrivacySimilarity(food=food)
    psim.setOutputDir(output)
    psim.setResultsFile(f"results{food.replace('structmappings','').split('/')[-1]}")

    return psim.processForSimilarity()

def main(path, appcount):

    if not os.path.isdir("full_results"):
        os.mkdir("full_results")

    if not os.path.isdir("processed_apks"):
        os.mkdir("processed_apks")

    master_dict = {}
    categories = (category for category in os.listdir(path))

    for cat in categories:
        apps = (app for app in os.listdir(os.path.join(path,cat)))
        os.mkdir(f"processed_apks/{cat}")
        master_dict[cat] = apps

    categories = (category for category in os.listdir(path))
    rceGen = None
    rpsGen = None
    count = 0
    cat = next(categories)
    app = next(master_dict[cat])
    rceDone = False

    while True:
            resultpath = os.path.join("full_results", cat)

            if not rceDone:
                if not rceGen:
                    mainpath = "/".join(app.replace(".","/").split("/")[0:-1])
                    apppath = os.path.join(path, cat, app)
                    target = os.path.join(apppath, "sources", mainpath)
                    rceGen = runCodeExtractor(target, app, resultpath)

                try:
                    extracted = next(rceGen)

                except StopIteration:
                    smapqueue.put((extracted, app, resultpath))

                    try:
                        cat = next(categories)

                    except StopIteration:
                        count += 1
                        
                        if count == appcount:
                            print(f"Struct Mappings created for [{appcount}] apps per category. Now just waiting for PrivacySimilarity.")
                            rceDone = True

                        else:
                            categories = (category for category in os.listdir(path))
                            print(f"\nCycling Categories for next iteration of processing: {count}/{appcount}")

                    try:
                        app = next(master_dict[cat])

                    except StopIteration:
                        print("No more apps in category:", cat)

                    rceGen = None 

            if rceDone and smapqueue.empty():
                break

            if rpsGen:
                try:
                    next(rpsGen)

                except StopIteration:
                    print("\n*** Finished Processing:", appname)
                    print("Remaining Queue:")

                    for i in list(smapqueue.queue):
                        print(i[1])

                    shutil.copytree(apppath, f"processed_apks/{_resultpath.split('/')[-1]}/{appname}")
                    rpsGen = None

            else:
                if not smapqueue.empty():
                    structmapfile, appname, _resultpath = smapqueue.get()
                    rpsGen = runPrivacySimilarity(structmapfile, _resultpath)

                    try:
                        next(rpsGen)

                    except StopIteration:
                        print("\nGot stop iteration immediately processing:", structmapfile)

if __name__ == "__main__":

    main(args.path,args.number_of_apps)
    print("Analysis Completed")

