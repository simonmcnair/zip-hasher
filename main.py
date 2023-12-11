#!/usr/bin/env python2

import argparse
import utils
import os
import tempfile
import csv
from PIL import Image

exts = Image.registered_extensions()
supported_image_extensions = {ex for ex, f in exts.items() if f in Image.OPEN}
supported_archive_extensions = ['.rar','.cbr','.zip','.cbz','.7z','.7zip']
supported_audio_extensions = ['.mp3','.flac']

pritest = tempfile.gettempdir() # prints the current temporary directory
createtempdir = tempfile.TemporaryDirectory()
#f = tempfile.TemporaryFile()



def main(args):
    dirtoprocess = os.path.normpath(args.dir)
    csv_file_path = os.path.normpath(args.outputcsv)
    logfile = os.path.normpath(args.logfile)
    remainfile = os.path.normpath(args.remainfile)
    utils.setup_logging(logfile)



    processing_dir = utils.get_directory(csv_file_path)
    sortedfilepath = os.path.join(processing_dir, 'sorted.csv')
    dupefilepath = os.path.join(processing_dir, 'dupepath.csv')



    utils.logging.info('path : ' + str(dirtoprocess))
    utils.logging.info('path : ' + str(csv_file_path))
    utils.logging.info('path : ' + str(logfile))
    utils.logging.info('path : ' + str(remainfile))
    utils.logging.info('path : ' + str(processing_dir ))
    utils.logging.info('path : ' + str(sortedfilepath ))
    utils.logging.info('path : ' + str(dupefilepath ))


    utils.logging.info('supported archive extensions : ' + str(supported_archive_extensions))
    utils.logging.info('supported image extensions   : ' + str(supported_image_extensions))
    utils.logging.info('supported Audio extensions   : ' + str(supported_audio_extensions))


    if os.path.isfile(csv_file_path):
        utils.logging.info("csv file present")
        filename_array = []

        with open(csv_file_path, 'r', encoding='utf-8', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            try:
                for row in csv_reader:
                    filename_array.append(row["filename"])
                    utils.logging.debug("adding " + row["filename"] + " to array.")
            except Exception as e:
                utils.logging.error(' FAILED to read csv row  Error ' + str(e))
                utils.sys.exit(1)
        array = True
    else:
        utils.logging.info("No csv file, create one.")
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file,quoting=csv.QUOTE_ALL)
            header = ["filename","archive","type", "path to file if archive","hash"]
            writer.writerow(header) 
            array = False   

    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file,quoting=csv.QUOTE_ALL)

        if os.path.exists(dirtoprocess):

            for root, dirs, files in os.walk(dirtoprocess):

                for file_name in files:

                    extension = os.path.splitext(file_name)[1].lower()
                    full_file_path = (os.path.join(root, file_name))

                    if array == True and full_file_path in filename_array:
                        utils.logging.info(f"file {full_file_path} is already in CSV.  Skipping and removing from array.  array size is " + str(len(filename_array)))
                        # Remove filename from the array
                        filename_array.remove(full_file_path)
                        continue
                    else:
                        # Process the file (replace this with your processing logic)
                        print(f"File not in CSV.  Processing file: {full_file_path}")

                        if os.path.normpath(full_file_path) == os.path.normpath(csv_file_path) or os.path.normpath(full_file_path) == os.path.normpath(logfile):
                            utils.logging.info("not processing csv or log file" + full_file_path)
                            continue

                        if extension in supported_archive_extensions:
                            utils.logging.info("Processing archive : " + full_file_path)
                            with tempfile.TemporaryDirectory() as path_to_extract:
                                utils.logging.info('created temporary directory' + path_to_extract)
                                result = utils.extractor(full_file_path, path_to_extract)
                                if result != False:
                                    list_of_all_files = utils.getListOfFiles(path_to_extract)
                                    for path_to_file in list_of_all_files:
                                        utils.logging.info("processing " + path_to_file)
                                        file_extension = os.path.splitext(path_to_file)[1].lower()
                                        relativefilename = utils.stripfilepath(path_to_file)

                                        if file_extension in supported_image_extensions:
                                            hash = utils.createimagehash(path_to_file)
                                            type = 'image'
                                        elif file_extension in supported_audio_extensions:
                                            hash = utils.createaudiohash(path_to_file)
                                            type= 'audio'
                                        else:
                                            utils.logging.info("unknown file just hash it. " + file_extension + " " + path_to_file)
                                            hash = utils.calculate_blake2b(path_to_file)
                                            type = 'other'

                                        if hash != False:
                                            #utils.writecsvrow(csv_file_path,[full_file_path,'archive',relativefilename,hash])
                                            writer.writerow([full_file_path,'archive',type,relativefilename,hash])
                                        else:
                                            utils.logging.warning("no hash created for " + full_file_path)


                        elif extension in supported_image_extensions:
                            utils.logging.info("Processing image : " + full_file_path)
                            hash = utils.createimagehash(full_file_path)
                            if hash != False:
                                #utils.writecsvrow(csv_file_path,[full_file_path,'image','-',hash])
                                writer.writerow([full_file_path,'-','image','-',hash])
                            else:
                                utils.logging.warning("no hash created for " + full_file_path)

                        elif extension in supported_audio_extensions:
                            utils.logging.info("Processing audio : " + full_file_path)
                            hash = utils.createaudiohash(full_file_path)
                            if hash != False:
                                #utils.writecsvrow(csv_file_path,[full_file_path,'audio','-',hash])
                                writer.writerow([full_file_path,'-','audio','-',hash])
                            else:
                                utils.logging.warning("no hash created for " + full_file_path)
                        else:
                            utils.logging.info("Processing file : " + full_file_path)
                            hash = utils.calculate_blake2b(full_file_path)
                            if hash != False:
                                #utils.writecsvrow(csv_file_path,[full_file_path,'other','-',hash])
                                writer.writerow([full_file_path,'-','other','-',hash])
                            else:
                                utils.logging.warning("no hash created for " + full_file_path)

    with open(remainfile, 'w', encoding='utf-8', newline='') as log_file:
        for remaining_file in filename_array:
            log_file.write(f"Unprocessed file: {remaining_file}\n")


    result = utils.remove_duplicates(csv_file_path,dupefilepath,'filename')
    result = utils.remove_unique_hashes(csv_file_path,sortedfilepath,'hash')
    result = utils.sortcsv(sortedfilepath,sortedfilepath,'hash')

    if result ==True :
        print("Sort success")
    else:
        print("Sort failed")


parser = argparse.ArgumentParser(description='Process some zip files to an XML.')
#parser.add_argument('-d', '--dir', action="store", dest="dir", type=str, help="pass the path to zip files", required=False,default="/srv/dev-disk-by-uuid-342ac512-ae09-47a7-842f-d3158537d395/mnt/Comics")
#parser.add_argument('-o', '--outputfile', action="store", dest="output", type=str, help="outputcsv", required=False,default="/srv/dev-disk-by-uuid-342ac512-ae09-47a7-842f-d3158537d395/mnt/Comics/output.csv")
#parser.add_argument('-l', '--logfile', action="store", dest="logfile", type=str, help="log file", required=False,default="/srv/dev-disk-by-uuid-342ac512-ae09-47a7-842f-d3158537d395/mnt/Comics/logfile.txt")

parser.add_argument('-d', '--dir', action="store", dest="dir", type=str, help="pass the path to zip files", required=False,default="/srv/dev-disk-by-uuid-342ac512-ae09-47a7-842f-d3158537d395/mnt/Audio")
parser.add_argument('-o', '--outputfile', action="store", dest="outputcsv", type=str, help="path to csv file", required=False,default="/srv/dev-disk-by-uuid-342ac512-ae09-47a7-842f-d3158537d395/mnt/Audio/output.csv")
parser.add_argument('-l', '--logfile', action="store", dest="logfile", type=str, help="log file path", required=False,default="/srv/dev-disk-by-uuid-342ac512-ae09-47a7-842f-d3158537d395/mnt/Audio/logfile.txt")
parser.add_argument('-r', '--remainder', action="store", dest="remainfile", type=str, help="remain file path", required=False,default="/srv/dev-disk-by-uuid-342ac512-ae09-47a7-842f-d3158537d395/mnt/Audio/remain.txt")

#parser.add_argument('-d', '--dir', action="store", dest="dir", type=str, help="pass the path to zip files", required=False,default="Z:/Audio")
#parser.add_argument('-o', '--outputfile', action="store", dest="outputcsv", type=str, help="outputcsv", required=False,default="Z:/Audio/output.csv")
#parser.add_argument('-l', '--logfile', action="store", dest="logfile", type=str, help="log file", required=False,default="Z:/Audio/logfile.txt")
#parser.add_argument('-r', '--remainder', action="store", dest="remainfile", type=str, help="remain file path", required=False,default="z:/Audio/remain.txt")

if __name__=='__main__':
    args = parser.parse_args()
    main(args)