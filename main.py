#!/usr/bin/env python2

import argparse
import utils
import XMLSerializer as XS

from Class import FileDetails


TEMP_DIR = utils.get_tmp_path()

def main(args):
    zipfilepath = args.zip
    if zipfilepath is None:
        print "pass arguements correctly!"
        exit(-1)
    xmlfilepath = args.xmlfile
    zip_path = zipfilepath
    if utils.valid_file(zip_path) is not True:
        print "bad zip"
        exit(-1)
    data_for_all_files = []
    path_to_extract = utils.random_temp_path(TEMP_DIR)
    utils.extractor(zip_path, path_to_extract)
    list_of_all_files = utils.getListOfFiles(path_to_extract)
    
    for path_to_file in list_of_all_files:
        uid = utils.get_uuid()
        filename = utils.stripfilepath(path_to_file)
        rel_path = utils.get_relative_path(path_to_file, path_to_extract)
        md5hash = utils.md5sum(path_to_file)
        filesize = utils.get_file_size(filepath=path_to_file)
        data = FileDetails(file_uuid=uid, file_name=filename, file_full_path=path_to_file, relative_path=rel_path, file_md5hash=md5hash, file_size=filesize)
        data_for_all_files.append(data)
    
    XS.XMLSerialize(data_for_all_files, xmlfilepath)
    utils.cleanup(path_to_extract)
    exit(0)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some zip files to an XML.')
    parser.add_argument('-z', '--zip', action="store", dest="zip", help="pass the path to zip file", required=True)
    parser.add_argument('-x', '--xml', action="store", dest="xmlfile", help="correct path to XML file", required=True)
    args = parser.parse_args()
    main(args)