# This script takes in a file name and file path and renames all pictures 
# in the file path to the passed in file name with an appended timestamp
# that is extract from the EXIF picture data
# TODO: Make portable by isolating WSL exclusive logic
#       Add mp4 functonality and other image types (non-EXIF metadata)
#       Add exception handling for extracting EXIF data

import sys
import os
import getopt
import re
import shutil

from PIL import Image
from PIL.ExifTags import TAGS

def get_timestamp(image_name):
    tag_id = 306 # 306 is number for exif datetime tag
    
    image = Image.open(image_name)
    exifdata = image.getexif()
    #data = exifdata.get(tag_id)
    #print(data)
    
    return exifdata.get(tag_id)

def back_up_file(FQP_file, backup_path):   # fully qualified path file 
    #print(FQP_file)
    try:
        shutil.copy2(FQP_file, backup_path) # copy2 preserves metadata and permissions
    except IOError:
        print("Unable to copy file")
        return 1

    print(f"file backed up successfully")
    
    return 0

    
def main(argv):
    #print(os.getcwd()) # WSL resolves this to /mnt/c/Users/Jason/...
    #print(argv)
    usage = 'usage: '+sys.argv[0]+' -n <new_file_name> -p <file_path>'
    
    try:
        opts, args = getopt.getopt(argv, "hn:p:", ["help", "name=", "path="])   # opts is a list (option,value) pairs, args is list of the rest
    except getopt.GetoptError:
        print(usage)
        print("use -h or --help for more options") 
        sys.exit(2)
        
    for opt, arg in opts:   # unpack opts into opt and arg 
        if(opt == "-h" or opt == "--help"):
            print(usage)
            print("-n --name= <new_file_name>\tfile names with spaces will be replaced with underscores")
            print("-p --path= <file_path>")
            sys.exit(0)
        
        elif(opt == "-n"):
            print(f"new filename: {arg}")
            base_filename = arg
            
        elif(opt == "-p"):
            print(f"file path: {arg}")
            win_path = arg
        else:
            print(f"unknown option: {opt}")
            sys.exit(2)

    print(f"looking in: {win_path}")
    
    # NOTE: this following is exclusive to the Windows Subsystem for Linux (WSL)
    working_dir = win_path.replace("\\", "/").replace("C:", "/mnt/c")
    
    # We don't tolerate whitespace in our filenames in this household
    base_filename = base_filename.replace(" ", "_")

    try:
        backup_path = working_dir + "/BACKUP" 
        os.mkdir(backup_path)
    except FileExistsError:
        print("backup directory already exists, continuing...")
    
    print(f"backing up files to: {backup_path}")
    
    with os.scandir(working_dir) as entries:
        for entry in entries:
            if(re.search('jpg', entry.name, flags=re.IGNORECASE)): # TODO: add more file extensions
                #print(entry.name)
                fn, fext = os.path.splitext(entry.name)
                fn_timestamp = get_timestamp(entry.name).replace(":", "_").replace(" ", "-")
                #fn_timestamp += fext
                filename = base_filename + "_" + fn_timestamp + fext
                
                ret = back_up_file(working_dir+"/"+entry.name, backup_path) # moved to separate function for tidiness
                
                if(ret != 0):   # shell habits kicking in
                    print(f"backup of {entry.name} failed. skipping file...")
                    continue

                print(f"renaming {entry.name} to {filename}")
                os.rename(entry.name, filename)

if (__name__) == "__main__":    # only run main if calling this script standalone. main won't run if imported
    main(sys.argv[1:])


