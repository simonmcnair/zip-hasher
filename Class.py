import collections

class FileDetails(object):
    
    def __init__(self, fullpath, file_name, relative_path, file_hash, file_size):
        self.fullpath = fullpath
        self.filename = file_name
        self.relfilepath = relative_path
        self.md5hash = file_hash
        self.filesize = file_size
    
    def getObjDetails(self):
        data = collections.OrderedDict()
        data['file'] = str(self.relfilepath)
        data['checksum'] = str(self.md5hash)
        data['size'] = str(self.filesize)

        return data
    
    def __str__(self):
        '''
        str function
        '''
        return  str(self.__class__) + '\n'+ '\n'.join(('{} = {}, {}'.format(item, self.__dict__[item], type(self.__dict__[item])) for item in self.__dict__))


