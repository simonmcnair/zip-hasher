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
from collections import defaultdict



def setup_logging(log_file):
    # Configure logging
    # Set up the root logger
    try:
        logger = logging.getLogger()

        if not logger.handlers:
            logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

            # Create a handler and set the level to the lowest level you want to log
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

            handler = logging.FileHandler(log_file)
            handler.setLevel(logging.DEBUG)
            # Create a formatter and set it on the handler
            handler.setFormatter(formatter)
            # Add the handler to the root logger
            logging.getLogger().addHandler(handler)

            # Add the console handler to the root logger
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)
            logging.getLogger().addHandler(console_handler)
        else:
            print(f"Handlers are already setup")
            input()


    except Exception as e:
        print(f"An error occurred during logging setup: {e}.  Press any key to continue")
        input()


def remove_duplicates(input_file, output_file,columname):
    # Read the CSV file and remove duplicates based on the 'filename' column
    unique_rows = {}
    duplicate_rows = []
    seen_filenames = []
    
    logging.info(" remove_duplicates")

    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            filename = row[columname]
            if filename not in seen_filenames:
                #unique_rows.append(row)
                #seen_filenames.append(filename)
                unique_rows[filename] = row
            else:
                duplicate_rows.append(row)

    # Write the unique rows back to a new CSV file
    fieldnames = unique_rows[list(unique_rows.keys())[0]].keys() if unique_rows else []
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_rows.values())

    if len(duplicate_rows) > 1:
        logging.info("more than 1 duplicate path in the file " + str(len(duplicate_rows)))
        for line in duplicate_rows:
            original_row = unique_rows[line]
            logging.info("removed " + str(line) + " as a duplicate of " + original_row)
    else:
        logging.info("no duplicate paths in file " + input_file)


    #for row in duplicate_rows:
    #    logging.info(f"Removed {row} as a duplicate of {row[column_name]}")

def remove_unique_hashes(inputfile,outputfile,field):

    # Dictionary to store lines with unique 'hash' values
    hash_lines = defaultdict(list)
    fieldnames = None
    logging.info("remove_unique_hashes")


    # Read the CSV file and store lines with unique 'hash' values
    with open(inputfile, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames  # Capture fieldnames inside the 'with' block
        for row in reader:
            hash_lines[row[field]].append(row)

    # Filter lines with non-unique 'hash' values
    #filtered_lines = [lines[0] for lines in hash_lines.values() if len(lines) == 1]
    filtered_lines = [line for lines in hash_lines.values() for line in lines if len(lines) > 1]

    # Write the filtered lines to the output CSV file
    with open(outputfile, 'w', newline='') as csvfile:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_lines)

def get_directory(full_path):
    # Using os.path.dirname to extract the directory
    directory = os.path.dirname(full_path)
    return directory

def sortcsv(input_csv_path,output_csv_path,field):

    logging.info("sortcsv")

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


