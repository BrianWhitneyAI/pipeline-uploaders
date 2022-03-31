import os
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
            self.wells, self.scene_dict = self.get_well_data(
                str(aqusition_block_1_paths[0])
            )
        else:
            raise Exception("Directory does not contain correct Aquisition Blocks")

        """
        This code block is a series if logic statements
        to pick filetype and assign necessary metadata
        """
        for dirpath, _, filenames in os.walk(dir_path):
            for filename in filenames:
                file_path = f"{dirpath}/{filename}"
                if str(self.barcode) in filename:
                    if ".czi" in filename:
                        if "10x" in filename:
                            # Labkey Metadata
                            # pipeline 4 annotations
                            self.files.append(
                                self.metadata_formatter(
                                    barcode=self.barcode,
                                    filename=file_path,
                                    file_type="czi",
                                    well=filename.split("_")[
                                        -1
                                    ],  # Need standard way to get Well ID
                                    magnification=10,
                                    env=self.env,
                                )
                            )
                        elif BLOCK in filename:
                            timepoint = int(
                                [s for s in filename.split("_") if BLOCK in s][0][-1]
                            )
                            # Labkey Metadata
                            # pipeline 4 annotations

                            self.files.append(
                                self.metadata_formatter(
                                    barcode=self.barcode,
                                    filename=file_path,
                                    file_type="czi",
                                    well=self.wells,
                                    magnification=63,
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
                                well=self.wells,
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
                            well=self.wells,
                            env=self.env,
                        )
                    )

    @staticmethod
    def metadata_formatter(
        barcode: str,
        filename: str,
        file_type: str,
        well: str,
        env: str,
        magnification=None,
        timepoint=None,
    ):

        # this can change for however metadata is wanted to be formatted
        metadata = {
            "microsocpy": {
                "plate_barcode": [barcode],
                "EMT": {
                    "well": [well],
                    "magnification": [magnification],
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

        scene_dict = {}
        wells = []

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

        return wells, scene_dict

    def upload(self):
        for file in self.files:
            file.upload()
