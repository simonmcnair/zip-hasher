#!/usr/bin/env python2

import argparse
import utils
import os
import tempfile
import csv
from PIL import Image

exts = Image.registered_extensions()
supported_image_extensions = {ex for ex, f in exts.items() if f in Image.OPEN}

pritest = tempfile.gettempdir() # prints the current temporary directory
createtempdir = tempfile.TemporaryDirectory()
#f = tempfile.TemporaryFile()
supported_extensions = ['.rar','.cbr','.zip','.cbz','.7z','.7zip']



def main(args):
    dirtoprocess = args.dir
    csv_file_path = args.output
    utils.setup_logging(args.logfile)

    utils.logging.error('supported extensions  ' + str(supported_extensions))
    utils.logging.error('supported image extensions  ' + str(supported_image_extensions))


    if not os.path.isfile(csv_file_path):
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file,quoting=csv.QUOTE_ALL)
            header = ["archive", 'path to file',"filename","hash"]
            writer.writerow(header)

    if os.path.exists(dirtoprocess):

        for root, dirs, files in os.walk(dirtoprocess):

            for file_name in files:

                
                extension = os.path.splitext(file_name)[1].lower()
                full_file_path = (os.path.join(root, file_name))

                if full_file_path == args.output or full_file_path == args.logfile:
                    print("not processing csv or log file")
                    continue

                if extension in supported_extensions:
                    with tempfile.TemporaryDirectory() as path_to_extract:
                        print('created temporary directory', path_to_extract)
                        utils.extractor(full_file_path, path_to_extract)
                        list_of_all_files = utils.getListOfFiles(path_to_extract)
                        with open(csv_file_path, mode='a', newline='') as file:
                            writer = csv.writer(file,quoting=csv.QUOTE_ALL)
                            for path_to_file in list_of_all_files:
                                print("processing " + path_to_file)
                                file_extension = os.path.splitext(path_to_file)[1].lower()
                                if file_extension in supported_image_extensions:
                                    ret = utils.test_image(path_to_file)
                                    if ret == False:
                                        print("oops corrupt image")                                    
                                        utils.logging.error(' corrupt image ' + path_to_file)
                                    elif ret == True:
                                        print("valid image")
                                else:
                                    print("Not an image file. " + extension)
                                    utils.logging.info("Not an image file. " + extension)

                                filename = utils.stripfilepath(path_to_file)
                                #rel_path = utils.get_relative_path(path_to_file, path_to_extract)
                                hash = utils.calculate_blake2(path_to_file)
                                writer.writerow([full_file_path,'-',filename,hash])

                elif extension in supported_image_extensions:
                    ret = utils.test_image(path_to_file)
                    if ret == False:
                        print("oops corrupt image")                                    
                        utils.logging.error(' corrupt image ' + path_to_file)
                    elif ret == True:
                        print("valid image")
                        hash = utils.calculate_blake2(full_file_path)
                        with open(csv_file_path, mode='a', newline='') as file:
                            writer = csv.writer(file,quoting=csv.QUOTE_ALL)
                            writer.writerow(['-',root,file_name,hash])

                else:
                    hash = utils.calculate_blake2(full_file_path)
                    with open(csv_file_path, mode='a', newline='') as file:
                        writer = csv.writer(file,quoting=csv.QUOTE_ALL)
                        writer.writerow(['-',root,file_name,hash])




parser = argparse.ArgumentParser(description='Process some zip files to an XML.')
parser.add_argument('-d', '--dir', action="store", dest="dir", type=str, help="pass the path to zip files", required=False,default="/srv/dev-disk-by-uuid-342ac512-ae09-47a7-842f-d3158537d395/mnt/Comics")
parser.add_argument('-o', '--outputfile', action="store", dest="output", type=str, help="outputcsv", required=False,default="/srv/dev-disk-by-uuid-342ac512-ae09-47a7-842f-d3158537d395/mnt/Comics/output.csv")
parser.add_argument('-l', '--logfile', action="store", dest="logfile", type=str, help="log file", required=False,default="/srv/dev-disk-by-uuid-342ac512-ae09-47a7-842f-d3158537d395/mnt/Comics/logfile.txt")

#parser.add_argument('-d', '--dir', action="store", dest="dir", type=str, help="pass the path to zip files", required=False,default="Y:/6tb1/root")
#parser.add_argument('-o', '--outputfile', action="store", dest="output", type=str, help="outputcsv", required=False,default="Y:/6tb1/root/output.csv")
#parser.add_argument('-l', '--logfile', action="store", dest="logfile", type=str, help="log file", required=False,default="Y:/6tb1/root/logfile.txt")

if __name__=='__main__':
    args = parser.parse_args()
    main(args)