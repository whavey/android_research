#!/usr/bin/python3
import os
from pathlib import Path

#Variables
decompiled_dir = "/store/whavey/apk_downloader/apks_20191216-225315/00_decompiled_apks/apks_20191216-225315/"
#decompiled_dir = "/store/church/test_common_sources/"
source_list = {}
reduced_list = []

def crawl():

    # Use os.walker to recursively search for the 'sources' directory for each APK
    for dir_path, dir_names, file_names in os.walk(decompiled_dir):       
        
        for current_folder in dir_names:
            
            # Look for APK Source Folders
            if current_folder == "sources":
                
                # Aboslute Path of Current APK Source Directory
                source_abs_path = (os.path.join(dir_path, current_folder))
                
                # Get Current APK Name
                check_file = (os.path.basename(Path(source_abs_path).parent))
                if check_file.endswith(".apk") == True:
                    current_apk = check_file

                # Negate Files
                if os.path.isdir(source_abs_path):

                    # Search Through External Libraries
                    for library in os.listdir(source_abs_path):
                        
                        # Absolute Path of Current External Library
                        library_abs_path = (os.path.join(source_abs_path, library))

                        # Negate Files
                        if os.path.isdir(library_abs_path):

                            # Repeated External Library
                            if library in source_list:
                                
                                source_list[library].append(current_apk)

                            # Unique External Library
                            else:

                                source_list[library] = [current_apk]
    
    # Reduce Source List for Repeated External Libraries
    for lib in source_list:
        if len(source_list[lib]) > 1:
            reduced_list.append(lib)

    # Print and Return Results
    print("\nSource List:\n")
    print(source_list)
    
    print("\nReduced List:\n")
    print(reduced_list)
    
    return reduced_list


def main():
   
    print("\nSearching for External Libraries.  Please wait...\n")

    crawl()

    print("\nFinished.  The Reduced External Library List has been returned.\n")

main()
