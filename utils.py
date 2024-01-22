import os
import sys
import csv
import logging
import hashlib
import platform
import shutil
from collections import defaultdict
import psutil

import patoolib

from PIL import Image
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

rename_bad_archive_files = True
rename_bad_audio_files = True
rename_bad_image_files = True
logger = ''

def setup_logging(log_file, errorlog_path,log_level='debug'):

    log_level_map = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING,'error': logging.ERROR}

    log_level = log_level.lower()
    if log_level not in log_level_map:
        print(f"Invalid log level: {log_level}. Defaulting to 'debug'.")
        log_level = 'debug'

    console_log_level = log_level_map['info']

    try:
            logger = logging.getLogger()
            if not logger.handlers:
                # Create a handler and set the level to the lowest level you want to log
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

                filehandler = logging.FileHandler(log_file)
                filehandler.setLevel(log_level_map[log_level])# file log level assigned elsewhere
                filehandler.setFormatter(formatter)
                logger.addHandler(filehandler)

                error_handler = logging.FileHandler(errorlog_path)
                error_handler.setLevel(log_level_map['error'])  # Only logs messages with ERROR level or higher
                error_handler.setFormatter(formatter)
                logger.addHandler(error_handler)

                console_handler = logging.StreamHandler()
                console_handler.setLevel(console_log_level) # log debug to console
                console_handler.setFormatter(formatter)
                logger.addHandler(console_handler)

                logger.setLevel(logging.DEBUG)
                print("Handlers are set up.")

            else:
                print("Handlers are already setup")

            return logger

    except Exception as e:
        print(f"An error occurred during logging setup: {e}.  Press any key to continue")


def remove_duplicates(input_file, output_file,columname):
    # Read the CSV file and remove duplicates based on the 'filename' column
    unique_rows = {}
    duplicate_rows = []
    seen_filenames = []

    logging.info(" remove_duplicates")

    with open(input_file, 'r', encoding='utf-8') as infile:
#        reader = csv.DictReader(infile, quoting=csv.QUOTE_NONNUMERIC)
        reader = csv.DictReader(infile, quoting=csv.QUOTE_NONNUMERIC)
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
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        writer.writerows(unique_rows.values())

    if len(duplicate_rows) > 1:
        logging.info("more than 1 duplicate path in the file %s", str(len(duplicate_rows)))
        for line in duplicate_rows:
            original_row = unique_rows[line]
            logging.info(f"removed {line} as a duplicate of {original_row}")
    else:
        logging.info('no duplicate paths in file ' + input_file)


    #for row in duplicate_rows:
    #    logging.info(f"Removed {row} as a duplicate of {row[column_name]}")

def extract_field(source_file, dest_file, field_name):
    try:
        with open(source_file, 'r') as source_csv, open(dest_file, 'w', newline='', encoding='utf-8') as dest_csv:
#            reader = csv.DictReader(source_csv, quoting=csv.QUOTE_NONNUMERIC)
            reader = csv.DictReader(source_csv)
            fieldnames = reader.fieldnames

            if field_name not in fieldnames:
                print(f"Field '{field_name}' not found in the source file.")
                return

            #writer = csv.DictWriter(dest_csv, fieldnames=[field_name], encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)
            writer = csv.DictWriter(dest_csv, fieldnames=[field_name], encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()

            for row in reader:
                extracted_data = {field_name: row[field_name]}
                writer.writerow(extracted_data)

            print(f"Extraction complete. Data saved to {dest_file}")

    except FileNotFoundError:
        print("File not found. Please check the file paths.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def remove_unique_hashes(inputfile,outputfile,field):

    # Dictionary to store lines with unique 'hash' values
    hash_lines = defaultdict(list)
    fieldnames = None
    logging.info("remove_unique_hashes")


    # Read the CSV file and store lines with unique 'hash' values
    with open(inputfile, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        fieldnames = reader.fieldnames  # Capture fieldnames inside the 'with' block
        for row in reader:
            hash_lines[row[field]].append(row)

    # Filter lines with non-unique 'hash' values
    #filtered_lines = [lines[0] for lines in hash_lines.values() if len(lines) == 1]
    #filtered_lines = [line for lines in hash_lines.values() for line in lines if len(lines) > 1]
    filtered_lines = [line for lines in hash_lines.values() if len(lines) > 1 for line in lines]

    # Write the filtered lines to the output CSV file
    with open(outputfile, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
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
            reader = csv.DictReader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            data = list(reader)

        # Sort the data based on the 'field' field
        sorted_data = sorted(data, key=lambda x: x[field])

        # Write the sorted data back to a new CSV file
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)

            # Write the header
            writer.writeheader()

            # Write the sorted rows
            writer.writerows(sorted_data)

        logging.info(f"CSV file sorted and saved to {output_csv_path}")
        return True

    except Exception as e:
        logging.error(f'failed to sort CSV.  Error: {e}')
        return False

def createimagehash(filetohash):
    global rename_bad_image_files
    logging.info("Reading in " + filetohash)

    try:
        with Image.open(filetohash, formats=None) as image:
            # Get the image data as bytes
            image.load()
            image_bytes = image.tobytes()
        # Create a hash object and update with image bytes
        hash_object = hashlib.blake2b(image_bytes)
        hash_value = hash_object.hexdigest()
        logging.info(hash_value + " is hash for " + filetohash)
        return hash_value
    except Exception as e:
        logging.warning("Could not create image hash for " + filetohash + " " +  str(e))
        if rename_bad_image_files == True:
            prepend_text_to_filename(filetohash, 'bad_image_')
        return False

def createaudiohash(filetohash):
    global rename_bad_audio_files
    logging.info("Hashing " + filetohash)
    #while True:
    try:
        audio = AudioSegment.from_file(filetohash)
        hash = hashlib.blake2b(audio.raw_data, digest_size=16).hexdigest()
        logging.info(hash + " is hash for " + filetohash)
        return hash
    except CouldntDecodeError as e:
        logging.error(f"Failed to decode audio file.{filetohash}: {e}")
    except IndexError as e:
        logging.error(f"Index out of range error.{filetohash}: {e}")
    except KeyboardInterrupt:
        # This block will be executed when Ctrl+C is pressed
        logging.info("Ctrl+C received. Exiting gracefully...")
        # Perform cleanup operations here, if needed
        sys.exit(0)
    except Exception as e:
        logging.warning(f"Could not create audio hash for {filetohash} : {e}")
    
    if rename_bad_audio_files == True:
        prepend_text_to_filename(filetohash, 'bad_audiofile_')
    return False

def is_file_larger_than(file_path, size_limit):
    # Convert human-readable size to bytes
    def human_readable_to_bytes(size_str):
        size_str = size_str.upper()
        multiplier = {'KB': 1024, 'MB': 1024 ** 2, 'GB': 1024 ** 3, 'TB': 1024 ** 4}
        for unit, factor in multiplier.items():
            if unit in size_str:
                return int(float(size_str.replace(unit, '')) * factor)
        return int(size_str)

    try:
        # Get the size of the file
        file_size = os.path.getsize(file_path)

        # Check if the file size is larger than the specified limit
        return file_size > human_readable_to_bytes(size_limit) , file_size
    except Exception as e:
        logging.error(f"Error: {e}")
        return False
    
def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def prepend_text_to_filename(filepath, text_to_prepend):
    directory, filename = os.path.split(filepath)
    base_name, extension = os.path.splitext(filename)
    if base_name.startswith(text_to_prepend):
        logging.info(f"{filepath} already begins with {text_to_prepend}")
        return filepath

    new_base_name = f"{text_to_prepend}_{base_name}"
    new_filepath = os.path.join(directory, new_base_name + extension)
    try:
        shutil.move(filepath,new_filepath)
    except Exception as e:
        logging.error(f"FAILED to move: {filepath} to {new_filepath} .  Error {e}")
        return

    return new_filepath

def writecsvrow(theoutputfile,contents):

    try:
        with open(theoutputfile, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(contents)
        file.close
        del file
    except Exception as e:
        logging.error(f'FAILED to insert csv row  Error {e}')
        return False
    return True

def check_disk_space_for_extraction(archive_path, destination_path='.'):
    try:
        # Get the size of the archive
       # archive_size = patoolib.get_archive_size(archive_path)
        #this doesn't exist.
        archive_size = 0
        # Get available disk space
        disk_space = psutil.disk_usage(destination_path).free

        # Check if there is enough disk space
        if disk_space >= archive_size:
            logging.error("There is enough disk space to extract the archive.")
            return True
        else:
            logging.error("Insufficient disk space to extract the archive.")
            return False
    except Exception as e:
        logging.error(f"Error: {e}")
        return False

def get_expanded_size(archive_path):
    try:
        size = patoolib.get_archive_size(archive_path)
        return size
    except Exception as e:
        logging.error(f"Error: {e}")
        return None

def get_disk_space():
    try:
        disk = psutil.disk_usage('/')
        free_space = disk.free
        return free_space
    except Exception as e:
        logging.error(f"Error: {e}")
        return None
    
def extractor(path_to_zip_file, directory_to_extract):
    global rename_bad_archive_files
    logging.info ("extracting files ...")

    result = check_disk_space_for_extraction(path_to_zip_file)
    if result == False:
        logging.error(f'FAILED to extract: {path_to_zip_file}.  Insufficient space to extract archive')
        return False

    try:
        patoolib.extract_archive(path_to_zip_file, outdir=directory_to_extract)
    except Exception as e:
        logging.error(f'FAILED to extract: {path_to_zip_file}.  {e}')
        if rename_bad_archive_files == True:
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
        logging.error(f"failed to calculate hash for {file_path}: {e}")
        return False

    # Return the hexadecimal digest of the hash


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
