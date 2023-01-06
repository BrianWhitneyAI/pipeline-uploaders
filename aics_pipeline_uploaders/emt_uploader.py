import os
from pathlib import Path
from typing import List
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import (
    tostring as xml_to_string,
)

from aicsfiles import FileManagementSystem
from aicsimageio import AICSImage

from .fms_uploader import FMSUploader

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
        self.barcode = int(
            Path(dir_path).name.split("_")[0]
        )  # this is oversimplified at moment
        self.files = []  # This is where files + metadata go

        # Sets a Path to Aqusition Block 1 to extract metadata from the dir_path
        aqusition_block_1_paths = [
            path for path in Path(dir_path).resolve().rglob("*pt1.czi")
        ]

        if aqusition_block_1_paths:
            aqusition_block_1_path = str(aqusition_block_1_paths[0])

            self.imaging_date = FMSUploader.get_imaging_date(
                file_path=aqusition_block_1_path
            )

            self.wells, self.scene_dict, self.rows, self.cols = self.get_well_data(
                file_path=aqusition_block_1_path
            )

            self.system = FMSUploader.get_system(file_path=aqusition_block_1_path)
            self.objective = FMSUploader.get_objective(file_path=aqusition_block_1_path)

            self.optical_control_path = FMSUploader.get_QC_daily_path(
                system=self.system,
                objective=self.objective,
                date=int(self.imaging_date.replace("-", "")),
            )

            self.optical_control_slide_id = Path(self.optical_control_path).name.split(
                "_"
            )[3]

            fms = FileManagementSystem(env="stg")
            builder = fms.create_file_metadata_builder()

            builder.add_annotation("Imaging Date", self.imaging_date).add_annotation(
                "Imaged By", "EMT Pipeline"
            ).add_annotation("Is Optical Control", True).add_annotation(
                "Instrument", FMSUploader.system_mapping(self.system)
            ).add_annotation(
                "Objective", FMSUploader.objective_mapping(self.objective)
            ).add_annotation(
                "Argolight Slide ID", self.optical_control_slide_id
            ).add_annotation(
                "Argolight pattern",
                "Field of rings",  # maybe should talk about changing to Capitol R
            )

            optical_control_metadata = builder.build()

            optical_control_metadata["file"] = {
                "disposition": "tape",  # This is added to avoid FSS automatically makeing tiffs from the CZIs
            }

            self.optical_control = fms.upload_file(
                self.optical_control_path,
                file_type="CZI Image",
                metadata=optical_control_metadata,
            )

            self.optical_control_id = self.optical_control.id

        else:
            raise Exception("Directory does not contain correct Aquisition Blocks")

        """
        This code block is a series if logic statements
        to pick filetype and assign necessary metadata
        """

        self.well_ids = []
        r = FMSUploader.get_labkey_metadata(self.barcode)

        for row, col in zip(self.rows, self.cols):
            self.well_ids.append(FMSUploader.get_well_id(r, row, col))

        for dirpath, _, filenames in os.walk(dir_path):
            for filename in filenames:
                file_path = f"{dirpath}/{filename}"
                if str(self.barcode) in filename:
                    if ".czi" in filename:
                        if "10x" in filename.lower():
                            self.files.append(
                                self.wellscan_metadata_formatter(
                                    barcode=self.barcode,
                                    filename=file_path,
                                    file_type="CZI Image",
                                    imaging_date=self.imaging_date,
                                    scene_map=self.scene_dict,
                                    well_ids=self.well_ids,
                                    optical_control_id=self.optical_control_id,
                                    env=self.env,
                                )
                            )
                        elif BLOCK in filename:
                            timepoint = int(
                                [s for s in filename.split("_") if BLOCK in s][0][-1]
                            )
                            self.files.append(
                                self.block_metadata_formatter(
                                    barcode=self.barcode,
                                    filename=file_path,
                                    file_type="CZI Image",
                                    imaging_date=self.imaging_date,
                                    scene_map=self.scene_dict,
                                    well_ids=self.well_ids,
                                    optical_control_id=self.optical_control_id,
                                    timepoint=timepoint,
                                    env=self.env,
                                )
                            )
                    elif ".czmbi" in filename:
                        # Labkey Metadata
                        # pipeline 4 annotations
                        self.files.append(
                            self.czmbi_metadata_formatter(
                                barcode=self.barcode,
                                filename=file_path,
                                file_type="Zen Time Stitching File",
                                imaging_date=self.imaging_date,
                                scene_map=self.scene_dict,
                                well_ids=self.well_ids,
                                env=self.env,
                            )
                        )

                elif ".czexp" in filename:
                    # Labkey Metadata
                    # pipeline 4 annotations
                    self.files.append(
                        self.czexp_metadata_formatter(
                            barcode=self.barcode,
                            filename=file_path,
                            file_type="ZEN Experiment File",
                            imaging_date=self.imaging_date,
                            scene_map=self.scene_dict,
                            well_ids=self.well_ids,
                            env=self.env,
                        )
                    )

    @staticmethod
    def block_metadata_formatter(
        barcode: int,
        filename: str,
        file_type: str,
        well_ids: List[int],
        env: str,
        imaging_date: str,
        scene_map: List[str],
        optical_control_id: str,
        timepoint: int,
    ):

        fms = FileManagementSystem(env="stg")
        builder = fms.create_file_metadata_builder()
        builder.add_annotation("Well", well_ids).add_annotation(
            "Plate Barcode", barcode
        ).add_annotation("Optical Control ID", optical_control_id).add_annotation(
            "EMT Timepoint", timepoint
        )  # TODO: make this annotation in file uploader

        metadata = builder.build()

        metadata["microscopy"] = {
            "well_id": well_ids[
                0
            ],  # current database criteria does not allow for our well_id's.
            "imaging_date": imaging_date,
            "plate_barcode": barcode,
            "EMT": {
                "scene_map": scene_map,
            },
        }

        metadata["file"] = {
            "disposition": "tape",  # This is added to avoid FSS automatically makeing tiffs from the CZIs
        }

        return FMSUploader(
            file_path=filename, file_type=file_type, metadata=metadata, env=env
        )

    @staticmethod
    def wellscan_metadata_formatter(
        barcode: int,
        filename: str,
        file_type: str,
        well_ids: List[int],
        env: str,
        imaging_date: str,
        scene_map: List[str],
        optical_control_id: str,
    ):

        fms = FileManagementSystem(env="stg")
        builder = fms.create_file_metadata_builder()
        builder.add_annotation("Well", well_ids).add_annotation(
            "Plate Barcode", barcode
        ).add_annotation("Optical Control ID", optical_control_id)

        metadata = builder.build()

        metadata["microscopy"] = {
            "well_id": well_ids[
                0
            ],  # current database criteria does not allow for our well_id's.
            "imaging_date": imaging_date,
            "plate_barcode": barcode,
            "EMT": {
                "scene_map": scene_map,
            },
        }

        metadata["file"] = {
            "disposition": "tape",  # This is added to avoid FSS automatically makeing tiffs from the CZIs
        }

        return FMSUploader(
            file_path=filename, file_type=file_type, metadata=metadata, env=env
        )

    @staticmethod
    def czmbi_metadata_formatter(
        barcode: int,
        filename: str,
        file_type: str,
        well_ids: List[int],
        env: str,
        imaging_date: str,
        scene_map: List[str],
    ):

        fms = FileManagementSystem(env="stg")
        builder = fms.create_file_metadata_builder()
        builder.add_annotation("Well", well_ids).add_annotation(
            "Plate Barcode", barcode
        )

        metadata = builder.build()

        metadata["microscopy"] = {
            "well_id": well_ids[
                0
            ],  # current database criteria does not allow for our well_id's.
            "imaging_date": imaging_date,
            "plate_barcode": barcode,
            "EMT": {
                "scene_map": scene_map,
            },
        }

        metadata["file"] = {
            "disposition": "tape",  # This is added to avoid FSS automatically makeing tiffs from the CZIs
        }

        return FMSUploader(
            file_path=filename, file_type=file_type, metadata=metadata, env=env
        )

    @staticmethod
    def czexp_metadata_formatter(
        barcode: int,
        filename: str,
        file_type: str,
        well_ids: List[int],
        env: str,
        imaging_date: str,
        scene_map: List[str],
    ):

        fms = FileManagementSystem(env="stg")
        builder = fms.create_file_metadata_builder()
        builder.add_annotation("Well", well_ids).add_annotation(
            "Plate Barcode", barcode
        )

        metadata = builder.build()

        metadata["microscopy"] = {
            "well_id": well_ids[
                0
            ],  # current database criteria does not allow for our well_id's.
            "imaging_date": imaging_date,
            "plate_barcode": barcode,
            "EMT": {
                "scene_map": scene_map,
            },
        }

        metadata["file"] = {
            "disposition": "tape",  # This is added to avoid FSS automatically makeing tiffs from the CZIs
        }

        return FMSUploader(
            file_path=filename, file_type=file_type, metadata=metadata, env=env
        )

    @staticmethod
    def get_well_data(file_path):
        block_img = AICSImage(file_path)

        row_code = {
            "A": 1,
            "B": 2,
            "C": 3,
            "D": 4,
            "E": 5,
            "F": 6,
            "G": 7,
            "H": 8,
        }

        scene_dict = {}
        wells = []
        rows = []
        cols = []

        with open("metadata.czi.xml", "w") as f:  # TODO: Make this not output a file
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

    def upload(self):
        for file in self.files:
            file.upload()
            print(file.file_path.name)
