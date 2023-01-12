import json
import pytest
from aics_pipeline_uploaders.util.celigo import BarcodeException, MMSException
import requests_mock

from ...util import CeligoUtil


def test_parse_filename() -> None:
    util = CeligoUtil('stg')
    filename = "3500001609_Scan_1-12-2018-6-03-16-AM_Well_F5_Ch1_-1um.tiff"
    plate_barcode, well_name, scan_date, scan_time = util.parse_filename(filename)
    assert plate_barcode == 3500001609
    assert well_name == 'F5'
    assert scan_date == '2018-01-12'
    assert scan_time == '06:03:16'


def test_lookup_well_id_multiple_plates() -> None:
    util = CeligoUtil('stg')

    with requests_mock.Mocker() as mock_request:
        mms_url = "http://stg-aics-api.corp.alleninstitute.org/metadata-management-service/1.0/plate/query?barcode=3500001609"  # noqa: E501
        mms_resp = {"data": [{
                "plate": {
                    "plateId": 328,
                    "barcode": "3500001609",
                    "imagingSessionId": 1,
                },
                "wellNameLookup": {
                    "A6": {
                        "wellId": 101190,
                        "row": 0,
                        "col": 5,
                        "cellPopulations": [],
                        "solutions": [],
                    },
                    "A5": {
                        "wellId": 101189,
                        "row": 0,
                        "col": 4,
                        "cellPopulations": [],
                        "solutions": [],
                    }
                }
            }, {
                "plate": {
                    "plateId": 329,
                    "barcode": "3500001609",
                    "imagingSessionId": 2,
                },
                "wellNameLookup": {
                    "A6": {
                        "wellId": 101190,
                        "row": 0,
                        "col": 5,
                        "cellPopulations": [],
                        "solutions": [],
                    },
                    "A5": {
                        "wellId": 101189,
                        "row": 0,
                        "col": 4,
                        "cellPopulations": [],
                        "solutions": [],
                    }
                }
            }]}
        mock_request.get(mms_url, text=json.dumps(mms_resp))
        with pytest.raises(BarcodeException):
            util.lookup_well_id("3500001609", "A5")


def test_lookup_well_id_404() -> None:
    util = CeligoUtil('stg')

    with requests_mock.Mocker() as mock_request:
        mms_url = "http://stg-aics-api.corp.alleninstitute.org/metadata-management-service/1.0/plate/query?barcode=3500001609"  # noqa: E501
        mock_request.get(mms_url, status_code=404)
        assert None == util.lookup_well_id("3500001609", "A5")


def test_lookup_well_id_500() -> None:
    util = CeligoUtil('stg')

    with requests_mock.Mocker() as mock_request:
        mms_url = "http://stg-aics-api.corp.alleninstitute.org/metadata-management-service/1.0/plate/query?barcode=3500001609"  # noqa: E501
        mock_request.get(mms_url, status_code=500)
        with pytest.raises(MMSException):
            util.lookup_well_id("3500001609", "A5")


def test_lookup_well_id_success() -> None:
    util = CeligoUtil('stg')
    mms_url = "http://stg-aics-api.corp.alleninstitute.org/metadata-management-service/1.0/plate/query?barcode=3500001609"  # noqa: E501
    mms_resp = {"data": [{
                    "wellNameLookup": {
                        "A6": {
                            "wellId": 101190,
                            "row": 0,
                            "col": 5,
                            "cellPopulations": [],
                            "solutions": [],
                        },
                        "A5": {
                            "wellId": 101189,
                            "row": 0,
                            "col": 4,
                            "cellPopulations": [],
                            "solutions": [],
                        }
                    }
                }]}
    with requests_mock.Mocker() as mock_request:
        mock_request.get(mms_url, text=json.dumps(mms_resp))
        well_id = util.lookup_well_id("3500001609", "A5")
        assert well_id == 101189

        

def test_lookup_well_id_no_well_name() -> None:
    util = CeligoUtil('stg')
    mms_url = "http://stg-aics-api.corp.alleninstitute.org/metadata-management-service/1.0/plate/query?barcode=3500001609"  # noqa: E501
    mms_resp = {"data": [{
                    "wellNameLookup": {
                        "A6": {
                            "wellId": 101190,
                            "row": 0,
                            "col": 5,
                            "cellPopulations": [],
                            "solutions": [],
                        },
                        "A5": {
                            "wellId": 101189,
                            "row": 0,
                            "col": 4,
                            "cellPopulations": [],
                            "solutions": [],
                        }
                    }
                }]}
    with requests_mock.Mocker() as mock_request:
        mock_request.get(mms_url, text=json.dumps(mms_resp))
        well_id = util.lookup_well_id("3500001609", "A99")
        assert well_id == None

