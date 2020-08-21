#!/usr/bin/python3
import shutil
import os
import argparse
import queue
import time

# Project Imports
import PrivacySimilarity
import CodeExtractor

# Create queue for struct mappings files
smapqueue = queue.Queue() 

# Parse command line arguments for this program
def parser():
    parser = argparse.ArgumentParser(description='Run full analysis.')
    parser.add_argument('-p','--path', type=str, help='path to all apps organized by category')
    parser.add_argument('-d','--debug', type=str, help='toggle debug mode.')
    parser.add_argument('-n','--number_of_apps', type=int, help='the number of apps to analyze per category')

    return parser

# Call the parser and get the args for this run
args = parser().parse_args()

def runCodeExtractor(path, app, output):
# Create the Code Extractor object and run it.

    ceObject = CodeExtractor.CodeExtractor()
    results = ceObject.run(path, app, output)
    return results

def runPrivacySimilarity(path,output):
# Create the PrivacySimilarity object and run it. 
  
    food = path # Just to keep the name consistent. Path feeds the psim object

    psim = PrivacySimilarity.PrivacySimilarity(food=food)
    psim.setOutputDir(output) # Where the results are stored

    # For the name of the Privacy Similarity results file just grab the app name from the structmappings files.
    psim.setResultsFile(f"results{food.replace('structmappings','').split('/')[-1]}") 

    return psim.processForSimilarity()

def main(path, appcount):

    # Setup result directories
    if not os.path.isdir("full_results"):
        os.mkdir("full_results")

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
    for cat in os.listdir("full_results"):                          # for each cat in the results dir
        for _file in os.listdir(os.path.join("full_results",cat)):  # for each file in cat

            if _file in structmaps_made:                            # if there is a struct mapping file made
                appname = _file.replace("structmappings-",'')       # Get the name

                if appname not in processed:                        # Check if theres a results file
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
        
        # Create generator for apps that need processing for cateogory
        apps = (app for app in os.listdir(os.path.join(path,cat)) if (app not in processed) and (f"structmappings-{app}" not in structmaps_made))

        master_dict[cat] = apps # Dictionary value for cat is generator

    # Set initial state for generators
    categories = (category for category in os.listdir(path))
    rceGen = None # Code extractor generator state
    rpsGen = None # Privacy similarity generator state
    count = 0
    cat = next(categories) # Current Category to process
    rceDone = False

    # This breaks out when all apps for all categories have been processed
    while True:
        try:
            app = next(master_dict[cat]) # Grab next app generator in cateogry
            break

        except StopIteration: # No apps left in generator
            print("All apps processed in cat",cat)

            try:
                cat = next(categories)

            except StopIteration: # No cateogories left in generator
                print("All cats processed")
                rceDone = True # Code extractor done

                break

    # Main processing loop
    while True:
        resultpath = os.path.join("full_results", cat)

        if not rceDone:
            if not rceGen: # No state for rce means need to grab an app and start Code Extractor
                mainpath = "/".join(app.replace(".","/").split("/")[0:-1]) # App name correlates to path to scan so can replace '.'s in name with '/'
                apppath = os.path.join(path, cat, app)
                target = os.path.join(apppath, "sources", mainpath)
                rceGen = runCodeExtractor(target, app, resultpath)

            try:
                extracted = next(rceGen) # Yield next step from Code Extractor

            except StopIteration: # Nothing left to yield from Code Extractor 
                smapqueue.put((extracted, app, resultpath)) # Add app structmappings file to queue since its fully extracted now

                try:
                    cat = next(categories) # Move to next category

                except StopIteration: # No categories left
                    count += 1
                    
                    if count == appcount: # If given appcount reached we are done extracting
                        print(f"Struct Mappings created for [{appcount}] apps per category. Now just waiting for PrivacySimilarity.")
                        rceDone = True

                    else: # More apps to process per category so reset category generator
                        categories = (category for category in os.listdir(path))
                        print(f"\nCycling Categories for next iteration of processing: {count}/{appcount}")

                try:
                    app = next(master_dict[cat]) # Get app from category

                except StopIteration: # None left
                    print("No more apps in category:", cat)

                rceGen = None 

        if rceDone and smapqueue.empty():
            break

        if rpsGen: # Generator for privacy similarity started?
            try:
                next(rpsGen) # yield next step in privacy similarity

            except StopIteration: # no more steps
                print("\n*** Finished Processing:", appname)

                # Show how many apps are left
                print(f"Remaining Queue: [{list(smapqueue.queue)}]")
                for i in list(smapqueue.queue):
                    print(i[1])

                rpsGen = None # rps is done so reset

        else: # Start privacy similarity generator
            if not smapqueue.empty(): # Check if there are structmappings files that can be processed
                structmapfile, appname, _resultpath = smapqueue.get() # Pop a file off the queue
                rpsGen = runPrivacySimilarity(structmapfile, _resultpath) # Start the rps generator

                try:
                    next(rpsGen) # Yield first step from Privacy similarity

                except StopIteration: # Something went wrong with the currently processing structmapfile
                    print("\nGot stop iteration immediately processing:", structmapfile)

if __name__ == "__main__":

    main(args.path, args.number_of_apps)
    print("Analysis Completed")

