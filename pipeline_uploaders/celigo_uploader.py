from .fms_uploader import FMSUploader


class CeligoUploader(FMSUploader):
    def __init__(
        self,
        file_type: str,
        file_path: str,
    ):

        # Defines path to original image to be uploaded
        self.file_path = file_path

        # File type label for data that goes to FMS
        self.file_type = file_type

        # Parsing name for metadata (lines 19 - 30)
        file_name = open(self.path).name.split("\\")[-1]

        raw_metadata = file_name.split("_")

        self.plate_barcode = raw_metadata[0]

        ts = raw_metadata[2].split("-")
        self.scan_date = ts[0] + "-" + ts[1] + "-" + ts[2]
        self.scan_time = ts[4] + "-" + ts[5] + "-" + ts[6]

        self.row = raw_metadata[4][0]
        self.col = raw_metadata[4][1:]

        # Establishing a connection to labkey=
        r = self.get_labkey_metadata(self.plate_barcode)

        self.metadata = {
            "microscopy": {
                "well_id": self.get_well_id(r.json(), self.row, self.col),
                "plate_barcode": self.plate_barcode,
                "celigo": {
                    "scan_time": self.scan_time,
                    "scan_date": self.scan_date,
                },
            }
        }
