import os
import re
import xml.etree.ElementTree as ET


def parse_xml(filename):
    """Return content of an XML file"""
    tree = ET.parse(filename)
    data = tree.getroot()

    return data


def get_xml_records(data):
    """Get data of a <Record> tag"""
    records_root = data.find("Records")
    records = records_root.findall("Record")

    return records


def get_order_xml(org_path):
    """Get xml with orders data"""
    group_dirs_names = os.listdir(org_path)
    for group_dir_name in group_dirs_names:
        orders_xml_dir = os.path.join(org_path, group_dir_name)
        orders_xml = os.listdir(orders_xml_dir)
        
        for of in orders_xml:
            if "Order" in of:
                yield orders_xml_dir + "/" + of


def get_mf_dir(org_path, group_dir_name):
    """Get xml files with Master Files data"""
    group_dir = os.path.join(org_path, group_dir_name)
    master_files_dir = os.path.join(group_dir, "Master Files")
    if not os.path.isdir(master_files_dir):
        master_files_dir = os.path.join(group_dir, "MASTER FILES")

    return master_files_dir


def get_mf_xml(mf_dir):
    """Return all files from Master Files directories"""
    master_files_xml = os.listdir(mf_dir)

    return master_files_xml


def check_tag_length(tag_text):
    """Returns True if tag is not empty or not None"""
    if tag_text is None:
        return False

    tag_content = re.findall("\w+", tag_text)

    if len(tag_content) > 0:
        return True
    else:
        return False
