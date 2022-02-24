import os
from aicsfiles import FileManagementSystem
from fms_uploader import FMSUploader
from pathlib import Path


'''
Starting code base for EMT Uploader 

    Goals: Upload EMT files to FMS 

        7 block experiments (.czi)

        Possibly upload combined file (.czi or .ome.tiff)


        NOTE: Super class for uploaders 
        NOTE: look into helper constructor


init: (self, dir_path, env = 'stg)
    self.env = 'env'
    define barcode 
    files to upload (path)
    list of dictionaries with metadata for each filepath in files to upload

    for dirpath, _, filenames in os.walk(dir_path):
        for filename in filenames:
            if filename contains barcode
                if .czi
                    if 10x
                        barcode
                        well
                        magnification
                        labkey metadata
                    elif blockduration 
                        barcode
                        well = MXS or labkey
                        magnification = 63 
                        timepoint
                        labkey metadata
                elif .czmbi
                    Barcode 
                    labkey metadata

            elif .czexp
                Barcode
                labkey metadata


'''
class EMTUploader(FMSUploader):
    BLOCK = "AcquisitionBlock"

    def __init__(self, file_path: str, env = 'stg'):
        self.barcode  = int(file_path.name[:9]) # this is oversimplified at moment 
        upload_files = []
        file_metadata  = [] 
        for dirpath, _, filenames in os.walk(dir_path):
            for filename in filenames:
                if str(self.barcode) in filename:
                    if '.czi' in filename:
                        if '10x' in filename:
                            upload_file.append(f'{dirpath}/{filename}')
                            well = filename.split("_")[-1]
                            magnification = 10
                            # labkey metadata
                            metadata = {
                                            "microsocpy": {
                                                "plate_barcode": [barcode],  
                                                "EMT": {
                                                    "well": [well],
                                                    "magnification": [magnification]
                                                },
                                            },
                                        }
                            file_metadata.append(metadata)
                        elif BLOCK in filename:
                            upload_file.append(f'{dirpath}/{filename}')
                            # well = MXS or labkey
                            magnification = 63 
                            timepoint = int([s for s in filename.split('_') if BLOCK in s][0][-1])
                            # labkey metadata
                            metadata = {
                                            "microsocpy": {
                                                "plate_barcode": [barcode],  
                                                "EMT": {
                                                    "well": [well],
                                                    "magnification": [magnification],
                                                    "timepoint": [timepoint]
                                                },
                                            },
                                        }
                            file_metadata.append(metadata)
                    elif '.czmbi' in filename:
                        upload_file.append(f'{dirpath}/{filename}')
                        #labkey metadata
                        metadata = {
                                        "microsocpy": {
                                            "plate_barcode": [barcode],  
                                            "EMT": {
                                            },
                                        },
                                    }
                        file_metadata.append(metadata)
            elif '.czexp' in filename:
                upload_file.append(f'{dirpath}/{filename}')
                #labkey metadata
                metadata = {
                                "microsocpy": {
                                    "plate_barcode": [barcode],  
                                    "EMT": {
                                    },
                                },
                            }
                file_metadata.append(metadata)

        for file_path, metadata in zip(upload_files,file_metadata):
            file_with_metadata = super.__init__(self.file_path, self.file_type, self.metadata, self.env)
            file_with_metadata.upload()

