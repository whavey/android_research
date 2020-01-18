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

    # Setup result directories
    if not os.path.isdir("full_results"):
        os.mkdir("full_results")

    if not os.path.isdir("processed_apks"):
        os.mkdir("processed_apks")

    # Generator for processing across categories
    categories = (category for category in os.listdir(path))

    # Dict for tracking what apps to process per cat
    master_dict = {}

    # Get processed already and print
    processed = []
    for cat in os.listdir("full_results"):
        for _file in os.listdir(os.path.join("full_results",cat)):
            if "results-" in _file:
                processed.append(_file.replace("results-",""))

    print(f"\nAlready Processed {len(processed)} apps:")
    print("------------------------")
    for apk in processed:
        print(apk)

    # Get apps where structmaps made
    structmaps_made = []
    for cat in os.listdir("full_results"):
        for _file in os.listdir(os.path.join("full_results",cat)):
            if "structmappings" in _file:
                if _file[0] != '.':
                    structmaps_made.append(_file)

    # Determine if structmaps files already processed
    unprocessed_struct_files = []
    for cat in os.listdir("full_results"):
        for _file in os.listdir(os.path.join("full_results",cat)):
            if _file in structmaps_made:
                appname = _file.replace("structmappings-",'')
                if appname not in processed:
                    unprocessed_struct_files.append(appname)
                    smapqueue.put((os.path.join("full_results",cat,_file),appname,os.path.join("full_results",cat)))

    print(f"\nPushing unprocessed already made {len(unprocessed_struct_files)} files to queue:")
    print("---------------------------------------------------------------------")
    for un in unprocessed_struct_files:
        print(un)
        
    # Determine apps that still need full processing
    _apps = []
    for cat in os.listdir(path):
        _apps = _apps + [app for app in os.listdir(os.path.join(path,cat)) if (app not in processed) and (f"structmappings-{app}" not in structmaps_made)]

    print(f"\nWill perform full process on {len(_apps)} apps:")
    print("-----------------------------------")
    for app in _apps:
        print(app)

    # Populate master dict with needed processing per cat
    for cat in categories:
        apps = (app for app in os.listdir(os.path.join(path,cat)) if (app not in processed) and (f"structmappings-{app}" not in structmaps_made))

        if not os.path.isdir(f"processed_apks/{cat}"):
            os.mkdir(f"processed_apks/{cat}")

        master_dict[cat] = apps

    # Set initial state for generators
    categories = (category for category in os.listdir(path))
    rceGen = None
    rpsGen = None
    count = 0
    cat = next(categories)

    while True:
        try:
            app = next(master_dict[cat])
            break
        except StopIteration:
            print("All apps processed in cat",cat)
            cat = next(categories)

    rceDone = False

    # Main processing loop
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
                print(f"Remaining Queue: [{list(smapqueue.queue)}]")

                for i in list(smapqueue.queue):
                    print(i[1])

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

