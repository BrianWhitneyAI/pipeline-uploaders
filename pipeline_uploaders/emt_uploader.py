import os
from numpy import NaN
from fms_uploader import FMSUploader


'''
Starting code base for EMT Uploader 

    Goals: Upload EMT files to FMS 

        7 block experiments (.czi)

        Possibly upload combined file (.czi or .ome.tiff)


        NOTE: Super class for uploaders 
        NOTE: look into helper constructor
'''
class EMTUploader():

    def __init__(self, dir_path: str, env = 'stg'):

        BLOCK = "AcquisitionBlock"
        self.env = env
        self.barcode  = int(dir_path.name[:9]) # this is oversimplified at moment 
        self.files = []
        self.wells = []

        for dirpath, _, filenames in os.walk(dir_path):
            for filename in filenames:
                file_path = f'{dirpath}/{filename}'
                if str(self.barcode) in filename:
                    if '.czi' in filename:
                        if '10x' in filename:
                            # Labkey Metadata
                            self.files.append(self.metadata_formatter(filename = file_path,
                                                                 file_type = 'czi',
                                                                 well = filename.split("_")[-1], 
                                                                 magnification = 10))
                        elif BLOCK in filename:
                            timepoint = int([s for s in filename.split('_') if BLOCK in s][0][-1])
                            # Labkey Metadata
                            self.files.append(self.metadata_formatter(filename = file_path,
                                                                 file_type = 'czi',
                                                                 magnification = 63,
                                                                 timepoint = timepoint))
                    elif '.czmbi' in filename:
                        # Labkey Metadata
                        self.files.append(self.metadata_formatter(filename = file_path, file_type = 'czmbi'))

                elif '.czexp' in filename:
                    # Labkey Metadata
                    self.files.append(self.metadata_formatter(filename = file_path, file_type = 'czexp'))

 # make static method 
    def metadata_formatter(self, filename:str,file_type: str, well = self.well, magnification = NaN, timepoint = NaN):

        # this can change for however metadata is wanted to be formatted 
        metadata = {
                    "microsocpy": {
                        "plate_barcode": [self.barcode],  
                        "EMT": {
                            "well": [well],
                            "magnification": [magnification],
                            "timepoint": [timepoint]
                        },
                    },
                }
        
        return FMSUploader( file_path = filename, 
                            file_type  = file_type,
                            metadata  = metadata , 
                            env = self.env)


    def upload(self):
        for file in self.files:
            file.upload()
