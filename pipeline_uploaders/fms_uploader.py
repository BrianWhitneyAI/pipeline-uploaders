import json
from pathlib import Path

import lkaccess.contexts
import requests
from aicsfiles import FileManagementSystem
from lkaccess import LabKey, QueryFilter

"""
This is a superclass for uploading ot FMS

"""


class FMSUploader:
    def __init__(self, file_path: str, file_type: str, metadata: dict, env="stg"):

        self.env = env
        self.file_path = Path(file_path)
        self.file_type = file_type
        self.metadata = metadata

    def upload(self):
        fms = FileManagementSystem(env=self.env)

        run_count = 0
        while run_count < 5:
            try:
                fms_file = fms.upload_file(
                    file_reference=self.file_path,
                    file_type=self.file_type,
                    metadata=self.metadata,
                )
                return fms_file.id
            except requests.exceptions.ReadTimeout:
                print("")
                run_count = run_count + 1
                continue
        return "Upload Failed"

    @staticmethod
    def get_labkey_metadata(barcode: str):
        lk = LabKey(server_context=lkaccess.contexts.PROD)

        my_rows = lk.select_rows_as_list(
            schema_name="microscopy",
            query_name="Plate",
            filter_array=[
                QueryFilter("Barcode", barcode),
            ],
        )

        plate_ID = my_rows[0]["PlateId"]

        r = requests.get(
            f"http://aics.corp.alleninstitute.org/metadata-management-service/1.0/plate/{plate_ID}",
            headers={
                "x-user-id": "brian.whitney"
            },  # this should change to a generic user
        )

        return r.json()

    @staticmethod
    def get_well_id(metadata_block: dict, row: int, col: int):  # TODO: Add typing to f

        wells = metadata_block["wells"]

        for well in wells:
            if (well["row"] == row) and (well["col"] == col):
                well_id = well["wellId"]
                return well_id
        if not well_id:
            raise Exception(
                f"The well at row {row} column {col} does not exist in labkey"
            )
