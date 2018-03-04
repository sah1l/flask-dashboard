from flask import Blueprint, render_template, url_for, redirect
from flask_login import current_user
from flask.views import View
from sqlalchemy.exc import OperationalError

from app import session_maker
from app.models import Organization, Order, Department, Group
from app.mod_auth.models import User
from app.mod_stats.stats_utils import StatsDataExtractor, PriceValue, calc_today_timeframe, calc_yesterday_timeframe, \
    calc_this_week_timeframe, calc_last_week_timeframe, calc_this_month_timeframe, calc_last_month_timeframe, \
    calc_this_quarter_timeframe, calc_last_quarter_timeframe
from app.mod_stats.forms import CustomizeStatsForm, CustomTimeSliceForm
from app.mod_db_manage.config import FREE_FUNC_ITEM_TYPE


# define Blueprint for statistics module
mod_stats = Blueprint('stats', __name__, url_prefix='/dashboard')


@mod_stats.before_request
def check_authenticated_user():
    """
    Restrict access to statistics to not authenticated users
    """
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))


@mod_stats.errorhandler(OperationalError)
def handle_operational_error(error):
    """
    Handles situation when there's no connection with database
    """
    return "No connection with database"


@mod_stats.route("/<org_id>/sale_<order_id>", methods=["GET"])
def get_order_details(org_id, order_id):
    session = session_maker()
    order = session.query(Order).filter_by(id=order_id).first()
    orderlines = order.items

    # order details
    clerk_name = order.clerk.name
    site = session.query(Organization).filter_by(id=org_id).first().name
    total_sale = 0

    for ol in orderlines:
        if ol.item_type == FREE_FUNC_ITEM_TYPE:
            total_sale = ol.value
            if ol.change:
                total_sale -= ol.change

    total_sale = PriceValue(total_sale).get_value()

    # sales information
    plu_sale_items = []
    plu_2nd_items = []
    free_func_items = []

    for sale in orderlines:
        # include only PLU, PLU 2nd and Free Function orderlines
        if sale.product_id:
            plu_sale_items.append({"name": sale.product.name,
                                   "qty": sale.qty,
                                   "price": PriceValue(sale.value).get_value()})
        elif sale.product_id_2nd:
            plu_2nd_items.append({"name": sale.product_2nd.name,
                                  "qty": sale.qty,
                                  "price": PriceValue(sale.value).get_value()})
        elif sale.free_func_id:
            free_func_items.append({"name": sale.free_function.name,
                                    "qty": sale.qty,
                                    "price": PriceValue(sale.value).get_value()})
            # consider change
            if sale.change:
                free_func_items.append({"name": "CHANGE",
                                        "qty": 0,
                                        "price": PriceValue(sale.change).get_value()})
        else:
            pass

    # get Group sales and Department sales
    group_sales = {}
    department_sales = {}

    for sale in orderlines:
        if sale.product_id:
            group_id = sale.product.group.id
            dep_id = sale.product.department.id

            # add group data
            if group_id not in group_sales.keys():
                group_sales[group_id] = {}
                group_name = sale.product.group.name
                group_sales[group_id] = {
                    "name": group_name,
                    "qty": sale.qty,
                    "price": PriceValue(sale.value).get_value()}
            else:
                group_sales[group_id]["qty"] += 1
                group_sales[group_id]["price"] += PriceValue(sale.value).get_value()

            # add department data
            if dep_id not in department_sales.keys():
                department_sales[dep_id] = {}
                dep_name = sale.product.department.name
                department_sales[dep_id] = {
                    "name": dep_name,
                    "qty": sale.qty,
                    "price": PriceValue(sale.value).get_value()}
            else:
                department_sales[dep_id]["qty"] += 1
                department_sales[dep_id]["price"] += PriceValue(sale.value).get_value()

    # get fixed totals
    fixed_totals = {}

    for sale in orderlines:
        if sale.fixed_total_id:
            ft_id = sale.fixed_total_id

            if ft_id not in fixed_totals.keys():
                fixed_totals[ft_id] = {}
                fixed_totals[ft_id] = {"name": sale.fixed_totalizer.name,
                                       "qty": sale.qty,
                                       "price": PriceValue(sale.value).get_value()}
            else:
                fixed_totals[ft_id]["qty"] += 1
                fixed_totals[ft_id]["price"] += PriceValue(sale.value).get_value()

    session.close()

    return render_template("stats/order_details.html",
                           order=order,
                           site=site,
                           clerk_name=clerk_name,
                           total_sale=total_sale,
                           plu_sale_items=plu_sale_items,
                           plu_2nd_items=plu_2nd_items,
                           free_func_items=free_func_items,
                           group_sales=group_sales,
                           department_sales=department_sales,
                           fixed_totals=fixed_totals)


class ShowDataView(View):
    """
    Generic class that gives statistics data  according to given timelines
    Is shown on dashboard
    """
    methods = ['GET', 'POST']

    def __init__(self, route_name, timeframes):
        self.org_id = None
        self.route_name = route_name
        self.start_datetime = timeframes[0]
        self.end_datetime = timeframes[1]

        self.session = session_maker()

    def check_org_id(self, user, _org_id):
        """
        Dashboard URL in left panel doesn't know which organizations are assigned to the user
        0 is generated automatically

        :param: user object
        """
        if _org_id == "0":
            _org_id = user.organizations[0].id

        return _org_id

    def dispatch_request(self, **kwargs):
        self.org_id = kwargs['org_id']

        # custome datetimes case
        try:
            self.start_datetime = kwargs['start_date']
            self.end_datetime = kwargs['end_date']
        except:
            pass

        user = self.session.query(User).filter_by(id=current_user.id).first()

        # user does not have any organizations
        if not user.organizations:
            return render_template("stats/base.html", error_message="You do not have any organizations yet.")

        self.org_id = self.check_org_id(user, self.org_id)
        org_name = self.session.query(Organization).filter_by(id=self.org_id).first().name

        # getting statistics data
        data_handler = StatsDataExtractor(self.org_id, self.start_datetime, self.end_datetime)
        department_sales_data = data_handler.get_department_sales_data()
        fixed_totalizers_data = data_handler.get_fixed_totalizers()
        plu_sales_data = data_handler.get_plu_sales_data()
        last_100_sales_data = data_handler.get_last_100_sales()
        clerks_breakdown_data = data_handler.get_clerks_breakdown()
        group_sales_total_data = data_handler.get_group_sales_data()
        free_function_data = data_handler.get_free_func()
        data_handler.close_session()

        # choose organization form
        org_form = CustomizeStatsForm()
        orgs = user.organizations
        org_form.organization.choices = [(org.id, org.name) for org in orgs]

        self.session.close()

        if org_form.validate_on_submit():
            new_org_id = org_form.organization.data
            return redirect(url_for("stats.{}".format(self.route_name),
                                    org_id=new_org_id,
                                    start_date=self.start_datetime,
                                    end_date=self.end_datetime))

        # custom timeline form
        dt_form = CustomTimeSliceForm()

        if dt_form.validate_on_submit():
            new_start_datetime = dt_form.start_date.data
            new_end_datetime = dt_form.end_date.data

            return redirect(url_for("stats.show_custom_datetime",
                                    org_id=self.org_id,
                                    start_date=new_start_datetime,
                                    end_date=new_end_datetime))

        return render_template("stats/base.html",
                               department_sales_data=department_sales_data,
                               fixed_totalizer_data=fixed_totalizers_data,
                               plu_sales_data=plu_sales_data,
                               last_100_sales_data=last_100_sales_data,
                               clerks_breakdown_data=clerks_breakdown_data,
                               group_sales_total_data=group_sales_total_data,
                               free_function_data=free_function_data,
                               org_form=org_form,
                               dt_form=dt_form,
                               organization_name=org_name,
                               organization_id=self.org_id
                               )


mod_stats.add_url_rule('/<org_id>/today', view_func=ShowDataView.as_view('show_today',
                                                                         route_name='show_today',
                                                                         timeframes=calc_today_timeframe()))
mod_stats.add_url_rule('/<org_id>/yesterday', view_func=ShowDataView.as_view('show_yesterday',
                                                                             route_name='show_yesterday',
                                                                             timeframes=calc_yesterday_timeframe()))
mod_stats.add_url_rule('/<org_id>/this_week', view_func=ShowDataView.as_view('show_this_week',
                                                                             route_name='show_this_week',
                                                                             timeframes=calc_this_week_timeframe()))
mod_stats.add_url_rule('/<org_id>/last_week', view_func=ShowDataView.as_view('show_last_week',
                                                                             route_name='show_last_week',
                                                                             timeframes=calc_last_week_timeframe()))
mod_stats.add_url_rule('/<org_id>/this_month', view_func=ShowDataView.as_view('show_this_month',
                                                                             route_name='show_this_month',
                                                                             timeframes=calc_this_month_timeframe()))
mod_stats.add_url_rule('/<org_id>/last_month', view_func=ShowDataView.as_view('show_last_month',
                                                                             route_name='show_last_month',
                                                                             timeframes=calc_last_month_timeframe()))
mod_stats.add_url_rule('/<org_id>/this_quarter', view_func=ShowDataView.as_view('show_this_quarter',
                                                                                route_name='show_this_quarter',
                                                                                timeframes=calc_this_quarter_timeframe()))
mod_stats.add_url_rule('/<org_id>/last_quarter', view_func=ShowDataView.as_view('show_last_quarter',
                                                                                route_name='show_last_quarter',
                                                                                timeframes=calc_last_quarter_timeframe()))
mod_stats.add_url_rule('/<org_id>/<start_date>_<end_date>', view_func=ShowDataView.as_view('show_custom_datetime',
                                                                                           route_name='show_custom_datetime',
                                                                                           timeframes=(None, None)))
