from datetime import datetime

import requests

SERVICE_MMS = "mms"
MMS_RESOURCE_PLATE_INFO = "plate_info"
MMS_STG_URL = "http://stg-aics-api.corp.alleninstitute.org/metadata-management-service/1.0/plate/query?barcode="
MMS_PROD_URL = "http://aics-api.corp.alleninstitute.org/metadata-management-service/1.0/plate/query?barcode="
ENV_SERVICE_MAP = {
    "stg": {SERVICE_MMS: {MMS_RESOURCE_PLATE_INFO: MMS_STG_URL}},
    "prod": {SERVICE_MMS: {MMS_RESOURCE_PLATE_INFO: MMS_PROD_URL}},
}


class CeligoUtil:
    def __init__(self, env: str = "stg"):
        self.env = env

    def lookup_well_id(self, plate_barcode, well_name):
        url = ENV_SERVICE_MAP[self.env][SERVICE_MMS][MMS_RESOURCE_PLATE_INFO] + str(
            plate_barcode
        )
        well_info_response = requests.get(url)
        well_info = well_info_response.json()
        if len(well_info["data"]) > 1:
            raise Exception(f"Barcode {plate_barcode} is used by more than one plate.")
        well_name_lookup = well_info["data"][0]["wellNameLookup"]

        return well_name_lookup[well_name]["wellId"]

    def parse_filename(self, file_name):
        raw_metadata = file_name.split("_")
        plate_barcode = int(raw_metadata[0])
        well_name = raw_metadata[4]
        scan_date_time_parts = raw_metadata[2].split("-")
        hours = int(scan_date_time_parts[3])
        if scan_date_time_parts[6] == "PM":
            hours = hours + 12
        scan_date_time = datetime(
            year=int(scan_date_time_parts[2]),
            month=int(scan_date_time_parts[0]),
            day=int(scan_date_time_parts[1]),
            hour=hours,
            minute=int(scan_date_time_parts[4]),
            second=int(scan_date_time_parts[5]),
        )
        # This is a bit ugly, but matches historical values

        standardized_scan_date_time_parts = scan_date_time.isoformat(
            timespec="auto"
        ).split("T")
        scan_time = standardized_scan_date_time_parts[1]
        scan_date = standardized_scan_date_time_parts[0]

        return plate_barcode, well_name, scan_date, scan_time
