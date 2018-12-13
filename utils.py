import zipfile
import os
import hashlib
import uuid

def extractor(path_to_zip_file, directory_to_extract):
    # extract zip files
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract)




def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    
    return allFiles


def md5sum(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    
    return hash_md5.hexdigest()


def path_exists(filepath):
    pass
    

def temp_dir_generator(dir_path):
    abspath = os.path.abspath(dir_path)
    uid = uuid.uuid4()
    new_temp_dir = os.path.join(abspath, str(uid))
    return new_temp_dir



def valid_file(file_path):
    if os.path.exists(file_path):
        return True
    else:
        return False

def valid_zip_file(zip_file):
    pass
