import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint, render_template, url_for, redirect
from flask_login import current_user
from sqlalchemy.exc import OperationalError

from app import session_maker
from app.models import Organization
from app.mod_auth.models import User
from app.mod_stats.stats_utils import StatsDataExtractor, calc_quarter_timerange
from app.mod_stats.forms import CustomizeStatsForm


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


@mod_stats.route("/<org_id>", methods=["GET", "POST"])
@mod_stats.route("/<org_id>/today", methods=["GET", "POST"])
def show_today(org_id):
    """
    Shows data for current day since 00:00:00
    """
    now_time = datetime.datetime.utcnow()
    start_time = now_time.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = now_time.replace(hour=23, minute=59, second=59)
    session = session_maker()
    user = session.query(User).filter_by(id=current_user.id).first()

    if not user.organizations:
        return render_template("stats/base.html", error_message="You do not have any organizations yet.")

    # fix this
    if org_id == 0:
        org_id = user.organizations[0].id

    data_handler = StatsDataExtractor(org_id, start_time, end_time)

    department_sales_data = data_handler.get_department_sales_data()
    fixed_totalizers_data = data_handler.get_fixed_totalizers()
    plu_sales_data = data_handler.get_plu_sales_data()
    last_100_sales_data = data_handler.get_last_100_sales()
    clerks_breakdown_data = data_handler.get_clerks_breakdown()
    group_sales_total_data = data_handler.get_group_sales_data()
    free_function_data = data_handler.get_free_func()

    data_handler.close_session()
    form = CustomizeStatsForm()
    orgs = user.organizations
    form.organization.choices = [(org.id, org.name) for org in orgs]
    org_name = session.query(Organization).filter_by(id=org_id).first().name
    session.close()

    if form.validate_on_submit():
        org_id = form.organization.data
        return redirect(url_for("stats.show_today", org_id=org_id))

    return render_template("stats/base.html",
                           group_sales_total_data=group_sales_total_data,
                           department_sales_data=department_sales_data,
                           fixed_totalizer_data=fixed_totalizers_data,
                           plu_sales_data=plu_sales_data,
                           last_100_sales_data=last_100_sales_data,
                           clerks_breakdown_data=clerks_breakdown_data,
                           free_function_data=free_function_data,
                           form=form,
                           organization_name=org_name
                           )

@mod_stats.route("/<org_id>/yesterday", methods=["GET", "POST"])
def show_yesterday(org_id):
    """
    Shows data for day before current day 

    (begins from 00:00:00, ends with 23:59:59)
    """
    yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    end_time = yesterday.replace(hour=23, minute=59, second=59, microsecond=0)  # 23:59:59 of the day
    start_time = end_time - datetime.timedelta(days=1) + datetime.timedelta(seconds=1)  # 00:00:00 of the day
    session = session_maker()
    user = session.query(User).filter_by(id=current_user.id).first()

    if not user.organizations:
        return render_template("stats/base.html", error_message="You do not have any organizations yet.")

    # fix this
    if org_id == 0:
        org_id = user.organizations[0].id

    data_handler = StatsDataExtractor(org_id, start_time, end_time)

    department_sales_data = data_handler.get_department_sales_data()
    fixed_totalizers_data = data_handler.get_fixed_totalizers()
    plu_sales_data = data_handler.get_plu_sales_data()
    last_100_sales_data = data_handler.get_last_100_sales()
    clerks_breakdown_data = data_handler.get_clerks_breakdown()
    group_sales_total_data = data_handler.get_group_sales_data()
    free_function_data = data_handler.get_free_func()

    data_handler.close_session()
    form = CustomizeStatsForm()
    orgs = user.organizations
    form.organization.choices = [(org.id, org.name) for org in orgs]
    org_name = session.query(Organization).filter_by(id=org_id).first().name
    session.close()

    if form.validate_on_submit():
        org_id = form.organization.data
        return redirect(url_for("stats.show_yesterday", org_id=org_id))

    return render_template("stats/base.html",
                           group_sales_total_data=group_sales_total_data,
                           department_sales_data=department_sales_data,
                           fixed_totalizer_data=fixed_totalizers_data,
                           plu_sales_data=plu_sales_data,
                           last_100_sales_data=last_100_sales_data,
                           clerks_breakdown_data=clerks_breakdown_data,
                           free_function_data=free_function_data,
                           form=form,
                           organization_name=org_name
                           )


@mod_stats.route("/<org_id>/this_week", methods=["GET", "POST"])
def show_this_week(org_id):
    """
    Shows data starting from Monday of this week (00:00:00) 

    to current weekday (with current time)
    """
    curr_weekday = datetime.datetime.utcnow()

    for day in range(7):
        end_weekday = curr_weekday + datetime.timedelta(days=day)
        if end_weekday.weekday() == 6:
            break

    end_weekday = end_weekday.replace(hour=23, minute=59, second=59)
    start_weekday = end_weekday - datetime.timedelta(days=6)
    start_weekday = start_weekday.replace(hour=0, minute=0, second=0, microsecond=0)
    session = session_maker()
    user = session.query(User).filter_by(id=current_user.id).first()

    if not user.organizations:
        return render_template("stats/base.html", error_message="You do not have any organizations yet.")

    # fix this
    if org_id == 0:
        org_id = user.organizations[0].id

    data_handler = StatsDataExtractor(org_id, start_weekday, end_weekday)

    department_sales_data = data_handler.get_department_sales_data()
    fixed_totalizers_data = data_handler.get_fixed_totalizers()
    plu_sales_data = data_handler.get_plu_sales_data()
    last_100_sales_data = data_handler.get_last_100_sales()
    clerks_breakdown_data = data_handler.get_clerks_breakdown()
    group_sales_total_data = data_handler.get_group_sales_data()
    free_function_data = data_handler.get_free_func()

    data_handler.close_session()
    form = CustomizeStatsForm()
    orgs = user.organizations
    form.organization.choices = [(org.id, org.name) for org in orgs]
    org_name = session.query(Organization).filter_by(id=org_id).first().name
    session.close()

    if form.validate_on_submit():
        org_id = form.organization.data
        return redirect(url_for("stats.show_this_week", org_id=org_id))

    return render_template("stats/base.html",
                           group_sales_total_data=group_sales_total_data,
                           department_sales_data=department_sales_data,
                           fixed_totalizer_data=fixed_totalizers_data,
                           plu_sales_data=plu_sales_data,
                           last_100_sales_data=last_100_sales_data,
                           clerks_breakdown_data=clerks_breakdown_data,
                           free_function_data=free_function_data,
                           form=form,
                           organization_name=org_name
                           )


@mod_stats.route("/<org_id>/last_week", methods=["GET", "POST"])
def show_last_week(org_id):
    """
    Shows data starting from Monday of the last week (00:00:00)

    to Sunday of the last week (23:59:59)
    """
    last_weekday = datetime.datetime.utcnow() - datetime.timedelta(days=7)

    for day in range(7):
        start_weekday = last_weekday - datetime.timedelta(days=day)
        if start_weekday.weekday() == 0:
            break

    start_weekday = start_weekday.replace(hour=0, minute=0, second=0, microsecond=0)
    end_weekday = start_weekday + datetime.timedelta(days=6)
    end_weekday = end_weekday.replace(hour=23, minute=59, second=59)
    session = session_maker()
    user = session.query(User).filter_by(id=current_user.id).first()

    if not user.organizations:
        return render_template("stats/base.html", error_message="You do not have any organizations yet.")

    # fix this
    if org_id == 0:
        org_id = user.organizations[0].id

    data_handler = StatsDataExtractor(org_id, start_weekday, end_weekday)

    department_sales_data = data_handler.get_department_sales_data()
    fixed_totalizers_data = data_handler.get_fixed_totalizers()
    plu_sales_data = data_handler.get_plu_sales_data()
    last_100_sales_data = data_handler.get_last_100_sales()
    clerks_breakdown_data = data_handler.get_clerks_breakdown()
    group_sales_total_data = data_handler.get_group_sales_data()
    free_function_data = data_handler.get_free_func()

    data_handler.close_session()
    form = CustomizeStatsForm()
    orgs = user.organizations
    form.organization.choices = [(org.id, org.name) for org in orgs]
    org_name = session.query(Organization).filter_by(id=org_id).first().name
    session.close()

    if form.validate_on_submit():
        org_id = form.organization.data
        return redirect(url_for("stats.show_last_week", org_id=org_id))

    return render_template("stats/base.html",
                           group_sales_total_data=group_sales_total_data,
                           department_sales_data=department_sales_data,
                           fixed_totalizer_data=fixed_totalizers_data,
                           plu_sales_data=plu_sales_data,
                           last_100_sales_data=last_100_sales_data,
                           clerks_breakdown_data=clerks_breakdown_data,
                           free_function_data=free_function_data,
                           form=form,
                           organization_name=org_name
                           )


@mod_stats.route("/<org_id>/this_month", methods=["GET", "POST"])
def show_this_month(org_id):
    """
    Shows data starting from the first day of current month to current day of the month
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
    session = session_maker()
    user = session.query(User).filter_by(id=current_user.id).first()

    if not user.organizations:
        return render_template("stats/base.html", error_message="You do not have any organizations yet.")

    # fix this
    if org_id == 0:
        org_id = user.organizations[0].id

    data_handler = StatsDataExtractor(org_id, start_month_day, end_month_day)

    department_sales_data = data_handler.get_department_sales_data()
    fixed_totalizers_data = data_handler.get_fixed_totalizers()
    plu_sales_data = data_handler.get_plu_sales_data()
    last_100_sales_data = data_handler.get_last_100_sales()
    clerks_breakdown_data = data_handler.get_clerks_breakdown()
    group_sales_total_data = data_handler.get_group_sales_data()
    free_function_data = data_handler.get_free_func()

    data_handler.close_session()
    form = CustomizeStatsForm()
    orgs = user.organizations
    form.organization.choices = [(org.id, org.name) for org in orgs]
    org_name = session.query(Organization).filter_by(id=org_id).first().name
    session.close()

    if form.validate_on_submit():
        org_id = form.organization.data
        return redirect(url_for("stats.show_this_month", org_id=org_id))

    return render_template("stats/base.html",
                           group_sales_total_data=group_sales_total_data,
                           department_sales_data=department_sales_data,
                           fixed_totalizer_data=fixed_totalizers_data,
                           plu_sales_data=plu_sales_data,
                           last_100_sales_data=last_100_sales_data,
                           clerks_breakdown_data=clerks_breakdown_data,
                           free_function_data=free_function_data,
                           form=form,
                           organization_name=org_name
                           )


@mod_stats.route("/<org_id>/last_month", methods=["GET", "POST"])
def show_last_month(org_id):
    """
    Shows data starting from the 1st day of last month

    to the last day of the last month
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

    session = session_maker()
    user = session.query(User).filter_by(id=current_user.id).first()

    if not user.organizations:
        return render_template("stats/base.html", error_message="You do not have any organizations yet.")

    # fix this
    if org_id == 0:
        org_id = user.organizations[0].id

    data_handler = StatsDataExtractor(org_id, start_last_month_day, end_last_month_day)

    department_sales_data = data_handler.get_department_sales_data()
    fixed_totalizers_data = data_handler.get_fixed_totalizers()
    plu_sales_data = data_handler.get_plu_sales_data()
    last_100_sales_data = data_handler.get_last_100_sales()
    clerks_breakdown_data = data_handler.get_clerks_breakdown()
    group_sales_total_data = data_handler.get_group_sales_data()
    free_function_data = data_handler.get_free_func()

    data_handler.close_session()
    form = CustomizeStatsForm()
    orgs = user.organizations
    form.organization.choices = [(org.id, org.name) for org in orgs]
    org_name = session.query(Organization).filter_by(id=org_id).first().name
    session.close()

    if form.validate_on_submit():
        org_id = form.organization.data
        return redirect(url_for("stats.show_last_month", org_id=org_id))

    return render_template("stats/base.html",
                           group_sales_total_data=group_sales_total_data,
                           department_sales_data=department_sales_data,
                           fixed_totalizer_data=fixed_totalizers_data,
                           plu_sales_data=plu_sales_data,
                           last_100_sales_data=last_100_sales_data,
                           clerks_breakdown_data=clerks_breakdown_data,
                           free_function_data=free_function_data,
                           form=form,
                           organization_name=org_name
                           )


@mod_stats.route("/<org_id>/this_quarter", methods=["GET", "POST"])
def show_this_quarter(org_id):
    """
    Shows data depending on current quarter of the year
    """
    now_time = datetime.datetime.utcnow()
    this_year = str(now_time.year)
    this_quarter = (now_time.month - 1) // 3 + 1
    start_month, end_month = calc_quarter_timerange(this_quarter, this_year)
    session = session_maker()
    user = session.query(User).filter_by(id=current_user.id).first()

    if not user.organizations:
        return render_template("stats/base.html", error_message="You do not have any organizations yet.")

    # fix this
    if org_id == 0:
        org_id = user.organizations[0].id

    data_handler = StatsDataExtractor(org_id, start_month, end_month)

    department_sales_data = data_handler.get_department_sales_data()
    fixed_totalizers_data = data_handler.get_fixed_totalizers()
    plu_sales_data = data_handler.get_plu_sales_data()
    last_100_sales_data = data_handler.get_last_100_sales()
    clerks_breakdown_data = data_handler.get_clerks_breakdown()
    group_sales_total_data = data_handler.get_group_sales_data()
    free_function_data = data_handler.get_free_func()

    data_handler.close_session()
    form = CustomizeStatsForm()
    orgs = user.organizations
    form.organization.choices = [(org.id, org.name) for org in orgs]
    org_name = session.query(Organization).filter_by(id=org_id).first().name
    session.close()

    if form.validate_on_submit():
        org_id = form.organization.data
        return redirect(url_for("stats.show_this_quarter", org_id=org_id))

    return render_template("stats/base.html",
                           group_sales_total_data=group_sales_total_data,
                           department_sales_data=department_sales_data,
                           fixed_totalizer_data=fixed_totalizers_data,
                           plu_sales_data=plu_sales_data,
                           last_100_sales_data=last_100_sales_data,
                           clerks_breakdown_data=clerks_breakdown_data,
                           free_function_data=free_function_data,
                           form=form,
                           organization_name=org_name
                           )


@mod_stats.route("/<org_id>/last_quarter", methods=["GET", "POST"])
def show_last_quarter(org_id):
    """
    Shows data depending on current quarter of the year
    """
    lq_time = datetime.datetime.utcnow() - relativedelta(months=3)
    lq_year = str(lq_time.year)
    # last_quarter = (lq_time.month - 1) // 3 + 1
    start_month, end_month = calc_quarter_timerange(lq_time, lq_year)
    session = session_maker()
    user = session.query(User).filter_by(id=current_user.id).first()

    if not user.organizations:
        return render_template("stats/base.html", error_message="You do not have any organizations yet.")

    # fix this
    if org_id == 0:
        org_id = user.organizations[0].id

    data_handler = StatsDataExtractor(org_id, start_month, end_month)

    department_sales_data = data_handler.get_department_sales_data()
    fixed_totalizers_data = data_handler.get_fixed_totalizers()
    plu_sales_data = data_handler.get_plu_sales_data()
    last_100_sales_data = data_handler.get_last_100_sales()
    clerks_breakdown_data = data_handler.get_clerks_breakdown()
    group_sales_total_data = data_handler.get_group_sales_data()
    free_function_data = data_handler.get_free_func()

    data_handler.close_session()
    form = CustomizeStatsForm()
    orgs = user.organizations
    form.organization.choices = [(org.id, org.name) for org in orgs]
    org_name = session.query(Organization).filter_by(id=org_id).first().name
    session.close()

    if form.validate_on_submit():
        org_id = form.organization.data
        return redirect(url_for("stats.show_last_quarter", org_id=org_id))

    return render_template("stats/base.html",
                           department_sales_data=department_sales_data,
                           fixed_totalizer_data=fixed_totalizers_data,
                           plu_sales_data=plu_sales_data,
                           last_100_sales_data=last_100_sales_data,
                           clerks_breakdown_data=clerks_breakdown_data,
                           group_sales_total_data=group_sales_total_data,
                           free_function_data=free_function_data,
                           form=form,
                           organization_name=org_name
                           )
