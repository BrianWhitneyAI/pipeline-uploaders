from typing import Literal

from .fms_uploader import FMSUploader
from .util.celigo import CeligoUtil

# Example file name "3500001609_Scan_1-12-2018-6-03-16-AM_Well_F5_Ch1_-1um.tiff"


class CeligoUploader(FMSUploader):
    def __init__(
        self, file_path: str, file_type: str, env: Literal["prod", "stg", "dev"] = "stg"
    ):

        super().__init__(file_path=file_path, file_type=file_type, env=env)

        # Get Metadata from filename
        util = CeligoUtil(self.env)

        (
            self.plate_barcode,
            self.well_name,
            self.scan_date,
            self.scan_timeutil,
        ) = util.parse_filename(self.file_name)
        self.well_id = util.lookup_well_id(self.plate_barcode, self.well_name)

        builder = self.fms.create_file_metadata_builder()
        builder.add_annotation("Well", self.well_id).add_annotation(
            "Plate Barcode", self.plate_barcode
        ).add_annotation("Celigo Scan Time", self.scan_timeutil).add_annotation(
            "Celigo Scan Date", self.scan_date
        )

        self.metadata = builder.build()
