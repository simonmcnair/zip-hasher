class FileDetails(object):
    
    def __init__(self, file_uuid, file_name, file_full_path, file_md5hash):
        self.fileuuid = file_uuid
        self.filename = file_name
        self.filefullpath = file_full_path
        self.md5hash = file_md5hash
    
    def getObjDetails(self):
        data = {}
        data['filename'] = self.filename
        data['hash'] = self.md5hash

        return data
    
    def __str__(self):
        '''
        str function
        '''
        return  str(self.__class__) + '\n'+ '\n'.join(('{} = {}, {}'.format(item, self.__dict__[item], type(self.__dict__[item])) for item in self.__dict__))
