from flask import Blueprint, request, flash, redirect, url_for, render_template
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


@mod_admin.route("/edit_user/<user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    form = RegistrationForm()
    session = session_maker()
    user = session.query(User).filter_by(id=user_id).first()
    if request.method == "GET":
        session.close()
        return render_template("admin_panel/edit_user.html", form=form, user=user)
    else:
        if form.validate_on_submit():
            user.username=form.username.data
            user.email=form.email.data
            user.set_password(form.password.data)
            user.is_admin = form.is_admin.data
            session.add(user)
            session.commit()
            session.close()
            return redirect(url_for("admin.show_panel"))
        else:
            return render_template("admin_panel/edit_user.html", form=form, user=user)


@mod_admin.route("/delete_user/<user_id>", methods=["GET", "POST"])
def delete_user(user_id):
    print('still working')
    session = session_maker()
    session.query(User).filter_by(id=user_id).delete()
    session.commit()
    session.close()
    return redirect(url_for("admin.show_panel"))