import zipfile
import os
import hashlib
import uuid
import platform
import ConfigParser


CONFIG = r'config.txt'
CONFIGPARSER = None

def extractor(path_to_zip_file, directory_to_extract):
    # extract zip files
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract)

def random_temp_path(global_path):
    uid = str(uuid.uuid4())
    random_path = os.path.join(global_path, uid)
    os.makedirs(random_path)
    return random_path


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

def get_file_size(filepath):
    statinfo = os.stat(filepath)
    return statinfo.st_size
    

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
        """Open the zip file a first time, to check that it is a valid zip archive."""
        try:
            zip = zipfile.ZipFile(zip_file)
        except zipfile.BadZipfile as e:
            print "bad zip file"
            return False
        bad_file = zip.testzip()
        if bad_file:
            zip.close()
            print('"%s" in the .zip archive is corrupt.' % bad_file)
            print "bad zip file"
            return False
        zip.close()  # Close file in all cases.
        return True


def get_uuid():
    uid = uuid.uuid4()
    return str(uid.hex)


def stripfilepath(full_file_path):
    return os.path.basename(full_file_path)


def get_platform():
    pform = platform.system()
    print pform
    return pform.lower()

def readConfig():
    configParser = ConfigParser.RawConfigParser()
    configFilePath = CONFIG
    configParser.read(configFilePath)
    return configParser

def get_tmp_path():
    configParser = readConfig()
    if get_platform() == 'windows':
        temp_dir = configParser.get('windows', 'tempdir')
        # hack for windows paths
        temp_dir = s = temp_dir.replace("\\", "\\\\") 
    elif get_platform() == 'linux' or get_platform() == 'darwin':
        temp_dir = configParser.get('unix', 'tempdir')
    else:
        print "not valid OS/Platform, contact developer : yodebu@gmail.com"
        exit(-1)
    
    return temp_dir


def get_xml_file():
    ConfigParser = readConfig()
    if get_platform() == 'windows':
        xml_path = ConfigParser.get('windows', 'xmlfile')
        # hack for windows paths
        xml_path = xml_path.replace('\\', '\\\\')
    elif get_platform() == 'linux' or get_platform() == 'darwin':
        xml_path = ConfigParser.get('unix', 'xmlfile')
    else:
        print "not valid OS/Platform, contact developer : yodebu@gmail.com"
        exit(-1)
    return xml_path