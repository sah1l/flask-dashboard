import datetime
from flask import Blueprint, render_template, url_for, redirect
from flask_login import current_user
from flask.views import View
from sqlalchemy.exc import OperationalError

from app import session_maker
from app.models import Organization
from app.mod_auth.models import User
from app.mod_stats.stats_utils import StatsDataExtractor, calc_today_timeframe, calc_yesterday_timeframe, \
    calc_this_week_timeframe, calc_last_week_timeframe, calc_this_month_timeframe, calc_last_month_timeframe, \
    calc_this_quarter_timeframe, calc_last_quarter_timeframe
from app.mod_stats.forms import CustomizeStatsForm, CustomTimeSliceForm


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


class ShowDataView(View):
    """
    Generic class that gives data according to given timelines
    """
    methods = ['GET', 'POST']

    def __init__(self, route_name, timeframes):
        self.org_id = None
        self.route_name = route_name
        self.start_datetime = timeframes[0]
        self.end_datetime = timeframes[1]

        self.session = session_maker()

    def check_org_id(self, user):
        """
        Dashboard URL in left panel doesn't know which organizations are assigned to the user
        0 is generated automatically

        :param: user object
        """
        if self.org_id == 0:
            self.org_id = user.organizations[0].id

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

        self.check_org_id(user)
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
                               organization_name=org_name
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
