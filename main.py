import ConfigParser
import sys
import utils
from Class import FileDetails
import XMLSerializer as XS

TEMP_DIR = utils.get_tmp_path()

def main():
    args = sys.argv
    if len(args)!= 2:
        print "pass arguements correctly!"
        exit(-1)
    
    zip_path = args[1]
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
        md5hash = utils.md5sum(path_to_file)
        filesize = utils.get_file_size(filepath=path_to_file)
        data = FileDetails(file_uuid=uid, file_name=filename, file_full_path=path_to_file, file_md5hash=md5hash, file_size=filesize)
        data_for_all_files.append(data)
    
    XS.XMLSerialize(data_for_all_files)
    utils.cleanup(path_to_extract)
    exit(0)



if __name__ == "__main__":
    main()