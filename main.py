#!/usr/bin/env python2

import argparse
import os
import tempfile
import csv
import sys
from PIL import Image
import utils
from pathlib import Path
#python3.11 -m venv venv
#source ./venv/bin/activate
#pip install pataool
#pip install psutil
#pip install pillow


exts = Image.registered_extensions()
supported_image_extensions = {ex for ex, f in exts.items() if f in Image.OPEN}
supported_archive_extensions = ['.rar','.cbr','.zip','.cbz','.7z','.7zip']
supported_audio_extensions = ['.mp3','.flac']

pritest = tempfile.gettempdir() # prints the current temporary directory
createtempdir = tempfile.TemporaryDirectory()
#f = tempfile.TemporaryFile()

def get_script_name():
    # Use os.path.basename to get the base name (script name) from the full path
    #basename = os.path.basename(path)
    return Path(__file__).stem
    #return os.path.basename(__file__)

def get_script_path():
    return os.path.dirname(os.path.realpath(__file__))


def main():
    """Main subroutine"""
    utils.logging.info('path : ' + str(dirtoprocess))
    utils.logging.info('path : ' + str(csv_file_path))
    utils.logging.info('path : ' + str(log_file_path))
    utils.logging.info('path : ' + str(remainfile))
    utils.logging.info('path : ' + str(dirtoprocess ))
    utils.logging.info('path : ' + str(sortedfilepath ))
    utils.logging.info('path : ' + str(dupefilepath ))

    utils.logging.info('supported archive extensions : ' + str(supported_archive_extensions))
    utils.logging.info('supported image extensions   : ' + str(supported_image_extensions))
    utils.logging.info('supported Audio extensions   : ' + str(supported_audio_extensions))

    if os.path.isfile(cache_file_path):
        utils.logging.info("csv file present")
        filename_array = []

        with open(cache_file_path, 'r', encoding='utf-8', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            try:
                for row in csv_reader:
                    filename_array.append(row["filename"])
                    utils.logging.debug("adding " + row["filename"] + " to array.")
            except Exception as e:
                utils.logging.error(' FAILED to read csv row  Error ' + str(e))
                utils.sys.exit(1)
        array = True
        utils.logging.debug("The number of cache entries is " + str(len(filename_array)))
    else:
        utils.logging.info("No csv file, create one.")
        utils.writecsvrow(cache_file_path,["filename","archive","type", "path to file if archive","hash"])

       # with open(cache_file_path, mode='w', newline='', encoding='utf-8') as file:
       #     writer = csv.writer(file,quoting=csv.QUOTE_ALL)
       #     header = ["filename","archive","type", "path to file if archive","hash"]
       #     writer.writerow(header) 
        array = False


    if os.path.exists(dirtoprocess):

        for root, dirs, files in os.walk(dirtoprocess):

            for file_name in files:

                hasher = []
                extension = os.path.splitext(file_name)[1].lower()
                full_file_path = os.path.join(root, file_name)

                if array is True and full_file_path in filename_array:
                    utils.logging.debug(f"file {full_file_path} is already in CSV.  Skipping and removing from array.  array size is " + str(len(filename_array)))
                    # Remove filename from the array
                    filename_array.remove(full_file_path)
                    continue
                else:
                    # Process the file (replace this with your processing logic)
                    utils.logging.info(f"File not in CSV.  Processing file: {full_file_path}")

                    if os.path.normpath(full_file_path) == os.path.normpath(cache_file_path) or os.path.normpath(full_file_path) == os.path.normpath(log_file_path):
                        utils.logging.info("not processing csv or log file" + full_file_path)
                        continue

                    isarchive = 'False'
                    hashret = False
                    relativefilename = '-'

                    if extension in supported_archive_extensions:
                        utils.logging.info("Processing archive : " + full_file_path)
                        isarchive = 'True'
                        if utils.is_file_larger_than(full_file_path, maxarchive_size):
                            utils.logging.warning("file "+ "full_file_path + is larger than " + str(maxarchive_size) + " so skip it")
                            continue

                        try:
                            with tempfile.TemporaryDirectory() as path_to_extract:
                                utils.logging.info('created temporary directory' + path_to_extract)
                                result = utils.extractor(full_file_path, path_to_extract)
                                if result is not False:
                                    list_of_all_files = utils.getListOfFiles(path_to_extract)
                                    for path_to_file in list_of_all_files:
                                        utils.logging.info("processing " + path_to_file)
                                        file_extension = os.path.splitext(path_to_file)[1].lower()
                                        relativefilename = utils.stripfilepath(path_to_file)

                                        if file_extension in supported_image_extensions:
                                            hash = (utils.createimagehash(path_to_file))
                                            filetype = 'image'
                                        elif file_extension in supported_audio_extensions:
                                            hash = (utils.createaudiohash(path_to_file))
                                            filetype= 'audio'
                                        else:
                                            utils.logging.info("unknown file just hash it. " + file_extension + " " + path_to_file)
                                            hash = (utils.calculate_blake2b(path_to_file))
                                            filetype = 'other'
                                        if hash != False:
                                            deets = [full_file_path,isarchive,filetype,relativefilename,hash]
                                            hasher.append (deets)
                                    hashret = True
                                else:
                                    hashret = False
                        except Exception as e:
                            utils.logging.error("extraction FAILED.  Error " + str(e))
                            hashret = False

                    elif extension in supported_image_extensions:
                        utils.logging.info("Processing image : " + full_file_path)
                        hashret = (utils.createimagehash(full_file_path))
                        filetype = 'image'

                    elif extension in supported_audio_extensions:
                        utils.logging.info("Processing audio : " + full_file_path)
                        hashret = (utils.createaudiohash(full_file_path))
                        filetype = 'audio'
                    else:
                        utils.logging.info("Processing file : " + full_file_path)
                        hashret = (utils.calculate_blake2b(full_file_path))
                        filetype = 'other'

                    if hashret != False:
                        if len(hasher) >0:
                            for each in hasher:
                                utils.writecsvrow(cache_file_path,[each[0],each[1],each[2],each[3],each[4]])
                        else:
                            utils.writecsvrow(cache_file_path,[full_file_path,isarchive,filetype,relativefilename,hashret])

                    else:
                        utils.logging.error("no hash created for " + full_file_path)


    with open(remainfile, 'w', encoding='utf-8', newline='') as log_file:
        for remaining_file in filename_array:
            log_file.write(f"Unprocessed file: {remaining_file}\n")


    utils.remove_duplicates(cache_file_path,dupefilepath,'filename')
    utils.remove_unique_hashes(dupefilepath,sortedfilepath,'hash')
    result = utils.sortcsv(sortedfilepath,sortedfilepath,'hash')

    if result is True :
        utils.logging.info("Sort success")
    else:
        utils.logging.info("Sort failed")


#processing_dir = os.path.dirname(os.path.abspath(__file__))
localoverridesfile = os.path.join(get_script_path(), "localoverridesfile_" + get_script_name() + '.py')
log_file_path =  os.path.join(get_script_path(),get_script_name() + '.log')
cache_file_path =  os.path.join(get_script_path(),get_script_name() + '.cache')
maxarchive_size='1GB'

if __name__=='__main__':
    if len(sys.argv) > 1:

        parser = argparse.ArgumentParser(description='Process some zip files to an XML.')

        parser.add_argument('-d', '--dir', action="store", dest="dir", type=str, help="pass the path to zip files", required=False,default="/folder/to/index")
        parser.add_argument('-o', '--outputfile', action="store", dest="outputcsv", type=str, help="path to csv file", required=False,default="/folder/to/output.csv")
        #parser.add_argument('-l', '--logfile', action="store", dest="log_file_path", type=str, help="log file path", required=False,default="/folder/to/logfile.txt")
        parser.add_argument('-r', '--remainder', action="store", dest="remainfile", type=str, help="remain file path", required=False,default="/folder/to/remain.txt")

        args = parser.parse_args()
        dirtoprocess = os.path.normpath(args.dir)
        csv_file_path = os.path.normpath(args.outputcsv)
        #log_file_path = os.path.normpath(args.logfile)
        remainfile = os.path.normpath(args.remainfile)
        cache_file_path = os.path.join(get_script_path(),   'cache.csv')
        sortedfilepath = os.path.join(get_script_path(),  'sorted.csv')
        dupefilepath = os.path.join(get_script_path(),  'dupepath.csv')

        utils.setup_logging(log_file_path, log_level=logging.INFO)
        main()
    else:

        dirtoprocess = "/folder/to/index"
        csv_file_path = os.path.join(get_script_path(),   'output.csv')
        cache_file_path = os.path.join(get_script_path(),   'cache.csv')
        remainfile = os.path.join(get_script_path(),   'remainfile.log')
        sortedfilepath = os.path.join(get_script_path(),  'sorted.csv')
        dupefilepath = os.path.join(get_script_path(),  'dupepath.csv')

        if os.path.exists(localoverridesfile):
            exec(open(localoverridesfile).read())
            #api_key = apikey
            #print("API Key:", api_key)
        else:
            print("No local overrides.")

        utils.setup_logging(log_file_path,'info')
        main()
