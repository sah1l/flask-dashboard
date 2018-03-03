"""
Helper class for statistics Blueprint.
Handles requests to database and extracts needed information.
Only reads database.
"""

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker

from app import db
from app.models import OrderLine, Order, Organization
from app.mod_db_manage.config import FREE_FUNC_ITEM_TYPE, PLU_ITEM_TYPE, PLU2ND_ITEM_TYPE


def calc_today_timeframe():
    """
    Return timeframes for "today"
    Start: <today> 00:00:00
    End: <today> 23:59:59
    :return: datetime object for starting point, datetime object for ending point
    """
    now_time = datetime.datetime.utcnow()
    start_time = now_time.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = now_time.replace(hour=23, minute=59, second=59)

    return start_time, end_time


def calc_yesterday_timeframe():
    """
    Return timeframes for "yesterday"
    Start: <yesterday> 00:00:00
    End: <yesterday> 23:59:59
    :return: datetime object for starting point, datetime object for ending point
    """
    yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    end_time = yesterday.replace(hour=23, minute=59, second=59, microsecond=0)  # 23:59:59 of the day
    start_time = end_time - datetime.timedelta(days=1) + datetime.timedelta(seconds=1)  # 00:00:00 of the day

    return start_time, end_time


def calc_this_week_timeframe():
    """
    Return timeframes for "this week"
    Start: Monday of <current week> 00:00:00
    End: Sunday of <current week> 23:59:59
    :return: datetime object for starting point, datetime object for ending point
    """
    curr_weekday = datetime.datetime.utcnow()

    for day in range(7):
        end_weekday = curr_weekday + datetime.timedelta(days=day)
        if end_weekday.weekday() == 6:
            break

    end_weekday = end_weekday.replace(hour=23, minute=59, second=59)
    start_weekday = end_weekday - datetime.timedelta(days=6)
    start_weekday = start_weekday.replace(hour=0, minute=0, second=0, microsecond=0)

    return start_weekday, end_weekday


def calc_last_week_timeframe():
    """
    Return timeframes for "last week"
    Start: Monday of <last week> 00:00:00
    End: Sunday of <last week> 23:59:59
    :return: datetime object for starting point, datetime object for ending point
    """
    last_weekday = datetime.datetime.utcnow() - datetime.timedelta(days=7)

    for day in range(7):
        start_weekday = last_weekday - datetime.timedelta(days=day)
        if start_weekday.weekday() == 0:
            break

    start_weekday = start_weekday.replace(hour=0, minute=0, second=0, microsecond=0)
    end_weekday = start_weekday + datetime.timedelta(days=6)
    end_weekday = end_weekday.replace(hour=23, minute=59, second=59)

    return start_weekday, end_weekday


def calc_this_month_timeframe():
    """
    Return timeframe for "this month"
    Start: First day of <current month> 00:00:00
    End: Last day of <current month> 23:59:59
    :return: datetime object for starting point, datetime object for ending point
    """
    today = datetime.datetime.utcnow()
    curr_month = today.month

    for day in range(31):
        end_month_day = today + datetime.timedelta(days=day)
        if end_month_day.month != curr_month:
            end_month_day = end_month_day - datetime.timedelta(days=1)
            end_month_day = end_month_day.replace(hour=23, minute=59, second=59)
            break

    start_month_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    return start_month_day, end_month_day


def calc_last_month_timeframe():
    """
    Return timeframe for "last month"
    Start: First day of <last month> 00:00:00
    End: Last day of <last month> 23:59:59
    :return: datetime object for starting point, datetime object for ending point
    """
    last_month_day = datetime.datetime.utcnow() - relativedelta(months=1)
    last_month = last_month_day.month
    start_last_month_day = last_month_day.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    for day in range(31):
        end_last_month_day = last_month_day + datetime.timedelta(days=day)
        if end_last_month_day.month != last_month:
            end_last_month_day = end_last_month_day - datetime.timedelta(days=1)
            end_last_month_day = end_last_month_day.replace(hour=23, minute=59, second=59)
            break

    return start_last_month_day, end_last_month_day


def match_dates_and_quarter(quarter, year):
    """
    Help function.
    Calculates months range for given quarter value (1 - 4)

    1 quarter: 01 of January - 31 of March

    2 quarter: 01 of April - 30 of June

    3 quarter: 01 of July - 30 of September

    4 quarter: 01 of October - 31 of December

    :return: datetime object for starting point, datetime object for ending point (according to quarter)
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


def calc_this_quarter_timeframe():
    """
    Returns timeframe for <this quarter>
    Start: 00:00:00 of <this quarter's start month>
    End: 23:59:59 of <this quarter's end month>
    :return: datetime object for starting point, datetime object for ending point
    """
    now_time = datetime.datetime.utcnow()
    this_year = str(now_time.year)
    this_quarter = (now_time.month - 1) // 3 + 1  # integer value from 0 to 3 that represents a quarter of the year
    start_month, end_month = match_dates_and_quarter(this_quarter, this_year)

    return start_month, end_month


def calc_last_quarter_timeframe():
    """
    Returns timeframe for <last quarter>
    Start: 00:00:00 of <last quarter's start month>
    End: 23:59:59 of <last quarter's end month>
    :return: datetime object for starting point, datetime object for ending point
    """
    lq_time = datetime.datetime.utcnow() - relativedelta(months=3)
    lq_year = str(lq_time.year)
    last_quarter = (lq_time.month - 1) // 3 + 1  # integer value from 0 to 3 that represents a quarter of the year
    start_month, end_month = match_dates_and_quarter(last_quarter, lq_year)

    return start_month, end_month


def dict_write_values(dictionary, entry_id, name, price, qty):
    """
    Write new values to dictionary.
    Entry's number is a key for top-level structure.
    If this is a new element, creates dictionary structure for it. 
    If this element is present, sums values up with their total values.
    """
    price = PriceValue(price).get_value()

    if entry_id in dictionary.keys():
        dictionary[entry_id]["price_sum"] += price
        dictionary[entry_id]["qty_sum"] += qty
    else:
        dictionary[entry_id] = {}
        dictionary[entry_id]["name"] = name
        dictionary[entry_id]["price_sum"] = price
        dictionary[entry_id]["qty_sum"] = qty

    dictionary[entry_id]["price_sum"] = PriceValue(dictionary[entry_id]["price_sum"]).round_half_up() # ATTENTION here
    
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


def accumulate_gross_net(dictionary, item_type, price, qty):
    """
    Sums up Gross and Net values

    How Gross is calculated:

    - if item type is PLU or PLU 2nd, accumulate price

    How Net is calculated:

    - if item type is Free Function, accumulate price

    :param dictionary: dictionary that contains accumulated values for each Fixed total
    :param item_type: integer that represents type of each item (
    PLU/PLU 2nd or Free Function, see app/mod_db_manage/config.py)
    :param price: price value
    :param qty: quantity value
    :return: dictionary with updated values of Gross and Net
    """
    price = PriceValue(price).get_value()

    # Calculating Gross
    if item_type == PLU_ITEM_TYPE or item_type == PLU2ND_ITEM_TYPE:
        # work with negative price here
        dictionary["Gross"]["price_sum"] += price
        dictionary["Gross"]["price_sum"] = PriceValue(dictionary["Gross"]["price_sum"]).round_half_up()
        dictionary["Gross"]["qty_sum"] += qty
    # Calculating Net
    elif item_type == FREE_FUNC_ITEM_TYPE:
        dictionary["Net"]["price_sum"] += price
        dictionary["Net"]["price_sum"] = PriceValue(dictionary["Net"]["price_sum"]).round_half_up()
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
    gross_value = PriceValue(gross_value_raw).get_value()
    divider = PriceValue(1 + tax_rate / 100).get_value()
    raw_net_amount = PriceValue(gross_value / divider).round_half_up()
    vat = PriceValue(-1 * (raw_net_amount - gross_value)).round_half_up()
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


class PriceValue:
    """
    Represents price.

    Rounds values half up by two decimals

    Uses get_value method to get price value
    """
    def __init__(self, value):
        self.value = Decimal(str(value))

    def get_value(self):
        return self.value

    def round_half_up(self):
        """
        Half up rounding of Decimal value
        :return: Decimal rounded half up by 2 numbers after floating point
        """
        return self.value.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)



class StatsDataExtractor:
    """
    Extracts statistics data from database according needed time frames.
    """
    def __init__(self, org_id, start_time, end_time):
        session_maker = sessionmaker(db)
        self.session = session_maker()
        self.org_id = org_id
        self.start_time = start_time
        self.end_time = end_time
        self.orderlines = self.session.query(OrderLine).join(OrderLine.order).filter(
            and_(
                Order.org_id == org_id,
                Order.date_time >= self.start_time,
                Order.date_time <= self.end_time
                )
            )

    def close_session(self):
        self.session.close()

    def get_department_sales_data(self):
        """
        Get Department sales
        """
        data_dict = {}

        for ol in self.orderlines:
            price = ol.value
            qty = ol.qty
            # encounter PLU and PLU2nd
            if ol.item_type == PLU_ITEM_TYPE:
                dep_id = ol.plu.department_id
                dep_name = ol.plu.department.name
            elif ol.item_type == PLU2ND_ITEM_TYPE:
                dep_id = ol.plu_2nd.department_id
                dep_name = ol.plu_2nd.department_name
            else:
                continue
            
            data_dict = dict_write_values(data_dict, dep_id, dep_name, price, qty)
        
        return data_dict

    def get_fixed_totalizers(self):
        """
        Accumulates values for fixed totals according to asked period of time
        Gross values:
        :return: dictionary with accumulated values of fixed totals
        """
        data_dict = {}
        data_dict = gross_net_fill_values(data_dict)

        for ol in self.orderlines:
            if ol.free_function:  # ATTENTION!!! FIX!!! skip statistics for HOLD items
                if ol.free_function.name == 'HOLD':
                    continue
            
            qty = ol.qty
            price = ol.value

            # calculate taxes
            if ol.item_type == PLU_ITEM_TYPE or ol.item_type == PLU2ND_ITEM_TYPE:

                if ol.item_type == PLU_ITEM_TYPE:
                    tax_name = ol.plu.tax.name
                    tax_rate = int(ol.plu.tax.rate)
                else:
                    tax_name = ol.plu_2nd.tax.name
                    tax_rate = int(ol.plu_2nd.tax.rate)

                tax_name_amt = tax_name + " AMT"
                vat, net_amount = calculate_vat_net(tax_rate, price)

                if tax_name in data_dict.keys():
                    data_dict[tax_name]["price_sum"] += vat
                    data_dict[tax_name_amt]["price_sum"] += net_amount
                else:
                    tax_fill_values(data_dict, tax_name, tax_name_amt, vat, net_amount)

            # there are such free functions as '3 for 2' (Group 3/Order2)
            # that have 1 item type and None free func, also with negative value
            # this value spoils results so check for None there
            elif ol.item_type == FREE_FUNC_ITEM_TYPE and ol.free_func_id is not None:
                ft_name = ol.fixed_totalizer.name
                data_dict = dict_write_values(data_dict, ft_name, ft_name, price, qty)

            data_dict = accumulate_gross_net(data_dict, ol.item_type, price, qty)

        return data_dict

    def get_plu_sales_data(self):
        """
        Get PLU sales
        """
        data_dict = {}

        for ol in self.orderlines:
            qty = ol.qty
            price = ol.value
            # encounter PLU and PLU2nd
            if ol.item_type == PLU_ITEM_TYPE:
                product_id = ol.product_id
                product_name = ol.product.name
            elif ol.item_type == PLU2ND_ITEM_TYPE:
                product_id = ol.product_id_2nd
                product_name = ol.product_2nd.name
            else:
                continue

            data_dict = dict_write_values(data_dict, product_id, product_name, price, qty)

        return data_dict

    def get_last_100_sales(self):
        """
        Get last 100 sales
        """
        orders = self.session.query(Order).filter(and_(
            Order.org_id == self.org_id,
            Order.date_time >= self.start_time,
            Order.date_time <= self.end_time
        )
        ).order_by(Order.date_time.desc()).all()

        if len(orders) > 100:
            orders = orders[:100]

        data_dict = {}

        for order in orders:
            date_time = order.date_time
            sale_id = order.id
            site = self.session.query(Organization).filter_by(id=self.org_id).first().name
            sales_total = 0
            
            for item in order.items:
                # count only Free Function item types that mean result values
                # if delete this, PLU and PLU 2nd items' values will be added to result values
                # this will cause doubling results
                if item.item_type == FREE_FUNC_ITEM_TYPE:
                    sales_total += item.value

            data_dict[sale_id] = {}
            data_dict[sale_id]["date_time"] = date_time
            data_dict[sale_id]["id"] = sale_id
            data_dict[sale_id]["site"] = site
            data_dict[sale_id]["sales_total"] = PriceValue(sales_total).round_half_up()

        return data_dict

    def get_clerks_breakdown(self):
        """
        Get Clerks breakdown sales
        """
        data_dict = {}

        for ol in self.orderlines:
            clerk_name = ol.order.clerk.name
            clerk_id = ol.order.clerk_id
            price = ol.value
            qty = ol.qty
            data_dict = dict_write_values(data_dict, clerk_id, clerk_name, price, qty)

        return data_dict

    def get_group_sales_data(self):
        """
        Get Group sales
        """
        data_dict = {}

        for ol in self.orderlines:
            qty = ol.qty
            price = ol.value
            # encounter PLU and PLU2nd
            if ol.item_type == PLU_ITEM_TYPE:
                group_id = ol.plu.group_id
                group_name = ol.plu.group.name
            elif ol.item_type == PLU2ND_ITEM_TYPE:
                group_id = ol.plu_2nd.group_id
                group_name = ol.plu_2nd.group_name
            else:
                continue

            data_dict = dict_write_values(data_dict, group_id, group_name, price, qty)

        return data_dict

    def get_free_func(self):
        """
        Get Free functions data
        """
        data_dict = {}

        for ol in self.orderlines:
            ff_id = ol.free_func_id
            if ff_id is None:
                continue 

            ff_name = ol.free_function.name
            if ff_name == "HOLD":  # skip statistics for HOLD items
                continue

            qty = ol.qty
            price = ol.value

            if ff_name == "VOID":  # VOID has negative values, so convert them to positive
                qty = abs(qty)
                price = abs(price)

            data_dict = dict_write_values(data_dict, ff_id, ff_name, price, qty)

        return data_dict
