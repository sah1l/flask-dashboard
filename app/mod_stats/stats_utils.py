"""
Helper class for statistics Blueprint.
Handles requests to database and extracts needed information.
Only reads database.
"""

import datetime
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker

from app import db
from app.models import OrderLine, Order


PLU_ITEM_TYPE = 0
FREE_FUNC_ITEM_TYPE = 1
PLU2ND_ITEM_TYPE = 3


def calc_quarter_timerange(quarter, year):
    """
    Calculates months range for given quarter value (1 - 4)

    1 quarter: 01 of January - 31 of March

    2 quarter: 01 of April - 30 of June

    3 quarter: 01 of July - 30 of September

    4 quarter: 01 of October - 31 of December
    """
    if quarter == 1:
        start_month = datetime.datetime.strptime("01/01/{} 00:00:00".format(year), "%d/%m/%Y %H:%M:%S")
        end_month = datetime.datetime.strptime("31/03/{} 23:59:59".format(year), "%d/%m/%Y %H:%M:%S")
    elif quarter == 2:
        start_month = datetime.datetime.strptime("01/04/{} 00:00:00".format(year), "%d/%m/%Y %H:%M:%S")
        end_month = datetime.datetime.strptime("30/06/{} 23:59:59".format(year), "%d/%m/%Y %H:%M:%S")
    elif quarter == 3:
        start_month = datetime.datetime.strptime("01/07/{} 00:00:00".format(year), "%d/%m/%Y %H:%M:%S")
        end_month = datetime.datetime.strptime("30/09/{} 23:59:59".format(year), "%d/%m/%Y %H:%M:%S")
    else:
        start_month = datetime.datetime.strptime("01/10/{} 00:00:00".format(year), "%d/%m/%Y %H:%M:%S")
        end_month = datetime.datetime.strptime("31/12/{} 23:59:59".format(year), "%d/%m/%Y %H:%M:%S")

    return start_month, end_month


def dict_write_values(dictionary, entry_id, name, price, qty):
    """
    Write new values to dictionary.
    Entry's number is a key for top-level structure.
    If this is a new element, creates dictionary structure for it. 
    If this element is present, sums values up with their total values.
    """
    if entry_id in dictionary.keys():
        dictionary[entry_id]["price_sum"] += price
        dictionary[entry_id]["qty_sum"] += qty

    else:
        dictionary[entry_id] = {}
        dictionary[entry_id]["name"] = name
        dictionary[entry_id]["price_sum"] = price
        dictionary[entry_id]["qty_sum"] = qty
    dictionary[entry_id]["price_sum"] = float("{0:.2f}".format(dictionary[entry_id]["price_sum"])) # ATTENTION here
    
    return dictionary


def gross_net_fill_values(dictionary):
    """
    Fills fixed_totalizer dictionary with values for Gross/Net totalizers
    """
    dictionary["Gross"] = {}
    dictionary["Gross"]["name"] = "Gross"
    dictionary["Gross"]["price_sum"] = 0
    dictionary["Gross"]["qty_sum"] = 0
    dictionary["Net"] = {}
    dictionary["Net"]["name"] = "Net"
    dictionary["Net"]["price_sum"] = 0
    dictionary["Net"]["qty_sum"] = 0

    return dictionary


def calculate_gross_net(dictionary, item_type, price, qty):
    """
    Sums up Gross and Net values
    """
    # Calculating Gross
    if item_type == PLU_ITEM_TYPE or item_type == PLU2ND_ITEM_TYPE:
        dictionary["Gross"]["price_sum"] += price
        dictionary["Gross"]["price_sum"] = float("{0:.2f}".format(dictionary["Gross"]["price_sum"])) # ATTENTION here
        dictionary["Gross"]["qty_sum"] += qty
    # Calculating Net
    elif item_type == FREE_FUNC_ITEM_TYPE:
        dictionary["Net"]["price_sum"] += price
        dictionary["Net"]["price_sum"] = float("{0:.2f}".format(dictionary["Net"]["price_sum"])) # ATTENTION here
        dictionary["Net"]["qty_sum"] += qty

    return dictionary


def calculate_vat_net(tax_rate, gross_value_raw):
    """
    Calculates excluded VAT (value-added tax) and Net amount from Gross price:

    1) calculate divider: divider = 1 + tax_rate / 100

    2) calculate raw Net (why raw? it will be used only in calculating VAT, and then rounded according to VAT value):
        raw_net_amount = gross_value / divider

    3) subtract gross value from raw Net amount to get negative and not rounded VAT:
        raw_net_amount - gross_value = - VAT

    4) multiply negative VAT to -1:
        vat = -1 * (-vat)

    5) round VAT to two decimals with half up (last number < 5 to least value, last number > 5 to greatest value)
    
    6) subtract resulted vat from gross to get resulted Net value

    Result precision was compared with this calculator: http://vatcalconline.com/
    """
    gross_value = Decimal(str(gross_value_raw))
    divider = Decimal(1) + Decimal(tax_rate / 100).quantize(Decimal('.01'))
    raw_net_amount = Decimal(gross_value / divider)
    vat = Decimal((-1*(raw_net_amount-gross_value)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
    net_amount = gross_value - vat

    return vat, net_amount


def tax_fill_values(dictionary, tax_name, tax_name_amt, vat, net_amount):
    """
    Creates fixed_totalizer dictionary structure for new tax
    """
    dictionary[tax_name] = {}
    dictionary[tax_name]["name"] = tax_name
    dictionary[tax_name]["price_sum"] = vat
    dictionary[tax_name]["qty_sum"] = 0
    dictionary[tax_name_amt] = {}
    dictionary[tax_name_amt]["name"] = tax_name_amt
    dictionary[tax_name_amt]["price_sum"] = net_amount
    dictionary[tax_name_amt]["qty_sum"] = 0

    return dictionary


class StatsDataExtractor():
    """
    Extracts statistics data from database.
    Handles time frames.
    """
    def __init__(self, start_time, end_time):
        session_maker = sessionmaker(db)
        self.session = session_maker()
        self.start_time = start_time
        self.end_time = end_time
        self.orderlines = self.session.query(OrderLine).join(OrderLine.order).filter(
            and_(
                Order.date_time>=self.start_time, 
                Order.date_time<=self.end_time
                )
            )


    def close_session(self):
        self.session.close()


    def get_department_sales_data(self):
        """
        Get Department sales
        """
        _dict = {}

        for ol in self.orderlines:
            price = ol.value
            qty = ol.qty
            # encounter PLU and PLU2nd
            if ol.item_type == PLU_ITEM_TYPE:
                dep_number = ol.plu.department_number
                dep_name = ol.plu.department.name
            elif ol.item_type == PLU2ND_ITEM_TYPE:
                dep_number = ol.plu_2nd.department_number
                dep_name = ol.plu_2nd.department_name
            else:
                continue
            
            _dict = dict_write_values(_dict, dep_number, dep_name, price, qty)
        
        return _dict


    def get_fixed_totalizers(self): # ATTENTION! NAMES are identifiers here, not Numbers! Consider this
                                    # Include VOID
        _dict = {}
        _dict = gross_net_fill_values(_dict)

        for ol in self.orderlines:
            if ol.free_func_number == 149:  # ATTENTION!!! FIX!!! skip statistics for HOLD items
                continue
            
            qty = ol.qty
            price = ol.value

            if ol.item_type == PLU_ITEM_TYPE or ol.item_type == PLU2ND_ITEM_TYPE:
                if ol.item_type == PLU_ITEM_TYPE:
                    tax_name = ol.plu.tax.name
                    tax_rate = int(ol.plu.tax.rate)
                else:
                    tax_name = ol.plu_2nd.tax.name
                    tax_rate = int(ol.plu_2nd.tax.rate)
                tax_name_amt = tax_name + " AMT"
                vat, net_amount = calculate_vat_net(tax_rate, price)

                if tax_name in _dict.keys():
                    _dict[tax_name]["price_sum"] += vat
                    _dict[tax_name_amt]["price_sum"] += net_amount
                else:
                    tax_fill_values(_dict, tax_name, tax_name_amt, vat, net_amount)

            # there are such free functions as '3 for 2' (Group 3/Order2)
            # that have 1 item type and None free func, also with negative value
            # this value spoils results so check for None there
            elif ol.item_type == FREE_FUNC_ITEM_TYPE and ol.free_func_number is not None:
                ft_name = ol.fixed_totalizer.name
                _dict = dict_write_values(_dict, ft_name, ft_name, price, qty)

            _dict = calculate_gross_net(_dict, ol.item_type, price, qty)

        return _dict



    def get_plu_sales_data(self):
        """
        Get PLU sales
        """
        _dict = {}

        for ol in self.orderlines:
            qty = ol.qty
            price = ol.value
            # encounter PLU and PLU2nd
            if ol.item_type == PLU_ITEM_TYPE:
                product_number = ol.product_number
                product_name = ol.product.name
            elif ol.item_type == PLU2ND_ITEM_TYPE:
                product_number = ol.product_number_2nd
                product_name = ol.product_2nd.name
            else:
                continue

            _dict = dict_write_values(_dict, product_number, product_name, price, qty)

        return _dict


    def get_last_100_sales(self):
        """
        Get last 100 sales
        """
        orders = self.session.query(Order).order_by(Order.date_time.desc()).all()  # add timelines here
        if len(orders) > 100:
            orders = orders[:100]

        _dict = {}

        for order in orders:
            date_time = order.date_time
            sale_id = order.id
            site = "Some restaurant"
            sales_total = 0
            
            for item in order.items:
                sales_total += item.value

            _dict[sale_id] = {}
            _dict[sale_id]["date_time"] = date_time
            _dict[sale_id]["id"] = sale_id
            _dict[sale_id]["site"] = site
            _dict[sale_id]["sales_total"] = sales_total

            _dict[sale_id]["sales_total"] = float("{0:.2f}".format(_dict[sale_id]["sales_total"])) # ATTENTION here

        return _dict


    def get_clerks_breakdown(self):
        """
        Get Clerks breakdown sales
        """
        _dict = {}

        for ol in self.orderlines:
            clerk_name = ol.order.clerk.name
            clerk_number = ol.order.clerk_number
            price = ol.value
            qty = ol.qty
            _dict = dict_write_values(_dict, clerk_number, clerk_name, price, qty)

        return _dict


    def get_group_sales_data(self):
        """
        Get Group sales
        """
        _dict = {}

        for ol in self.orderlines:
            qty = ol.qty
            price = ol.value
            # encounter PLU and PLU2nd
            if ol.item_type == PLU_ITEM_TYPE:
                group_number = ol.plu.group_number
                group_name = ol.plu.group.name
            elif ol.item_type == PLU2ND_ITEM_TYPE:
                group_number = ol.plu_2nd.group_number
                group_name = ol.plu_2nd.group_name
            else:
                continue

            _dict = dict_write_values(_dict, group_number, group_name, price, qty)

        return _dict


    def get_free_func(self):
        """
        Get Free functions data
        """
        _dict = {}

        for ol in self.orderlines:
            ff_number = ol.free_func_number
            if ff_number is None:
                continue 

            ff_name = ol.free_function.name
            if ff_name == "HOLD":  # skip statistics for HOLD items
                continue

            qty = ol.qty
            price = ol.value

            if ff_name == "VOID":  # VOID has negative values, so convert them to positive
                qty = abs(qty)
                price = abs(price)

            _dict = dict_write_values(_dict, ff_number, ff_name, price, qty)

        return _dict
