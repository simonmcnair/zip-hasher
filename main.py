#!/usr/bin/env python2

import argparse
import utils
import os
from Class import FileDetails
import tempfile
import csv

pritest = tempfile.gettempdir() # prints the current temporary directory
createtempdir = tempfile.TemporaryDirectory()
#f = tempfile.TemporaryFile()
supported_extensions = ['.rar','.cbr','.zip','cbz']

def main(args):
    dirtoprocess = args.dir
    csv_file_path = args.output
    if not os.path.isfile(csv_file_path):
        with open(csv_file_path, mode='a', newline='',quoting=csv.QUOTE_ALL) as file:
            writer = csv.writer(file)
            header = ["archive", 'path to file',"filename","hash"]
            writer.writerow(header)

    if os.path.exists(dirtoprocess):

        for root, dirs, files in os.walk(dirtoprocess):

            for file_name in files:

                extension = os.path.splitext(file_name)[1].lower()
                full_file_path = (os.path.join(root, file_name))

                if extension in supported_extensions:
                    if utils.valid_file(full_file_path) is not True:
                        print ("bad zip")

                    with tempfile.TemporaryDirectory() as path_to_extract:
                        print('created temporary directory', path_to_extract)
                        utils.extractor(full_file_path, path_to_extract)
                        list_of_all_files = utils.getListOfFiles(path_to_extract)
                        with open(csv_file_path, mode='a', newline='',quoting=csv.QUOTE_ALL) as file:
                            writer = csv.writer(file)

                            for path_to_file in list_of_all_files:
                                filename = utils.stripfilepath(path_to_file)
                                #rel_path = utils.get_relative_path(path_to_file, path_to_extract)
                                #hash = utils.md5sum(path_to_file)
                                hash = utils.calculate_blake2(path_to_file)
                                #filesize = utils.get_file_size(filepath=path_to_file)
                                #data = FileDetails(fullpath=full_file_path, full_file_path=filename, relative_path=rel_path, file_hash=hash, file_size=filesize)
                                #writer.writerow([full_file_path,filename,rel_path,hash,filesize])
                                writer.writerow([full_file_path,'-',filename,hash])

                elif extension == '.jpg' or extension == '.jpeg' or extension == '.gif':
                    hash = utils.calculate_blake2(full_file_path)
                    with open(csv_file_path, mode='a', newline='',quoting=csv.QUOTE_ALL) as file:
                        writer = csv.writer(file)
                        writer.writerow(['-',root,file_name,hash])

                else:
                    print("Unsupported extension " + extension + "({full_file_path})")




parser = argparse.ArgumentParser(description='Process some zip files to an XML.')
parser.add_argument('-d', '--dir', action="store", dest="dir", type=str, help="pass the path to zip files", required=False,default="/srv/dev-disk-by-uuid-342ac512-ae09-47a7-842f-d3158537d395/mnt/Comics")
parser.add_argument('-o', '--outputfile', action="store", dest="output", type=str, help="outputcsv", required=False,default="/srv/dev-disk-by-uuid-342ac512-ae09-47a7-842f-d3158537d395/mnt/Comics/output.csv")

if __name__=='__main__':
    args = parser.parse_args()
    main(args)