import os
import hashlib
import platform
import shutil
import patoolib
from PIL import Image
import logging
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
import sys
import csv


def setup_logging(log_file):
    # Configure logging
    # Set up the root logger
    logger = logging.getLogger('my_logger')
    if not logger.handlers:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        # Create a handler and set the level to the lowest level you want to log
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.DEBUG)

        # Create a formatter and set it on the handler
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Add the handler to the root logger
        logging.getLogger('my_logger').addHandler(handler)

        # Add the console handler to the root logger
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logging.getLogger('my_logger').addHandler(console_handler)


def sortcsv(input_csv_path,output_csv_path,field):

    try:
            # Read the CSV file into a list of dictionaries
        with open(input_csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)

        # Sort the data based on the 'field' field
        sorted_data = sorted(data, key=lambda x: x[field])

        # Write the sorted data back to a new CSV file
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write the header
            writer.writeheader()
            
            # Write the sorted rows
            writer.writerows(sorted_data)

        logging.info(f"CSV file sorted and saved to {output_csv_path}")
        return True

    except Exception as e:
        logging.error( ' failed to sort CSV.  Error: ' + str(e))
        return False
    
def createimagehash(picture_path):
    logging.info("Reading in " + picture_path)
 
    try:
        with Image.open(picture_path, formats=None) as image:
            # Get the image data as bytes
            image.load()
            image_bytes = image.tobytes()
        # Create a hash object and update with image bytes
        hash_object = hashlib.blake2b(image_bytes)
        hash_value = hash_object.hexdigest()
        logging.info(hash_value + " is hash for " + picture_path)
        return hash_value
    except Exception as e:
        logging.warning(picture_path + ' failed to generate image hash.  Error: ' + str(e))
        return None


def createaudiohash(filetohash):
    logging.info("Hashing " + filetohash)
    #while True:
    try:
        audio = AudioSegment.from_file(filetohash)
        hash = hashlib.blake2b(audio.raw_data, digest_size=16).hexdigest()
        logging.info(hash + " is hash for " + filetohash)
        return hash
    except CouldntDecodeError as e:
        logging.error(f"Failed to decode audio file: {e}")
        return None
    except IndexError as e:
        logging.error(f"Index out of range error: {e}")
        return None
    except KeyboardInterrupt:
        # This block will be executed when Ctrl+C is pressed
        logging.info("Ctrl+C received. Exiting gracefully...")
        # Perform cleanup operations here, if needed
        sys.exit(0)
    except Exception as e:
        logging.error("Could not create audio hash " +  str(e))
        return None

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
  
def writecsvrow(theoutputfile,contents):

    try:
        with open(theoutputfile, mode='a', newline='') as file:
            writer = csv.writer(file,quoting=csv.QUOTE_ALL)
            writer.writerow(contents)
        file.close
        del file
    except Exception as e:
        logging.error(' FAILED to insert csv row  Error ' + str(e))
        return False
    return True


def extractor(path_to_zip_file, directory_to_extract):
    logging.info ("extracting files ...")

    try:
        patoolib.extract_archive(path_to_zip_file, outdir=directory_to_extract)
    except Exception as e:
        logging.error(' FAILED to extract: ' + path_to_zip_file + ".  Error " + str(e))
        prepend_text_to_filename(path_to_zip_file, 'bad_archive_')
        return False
    return True

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

def calculate_blake2b(file_path, block_size=65536):
    hasher = hashlib.blake2b()
    try:
        with open(file_path, 'rb') as file:
            # Read the file in blocks and update the hash
            for block in iter(lambda: file.read(block_size), b''):
                hasher.update(block)
            result = hasher.hexdigest()
        logging.info("Hash for " + file_path + " is " + result)
        return result

    except Exception as e:
        logging.error("failed to calculate hash " + str(e))
        return False

    # Return the hexadecimal digest of the hash

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


