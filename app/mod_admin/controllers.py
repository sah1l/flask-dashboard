from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import current_user

from app import session_maker
from app.mod_auth.models import User
from app.mod_auth.forms import RegistrationForm

# define Blueprint for admin module
mod_admin = Blueprint('admin', __name__, url_prefix='/admin_panel')


@mod_admin.before_request
def check_authenticated_user():
    """
    Restrict access to admin panel to non-admin users
    """
    if not current_user.is_authenticated:  # user is not authenticated
        flash("User is not recognized!")
        return redirect(url_for("auth.login"))
    else:
        if not current_user.is_admin:  # user is not admin
            flash("You don't have admin rights to view this page!")
            return redirect(url_for("stats.show_today"))


@mod_admin.route("/", methods=["GET"])
def show_panel():
    session = session_maker()
    users = session.query(User).all()
    session.close()
    return render_template("admin_panel/list_users.html", users=users)


@mod_admin.route("/add_user", methods=["GET", "POST"])
def add_user():
    form = RegistrationForm()
    if form.validate_on_submit():
        session = session_maker()
        user = User(username=form.username.data, email=form.email.data, is_admin=form.is_admin.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        session.close()
        flash("Registration completed successfully.")
        return redirect(url_for("admin.add_user"))
    return render_template('admin_panel/create_user.html', form=form)
