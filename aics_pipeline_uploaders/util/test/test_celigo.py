from ...util import CeligoUtil

def test_parse_filename() -> None:
    plate_barcode, well_name, scan_date, scan_time = CeligoUtil.parse_filename("3500001609_Scan_1-12-2018-6-03-16-AM_Well_F5_Ch1_-1um.tiff")
    assert plate_barcode == 3500001609
    assert well_name == 'F5'
    assert scan_date == '2018-01-12'
    assert scan_time == '06:03:16'