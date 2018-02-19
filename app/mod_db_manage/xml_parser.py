import os

from datetime import datetime

from app.mod_db_manage.utils import parse_xml, get_xml_records, get_order_xml, get_mf_dir, get_mf_xml, check_tag_length
from app.mod_db_manage.config import DATA_DIR, SCRIPT_DIR


GROUP_DIRS = []


def get_orders_gen():
    """Get orders data"""
    order_files_gen = get_order_xml(GROUP_DIRS)

    for of in order_files_gen:
        data = parse_xml(of)
        yield OrderData(data, of)


def get_order_items_gen(order_file):
    """Get each order item"""
    data = parse_xml(order_file)
    items = data.findall("Item")

    for item in items:
        yield ItemData(item)


def get_fixed_total_gen(org_directory):
    """Get Fixed Totaliser data"""
    group_dirs = os.listdir(os.path.join(SCRIPT_DIR,os.path.join(DATA_DIR, org_directory)))
    print(group_dirs)
    for group_dir in group_dirs:
        mf_dir = get_mf_dir(SCRIPT_DIR + DATA_DIR, group_dir)
        mf_xml_files = get_mf_xml(mf_dir)

        for mf_file in mf_xml_files:
            data = parse_xml(os.path.join(mf_dir,mf_file))
            name_tag = data.find("Name").text

            # fixed totaliser
            if name_tag == "Fixed Totaliser":
                records = get_xml_records(data)

                for record in records:
                    path = os.path.join(mf_dir, mf_file)
                    yield FixedTotalizerData(data, path, record)

            else:
                continue


def get_free_func_gen():
    """Get Free function data"""
    for group_dir in GROUP_DIRS:
        mf_dir = get_mf_dir(SCRIPT_DIR + DATA_DIR, group_dir)
        mf_xml_files = get_mf_xml(mf_dir)

        for mf_file in mf_xml_files:
            data = parse_xml(mf_dir + mf_file)
            name_tag = data.find("Name").text

            if name_tag == "Free Function":
                records = get_xml_records(data)

                for record in records:
                    ff_name = record.find("Name").text

                    # discard empty tags
                    if not check_tag_length(ff_name):
                        continue

                    path = mf_dir + mf_file
                    yield FreeFunctionData(data, path, record)

            else:
                continue


def get_group_gen():
    """Get Group data"""
    for group_dir in GROUP_DIRS:
        mf_dir = get_mf_dir(SCRIPT_DIR + DATA_DIR, group_dir)
        mf_xml_files = get_mf_xml(mf_dir)

        for mf_file in mf_xml_files:
            data = parse_xml(mf_dir + mf_file)
            name_tag = data.find("Name").text

            if name_tag == "Group":
                records = get_xml_records(data)

                for record in records:
                    group_name = record.find("Name").text

                    # discard empty tags
                    if not check_tag_length(group_name):
                        continue

                    path = mf_dir + mf_file
                    yield GroupData(data, path, record)

            else:
                continue


def get_department_gen():
    """Get Department data"""
    for group_dir in GROUP_DIRS:
        mf_dir = get_mf_dir(SCRIPT_DIR + DATA_DIR, group_dir)
        mf_xml_files = get_mf_xml(mf_dir)

        for mf_file in mf_xml_files:
            data = parse_xml(mf_dir + mf_file)
            name_tag = data.find("Name").text

            if name_tag == "Department":
                records = get_xml_records(data)

                for record in records:
                    dep_name = record.find("Name").text

                    # discard empty tags
                    if not check_tag_length(dep_name):
                        continue

                    path = mf_dir + mf_file
                    yield DepartmentData(data, path, record)

            else:
                continue


def get_plu_gen():
    """Get PLU data"""
    for group_dir in GROUP_DIRS:
        mf_dir = get_mf_dir(SCRIPT_DIR + DATA_DIR, group_dir)
        mf_xml_files = get_mf_xml(mf_dir)

        for mf_file in mf_xml_files:
            data = parse_xml(mf_dir + mf_file)
            name_tag = data.find("Name").text

            if name_tag == "PLU":
                records = get_xml_records(data)

                for record in records:
                    plu_name = record.find("Name").text

                    if not check_tag_length(plu_name):
                        continue

                    path = mf_dir + mf_file
                    yield PLUData(data, path, record)

            else:
                continue


def get_plu2nd_gen():
    """Get PLU data"""
    for group_dir in GROUP_DIRS:
        mf_dir = get_mf_dir(SCRIPT_DIR + DATA_DIR, group_dir)
        mf_xml_files = get_mf_xml(mf_dir)

        for mf_file in mf_xml_files:
            data = parse_xml(mf_dir + mf_file)
            name_tag = data.find("Name").text

            if name_tag == "PLU 2nd":
                records = get_xml_records(data)

                for record in records:
                    plu_name = record.find("Name").text

                    if not check_tag_length(plu_name):
                        continue

                    path = mf_dir + mf_file
                    yield PLU2ndData(data, path, record)

            else:
                continue


def get_clerk_gen():
    """Get PLU data"""
    for group_dir in GROUP_DIRS:
        mf_dir = get_mf_dir(SCRIPT_DIR + DATA_DIR, group_dir)
        mf_xml_files = get_mf_xml(mf_dir)

        for mf_file in mf_xml_files:
            data = parse_xml(mf_dir + mf_file)
            name_tag = data.find("Name").text

            if name_tag == "Clerk":
                records = get_xml_records(data)

                for record in records:
                    clerk_name = record.find("Name").text

                    if not check_tag_length(clerk_name):
                        continue

                    path = mf_dir + mf_file
                    yield ClerkData(data, path, record)

            else:
                continue


def get_customer_gen():
    """Get PLU data"""
    for group_dir in GROUP_DIRS:
        mf_dir = get_mf_dir(SCRIPT_DIR + DATA_DIR, group_dir)
        mf_xml_files = get_mf_xml(mf_dir)

        for mf_file in mf_xml_files:
            data = parse_xml(mf_dir + mf_file)
            name_tag = data.find("Name").text

            if name_tag == "Customers":
                records = get_xml_records(data)

                for record in records:
                    customer_fname = record.find("FirstName").text
                    customer_sname = record.find("Surname").text

                    if not check_tag_length(customer_fname) or not check_tag_length(customer_sname):
                        continue

                    path = mf_dir + mf_file
                    yield CustomerData(data, path, record)

            else:
                continue


def get_mixmatch_gen():
    """Get Mix & Match data"""
    for group_dir in GROUP_DIRS:
        mf_dir = get_mf_dir(SCRIPT_DIR + DATA_DIR, group_dir)
        mf_xml_files = get_mf_xml(mf_dir)

        for mf_file in mf_xml_files:
            data = parse_xml(mf_dir + mf_file)
            name_tag = data.find("Name").text

            if name_tag == "Mix & Match":
                records = get_xml_records(data)

                for record in records:
                    mm_name = record.find("Name").text

                    if not check_tag_length(mm_name):
                        continue

                    path = mf_dir + mf_file
                    yield MixMatchData(data, path, record)

            else:
                continue


def get_tax_gen():
    """Get tax data"""
    for group_dir in GROUP_DIRS:
        mf_dir = get_mf_dir(SCRIPT_DIR + DATA_DIR, group_dir)
        mf_xml_files = get_mf_xml(mf_dir)

        for mf_file in mf_xml_files:
            data = parse_xml(mf_dir + mf_file)
            name_tag = data.find("Name").text

            if name_tag == "Tax table":
                records = get_xml_records(data)

                for record in records:
                    tax_name = record.find("Name").text

                    if not check_tag_length(tax_name):
                        continue

                    path = mf_dir + mf_file
                    yield TaxData(data, path, record)

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
        self.random_code = record.find("RandomeCode").text
        self.mix_match = record.find("MixMatch").text
        self.description = record.find("Description").text


class PLU2ndData(MasterData):
    def __init__(self, data, path, record):
        super(PLU2ndData, self).__init__(data, path)
        self.number = record.find("Number").text
        self.name = record.find("Name").text
        self.group_number = record.find("GroupNo").text
        self.department_number = record.find("DepartmentNo").text
        self.price = record.find("Price").text
        self.tax_number = record.find("TaxNo").text


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
