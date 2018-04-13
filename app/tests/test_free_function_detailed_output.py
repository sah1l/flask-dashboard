import pytest
from app.mod_stats.stats_utils import StatsDataExtractor, PriceValue
from app.models import Order


ORG_ID = 16
ORDER_ID = 400


def create_order():
    """
    Creates order object

    :return: order object, start_datetime, end_datetime
    """
    order = Order.query.filter_by(id=ORDER_ID).first()
    start_datetime = order.date_time
    end_datetime = order.date_time

    return order, start_datetime, end_datetime


@pytest.fixture
def data_handler():
    """
    :return: StatsDataExtractor object
    """
    order, start_datetime, end_datetime = create_order()
    data_handler = StatsDataExtractor(ORG_ID, start_datetime, end_datetime)

    return data_handler


def test_get_free_func_no_details(data_handler):
    """
    Checks free function output with no details
    This approach tells to subtract change from CASH-type Tender functions

    Data for checks: {'2494_': {'name': 'CASH', 'price_sum': Decimal('21.95'), 'qty_sum': 0}}

    :param data_handler: fixture object
    :assert: current PriceValue object with control PriceValue object. Must be True
    """
    free_func_sales_data = data_handler.get_free_func()
    item = free_func_sales_data["2494_"]
    price = PriceValue(item['price_sum']).get_value()
    control_price = PriceValue(21.95).get_value()

    assert price == control_price


def test_get_free_func_detailed(data_handler):
    """
    Checks free function output with no details
    This approach tells NOT to subtract change from CASH-type Tender functions

    Data for checks: {'2494_': {'name': 'CASH', 'price_sum': Decimal('30.00'), 'qty_sum': 0}}

    :param data_handler: fixture object
    :assert: current PriceValue object with control PriceValue object. Must be True
    """
    free_func_sales_data = data_handler.get_free_func(detailed_report=True)
    item = free_func_sales_data["2494_"]
    price = PriceValue(item['price_sum']).get_value()
    control_price = PriceValue(30.00).get_value()

    assert price == control_price
