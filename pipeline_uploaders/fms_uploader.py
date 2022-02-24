from aicsfiles import FileManagementSystem
from pathlib import Path


'''
This is a superclass for uploading ot FMS

'''
class FMSUploader:
    
    def __init__(self, file_path: str, file_type : str, metadata : dict, env = 'stg'):
        self.env = env
        self.file_path = Path(file_path)
        self.file_type = file_type
        self.metadata = metadata

    def upload(self):
        fms = FileManagementSystem(env = self.env)
        fms.upload_file(file_reference = self.file_path,
                        file_type = self.file_type,
                        metadata = self.metadata)



