"""
Connects to database and adds new data from XML files
"""
from sqlalchemy.orm import sessionmaker
import traceback

from app import db, base
from app.models import Organization, FixedTotalizer, FreeFunction, Department, Group, PLU, PLU2nd, MixMatch, Tax, \
                        Clerk, Customer, Order, OrderLine
from app.mod_db_manage.xml_parser import get_orders_gen, get_order_items_gen, extract_master_files_data
from app.mod_db_manage.config import *
from app.mod_db_manage.utils import check_group_dirs, check_master_files_dirs, DATATYPES_NAMES


class DBInsert:
    """
    Inserts new data from XML files to database
    New instance is created for each valid Group directory of organization directory
    """
    def __init__(self, session_maker, org_dir, org_id):
        self.session = session_maker()
        self.org_dir = org_dir
        self.org_id = org_id

    def create_all_tables(self):
        base.metadata.create_all(db)

    def db_check_duplicate(self, classname, **kwargs):
        """
        Try to find an entry's duplicate in database
        """
        duplicate = self.session.query(classname).filter_by(**kwargs).first()

        if duplicate:
            return True
        else:
            return False

    def close_session(self):
        self.session.close()

    def insert_fixed_totalizer(self):
        fixed_totalizers = extract_master_files_data(self.org_dir, DATATYPES_NAMES["fixed_totalizer"])

        for ft in fixed_totalizers:
            ft_duplicate = self.db_check_duplicate(FixedTotalizer, number=ft.number, org_id=self.org_id)
            if ft_duplicate:
                continue

            db_ft = FixedTotalizer(number=ft.number,
                                   date_time=ft.date_time,
                                   filepath=ft.filepath,
                                   data_dir=ft.data_dir,
                                   org_id=self.org_id,
                                   name=ft.name
                                   )
            self.session.add(db_ft)
            self.session.commit()
            print(db_ft)

    def insert_free_function(self):
        free_functions = extract_master_files_data(self.org_dir, DATATYPES_NAMES["free_function"])

        for ff in free_functions:
            ff_duplicate = self.db_check_duplicate(FreeFunction, number=ff.number, org_id=self.org_id)
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
            self.session.add(db_ff)
            self.session.commit()
            print(db_ff)

    def insert_group(self):
        groups = extract_master_files_data(self.org_dir, DATATYPES_NAMES["group_name"])

        for group in groups:
            group_duplicate = self.db_check_duplicate(Group, number=group.number, org_id=self.org_id)
            if group_duplicate:
                continue

            db_group = Group(number=group.number,
                             date_time=group.date_time,
                             filepath=group.filepath,
                             data_dir=group.data_dir,
                             org_id=self.org_id,
                             name=group.name,
                             )
            self.session.add(db_group)
            self.session.commit()
            print(db_group)

    def insert_departments(self):
        departments = extract_master_files_data(self.org_dir, DATATYPES_NAMES["department_name"])

        for dep in departments:
            dep_duplicate = self.db_check_duplicate(Department, number=dep.number, org_id=self.org_id)
            if dep_duplicate:
                continue

            # check for group with non-existing number
            valid_group = self.session.query(Group).filter_by(number=dep.group_number).first()
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
            self.session.add(db_dep)
            self.session.commit()
            print(db_dep)

    def insert_mixmatch(self):
        mixmatch = extract_master_files_data(self.org_dir, DATATYPES_NAMES["mixmatch_name"])

        for mm in mixmatch:
            mm_duplicate = self.db_check_duplicate(MixMatch, number=mm.number, org_id=self.org_id)
            if mm_duplicate:
                continue

            db_mm = MixMatch(number=mm.number,
                             date_time=mm.date_time,
                             filepath=mm.filepath,
                             data_dir=mm.data_dir,
                             org_id=self.org_id,
                             name=mm.name,
                             operation_type=mm.operation_type,
                             qty_req=mm.qty_req,
                             amount=mm.amount
                             )
            self.session.add(db_mm)
            self.session.commit()
            print(db_mm)

    def insert_taxes(self):
        taxes = extract_master_files_data(self.org_dir, DATATYPES_NAMES["tax_name"])

        for tax in taxes:
            tax_duplicate = self.db_check_duplicate(Tax, number=tax.number, org_id=self.org_id)
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
            self.session.add(db_tax)
            self.session.commit()
            print(db_tax)

    def insert_plu(self):
        plu_s = extract_master_files_data(self.org_dir, DATATYPES_NAMES["plu_name"])

        for plu in plu_s:
            plu_duplicate = self.db_check_duplicate(PLU, number=plu.number, org_id=self.org_id)
            if plu_duplicate:
                continue

            # check for group, department and mixmatch with non-existing number
            valid_group = self.session.query(Group).filter_by(number=plu.group_number).first()
            if not valid_group:
                plu.group_id = None
            else:
                plu.group_id = valid_group.id

            valid_dep = self.session.query(Department).filter_by(number=plu.department_number).first()
            if not valid_dep:
                plu.department_id = None
            else:
                plu.department_id = valid_dep.id

            valid_mixmatch = self.session.query(MixMatch).filter_by(number=plu.mix_match_number).first()
            if not valid_mixmatch:
                plu.mix_match_id = None
            else:
                plu.mix_match_id = valid_mixmatch.id

            valid_tax = self.session.query(Tax).filter_by(number=plu.tax_number).first()
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
                         mix_match_id=plu.mix_match_id
                         )
            self.session.add(db_plu)
            self.session.commit()
            print(db_plu)

    def insert_plu_2nd(self):
        plu_s = extract_master_files_data(self.org_dir, DATATYPES_NAMES["plu2nd_name"])

        for plu in plu_s:
            plu_duplicate = self.db_check_duplicate(PLU2nd, number=plu.number, org_id=self.org_id)
            if plu_duplicate:
                continue

            # check for group and department with non-existing number
            valid_group = self.session.query(Group).filter_by(number=plu.group_number).first()
            if not valid_group:
                plu.group_id = None
            else:
                plu.group_id = valid_group.id

            valid_dep = self.session.query(Department).filter_by(number=plu.department_number).first()
            if not valid_dep:
                plu.department_id = None
            else:
                plu.department_id = valid_dep.id

            # valid_tax = self.session.query(Tax).filter_by(number=plu.tax_number).first()
            # if not valid_tax:
            #     plu.tax_number = None

            db_plu = PLU2nd(number=plu.number,
                            date_time=plu.date_time,
                            filepath=plu.filepath,
                            data_dir=plu.data_dir,
                            org_id=self.org_id,
                            name=plu.name,
                            group_id=plu.group_id,
                            department_id=plu.department_id,
                            price=plu.price,
                            # tax_number=plu.tax_number
                            )
            self.session.add(db_plu)
            self.session.commit()
            print(db_plu)

    def insert_clerks(self):
        clerks = extract_master_files_data(self.org_dir, DATATYPES_NAMES["clerk_name"])

        for clerk in clerks:
            clerk_duplicate = self.db_check_duplicate(Clerk, number=clerk.number, org_id=self.org_id)
            if clerk_duplicate:
                continue

            db_clerk = Clerk(number=clerk.number,
                             date_time=clerk.date_time,
                             filepath=clerk.filepath,
                             data_dir=clerk.data_dir,
                             org_id=self.org_id,
                             name=clerk.name
                             )
            self.session.add(db_clerk)
            self.session.commit()
            print(db_clerk)

    def insert_customers(self):
        customers = extract_master_files_data(self.org_dir, DATATYPES_NAMES["customer_name"])

        for customer in customers:
            customer_duplicate = self.db_check_duplicate(Customer, number=customer.number, org_id=self.org_id)
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
            self.session.add(db_customer)
            self.session.commit()
            print(db_customer)

    def customize_orderline_plu(self, db_orderline, plu_number):
        """
        Customize OrderLine object with PLU details (for ItemType = 0)
        """
        db_orderline.product_id = self.session.query(PLU).filter_by(number=plu_number).first().id
        db_orderline.mix_match_id = self.session.query(PLU).filter_by(number=plu_number).first().mix_match_id

        return db_orderline

    def customize_orderline_freefunc(self, order_item, db_orderline):
        """
        Customize OrderLine object with FreeFunction details (for ItemType = 1)
        """
        valid_ffunc = self.session.query(FreeFunction).filter_by(number=order_item.item_number).first()

        if not valid_ffunc:
            db_orderline.free_func_id = None
        else:
            db_orderline.free_func_id = valid_ffunc.id

        # for counting CAID, CRID, CHID and CQID (id-drawers)
        fixed_total_number = int(order_item.option[-1]) + MAGIC_INDRAWER_NUMBER
        fixed_total = self.session.query(FixedTotalizer).filter_by(number=fixed_total_number).first()
        db_orderline.fixed_total_id = fixed_total.id

        return db_orderline

    def customize_orderline_plu_2nd(self, db_orderline, plu2nd_number):
        db_orderline.product_id_2nd = self.session.query(PLU2nd).filter_by(number=plu2nd_number).first().id

        return db_orderline

    def customize_orderline_fixedtotal(self, order_item, db_orderline):
        """Customize OrderLine object with FixedTotalizer details (for ItemType = 4)"""
        db_orderline.fixed_total_id = self.session.query(FixedTotalizer).filter_by(name=order_item.name).first().id

        return db_orderline

    def get_order_lines(self, db_order, order_lines):
        """
        Insert order lines of particular order to database
        :param db_order: Order object
        :param order_lines:
        """
        for ol_num, order_item in enumerate(order_lines):
            db_orderline = OrderLine()
            db_orderline.order_id = db_order.id
            db_orderline.qty = order_item.qty

            # work with negative quantity
            # add free function VOID
            if int(order_item.qty) < 0:
                void_free_function = session.query(FreeFunction).filter_by(org_id=self.org_id, name='VOID').first()
                db_orderline.free_func_number = void_free_function.id

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
                db_orderline = self.customize_orderline_plu_2nd(db_orderline, order_item.item_number)

            # process Fixed totalizer-type item
            elif order_item.item_type == str(FIXED_TOTAL_TYPE):
                db_orderline = self.customize_orderline_fixedtotal(order_item, db_orderline)

            else:
                continue

            self.session.add(db_orderline)
            self.session.commit()

    def insert_order_data(self):
        """
        Insert orders to database
        """
        orders = get_orders_gen(self.org_dir)

        for order in orders:
            order_duplicate = self.db_check_duplicate(Order,
                                                      consecutive_number=order.consecutive_number,
                                                      date_time=order.date_time,
                                                      org_id=self.org_id)
            if order_duplicate:
                continue

            # get clerk id
            valid_clerk = self.session.query(Clerk).filter_by(number=order.clerk_number, org_id=self.org_id).first()
            if not valid_clerk:
                clerk_id = None
            else:
                clerk_id = valid_clerk.id

            # get customer id
            valid_customer = self.session.query(Customer).filter_by(
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
            self.session.add(db_order)
            self.session.commit()

            # process order lines
            order_lines = list(get_order_items_gen(db_order.filepath))
            self.get_order_lines(db_order, order_lines)


if __name__ == "__main__":
    session_maker = sessionmaker(db)
    base.metadata.create_all(db)

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

        session = session_maker()
        org_id = session.query(Organization.id).filter_by(data_dir=org_dir).first()
        session.close()

        # check if there is no existing organization for this directory
        if not org_id:
            print('Organization with directory "{}" was not found. Abort.'.format(org_dir))
            continue

        db_insert = DBInsert(session_maker, org_data_path, org_id)
        # db_insert.create_all_tables()

        try:
            db_insert.insert_fixed_totalizer()
            db_insert.insert_free_function()
            db_insert.insert_group()
            db_insert.insert_departments()
            db_insert.insert_mixmatch()
            db_insert.insert_taxes()
            db_insert.insert_plu()
            db_insert.insert_plu_2nd()
            db_insert.insert_clerks()
            db_insert.insert_customers()
            db_insert.insert_order_data()

            print("Processed successfully")

        except Exception:
            print("Processed with error:")
            traceback.print_exc()

        db_insert.close_session()

    # session = session_maker()
    # user = User(username="admin", email="admin@mail.com", is_admin=True)
    # user.set_password("12345")
    # session.add(user)
    # session.commit()
    # session.close()
