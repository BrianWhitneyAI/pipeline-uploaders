from logging import raiseExceptions
from pathlib import Path

from aicsfiles import FileManagementSystem
from pathlib import Path
from xml.etree.ElementTree import tostring as xml_to_string

import lkaccess.contexts
import requests
from lkaccess import LabKey, QueryFilter
import json

"""
This is a superclass for uploading ot FMS

"""


class FMSUploader:
    def __init__(self, file_path: str, file_type: str, metadata: dict, env="stg"):
        self.env = env
        self.file_path = Path(file_path)
        self.file_type = file_type
        self.metadata = metadata

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
            headers={"x-user-id": "brian.whitney"}, # this should change to a generic user
        )  

        return (
            r.json()
        )

    def get_well_id(f,row,col):

        wells = json.load(f)['wells']

        for well in wells:
            if (well['row'] == row) and (well['col'] == col):
                well_id = well['wellId']
                return well_id
        if not well_id:
            raise Exception(f'The well at row {row} column {col} does not exist in the labkey metadata for the specified plate')

    def upload(self):
        fms = FileManagementSystem(env=self.env)

        run_count = 0
        while run_count < 5:
            try:
                return fms.upload_file(
                    file_reference=self.file_path,
                    file_type=self.file_type,
                    metadata=self.metadata,
                )
            except requests.exceptions.ReadTimeout:
                print("")
                run_count = run_count + 1
                continue
            break
        return None


 


