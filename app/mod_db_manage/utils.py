import os
import re
import xml.etree.ElementTree as ET

from app.mod_db_manage.config import DATA_DIR, SCRIPT_DIR


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


def get_order_xml(group_dirs):
    """Get xml with orders data"""
    for group_dir in group_dirs:
        orders_xml_dir = SCRIPT_DIR + DATA_DIR + group_dir
        orders_xml = os.listdir(orders_xml_dir)
        
        for of in orders_xml:
            if "Order" in of:
                yield orders_xml_dir + "/" + of


def get_mf_dir(data_dir, group_dir):
    """Get xml files with Master Files data"""
    try:
        master_files_dir = data_dir + group_dir + "/Master Files/"
        master_files_xml = os.listdir(master_files_dir)
    except:
        master_files_dir = data_dir + group_dir + "/MASTER FILES/"
        master_files_xml = os.listdir(master_files_dir)

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
