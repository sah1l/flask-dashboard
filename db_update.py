"""
Connects to database and adds new data from XML files
"""

from sqlalchemy.orm import sessionmaker

from app import db, base
from app.models import FixedTotalizer, FreeFunction, Department, Group, PLU, Clerk, Customer, \
                        MixMatch, Order, OrderLine, PLU2nd, Tax
from app.mod_db_manage.xml_parser import get_orders_gen, get_order_items_gen, get_fixed_total_gen, get_free_func_gen, \
                        get_department_gen, get_group_gen, get_plu_gen, get_clerk_gen, get_customer_gen, \
                        get_mixmatch_gen, get_plu2nd_gen, get_tax_gen


MAGIC_INDRAWER_NUMBER = 3  # a number to calculate in-drawer records


class DBInsert:
    """
    Inserts new data from XML files to database
    """
    def __init__(self, _session_maker):
        self.session = _session_maker()

    def create_all_tables(self, _db):
        base.metadata.create_all(_db)

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
        fixed_totalizers = get_fixed_total_gen()

        for ft in fixed_totalizers:
            ft_duplicate = self.db_check_duplicate(FixedTotalizer, number=ft.number)
            if ft_duplicate:
                continue

            db_ft = FixedTotalizer(number=ft.number,
                                   date_time=ft.date_time,
                                   filepath=ft.filepath,
                                   data_dir=ft.data_dir,
                                   name=ft.name
                                   )
            self.session.add(db_ft)
            self.session.commit()
            print(db_ft)

    def insert_free_function(self):
        free_functions = get_free_func_gen()

        for ff in free_functions:
            ff_duplicate = self.db_check_duplicate(FreeFunction, number=ff.number)
            if ff_duplicate:
                continue

            db_ff = FreeFunction(number=ff.number,
                                 date_time=ff.date_time,
                                 filepath=ff.filepath,
                                 data_dir=ff.data_dir,
                                 name=ff.name,
                                 function_number=ff.function_number
                                 )
            self.session.add(db_ff)
            self.session.commit()
            print(db_ff)

    def insert_group(self):
        groups = get_group_gen()

        for group in groups:
            group_duplicate = self.db_check_duplicate(Group, number=group.number)
            if group_duplicate:
                continue

            db_group = Group(number=group.number,
                             date_time=group.date_time,
                             filepath=group.filepath,
                             data_dir=group.data_dir,
                             name=group.name,
                             )
            self.session.add(db_group)
            self.session.commit()
            print(db_group)

    def insert_departments(self):
        departments = get_department_gen()

        for dep in departments:
            dep_duplicate = self.db_check_duplicate(Department, number=dep.number)
            if dep_duplicate:
                continue

            # check for group with non-existing number
            valid_group = self.session.query(Group).filter_by(number=dep.group_number).first()
            if not valid_group:
                dep.group_number = None

            db_dep = Department(number=dep.number,
                                date_time=dep.date_time,
                                filepath=dep.filepath,
                                data_dir=dep.data_dir,
                                name=dep.name,
                                group_number=dep.group_number
                                )
            self.session.add(db_dep)
            print(db_dep)

    def insert_mixmatch(self):
        mixmatch = get_mixmatch_gen()

        for mm in mixmatch:
            mm_duplicate = self.db_check_duplicate(MixMatch, number=mm.number)
            if mm_duplicate:
                continue

            db_mm = MixMatch(number=mm.number,
                             date_time=mm.date_time,
                             filepath=mm.filepath,
                             data_dir=mm.data_dir,
                             name=mm.name,
                             operation_type=mm.operation_type,
                             qty_req=mm.qty_req,
                             amount=mm.amount
                             )
            self.session.add(db_mm)
            self.session.commit()
            print(db_mm)

    def insert_taxes(self):
        taxes = get_tax_gen()

        for tax in taxes:
            tax_duplicate = self.db_check_duplicate(Tax, number=tax.number)
            if tax_duplicate:
                continue

            db_tax = Tax(number=tax.number,
                         date_time=tax.date_time,
                         filepath=tax.filepath,
                         data_dir=tax.data_dir,
                         name=tax.name,
                         rate=tax.rate
                         )
            self.session.add(db_tax)
            self.session.commit()
            print(db_tax)

    def insert_plu(self):
        plu_s = get_plu_gen()

        for plu in plu_s:
            plu_duplicate = self.db_check_duplicate(PLU, number=plu.number)
            if plu_duplicate:
                continue

            # check for group, department and mixmatch with non-existing number
            valid_group = self.session.query(Group).filter_by(number=plu.group_number).first()
            if not valid_group:
                plu.group_number = None

            valid_dep = self.session.query(Department).filter_by(number=plu.department_number).first()
            if not valid_dep:
                plu.department_number = None

            valid_mixmatch = self.session.query(MixMatch).filter_by(number=plu.mix_match).first()
            if not valid_mixmatch:
                plu.mix_match = None

            valid_tax = self.session.query(Tax).filter_by(number=plu.tax_number).first()
            if not valid_tax:
                plu.tax_number = None

            db_plu = PLU(number=plu.number,
                         date_time=plu.date_time,
                         filepath=plu.filepath,
                         data_dir=plu.data_dir,
                         name=plu.name,
                         group_number=plu.group_number,
                         department_number=plu.department_number,
                         price=plu.price,
                         tax_number=plu.tax_number,
                         mix_match=plu.mix_match
                         )
            self.session.add(db_plu)
            self.session.commit()
            print(db_plu)

    def insert_plu_2nd(self):
        plu_s = get_plu2nd_gen()

        for plu in plu_s:
            plu_duplicate = self.db_check_duplicate(PLU2nd, number=plu.number)
            if plu_duplicate:
                continue

            # check for group and department with non-existing number
            valid_group = self.session.query(Group).filter_by(number=plu.group_number).first()
            if not valid_group:
                plu.group_number = None

            valid_dep = self.session.query(Department).filter_by(number=plu.department_number).first()
            if not valid_dep:
                plu.department_number = None

            valid_tax = self.session.query(Tax).filter_by(number=plu.tax_number).first()
            if not valid_tax:
                plu.tax_number = None

            db_plu = PLU2nd(number=plu.number,
                            date_time=plu.date_time,
                            filepath=plu.filepath,
                            data_dir=plu.data_dir,
                            name=plu.name,
                            group_number=plu.group_number,
                            department_number=plu.department_number,
                            price=plu.price,
                            tax_number=plu.tax_number
                            )
            self.session.add(db_plu)
            self.session.commit()
            print(db_plu)

    def insert_clerks(self):
        clerks = get_clerk_gen()

        for clerk in clerks:
            clerk_duplicate = self.db_check_duplicate(Clerk, number=clerk.number)
            if clerk_duplicate:
                continue

            db_clerk = Clerk(number=clerk.number,
                             date_time=clerk.date_time,
                             filepath=clerk.filepath,
                             data_dir=clerk.data_dir,
                             name=clerk.name
                             )
            self.session.add(db_clerk)
            self.session.commit()
            print(db_clerk)

    def insert_customers(self):
        customers = get_customer_gen()

        for customer in customers:
            customer_duplicate = self.db_check_duplicate(Customer, number=customer.number)
            if customer_duplicate:
                continue

            db_customer = Customer(number=customer.number,
                                   date_time=customer.date_time,
                                   filepath=customer.filepath,
                                   data_dir=customer.data_dir,
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

    def customize_orderline_plu(self, order_item, db_orderline):
        """Customize OrderLine object with PLU details (for ItemType = 0)"""
        db_orderline.product_number = order_item.item_number
        db_orderline.mix_match_number = self.session.query(PLU).filter_by(number=db_orderline.product_number).first().mix_match

        return db_orderline

    def customize_orderline_freefunc(self, order_item, db_orderline):
        """Customize OrderLine object with FreeFunction details (for ItemType = 1)"""
        valid_ffunc = self.session.query(FreeFunction).filter_by(number=order_item.item_number).first()
        
        if not valid_ffunc:
            db_orderline.free_func_number = None
        else:
            db_orderline.free_func_number = order_item.item_number

        # for counting CAID, CRID, CHID and CQID (id-drawers)
        db_orderline.fixed_total_number = int(order_item.option[-1]) + MAGIC_INDRAWER_NUMBER
        return db_orderline

    def customize_orderline_plu_2nd(self, order_item, db_orderline):
        db_orderline.product_number_2nd = order_item.item_number
        return db_orderline

    def customize_orderline_fixedtotal(self, order_item, db_orderline):
        """Customize OrderLine object with FixedTotalizer details (for ItemType = 4)"""
        # db_orderline.fixed_total_number = order_item.item_number
        db_orderline.fixed_total_number = self.session.query(FixedTotalizer.number).filter_by(name=order_item.name).first()
        return db_orderline

    def insert_order_data(self):
        orders = get_orders_gen()

        for order in orders:
            order_duplicate = self.db_check_duplicate(Order,
                                                      consecutive_number=order.consecutive_number,
                                                      date_time=order.date_time
                                                      )
            if order_duplicate:
                continue

            db_order = Order(date_time=order.date_time,
                             filepath=order.filepath,
                             mode=order.mode,
                             consecutive_number=order.consecutive_number,
                             terminal_number=order.terminal_number,
                             terminal_name=order.terminal_name,
                             clerk_number=order.clerk_number,
                             customer_number=order.customer_number,
                             table_number=order.table_number
                             )
            self.session.add(db_order)
            self.session.commit()
            order_items = list(get_order_items_gen(db_order.filepath))

            for ol_num, order_item in enumerate(order_items):
                db_orderline = OrderLine()
                db_orderline.order_id = db_order.id
                db_orderline.qty = order_item.qty

                # work with negative quantity
                # add free function VOID
                if int(order_item.qty) < 0:
                    db_orderline.free_func_number = 141

                db_orderline.value = order_item.value
                db_orderline.item_type = order_item.item_type

                if order_item.item_type == "0":
                    db_orderline = self.customize_orderline_plu(order_item, db_orderline)
                    
                elif order_item.item_type == "1":
                    db_orderline = self.customize_orderline_freefunc(order_item, db_orderline)

                    # check if item has a change (for cash-type free functions)
                    if "CASH" in order_item.name:
                        if ol_num < len(order_items) - 1:
                            next_item = order_items[ol_num+1]
                            if next_item.item_type == "2" and next_item.name == "CHANGE":
                                db_orderline.value = float(order_item.value) - float(next_item.value)
                                db_orderline.change = next_item.value
                            else:
                                pass
                    else:
                        pass

                elif order_item.item_type == "3":
                    db_orderline = self.customize_orderline_plu_2nd(order_item, db_orderline)
                
                elif order_item.item_type == "4":
                    db_orderline = self.customize_orderline_fixedtotal(order_item, db_orderline)
                
                else:
                    continue

                self.session.add(db_orderline)
                self.session.commit()


if __name__ == "__main__":
    session_maker = sessionmaker(db)
    db_insert = DBInsert(session_maker)
    db_insert.create_all_tables(db)

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

    db_insert.close_session()

