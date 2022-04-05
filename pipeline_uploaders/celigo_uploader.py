from .fms_uploader import FMSUploader
from pathlib import Path

class CeligoUploader(FMSUploader):
    def __init__(
        self,
        file_path: str,
    ):


        self.file_type = 'TIFF Image'
        self.file_path = file_path

        file_name = Path(file_path).name

        raw_metadata = file_name.split("_")

        self.plate_barcode = raw_metadata[0]

        ts = raw_metadata[2].split("-")
        self.scan_date = ts[0] + "-" + ts[1] + "-" + ts[2]
        self.scan_time = ts[4] + "-" + ts[5] + "-" + ts[6]

        self.row = int(raw_metadata[4][0])
        self.col = int(raw_metadata[4][1:])

        # Establishing a connection to labkey=
        r = self.get_labkey_metadata(self.plate_barcode)
        self.well_ids = FMSUploader.get_well_id(r, self.row, self.col)

        self.metadata = {
            "microscopy": {
                "well_id": self.well_ids[0],
                "plate_barcode": self.plate_barcode,
                "celigo": {
                    "scan_time": self.scan_time,
                    "scan_date": self.scan_date,
                    "well_ids": self.well_ids,
                },
            }
        }
