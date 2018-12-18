import collections

class FileDetails(object):
    
    def __init__(self, file_uuid, file_name, relative_path, file_full_path, file_md5hash, file_size):
        self.fileuuid = file_uuid
        self.filename = file_name
        self.relfilepath = relative_path
        self.filefullpath = file_full_path
        self.md5hash = file_md5hash
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


