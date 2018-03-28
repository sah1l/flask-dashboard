from flask_login import UserMixin
# from sqlalchemy import Table, Column, String, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


# Bind users and organizations
users_orgs_association_table = db.Table("users_orgs_association",
                                        db.Column("org_id",
                                                  db.Integer,
                                                  db.ForeignKey("organizations.id", ondelete="CASCADE")),
                                        db.Column("user_id",
                                                  db.Integer,
                                                  db.ForeignKey("users.id", ondelete="CASCADE")))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    organizations = db.relationship("Organization",
                                 secondary=users_orgs_association_table,
                                 back_populates="users")

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    user_id = db.session.query(User).get(int(id))

    return user_id


class Organization(db.Model):
    __tablename__ = "organizations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, index=True)
    data_dir = db.Column(db.String(200), unique=True, index=True)
    users = db.relationship("User",
                         secondary=users_orgs_association_table,
                         back_populates="organizations")
    fixed_totalizers = db.relationship("FixedTotalizer", cascade="delete")
    free_functions = db.relationship("FreeFunction", cascade="delete")
    groups = db.relationship("Group", cascade="delete")
    departments = db.relationship("Department", cascade="delete")
    taxes = db.relationship("Tax", cascade="delete")
    plus = db.relationship("PLU", cascade="delete")
    clerks = db.relationship("Clerk", cascade="delete")
    customers = db.relationship("Customer", cascade="delete")
    orders = db.relationship("Order", cascade="delete")


class Master(db.Model):
    """Base class for Master files data (abstract class, not a table)"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    date_time = db.Column(db.DateTime, nullable=False)
    filepath = db.Column(db.String(100), nullable=False)
    data_dir = db.Column(db.String(100), nullable=False)


class FixedTotalizer(Master):
    __tablename__ = "fixed_totalizers"

    org_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"))
    name = db.Column(db.String(50))
    orderlines = relationship("OrderLine", back_populates="fixed_totalizer")

    def __repr__(self):
        return "Fixed Totalizer: id=%s number=%s name=%s" % (
                self.id, self.number, self.name)


class FreeFunction(Master):
    __tablename__ = "free_functions"

    org_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"))
    name = db.Column(db.String(50))
    function_number = db.Column(db.String(50))
    orderlines = relationship("OrderLine", back_populates="free_function")

    def __repr__(self):
        return "Free Function: id=%s number=%s name=%s" % (
                self.id, self.number, self.name)


class Group(Master):
    __tablename__ = "groups"

    org_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"))
    name = db.Column(db.String(50))
    departments = relationship("Department", back_populates="group")
    plus = relationship("PLU", back_populates="group")

    def __repr__(self):
        return "Group: id=%s number=%s name=%s" % (
                self.id, self.number, self.name)


class Department(Master):
    __tablename__ = "departments"

    org_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"))
    name = db.Column(db.String(50))
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=True)
    group = relationship("Group", back_populates="departments")
    plus = relationship("PLU", back_populates="department")

    def __repr__(self):
        return "Department: id=%s number=%s name=%s group_id=%s" % (
                self.id, self.number, self.name, self.group_id)


class Tax(Master):
    __tablename__ = "taxes"

    org_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"))
    name = db.Column(db.String(50))
    rate = db.Column(db.Integer)
    plus = relationship("PLU", back_populates="tax")

    def __repr__(self):
        return "Tax: id=%s number=%s name=%s rate=%s" % (
            self.id, self.number, self.name, self.rate)


class PLU(Master):
    __tablename__ = "plu"

    org_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"))
    name = db.Column(db.String(50))
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=True)
    group = relationship("Group", back_populates="plus")
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)
    department = relationship("Department", back_populates="plus")
    price = db.Column(db.Float)
    tax_id = db.Column(db.Integer, db.ForeignKey("taxes.id"), nullable=True)
    tax = relationship("Tax", uselist=False, back_populates="plus")
    orderlines = relationship("OrderLine", backref="plu", lazy="dynamic")

    def __repr__(self):
        return "PLU: id=%s name=%s number=%s group_number=%s department_number=%s price=%s" % (
                self.id, self.name, self.number, self.group_id, self.department_id, self.price)


class Clerk(Master):
    __tablename__ = "clerks"

    org_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"))
    name = db.Column(db.String(50))
    orders = relationship("Order", back_populates="clerk")

    def __repr__(self):
        return "Clerk: id=%s name=%s" % (self.number, self.name)


class Customer(Master):
    __tablename__ = "customers"

    org_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"))
    first_name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    addr1 = db.Column(db.String(100))
    addr2 = db.Column(db.String(100))
    addr3 = db.Column(db.String(100))
    postcode = db.Column(db.String(20))
    phone = db.Column(db.String(30))
    email = db.Column(db.String(50))
    overdraft_limit = db.Column(db.String(20))
    custgroup_number = db.Column(db.Integer)
    orders = relationship("Order", backref="customer", lazy="dynamic")

    def __repr__(self):
        return "Customer: id=%s first_name=%s surname=%s" % (self.id, self.first_name, self.surname)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime)
    filepath = db.Column(db.String(100))
    org_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"))
    mode = db.Column(db.String(50))
    consecutive_number = db.Column(db.Integer)
    terminal_number = db.Column(db.Integer)
    terminal_name = db.Column(db.String(50))
    clerk_id = db.Column(db.Integer, db.ForeignKey("clerks.id"))
    clerk = relationship("Clerk", back_populates="orders")
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True)
    table_number = db.Column(db.Integer)
    payment_type = db.Column(db.String(20))
    items = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return "Order: ID=%s" % (self.id)


class OrderLine(db.Model):
    __tablename__ = "order_lines"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    order = relationship("Order", uselist=False, back_populates="items")
    item_type = db.Column(db.Integer, nullable=False)
    func_number = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(50))
    qty = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Float, nullable=False)

    # for item type = 0 and 3 (PLU and PLU 2nd)
    product_id = db.Column(db.Integer, db.ForeignKey("plu.id"), nullable=True)
    product = relationship("PLU")

    # for item type = 1 (Free Functions)
    free_func_id = db.Column(db.Integer, db.ForeignKey("free_functions.id"), nullable=True)
    free_function = relationship("FreeFunction", uselist=False, back_populates="orderlines")
    change = db.Column(db.Float, nullable=True)  # for cash and cash-related items

    # for item type = 4 and 1 (Fixed Totalizers and Free Functions)
    fixed_total_id = db.Column(db.Integer, db.ForeignKey("fixed_totalizers.id"), nullable=True)
    fixed_totalizer = relationship("FixedTotalizer", uselist=False, back_populates="orderlines")

    def __repr__(self):
        return "OrderLine: id=%s order_id=%s product_id=%s qty=%s value=%s" % (
                self.id, self.order_id, self.product_id, self.qty, self.value)
