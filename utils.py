import os
import hashlib
import platform
import shutil
import patoolib
from PIL import Image
import logging

def setup_logging(log_file):
    # Configure logging
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def prepend_text_to_filename(filepath, text_to_prepend):
    directory, filename = os.path.split(filepath)
    base_name, extension = os.path.splitext(filename)
    if base_name.startswith(text_to_prepend):
        logging.info(filepath + " already begins with " + text_to_prepend)
        return filepath
     
    new_base_name = f"{text_to_prepend}_{base_name}"
    new_filepath = os.path.join(directory, new_base_name + extension)
    try:
        shutil.move(filepath,new_filepath)
    except Exception as e:
        logging.error(' FAILED to move: ' + filepath + " to " + new_filepath + ".  Error " + str(e))
        return

    return new_filepath

def test_image(infile):
    try:
        with Image.open(infile, mode='r', formats=None) as im:
            try:
                im.load()
            except Exception as e:
                logging.error(' FAILED to load: ' + infile + " as an image.  Error " + str(e))
                return False
    except Exception as e:
        logging.error(' FAILED to open: ' + infile + " as an image.  Error " + str(e))
        return False
    return True


        
def extractor(path_to_zip_file, directory_to_extract):
    print ("extracting files ...")

    try:
        patoolib.extract_archive(path_to_zip_file, outdir=directory_to_extract)
    except Exception as e:
        print("Failed to test archive")
        logging.error(' FAILED to extract: ' + path_to_zip_file + ".  Error " + str(e))
        prepend_text_to_filename(path_to_zip_file, 'bad_archive_')
        return

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

def stripfilepath(full_file_path):
    return os.path.basename(full_file_path)


def get_platform():
    pform = platform.system()
    return pform.lower()


