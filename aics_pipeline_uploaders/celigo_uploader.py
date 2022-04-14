from pathlib import Path

from aicsfiles import FileManagementSystem

from .fms_uploader import FMSUploader


class CeligoUploader(FMSUploader):
    def __init__(self, file_path: str, file_type: str, env: str = "stg"):

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
        self.env = env
        self.file_type = file_type
        self.file_path = Path(file_path)

        file_name = self.file_path.name

        raw_metadata = file_name.split("_")

        self.plate_barcode = int(raw_metadata[0])

        ts = raw_metadata[2].split("-")
        self.scan_date = ts[2] + "-" + ts[1] + "-" + ts[0]
        self.scan_time = ts[3] + ":" + ts[4] + ":" + ts[5] + " " + ts[6]

        self.row = int(row_code[raw_metadata[4][0]])
        self.col = int(raw_metadata[4][1:])

        # Establishing a connection to labkey=
        r = self.get_labkey_metadata(self.plate_barcode)
        self.well_id = FMSUploader.get_well_id(r, self.row, self.col)
        self.well = raw_metadata[4]

        fms = FileManagementSystem()
        builder = fms.create_file_metadata_builder()
        builder.add_annotation("Well", self.well_id).add_annotation(
            "Plate Barcode", self.plate_barcode
        ).add_annotation("Celigo Scan Time", self.scan_time).add_annotation(
            "Celigo Scan Date", self.scan_date
        )

        self.metadata = builder.build()

        self.metadata["microscopy"] = {
            "well_id": self.well_id,  # current database criteria does not allow for our well_id's 3500004923
            "plate_barcode": self.plate_barcode,
            "celigo": {
                "scan_time": self.scan_time,
                "scan_date": self.scan_date,
            },
        }

    def upload(self):
        return super().upload()
