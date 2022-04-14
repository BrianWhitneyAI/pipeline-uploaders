'''
from pathlib import Path

from fms_uploader import FMSUploader

"""
Starting code base for EMT Uploader

    Goals: Upload EMT files to FMS

        7 block experiments (.czi)

        Possibly upload combined file (.czi or .ome.tiff)


        NOTE: Super class for uploaders
        NOTE: look into helper constructor


"""
class DrugUploader(FMSUploader):
    def __init__(self, file_path: str, env="stg"):
        self.file_path = Path(file_path)
        self.env = env
        if file_path.suffix in [".tiff", ".czi"]:
            self.file_type = "raw_image"  # check what file types are in FMS
        elif file_path.suffix in [".csv", ".text", ".xlsx"]:
            self.file_type = "data"  # check what file types are in FMS

        # defining metadata potential helper
        self.metadata = {}

        super.__init__(self.file_path, self.file_type, self.metadata, self.env)
'''
