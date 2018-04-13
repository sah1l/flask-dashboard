import pytest
from app.mod_stats.stats_utils import StatsDataExtractor
from app.models import Order


ORG_ID = 15
ORDER_ID = 364


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


def test_get_free_func_no_free_text_no_details(data_handler):
    """
    Checks that FREE TEXT free function will not be shown for not detailed report

    Data for cheks: {'2291_': {'name': 'FREE TEXT', 'price_sum': Decimal('0.00'), 'qty_sum': 0}}

    :param data_handler: fixture object
    :assert: must be False
    """
    free_text_found = False
    free_func_sales_data = data_handler.get_free_func()

    for id_, subdict in free_func_sales_data.items():
        if subdict['name'] == "FREE TEXT":
            free_text_found = True

    assert free_text_found == False


def test_get_free_func_free_text_detailed(data_handler):
    """
    Checks that FREE TEXT free function is considered but appears in other name

    Data for checks: {
    '2291_': {'name': 'NO SAUCE', 'price_sum': Decimal('0.00'), 'qty_sum': 0},
    '2306_': {'name': 'HOLD ', 'price_sum': Decimal('6.65'), 'qty_sum': 0}
    }

    :param data_handler: fixture object
    :assert: must be True
    """
    free_text_found = False
    free_func_sales_data = data_handler.get_free_func(detailed_report=True)

    for id_, subdict in free_func_sales_data.items():
        if subdict['name'] == "NO SAUCE":
            free_text_found = True

    assert free_text_found == True