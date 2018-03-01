from sqlalchemy import Table, Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from app import base


"""
Bind users and organizations
"""
users_orgs_association_table = Table("users_orgs_association", base.metadata,
                                     Column("org_id", Integer, ForeignKey("organizations.id", ondelete="CASCADE")),
                                     Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")))


class Organization(base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, index=True)
    data_dir = Column(String(200), unique=True, index=True)
    users = relationship("User",
                         secondary=users_orgs_association_table,
                         back_populates="organizations")
    fixed_totalizers = relationship("FixedTotalizer", cascade="delete")
    free_functions = relationship("FreeFunction", cascade="delete")
    groups = relationship("Group", cascade="delete")
    departments = relationship("Department", cascade="delete")
    mixmatch = relationship("MixMatch", cascade="delete")
    taxes = relationship("Tax", cascade="delete")
    plus = relationship("PLU", cascade="delete")
    plus2nd = relationship("PLU2nd", cascade="delete")
    clerks = relationship("Clerk", cascade="delete")
    customers = relationship("Customer", cascade="delete")
    orders = relationship("Order", cascade="delete")


class Master(base):
    """Base class for Master files data"""
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    date_time = Column(DateTime, nullable=False)
    filepath = Column(String(100), nullable=False)
    data_dir = Column(String(100), nullable=False)


class FixedTotalizer(Master):
    __tablename__ = "fixed_totalizers"

    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    name = Column(String(50))
    orderlines = relationship("OrderLine", back_populates="fixed_totalizer")

    def __repr__(self):
        return "Fixed Totalizer: id=%s number=%s name=%s" % (
                self.id, self.number, self.name)


class FreeFunction(Master):
    __tablename__ = "free_functions"

    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    name = Column(String(50))
    function_number = Column(String(50))
    orderlines = relationship("OrderLine", back_populates="free_function")

    def __repr__(self):
        return "Free Function: id=%s number=%s name=%s" % (
                self.id, self.number, self.name)


class Group(Master):
    __tablename__ = "groups"

    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    name = Column(String(50))
    departments = relationship("Department", back_populates="group")
    plus = relationship("PLU", back_populates="group")
    plus_2nd = relationship("PLU2nd", back_populates="group")

    def __repr__(self):
        return "Group: id=%s number=%s name=%s" % (
                self.id, self.number, self.name)


class Department(Master):
    __tablename__ = "departments"

    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    name = Column(String(50))
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    group = relationship("Group", back_populates="departments")
    plus = relationship("PLU", back_populates="department")
    plus_2nd = relationship("PLU2nd", back_populates="department")

    def __repr__(self):
        return "Department: id=%s number=%s name=%s group_id=%s" % (
                self.id, self.number, self.name, self.group_id)


class MixMatch(Master):
    __tablename__ = "mix_match"

    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    name = Column(String(50))
    operation_type = Column(Integer)
    qty_req = Column(Integer)
    amount = Column(Integer)
    plus = relationship("PLU", backref="plus", lazy="dynamic")

    def __repr__(self):
        return "MixMatch: id=%s number=%s name=%s" % (
            self.id, self.number, self.name)


class Tax(Master):
    __tablename__ = "taxes"

    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    name = Column(String(50))
    rate = Column(Integer)
    plus = relationship("PLU", back_populates="tax")
    plus2nd = relationship("PLU2nd", back_populates="tax")

    def __repr__(self):
        return "Tax: id=%s number=%s name=%s rate=%s" % (
            self.id, self.number, self.name, self.rate)


class PLU(Master):
    __tablename__ = "plu"

    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    name = Column(String(50))
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    group = relationship("Group", back_populates="plus")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    department = relationship("Department", back_populates="plus")
    price = Column(Float)
    tax_id = Column(Integer, ForeignKey("taxes.id"), nullable=True)
    tax = relationship("Tax", uselist=False, back_populates="plus")
    mix_match_id = Column(Integer, ForeignKey("mix_match.id"), nullable=True)
    orderlines = relationship("OrderLine", backref="plu", lazy="dynamic")

    def __repr__(self):
        return "PLU: id=%s name=%s number=%s group_number=%s department_number=%s price=%s" % (
                self.id, self.name, self.number, self.group_id, self.department_id, self.price)


class PLU2nd(Master):
    __tablename__ = "plu_2nd"

    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    name = Column(String(50))
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    group = relationship("Group", back_populates="plus_2nd")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    department = relationship("Department", back_populates="plus_2nd")
    price = Column(Float)
    tax_id = Column(Integer, ForeignKey("taxes.id"), nullable=True)
    tax = relationship("Tax", uselist=False, back_populates="plus2nd")
    orderlines = relationship("OrderLine", backref="plu_2nd", lazy="dynamic")

    def __repr__(self):
        return "PLU2nd: id=%s name=%s number=%s group_number=%s department_number=%s price=%s" % (
                self.id, self.name, self.number, self.group_id, self.department_id, self.price)


class Clerk(Master):
    __tablename__ = "clerks"

    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    name = Column(String(50))
    orders = relationship("Order", back_populates="clerk")

    def __repr__(self):
        return "Clerk: id=%s name=%s" % (self.number, self.name)


class Customer(Master):
    __tablename__ = "customers"

    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    first_name = Column(String(50))
    surname = Column(String(50))
    addr1 = Column(String(100))
    addr2 = Column(String(100))
    addr3 = Column(String(100))
    postcode = Column(String(20))
    phone = Column(String(30))
    email = Column(String(50))
    overdraft_limit = Column(String(20))
    custgroup_number = Column(Integer)
    orders = relationship("Order", backref="customer", lazy="dynamic")

    def __repr__(self):
        return "Customer: id=%s first_name=%s surname=%s" % (self.id, self.first_name, self.surname)


class Order(base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    date_time = Column(DateTime)
    filepath = Column(String(100))
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    mode = Column(String(50))
    consecutive_number = Column(Integer)
    terminal_number = Column(Integer)
    terminal_name = Column(String(50))
    clerk_id = Column(Integer, ForeignKey("clerks.id"))
    clerk = relationship("Clerk", back_populates="orders")
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    table_number = Column(Integer)
    payment_type = Column(String(20))
    items = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return "Order: ID=%s" % (self.id)


class OrderLine(base):
    __tablename__ = "order_lines"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    order = relationship("Order", uselist=False, back_populates="items")
    item_type = Column(Integer, nullable=False)
    qty = Column(Integer, nullable=False)
    value = Column(Float, nullable=False)

    # for item type = 0
    product_id = Column(Integer, ForeignKey("plu.id"), nullable=True)
    product = relationship("PLU")
    mix_match_id = Column(Integer, ForeignKey("mix_match.id"), nullable=True)

    # for item type = 1
    free_func_id = Column(Integer, ForeignKey("free_functions.id"), nullable=True)
    free_function = relationship("FreeFunction", uselist=False, back_populates="orderlines")
    change = Column(Float, nullable=True)  # for cash and cash-related items

    # for item type = 3
    product_id_2nd = Column(Integer, ForeignKey("plu_2nd.id"), nullable=True)
    product_2nd = relationship("PLU2nd")

    # for item type = 4 and 1
    fixed_total_id = Column(Integer, ForeignKey("fixed_totalizers.id"), nullable=True)
    fixed_totalizer = relationship("FixedTotalizer", uselist=False, back_populates="orderlines")

    def __repr__(self):
        return "OrderLine: id=%s order_id=%s product_id=%s qty=%s value=%s mixmatch=%s" % (
                self.id, self.order_id, self.product_id, self.qty, self.value, self.mix_match_id)
