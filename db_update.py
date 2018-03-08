"""
Connects to database and adds new data from XML files
"""
import argparse
import traceback

from app import db
from app.models import User, Organization, FixedTotalizer, FreeFunction, Department, Group, PLU, Tax, \
                        Clerk, Customer, Order, OrderLine
from app.mod_db_manage.xml_parser import get_orders_gen, get_order_items_gen, extract_master_files_data
from app.mod_db_manage.config import *
from app.mod_db_manage.utils import check_group_dirs, check_master_files_dirs, DATATYPES_NAMES


class DBInsert:
    """
    Inserts new data from XML files to database
    New instance is created for each valid Group directory of organization directory
    """
    def __init__(self, org_dir, org_id):
        self.org_dir = org_dir
        self.org_id = org_id

    def if_duplicate_exists(self, classname, **kwargs):
        """
        Try to find an entry's duplicate in database

        :param classname: a class for searching (for example, User, Organization, FreeFunction etc.)
        :param kwargs: keyword parameter to find certain object
        :return: True, if duplicate found, False if not found
        """
        duplicate = classname.query.filter_by(**kwargs).first()

        if duplicate:
            return True
        else:
            return False

    def insert_fixed_totalizer(self):
        fixed_totalizers = extract_master_files_data(self.org_dir, DATATYPES_NAMES["fixed_totalizer"])

        for ft in fixed_totalizers:
            ft_duplicate = self.if_duplicate_exists(FixedTotalizer, number=ft.number, org_id=self.org_id)
            if ft_duplicate:
                continue

            db_ft = FixedTotalizer(number=ft.number,
                                   date_time=ft.date_time,
                                   filepath=ft.filepath,
                                   data_dir=ft.data_dir,
                                   org_id=self.org_id,
                                   name=ft.name
                                   )
            db.session.add(db_ft)
            db.session.commit()
            print(db_ft)

    def insert_free_function(self):
        free_functions = extract_master_files_data(self.org_dir, DATATYPES_NAMES["free_function"])

        for ff in free_functions:
            ff_duplicate = self.if_duplicate_exists(FreeFunction, number=ff.number, org_id=self.org_id)
            if ff_duplicate:
                continue

            db_ff = FreeFunction(number=ff.number,
                                 date_time=ff.date_time,
                                 filepath=ff.filepath,
                                 data_dir=ff.data_dir,
                                 org_id=self.org_id,
                                 name=ff.name,
                                 function_number=ff.function_number
                                 )
            db.session.add(db_ff)
            db.session.commit()
            print(db_ff)

    def insert_group(self):
        groups = extract_master_files_data(self.org_dir, DATATYPES_NAMES["group_name"])

        for group in groups:
            group_duplicate = self.if_duplicate_exists(Group, number=group.number, org_id=self.org_id)
            if group_duplicate:
                continue

            db_group = Group(number=group.number,
                             date_time=group.date_time,
                             filepath=group.filepath,
                             data_dir=group.data_dir,
                             org_id=self.org_id,
                             name=group.name,
                             )
            db.session.add(db_group)
            db.session.commit()
            print(db_group)

    def insert_departments(self):
        departments = extract_master_files_data(self.org_dir, DATATYPES_NAMES["department_name"])

        for dep in departments:
            dep_duplicate = self.if_duplicate_exists(Department, number=dep.number, org_id=self.org_id)
            if dep_duplicate:
                continue

            # check for group with non-existing number
            valid_group = db.session.query(Group).filter_by(number=dep.group_number).first()
            if not valid_group:
                dep.group_id = None
            else:
                dep.group_id = valid_group.id

            db_dep = Department(number=dep.number,
                                date_time=dep.date_time,
                                filepath=dep.filepath,
                                data_dir=dep.data_dir,
                                org_id=self.org_id,
                                name=dep.name,
                                group_id=dep.group_id)
            db.session.add(db_dep)
            db.session.commit()
            print(db_dep)

    def insert_taxes(self):
        taxes = extract_master_files_data(self.org_dir, DATATYPES_NAMES["tax_name"])

        for tax in taxes:
            tax_duplicate = self.if_duplicate_exists(Tax, number=tax.number, org_id=self.org_id)
            if tax_duplicate:
                continue

            db_tax = Tax(number=tax.number,
                         date_time=tax.date_time,
                         filepath=tax.filepath,
                         data_dir=tax.data_dir,
                         org_id=self.org_id,
                         name=tax.name,
                         rate=tax.rate
                         )
            db.session.add(db_tax)
            db.session.commit()
            print(db_tax)

    def insert_plu(self):
        # merge PLU and PLU 2nd items together
        plu_items = list(extract_master_files_data(self.org_dir, DATATYPES_NAMES["plu_name"]))
        plu2nd_items = list(extract_master_files_data(self.org_dir, DATATYPES_NAMES["plu2nd_name"]))

        for plu in plu_items + plu2nd_items:
            plu_duplicate = self.if_duplicate_exists(PLU, number=plu.number, name=plu.name, org_id=self.org_id)
            if plu_duplicate:
                continue

            # check for group and department with non-existing number
            valid_group = Group.query.filter_by(number=plu.group_number).first()
            if not valid_group:
                plu.group_id = None
            else:
                plu.group_id = valid_group.id

            valid_dep = Department.query.filter_by(number=plu.department_number).first()
            if not valid_dep:
                plu.department_id = None
            else:
                plu.department_id = valid_dep.id

            valid_tax = Tax.query.filter_by(number=plu.tax_number).first()
            if not valid_tax:
                plu.tax_id = None
            else:
                plu.tax_id = valid_tax.id

            db_plu = PLU(number=plu.number,
                         date_time=plu.date_time,
                         filepath=plu.filepath,
                         data_dir=plu.data_dir,
                         org_id=self.org_id,
                         name=plu.name,
                         group_id=plu.group_id,
                         department_id=plu.department_id,
                         price=plu.price,
                         tax_id=plu.tax_id,
                         )
            db.session.add(db_plu)
            db.session.commit()
            print(db_plu)

    def insert_clerks(self):
        clerks = extract_master_files_data(self.org_dir, DATATYPES_NAMES["clerk_name"])

        for clerk in clerks:
            clerk_duplicate = self.if_duplicate_exists(Clerk, number=clerk.number, org_id=self.org_id)
            if clerk_duplicate:
                continue

            db_clerk = Clerk(number=clerk.number,
                             date_time=clerk.date_time,
                             filepath=clerk.filepath,
                             data_dir=clerk.data_dir,
                             org_id=self.org_id,
                             name=clerk.name
                             )
            db.session.add(db_clerk)
            db.session.commit()
            print(db_clerk)

    def insert_customers(self):
        customers = extract_master_files_data(self.org_dir, DATATYPES_NAMES["customer_name"])

        for customer in customers:
            customer_duplicate = self.if_duplicate_exists(Customer, number=customer.number, org_id=self.org_id)
            if customer_duplicate:
                continue

            db_customer = Customer(number=customer.number,
                                   date_time=customer.date_time,
                                   filepath=customer.filepath,
                                   data_dir=customer.data_dir,
                                   org_id=self.org_id,
                                   first_name=customer.first_name,
                                   surname=customer.surname,
                                   addr1=customer.addr1,
                                   addr2=customer.addr2,
                                   addr3=customer.addr3,
                                   postcode=customer.postcode,
                                   phone=customer.phone,
                                   email=customer.email,
                                   overdraft_limit=customer.overdraft_limit,
                                   custgroup_number=customer.custgroup_number
                                   )
            db.session.add(db_customer)
            db.session.commit()
            print(db_customer)

    def customize_orderline_plu(self, db_orderline, plu_number):
        """
        Customize OrderLine object with PLU details (for ItemType = 0)
        """
        db_orderline.product_id = PLU.query.filter_by(org_id=self.org_id, number=plu_number).first().id

        return db_orderline

    def customize_orderline_freefunc(self, order_item, db_orderline):
        """
        Customize OrderLine object with FreeFunction details (for ItemType = 1)
        """
        valid_ffunc = FreeFunction.query.filter_by(number=order_item.item_number).first()

        if not valid_ffunc:
            db_orderline.free_func_id = None
        else:
            db_orderline.free_func_id = valid_ffunc.id

        # for counting CAID, CRID, CHID and CQID (id-drawers)
        fixed_total_number = int(order_item.option[-1]) + MAGIC_INDRAWER_NUMBER
        # fixed_total = FixedTotalizer.query.filter_by(number=fixed_total_number).first()
        # db_orderline.fixed_total_id = fixed_total.id
        fixed_total_id = FixedTotalizer.query.filter_by(org_id=self.org_id, number=fixed_total_number).first().id
        db_orderline.fixed_total_id = fixed_total_id

        return db_orderline

    def customize_orderline_fixedtotal(self, order_item, db_orderline):
        """Customize OrderLine object with FixedTotalizer details (for ItemType = 4)"""
        db_orderline.fixed_total_id = FixedTotalizer.query.filter_by(name=order_item.name).first().id

        return db_orderline

    def get_order_lines(self, db_order, order_lines):
        """
        Insert order lines of particular order to database
        :param db_order: Order object
        :param order_lines: order lines (items of the order)
        """
        for ol_num, order_item in enumerate(order_lines):
            db_orderline = OrderLine()
            db_orderline.order_id = db_order.id
            db_orderline.qty = order_item.qty

            # work with VOID free functions
            # add free function VOID
            if "VD:" in order_item.name:
                void_free_function = FreeFunction.query.filter_by(org_id=self.org_id, name='VOID').first()
                db_orderline.free_func_id = void_free_function.id

            db_orderline.value = order_item.value
            db_orderline.item_type = order_item.item_type

            # process PLU-type item
            if order_item.item_type == str(PLU_ITEM_TYPE):
                db_orderline = self.customize_orderline_plu(db_orderline, order_item.item_number)

            # process Free Function-type item
            elif order_item.item_type == str(FREE_FUNC_ITEM_TYPE):
                db_orderline = self.customize_orderline_freefunc(order_item, db_orderline)

                # check if item has a change (for cash-type free functions)
                if "CASH" in order_item.name:

                    if ol_num < len(order_lines) - 1:
                        next_item = order_lines[ol_num + 1]

                        if next_item.item_type == str(TEXT_ITEM_TYPE) and next_item.name == "CHANGE":
                            db_orderline.change = next_item.value

            # process PLU 2nd-type item
            elif order_item.item_type == str(PLU2ND_ITEM_TYPE):
                db_orderline = self.customize_orderline_plu(db_orderline, order_item.item_number)

            # process Fixed totalizer-type item
            elif order_item.item_type == str(FIXED_TOTAL_TYPE):
                db_orderline = self.customize_orderline_fixedtotal(order_item, db_orderline)

            else:
                continue

            db.session.add(db_orderline)
            db.session.commit()
            print(db_orderline)

    def insert_order_data(self):
        """
        Insert orders to database
        """
        orders = get_orders_gen(self.org_dir)

        for order in orders:
            order_duplicate = self.if_duplicate_exists(Order,
                                                      consecutive_number=order.consecutive_number,
                                                      date_time=order.date_time,
                                                      org_id=self.org_id)
            if order_duplicate:
                continue

            # get clerk id
            valid_clerk = Clerk.query.filter_by(number=order.clerk_number, org_id=self.org_id).first()
            if not valid_clerk:
                clerk_id = None
            else:
                clerk_id = valid_clerk.id

            # get customer id
            valid_customer = Customer.query.filter_by(
                number=order.customer_number, org_id=self.org_id).first()
            if not valid_customer:
                customer_id = None
            else:
                customer_id = valid_customer.id

            db_order = Order(date_time=order.date_time,
                             filepath=order.filepath,
                             org_id=self.org_id,
                             mode=order.mode,
                             consecutive_number=order.consecutive_number,
                             terminal_number=order.terminal_number,
                             terminal_name=order.terminal_name,
                             clerk_id=clerk_id,
                             customer_id=customer_id,
                             table_number=order.table_number
                             )
            db.session.add(db_order)
            db.session.commit()
            print(db_order)

            # process order lines
            order_lines = list(get_order_items_gen(db_order.filepath))
            self.get_order_lines(db_order, order_lines)


from app import session_add, session_commit


def create_admin():
    user = User(username="admin", email="admin@mail.com", is_admin=True)
    user.set_password("12345")
    session_add(user)
    session_commit()


def main():
    db.create_all()

    # check arguments
    parser = argparse.ArgumentParser(description="Specify if create admin with --create_admin")
    parser.add_argument("--create_admin", action="store_true", help="If set, admin user will be created")
    parser.add_argument("--nodata", action="store_true", help="If set, no data will be added")
    args = parser.parse_args()

    if args.create_admin:
        try:
            create_admin()
        except:
            print("Admin user exists already")

    if args.nodata:
        return

    data_path = os.path.join(SCRIPT_DIR, DATA_DIR)
    org_dirs = os.listdir(data_path)

    # go through each directory in data storage
    for org_dir in org_dirs:
        print(org_dir)
        org_data_path = os.path.join(data_path, org_dir)

        # check if organization directory contains any group directories
        if not check_group_dirs(org_data_path):
            print("This directory ({}) does not contain Group directories. Abort.".format(org_dir))
            continue

        # check if organization directory has at least one Master Files directory in all group subdirectories
        if not check_master_files_dirs(org_data_path):
            print("This directory ({}) does not contain Master Files directories. Abort.".format(org_dir))
            continue

        org_id = Organization.query.filter_by(data_dir=org_dir).with_entities(Organization.id).first()

        # check if there is no existing organization for this directory
        if not org_id:
            print('Organization with directory "{}" was not found. Abort.'.format(org_dir))
            continue

        db_insert = DBInsert(org_data_path, org_id)

        try:
            db_insert.insert_fixed_totalizer()
            db_insert.insert_free_function()
            db_insert.insert_group()
            db_insert.insert_departments()
            db_insert.insert_taxes()
            db_insert.insert_plu()
            db_insert.insert_clerks()
            db_insert.insert_customers()
            db_insert.insert_order_data()

            print("Processed successfully")

        except Exception:
            print("Processed with error:")
            traceback.print_exc()


if __name__ == "__main__":
    main()
