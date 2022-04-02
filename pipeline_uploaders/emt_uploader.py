import os
from re import A
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.etree.ElementTree import tostring as xml_to_string

from aicsimageio import AICSImage
from fms_uploader import FMSUploader


"""
Starting code base for EMT Uploader 

    Goals: Upload EMT files to FMS 

        7 block experiments (.czi)

        Possibly upload combined file (.czi or .ome.tiff)


        NOTE: Super class for uploaders 
        NOTE: look into helper constructor
"""


class EMTUploader:
    def __init__(self, dir_path: str, env="stg"):

        BLOCK = "AcquisitionBlock"
        self.env = env
        self.barcode = str(Path(dir_path).name[:9])  # this is oversimplified at moment
        self.files = []  # This is where files + metadata go

        # Sets a Path to Aqusition Block 1 to extract metadata from the dir_path
        aqusition_block_1_paths = [
            path for path in Path(dir_path).resolve().rglob("*pt1.czi")
        ]

        # Creates a List of all active wells and a Dictionary of Scene-Well relationship
        if not aqusition_block_1_paths:
            self.wells, self.scene_dict, self.rows, self.cols = self.get_well_data(
                str(aqusition_block_1_paths[0])
            )
        else:
            raise Exception("Directory does not contain correct Aquisition Blocks")

        """
        This code block is a series if logic statements
        to pick filetype and assign necessary metadata
        """
        self.well_ids = []
        r = FMSUploader.get_labkey_metadata(self.barcode)
        for row,col in zip(self.rows,self.cols):
            self.well_ids.append(FMSUploader.get_well_id(r,row,col))

        for dirpath, _, filenames in os.walk(dir_path):
            for filename in filenames:
                file_path = f"{dirpath}/{filename}"
                if str(self.barcode) in filename:
                    if ".czi" in filename:
                        imaging_date = get_imaging_date(file_path)
                        if "10x" in filename:

                            self.files.append(
                                self.metadata_formatter(
                                    barcode=self.barcode,
                                    filename=file_path,
                                    file_type="czi", # needs to chage
                                    imaging_date = self.imaging_date,
                                    well_ids=self.well_ids,  # Need standard way to get Well ID
                                    objective=10, # objectiive
                                    env=self.env,
                                )
                            )
                        elif BLOCK in filename:
                            timepoint = int(
                                [s for s in filename.split("_") if BLOCK in s][0][-1]
                            )
                            self.files.append(
                                self.metadata_formatter(
                                    barcode=self.barcode,
                                    filename=file_path,
                                    file_type="czi",
                                    imaging_date = self.imaging_date,
                                    well_ids =self.well_ids,
                                    objective=63,
                                    timepoint=timepoint,
                                    env=self.env,
                                )
                            )
                    elif ".czmbi" in filename:
                        # Labkey Metadata
                        # pipeline 4 annotations
                        self.files.append(
                            self.metadata_formatter(
                                barcode=self.barcode,
                                filename=file_path,
                                file_type="czmbi",
                                imaging_date = self.imaging_date,
                                well_ids =self.well_ids,
                                env=self.env,
                            )
                        )

                elif ".czexp" in filename:
                    # Labkey Metadata
                    # pipeline 4 annotations
                    self.files.append(
                        self.metadata_formatter(
                            barcode=self.barcode,
                            filename=file_path,
                            file_type="czexp",
                            imaging_date = self.imaging_date,
                            well_ids=self.well_ids,
                            env=self.env,
                        )
                    )

    @staticmethod
    def metadata_formatter(
        barcode: str,
        filename: str,
        file_type: str,
        well_ids: str,
        env: str,
        imaging_date: str,
        objective=None,
        timepoint=None,
    ):

        # this can change for however metadata is wanted to be formatted
        # microscopy.wellid, micoroscoy.imaging_date, micorcospy.fov_id, micorsocpy.objective, microsocpy.plate_barcode
        #
        r = FMSUploader.get_labkey_metadata(barcode)

        metadata = {
            "microscopy": {
                "well_ids" : [well_ids],
                "imaging_date" : [imaging_date],
                "objective": [objective],
                "plate_barcode": [barcode],
                "EMT": {
                    "timepoint": [timepoint],
                },
            },
        }

        return FMSUploader(
            file_path=filename, file_type=file_type, metadata=metadata, env=env
        )

    @staticmethod
    def get_well_data(block_path):
        block_img = AICSImage(block_path)

        row_code = {
                'A': 1,
                'B': 2,
                'C': 3,
                'D': 4,
                'E': 5,
                'F': 6,
                'G': 7,
                'H': 8,
        }

        scene_dict = {}
        wells = []
        rows = []
        cols =  []

        with open("metadata.czi.xml", "w") as f:
            f.write(xml_to_string(block_img.metadata, encoding="unicode"))
        tree = ET.parse("metadata.czi.xml")
        root = tree.getroot()

        for Scene in root.iter("Scene"):
            # Add Scene and Well to scene_dict
            scene_dict[Scene.get("Name")] = Scene.find("Shape").get("Name")

            # Add new well to well list
            if (Scene.find("Shape").get("Name")) not in wells:
                wells.append(Scene.find("Shape").get("Name"))

        for well in wells:
            rows.append(int(row_code[well[0]]))
            cols.append(int(well[1:]))

        return wells, scene_dict, rows, cols

    def get_imaging_date(file_path):
        # path = './ImageDocument/Metadata/Information/Image/AcquisitionDateAndTime'
        file_img = AICSImage(file_path)

        with open("metadata.czi.xml", "w") as f:
            f.write(xml_to_string(file_img.metadata, encoding="unicode"))
        tree = ET.parse("metadata.czi.xml")
        root = tree.getroot()

        return tree.findall(".//AcquisitionDateAndTime")[0].text 







    def upload(self):
        for file in self.files:
            file.upload()
