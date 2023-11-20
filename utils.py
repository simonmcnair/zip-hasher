import zipfile
import os
import hashlib
import platform
import shutil
import patoolib

#import ConfigParser


#CONFIG = r'config.txt'
#CONFIGPARSER = None

def extractor(path_to_zip_file, directory_to_extract):
    print ("extracting files ...")
    # extract zip files
    extension = os.path.splitext(path_to_zip_file)
    if extension[1].lower() == '.cbr' or extension.lower() == '.rar':
        patoolib.extract_archive(path_to_zip_file, outdir=directory_to_extract)
    elif extension[1].lower() == '.cbz' or extension.lower() == '.zip':
        with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
            zip_ref.extractall(directory_to_extract)

def get_relative_path(path_to_file, temp_dir):
    return os.path.relpath(path_to_file, temp_dir)

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

def calculate_blake2(file_path, block_size=65536):
    hasher = hashlib.blake2b()

    with open(file_path, 'rb') as file:
        # Read the file in blocks and update the hash
        for block in iter(lambda: file.read(block_size), b''):
            hasher.update(block)

    # Return the hexadecimal digest of the hash
    return hasher.hexdigest()

def md5sum(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    
    return hash_md5.hexdigest()


def path_exists(filepath):
    pass

def get_file_size(filepath):
    statinfo = os.stat(filepath)
    return statinfo.st_size
    
def valid_file(file_path):
    if os.path.exists(file_path):
        return True
    else:
        return False

def valid_zip_file(zip_file):
        #"""Open the zip file a first time, to check that it is a valid zip archive."""
        try:
            zip = zipfile.ZipFile(zip_file)
        except zipfile.BadZipfile as e:
            print ("bad zip file")
            return False
        bad_file = zip.testzip()
        if bad_file:
            zip.close()
            print('"%s" in the .zip archive is corrupt.' % bad_file)
            print ("bad zip file")
            return False
        zip.close()  # Close file in all cases.
        print ("good zip file")
        return True


def stripfilepath(full_file_path):
    return os.path.basename(full_file_path)


def get_platform():
    pform = platform.system()
    return pform.lower()

#def readConfig():
#    print ("reading config..")
#    configParser = ConfigParser.RawConfigParser()
#    configFilePath = CONFIG
#    configParser.read(configFilePath)
#    return configParser





def cleanup(dir_path):
    shutil.rmtree(dir_path)
    print ("deleted temp dir")
