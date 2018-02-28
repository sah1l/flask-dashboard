from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import current_user, login_user, logout_user

from app import session_maker
from app.models import Organization
from app.mod_auth.models import User
from app.mod_auth.forms import LoginForm


# define Blueprint for auth module
mod_auth = Blueprint('auth', __name__, url_prefix='/login')


@mod_auth.route("/", methods=["GET", "POST"])
def login():
    """
    Logging in

    If successful, statistics for current day is shown (/statistics/show_today)
    """
    session = session_maker()
    if current_user.is_authenticated:
        user = session.query(User).filter_by(email=current_user.email).first()

        # change this
        if user.organizations:
            org_id = user.organizations[0].id
        else:
            org_id = 0
        session.close()
        import datetime
        return redirect(url_for('stats.show_last_quarter', org_id=org_id)) ################################

    form = LoginForm()
    if form.validate_on_submit():
        user = session.query(User).filter_by(email=form.email.data).first()

        # change this
        if user.organizations:
            org_id = user.organizations[0].id
        else:
            org_id = 0

        session.close()
        if user is None or not user.check_password(form.password.data):
            form.password.errors.append("Email or password are incorrect.")
            return render_template('auth/login.html', title='Sign In', form=form)

        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('stats.show_today', org_id=org_id))

    return render_template('auth/login.html', title='Sign In', form=form)


@mod_auth.route('/logout')
def logout():
    """
    Logging out

    If successful, shows login page
    """
    logout_user()
    return redirect(url_for('auth.login'))
