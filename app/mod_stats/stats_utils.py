"""
Helper class for statistics Blueprint.
Handles requests to database and extracts needed information.
Only reads database.
"""

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import and_

from app.models import OrderLine, Order, Organization
from app.mod_db_manage.config import FREE_FUNC_ITEM_TYPE, PLU_ITEM_TYPE, PLU2ND_ITEM_TYPE, TENDER_FUNCTION_NUMBER,\
    VOID_NAME_IDENTIFIER


# The following functions have a fixed quantity of 1:
#+, -, +%, -%, tender (cash, card, etc), no sale, paid out, Deposit,
# Receive on account, media exchange, tip, pay account, membership fee.
# So, ONE_QTY_SET has FunctionNo data for Free Functions mentioned above
ONE_QTY_SET = ["TENDER", "+", "-", "+%", "-%",  "NS", "PAID OUT", "DEPOSIT", "MEDIA EXCHANGE", "TIP",
               "PAID ON ACCOUNT", "PAY ACCOUNT", "ADD CHECKS"]


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


def accumulate_gross_net(dictionary, item_type, price, qty, func_number):
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
    :param func_number: number of function (we look for a certain one, tender function)
    :return: dictionary with updated values of Gross and Net
    """
    price = PriceValue(price).get_value()
    # print(item_type)

    # Calculating Gross
    if item_type == PLU_ITEM_TYPE or item_type == PLU2ND_ITEM_TYPE:
        # work with negative price here
        dictionary["Gross"]["price_sum"] += price
        dictionary["Gross"]["price_sum"] = PriceValue(dictionary["Gross"]["price_sum"]).get_value()
        dictionary["Gross"]["qty_sum"] += qty
    # Calculating Net
    elif item_type == FREE_FUNC_ITEM_TYPE and func_number == TENDER_FUNCTION_NUMBER:
        dictionary["Net"]["price_sum"] += price
        dictionary["Net"]["price_sum"] = PriceValue(dictionary["Net"]["price_sum"]).get_value()
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
    raw_net_amount = PriceValue(gross_value / divider).get_value()
    vat = PriceValue(-1 * (raw_net_amount - gross_value)).get_value()
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
    def __init__(self, price_value):
        self.price_value = Decimal(str(price_value)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

    def get_value(self):
        return self.price_value


class StatsDataExtractor:
    """
    Extracts statistics data from database according needed time frames.
    """
    def __init__(self, org_id, start_time, end_time):
        """
        :param org_id: ID of the requested organization
        :param start_time: start time to get data from database
        :param end_time: end time to get data from database

        Parameter of methods that get statistics data for PLU sales (get_plu_sales_data):
        :param detailed_report: keyword argument to specify if detailed report is needed or not.

        Detailed report means that values of price and quantity will not be summed up to each other.
        Example concept:

        Input data:
        Orderline 1: name: Sandwich, quantity: 1, price: 3.95
        Orderline 2: name: Sandwich, quantity: 1, price: 3.95

        Detailed report:
        {
            {"unique_item_1": {"name": "Sandwich", quantity: 1, price: 3.95}}
            {"unique_item_2": {"name": "Sandwich", quantity: 1, price: 3.95}}
        }
        Detailed report is required in Order Details page, PLU / PLU 2nd items

        Summed report:
        {
            {"item": {"name": "Sandwich", quantity: 2, price: 7.90}}
        }
        Summed report is used in most cases in statistics data shown in dashboard
        """
        self.org_id = org_id
        self.start_time = start_time
        self.end_time = end_time
        self.orderlines = OrderLine.query.join(OrderLine.order).filter(
            and_(
                Order.org_id == org_id,
                Order.date_time >= self.start_time,
                Order.date_time <= self.end_time
                )
            )

    def dict_write_values(self, dictionary, entry_id, name, price, qty, unique_id=""):
        """
        Write new values to dictionary.
        Entry's number is a key for top-level structure.

        Summing up case:
        If this is a new element, creates dictionary structure for it.
        If this element is present, sums values up with their total values.

        Detailed case:
        Each element is unique, values are not summed up

        :param dictionary: dictionary with accumulated data
        :param entry_id: ID of the element in database (or name in a few cases)
        :param name: a string that identifies the entry
        :param price
        :param qty: quantity
        :param unique_id: empty string for summing up case, orderline ID for detailed case
        :return: renewed values of dictionary
        """
        price = PriceValue(price).get_value()
        item_id = str(entry_id) + "_" + str(unique_id)

        if item_id in dictionary.keys():
            dictionary[item_id]["price_sum"] += price
            dictionary[item_id]["qty_sum"] += qty
        else:
            dictionary[item_id] = {}
            dictionary[item_id]["name"] = name
            dictionary[item_id]["price_sum"] = price
            dictionary[item_id]["qty_sum"] = qty

        dictionary[item_id]["price_sum"] = PriceValue(dictionary[item_id]["price_sum"]).get_value()

        return dictionary

    def get_department_sales_data(self):
        """
        Get Department sales
        """
        data_dict = {}

        for ol in self.orderlines:
            price = ol.value
            qty = ol.qty

            # encounter PLU and PLU2nd
            if ol.item_type == PLU_ITEM_TYPE or ol.item_type == PLU2ND_ITEM_TYPE:
                dep_id = ol.plu.department_id

                # some product may not have a department
                if not dep_id:
                    continue

                dep_name = ol.plu.department.name
            else:
                continue
            
            data_dict = self.dict_write_values(data_dict, dep_id, dep_name, price, qty)
        
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
            if ol.free_function:  # skip statistics for HOLD items
                if ol.free_function.name == 'HOLD':
                    continue
            
            qty = ol.qty
            price = PriceValue(ol.value).get_value()
            func_number = ol.func_number

            # calculate taxes
            if ol.item_type == PLU_ITEM_TYPE or ol.item_type == PLU2ND_ITEM_TYPE:
                
                # some product may not have a tax
                if not ol.plu.tax_id:
                    continue

                # print('this product has tax')
                tax_name = ol.plu.tax.name
                # print('tax name', tax_name)
                tax_rate = int(ol.plu.tax.rate)
                # print('tax rate', tax_rate)
                tax_name_amt = tax_name + " AMT"
                # print('amount', tax_name_amt)
                vat, net_amount = calculate_vat_net(tax_rate, price)
                # print('vat', vat, 'net amount', net_amount)

                if tax_name in data_dict.keys():
                    data_dict[tax_name]["price_sum"] += vat
                    data_dict[tax_name_amt]["price_sum"] += net_amount
                else:
                    tax_fill_values(data_dict, tax_name, tax_name_amt, vat, net_amount)
                # print(data_dict)

            # there are such free functions as '3 for 2' (Group 3/Order2)
            # that have 1 item type and None free func, also with negative value
            # this value spoils results so check for None there
            elif ol.item_type == FREE_FUNC_ITEM_TYPE \
                    and ol.free_func_id is not None \
                    and func_number == TENDER_FUNCTION_NUMBER:

                # consider change for CASH-type items
                if ol.change:
                    price -= PriceValue(ol.change).get_value()

                ft_name = ol.fixed_totalizer.name
                data_dict = self.dict_write_values(data_dict, ft_name, ft_name, price, qty)

            data_dict = accumulate_gross_net(data_dict, ol.item_type, price, qty, func_number)
        # print(data_dict)

        return data_dict

    def get_plu_sales_data(self, detailed_report=False):
        """
        Get PLU sales

        :param detailed_report: True for order details page (/sale_<sale_id>), False for general statistics page
        :return: dictionary with accumulated values of PLU sales
        """
        data_dict = {}

        for ol in self.orderlines:
            qty = ol.qty
            price = PriceValue(ol.value).get_value()

            # encounter PLU and PLU2nd
            if ol.item_type == PLU_ITEM_TYPE or ol.item_type == PLU2ND_ITEM_TYPE:
                product_id = ol.product_id
                product_name = ol.product.name
            else:
                continue

            # specify unique ID for each PLU element
            if detailed_report:
                unique_id = ol.id
            else:
                unique_id = ""

            # add "**VOID**" word to the product name if it is a VOIDED product
            if ol.free_function and ol.free_function.name == "VOID":
                product_name = VOID_NAME_IDENTIFIER + product_name

            data_dict = self.dict_write_values(data_dict, product_id, product_name, price, qty, unique_id=unique_id)

        return data_dict

    def get_last_100_sales(self):
        """
        Get last 100 sales
        """
        orders = Order.query.filter(and_(
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
            site = Organization.query.filter_by(id=self.org_id).first().name
            sales_total = 0
            
            for item in order.items:
                # count only Free Function item types that mean result values
                # if delete this, PLU and PLU 2nd items' values will be added to result values
                # this will cause doubling results
                if item.item_type == FREE_FUNC_ITEM_TYPE and item.func_number == TENDER_FUNCTION_NUMBER:
                    sales_total += item.value

                    # consider change:
                    if item.change:
                        sales_total -= item.change

            data_dict[sale_id] = {}
            data_dict[sale_id]["date_time"] = date_time
            data_dict[sale_id]["id"] = sale_id
            data_dict[sale_id]["site"] = site
            data_dict[sale_id]["sales_total"] = PriceValue(sales_total).get_value()

        return data_dict

    def get_clerks_breakdown(self):
        """
        Get Clerks breakdown sales
        """
        data_dict = {}

        for ol in self.orderlines:
            # count only free functions
            if ol.item_type == FREE_FUNC_ITEM_TYPE and ol.func_number == TENDER_FUNCTION_NUMBER:
                clerk_name = ol.order.clerk.name
                clerk_id = ol.order.clerk_id
                price = ol.value

                # encounter change
                if ol.change:
                    price -= ol.change

                qty = ol.qty
                data_dict = self.dict_write_values(data_dict, clerk_id, clerk_name, price, qty)

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
            if ol.item_type == PLU_ITEM_TYPE or ol.item_type == PLU2ND_ITEM_TYPE:
                group_id = ol.plu.group_id

                # some product may not have a group
                if not group_id:
                    continue

                group_name = ol.plu.group.name
            else:
                continue

            data_dict = self.dict_write_values(data_dict, group_id, group_name, price, qty)

        return data_dict

    def get_free_func(self, detailed_report=False):
        """
        Get Free functions data

        :param detailed_report: True for order details page (/sale_<sale_id>), False for general statistics page
        If True:
            - doesn't subtract change from CASH-type Tender functions
            - show specific Free Functions name specified in orderline

                In other words,
                in orderline, free function's name may be another
                Example:
                in master files, function is called 'FREE TEXT'
                but in orderline, it's called 'NO SAUCE'
                so in detailed report, second (full) name will be shown
            - price and quantity are always positive except for DEPOSIT function

        If False:
            - doesn't encounter HOLD free functions (it will not be shown in a table)
            - doesn't encounter FREE TEXT free functions (it will not be shown in a table)
            - subtract change from CASH-type Tender functions
            - show function name from master files if detailed report is not necessary
            - price and quantity are always positive
        """
        data_dict = {}

        for ol in self.orderlines:
            ff_id = ol.free_func_id
            if ff_id is None:
                continue

            qty = self.get_free_function_qty(ol)
            price = ol.value

            # turn everything into positive values
            price = abs(price)
            qty = abs(qty)

            if not detailed_report:
                # don't encounter HOLD free function
                if ol.free_function.name == "HOLD":
                    continue

                # don't encounter FREE TEXT free function
                if ol.free_function.name == "FREE TEXT":
                    continue

                # choose name
                ff_name = ol.free_function.name

                # subtract change from CASH-type Tender functions
                if ol.change:
                    price -= ol.change

            else:
                # name of the orderline
                ff_name = ol.name

                # for DEPOSIT free function, make price negative
                if ol.free_function.function_number == "DEPOSIT":
                    price = -price

            # VOID has negative values, so convert them to positive
            # this will show VOIDs in free function data, but, with positive values
            # if ff_name == "VOID":
            #     qty = abs(qty)
            #     price = abs(price)

            data_dict = self.dict_write_values(data_dict, ff_id, ff_name, price, qty)

        return data_dict

    def get_free_function_qty(self, ol):
        """
        Some Free Functions have a fixed quantity equal to 1.
        This is not specified anywhere :( So had to hardcode this in ONE_QTY_SET.
        Thus, method checks if Free Function's function_number field in in ONE_QTY_SET.

        :param ol: orderline
        :return: 1 if quantity is fixed, <qty> if has some other quantity.
        """
        if ol.free_function.function_number in ONE_QTY_SET:
            return 1
        else:
            return ol.qty

    def calculate_change(self):
        """
        Sums up Free Function items with CHANGE field

        This works for CASH-type orderlines (CASH, CASH-10)
        :return: result sum of total change for period of time
        """
        total_change = 0

        for ol in self.orderlines:
            if ol.item_type == FREE_FUNC_ITEM_TYPE:
                if ol.change:
                    total_change += ol.change

        return PriceValue(total_change).get_value()

    def calculate_total_sales(self):
        """
        Calculates total sum of Free Function items, change is considered
        :return: total sum
        """
        total_sales = 0

        for ol in self.orderlines:
            if ol.item_type == FREE_FUNC_ITEM_TYPE and ol.func_number == TENDER_FUNCTION_NUMBER:
                price = ol.value
                if ol.change:
                    price -= ol.change
                total_sales += price

        return PriceValue(total_sales).get_value()
