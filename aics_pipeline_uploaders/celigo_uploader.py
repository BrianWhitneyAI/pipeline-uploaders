from datetime import datetime
from pathlib import Path

from aicsfiles import FileManagementSystem
import requests

from .fms_uploader import FMSUploader

# Example file name 3500002920_Scan_4-19-2019-6-56-27-AM_Well_G3_Ch1_-1um

ENDPOINT = "http://aics-api.corp.alleninstitute.org/metadata-management-service/1.0/plate/query?barcode="


class CeligoUploader(FMSUploader):
    def __init__(self, file_path: str, file_type: str, env: str = "stg"):

        self.env = env
        self.file_type = file_type
        self.file_path = Path(file_path)
        file_name = self.file_path.name
        raw_metadata = file_name.split("_")

        # Get barcode from filename
        self.plate_barcode = int(raw_metadata[0])

        # Build time based metadata from file name
        ts = raw_metadata[2].split("-")
        if len(ts[0]) < 2:
            ts[0] = "0" + ts[0]
        if len(ts[1]) < 2:
            ts[1] = "0" + ts[1]
        self.scan_date = ts[2] + "-" + ts[0] + "-" + ts[1]
        self.scan_time = ts[3] + ":" + ts[4] + ":" + ts[5] + " " + ts[6]
        hours = int(ts[3])
        if ts[6] == "PM":
            hours = hours + 12
        self.datetime = datetime(
            year=int(ts[2]),
            month=int(ts[0]),
            day=int(ts[1]),
            hour=hours,
            minute=int(ts[4]),
            second=int(ts[5]),
        )

        # Get Plate Metadata from Labkey
        response = requests.get(
            f"{ENDPOINT}{self.plate_barcode}",
            headers={"Accept": "application/json"},
        )
        plate_metadata = response.json()["data"]

        # Pull Specific well ID, if file has multiple sessions raise ValueError
        if len(plate_metadata) > 1:
            raise ValueError(
                f"Barcode:{self.plate_barcode} has more than one imaging date."
            )
        else:
            self.well_id = plate_metadata[0]["wellNameLookup"][raw_metadata[4]][
                "wellId"
            ]

        # Build fms object
        fms = FileManagementSystem()
        builder = fms.create_file_metadata_builder()
        builder.add_annotation("Well", self.well_id).add_annotation(
            "Plate Barcode", self.plate_barcode
        ).add_annotation(
            "Celigo Scan Time", self.datetime.isoformat(sep="T", timespec="auto")
        ).add_annotation(
            "Celigo Scan Date", self.scan_date
        )
