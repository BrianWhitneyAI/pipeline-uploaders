from aicsimageio import AICSImage
from xml.etree.ElementTree import tostring as xml_to_string
import xml.etree.ElementTree as ET
import pandas as pd

def find_wellscan_metadata(wellscans):
    wellscan_data = []
    for wellscan in wellscans:
        well_img = AICSImage(wellscan)
        with open("metadata.czi.xml", "w") as f:
            f.write(xml_to_string(well_img.metadata, encoding="unicode"))
        tree = ET.parse('metadata.czi.xml')
        root = tree.getroot()
        
        centerpoint = root.find("./Metadata/ExperimentBlocks/AqusitionBlock/SubDimensionSetups/RegionSetup/SampleHolder/TileRegions/TileRegion/Centerpoint").attrib
        width = root.find("./Metadata/ExperimentBlocks/AqusitionBlock/SubDimensionSetups/RegionSetup/SampleHolder/TileDimension/Width").attrib
        height = root.find("./Metadata/ExperimentBlocks/AqusitionBlock/SubDimensionSetups/RegionSetup/SampleHolder/TileDimension/Height").attrib

        dict = {
            'well': well,
            'centerpoint': centerpoint,
            'width' : width,
            'height': height
        }

        wellscan_data.append(dict)
    return wellscan_data

def get_wells(block_metadata, wellscan_data):
    block_img = AICSImage(block_metadata)
    with open("metadata.czi.xml", "w") as f:
        f.write(xml_to_string(block_img.metadata, encoding="unicode"))
    tree = ET.parse('metadata.czi.xml')
    root = tree.getroot()
    metadata = []
    for position in root.findall('SingleTileRegion'):
        dict = {
            'name' : position.get('name'),
            'X' : position.find('X'),
            'Y' : position.find('Y'),
            'Z' : position.find('Z'),
            'Well' : find_matching_well(x = position.find('X'),
                               y = position.find('Y'),
                               wellscan_data = wellscan_data)
        }
        metadata.append(dict)
    return metadata

def find_matching_well(x,y,wellscan_data):
    for well in wellscan_data:
        if (x is < well['centerpoint'][0] + 0.5 * well[width])
                and (x is > well['centerpoint'][0] - 0.5 * well[width])
                and (y is < well['centerpoint'][0] + 0.5 * well[height])
                and (y is > well['centerpoint'][0] - 0.5 * well[height]):
                return well['well']
    print('Error: this positon does not fall within any of the given wells')
    return None


def run_all(block_path : str, wellscans : list):
    wellscan_data = find_wellscan_metadata(wellscans)
    metadata = get_wells(block_path, wellscan_data)
    metadata = pd.dataframe(metadata) # or whatever output you want for the data
