import os
import re
import xml.etree.ElementTree as ET


DATATYPES_NAMES = {
    "fixed_totalizer": "Fixed Totaliser",
    "free_function": "Free Function",
    "group_name": "Group",
    "department_name": "Department",
    "plu_name": "PLU",
    "plu2nd_name": "PLU 2nd",
    "clerk_name": "Clerk",
    "customer_name": "Customers",
    "mixmatch_name": "Mix & Match",
    "tax_name": "Tax table"
}

def check_group_dirs(org_data_path):
    """
    Checks whether organization directory contains Group directories
    :param org_data_path: path for organization directory
    :return: True if present, False if not present
    """
    content = os.listdir(org_data_path)
    for item_name in content:
        item_path = os.path.join(org_data_path, item_name)

        # a directory found, check if this is a group directory
        if os.path.isdir(item_path):
            if "group" in item_name.lower():
                return True

    return False


def check_master_files_dirs(org_data_path):
    """
    Checks whether Master Files directory is present anywhere in organization directory (in groups subdirectories)
    And Master Files directory is not empty
    :param org_data_path: path for organization directory
    :return: True if present, False if not present
    """
    content = os.listdir(org_data_path)

    # go through each item in organization directory
    for item_name in content:
        item_path = os.path.join(org_data_path, item_name)

        if os.path.isdir(item_path):
            group_dir_content = os.listdir(item_path)

            # go through each item of a directory
            for group_dir_item_name in group_dir_content:
                group_dir_item_path = os.path.join(item_path, group_dir_item_name)

                # master files directory found
                if os.path.isdir(group_dir_item_path) and 'master files' in group_dir_item_name.lower():
                    master_files_content = os.listdir(group_dir_item_path)
                    if len(master_files_content) > 0:
                        return True

    return False


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
