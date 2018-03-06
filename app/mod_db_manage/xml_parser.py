from datetime import datetime

from app.mod_db_manage.utils import *
from app.mod_db_manage.config import DATA_DIR


def get_orders_gen(org_path):
    """
    Get orders data
    :param org_path: path of Group directory with order XML files
    :return: OrderData class object
    """
    order_files_gen = get_order_xml(org_path)

    for of in order_files_gen:
        data = parse_xml(of)
        yield OrderData(data, of)


def get_order_items_gen(order_file):
    """
    Get each order item
    :param order_file: XML file from which order data will be extracted
    :return: ItemData class object
    """
    data = parse_xml(order_file)
    items = data.findall("Item")

    for item in items:
        yield ItemData(item)


def choose_data_class(name):
    """
    Matches tag name with associated class
    :param name: tag_name
    :return: matching class or None
    """
    if name == DATATYPES_NAMES["fixed_totalizer"]:
        return FixedTotalizerData
    elif name == DATATYPES_NAMES["free_function"]:
        return FreeFunctionData
    elif name == DATATYPES_NAMES["group_name"]:
        return GroupData
    elif name == DATATYPES_NAMES["department_name"]:
        return DepartmentData
    elif name == DATATYPES_NAMES["plu_name"]:
        return PLUData
    elif name == DATATYPES_NAMES["plu2nd_name"]:
        return PLUData
    elif name == DATATYPES_NAMES["clerk_name"]:
        return ClerkData
    elif name == DATATYPES_NAMES["customer_name"]:
        return CustomerData
    elif name == DATATYPES_NAMES["mixmatch_name"]:
        return MixMatchData
    elif name == DATATYPES_NAMES["tax_name"]:
        return TaxData
    else:
        return None


def extract_master_files_data(org_path, data_type_name):
    """
    Generic class for getting XML data
    :param org_path: path of organization directory
    :param data_type_name: name of data type needed (whether data should be searched for fixed totals, free functions etc.)
    :return: <datatype> class object with parsed data
    """
    group_dirs_names = os.listdir(org_path)

    for group_dir_name in group_dirs_names:
        mf_dir = get_mf_dir(org_path, group_dir_name)
        mf_xml_files = get_mf_xml(mf_dir)

        # go through each master file in a directory
        # if there are several master files that represent same data type, they all will be processed
        for mf_file in mf_xml_files:
            data = parse_xml(os.path.join(mf_dir, mf_file))
            name_tag = data.find("Name").text

            if name_tag == data_type_name:
                records = get_xml_records(data)

                for record in records:
                    # discard empty tags

                    # special case for Customer data type
                    if name_tag == DATATYPES_NAMES["customer_name"]:
                        customer_fname = record.find("FirstName").text
                        customer_sname = record.find("Surname").text

                        if not check_tag_length(customer_fname) or not check_tag_length(customer_sname):
                            continue
                    # general way of getting record names
                    else:
                        record_name = record.find("Name").text

                        if not check_tag_length(record_name):
                            continue

                    path = os.path.join(mf_dir, mf_file)
                    classname = choose_data_class(data_type_name)

                    yield classname(data, path, record)

            else:
                continue


class MasterData():
    def __init__(self, data, path):
        date = data.find("Date").text
        time = data.find("Time").text
        self.date_time = datetime.strptime(date + " " + time, "%d/%m/%Y %H:%M")
        self.filepath = path
        self.data_dir = DATA_DIR


class FixedTotalizerData(MasterData):
    def __init__(self, data, path, record):
        super(FixedTotalizerData, self).__init__(data, path)
        self.number = record.find("Number").text
        self.name = record.find("Name").text


class FreeFunctionData(MasterData):
    def __init__(self, data, path, record):
        super(FreeFunctionData, self).__init__(data, path)
        self.number = record.find("Number").text
        self.name = record.find("Name").text.strip()
        self.function_number = record.find("FunctionNo").text


class GroupData(MasterData):
    def __init__(self,data, path, record):
        super(GroupData, self).__init__(data, path)
        self.number = record.find("Number").text
        self.name = record.find("Name").text


class DepartmentData(MasterData):
    def __init__(self, data, path, record):
        super(DepartmentData, self).__init__(data, path)
        self.number = record.find("Number").text
        self.name = record.find("Name").text
        self.group_number = record.find("GroupNo").text


class PLUData(MasterData):
    def __init__(self, data, path, record):
        super(PLUData, self).__init__(data, path)
        self.number = record.find("Number").text
        self.name = record.find("Name").text
        self.group_number = record.find("GroupNo").text
        self.department_number = record.find("DepartmentNo").text
        self.price = record.find("Price").text
        self.tax_number = record.find("TaxNo").text
        try:
            self.mix_match_number = record.find("MixMatch").text
        except:
            self.mix_match_number = None


# class PLU2ndData(MasterData):
#     def __init__(self, data, path, record):
#         super(PLU2ndData, self).__init__(data, path)
#         self.number = record.find("Number").text
#         self.name = record.find("Name").text
#         self.group_number = record.find("GroupNo").text
#         self.department_number = record.find("DepartmentNo").text
#         self.price = record.find("Price").text
#         self.tax_number = record.find("TaxNo").text


class ClerkData(MasterData):
    def __init__(self, data, path, record):
        super(ClerkData, self).__init__(data, path)
        self.number = record.find("Number").text
        self.name = record.find("Name").text


class CustomerData(MasterData):
    def __init__(self, data, path, record):
        super(CustomerData, self).__init__(data, path)
        self.number = record.find("Number").text
        self.first_name = record.find("FirstName").text
        self.surname = record.find("Surname").text
        self.addr1 = record.find("Address1").text
        self.addr2 = record.find("Address2").text
        self.addr3 = record.find("Address3").text
        self.postcode = record.find("Postcode").text
        self.phone = record.find("Telephone").text
        self.email = record.find("Email").text
        self.overdraft_limit = record.find("OverDraftLimit").text
        self.custgroup_number = record.find("CustGroupNo").text


class MixMatchData(MasterData):
    def __init__(self, data, path, record):
        super(MixMatchData, self).__init__(data, path)
        self.number = record.find("Number").text
        self.name = record.find("Name").text
        self.operation_type = record.find("OperationType").text
        self.qty_req = record.find("QtyReq").text
        self.amount = record.find("Amount").text


class TaxData(MasterData):
    def __init__(self, data, path, record):
        super(TaxData, self).__init__(data, path)
        self.number = record.find("Number").text
        self.name = record.find("Name").text
        self.rate = record.find("Rate").text


class OrderData():
    def __init__(self, order, path):
        date = order.find("Date").text
        time = order.find("Time").text
        self.date_time = datetime.strptime(date + " " + time, "%d/%m/%Y %H:%M:%S")
        self.mode = order.find("Mode").text
        self.consecutive_number = order.find("ConsecutiveNo").text
        self.terminal_number = order.find("TerminalNo").text
        self.terminal_name = order.find("TerminalName").text
        self.clerk_number = order.find("ClerkNo").text
        self.table_number = order.find("TableNo").text
        self.filepath = path
        try:
            self.customer_number = order.find("Customer").find("CustomerID").text
        except:
            self.customer_number = None


class ItemData():
    def __init__(self, item):
        self.item_type = item.find("ItemType").text
        self.item_number = item.find("ItemNo").text
        self.name = item.find("ItemName").text
        self.qty = item.find("Qty").text
        self.value = item.find("Value").text
        try:
            self.option = item.find("Options").text
        except:
            self.option = None
