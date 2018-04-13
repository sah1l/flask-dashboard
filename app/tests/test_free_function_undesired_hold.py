import pytest
from app.mod_stats.stats_utils import StatsDataExtractor
from app.models import Order


ORG_ID = 16
ORDER_ID = 397


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


def test_get_free_func_no_hold_no_details(data_handler):
    """
    Checks that HOLD free functions WILL NOT be shown in statistics results for no detailed report

    Data for checks: {'2468_': {'name': 'VOID', 'price_sum': Decimal('2.50'), 'qty_sum': 1}}

    :param data_handler: fixture object
    :assert: must be False
    """
    hold_found = False

    free_func_sales_data = data_handler.get_free_func()
    for id_, subdict in free_func_sales_data.items():
        if subdict['name'] == "HOLD":
            hold_found = True

    assert hold_found == False


def test_get_free_func_no_hold_detailed(data_handler):
    """
    Checks that HOLD free functions CAN BE be shown in statistics results for no detailed report

    Data for checks: {
    '2468_': {'name': 'VD:SAMOSA CHICKEN LARGE', 'price_sum': Decimal('-2.50'), 'qty_sum': -1},
    '2476_': {'name': 'HOLD ', 'price_sum': Decimal('10.30'), 'qty_sum': 0}
    }

    :param data_handler: fixture object
    :assert: must be True
    """
    hold_found = False

    free_func_sales_data = data_handler.get_free_func(detailed_report=True)

    for id_, subdict in free_func_sales_data.items():
        if subdict['name'] == "HOLD ":
            hold_found = True

    assert hold_found == True
