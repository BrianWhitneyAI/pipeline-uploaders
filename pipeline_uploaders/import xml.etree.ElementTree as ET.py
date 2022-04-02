import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring as xml_to_string

from aicsimageio import AICSImage
path = "/allen/aics/microscopy/PRODUCTION/PIPELINE_8_1/5500000622_DD_1-01/5500000622_DD_1-01_AcquisitionBlock1/5500000622_DD_1-01_AcquisitionBlock1_pt1.czi"

def get_well_data(block_path):
    block_img = AICSImage(block_path)

    scene_dict = {}
    wells = []

    with open("metadata.czi.xml", "w") as f:
        f.write(xml_to_string(block_img.metadata, encoding="unicode"))
    tree = ET.parse("metadata.czi.xml")
    root = tree.getroot()

    for Scene in root.iter("Scene"):
        # Add Scene and Well to scene_dict
        scene_dict[Scene.get("Name")] = Scene.find("Shape").get("Name")

        # Add new well to well list
        if (Scene.find("Shape").get("Name")) not in wells:
            wells.append(Scene.find("Shape").get("Name"))

    return wells, scene_dict

wells, scene_dict = get_well_data(path)
print(wells)
print(scene_dict)