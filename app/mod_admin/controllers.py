from flask import Blueprint, redirect, url_for, render_template
from flask_login import current_user

from app import session_commit, session_add, session_delete
from app.models import Organization, User
from app.mod_admin.forms import OrgInfoForm, OrgCreateForm, UserCreateForm, UserInfoForm, EmailForm, PasswordForm

# define Blueprint for admin module
mod_admin = Blueprint('admin', __name__, url_prefix='/admin_panel')


@mod_admin.before_request
def check_authenticated_user():
    """
    Restrict access to admin panel to non-admin users
    """
    if not current_user.is_authenticated:  # user is not authenticated
        return redirect(url_for("auth.login"))
    else:
        if not current_user.is_admin:  # user is not admin
            org_id = current_user.organizations[0].id
            return redirect(url_for("stats.show_today", org_id=org_id))


@mod_admin.route("/", methods=["GET"])
def show_panel():
    users = User.query.all()
    return render_template("admin_panel/list_users.html", users=users)


@mod_admin.route("/add_user", methods=["GET", "POST"])
def add_user():
    form = UserCreateForm()
    orgs = Organization.query.all()
    form.organizations.choices = [(org.id, org.name) for org in orgs]

    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    is_admin=form.is_admin.data,
                    )
        user.set_password(form.password.data)
        orgs = []

        for org_id in form.organizations.data:
            org = Organization.query.filter_by(id=org_id).first()
            orgs.append(org)

        user.organizations = orgs
        session_add(user)
        session_commit()

        return redirect(url_for("admin.show_panel"))

    return render_template('admin_panel/create_user.html', form=form)


@mod_admin.route("/edit_user/<user_id>", methods=["GET", "POST"])
def change_userinfo(user_id):
    form = UserInfoForm()
    user = User.query.filter_by(id=user_id).first()
    orgs = Organization.query.all()
    form.organizations.choices = [(org.id, org.name) for org in orgs]

    if form.validate_on_submit():
        user.username = form.username.data
        user.is_admin = form.is_admin.data
        orgs = []

        for org_id in form.organizations.data:
            org = Organization.query.filter_by(id=org_id).first()
            orgs.append(org)

        user.organizations = orgs
        session_commit()

        return redirect(url_for("admin.show_panel"))

    return render_template("admin_panel/change_userinfo.html", form=form, user=user)


@mod_admin.route("/edit_user/<user_id>/email", methods=["GET", "POST"])
def change_email(user_id):
    form = EmailForm()
    user = User.query.filter_by(id=user_id).first()

    if form.validate_on_submit():
        user.email = form.email.data
        session_commit()

        return redirect(url_for("admin.show_panel"))

    return render_template("admin_panel/change_email.html", form=form, user=user)


@mod_admin.route("/edit_user/<user_id>/password", methods=["GET", "POST"])
def change_password(user_id):
    form = PasswordForm()
    user = User.query.filter_by(id=user_id).first()

    if form.validate_on_submit():
        user.set_password(form.password.data)
        session_commit()

        return redirect(url_for("admin.show_panel"))

    return render_template("admin_panel/change_password.html", form=form, user=user)


@mod_admin.route("/delete_user/<user_id>", methods=["GET", "POST"])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    session_delete(user)
    session_commit()

    return redirect(url_for("admin.show_panel"))


@mod_admin.route("/list_organizations", methods=["GET"])
def list_organizations():
    orgs = Organization.query.all()

    return render_template("admin_panel/list_organizations.html", orgs=orgs)


@mod_admin.route("/add_organization", methods=["GET", "POST"])
def add_organization():
    form = OrgCreateForm()
    users = User.query.all()
    # empty_choice = [(0, " " * 10)]
    form.users.choices = [(user.id, user.email) for user in users]

    if form.validate_on_submit():
        org = Organization(name=form.name.data,
                           data_dir=form.data_dir.data)
        users = []

        for user_id in form.users.data:
            user = User.query.filter_by(id=user_id).first()
            users.append(user)

        org.users = users
        session_add(org)
        session_commit()

        return redirect(url_for("admin.add_organization"))

    return render_template("admin_panel/create_organization.html", form=form)


@mod_admin.route("/edit_organization/<org_id>", methods=["GET", "POST"])
def edit_organization(org_id):
    form = OrgInfoForm()
    users = User.query.all()
    form.users.choices = [(user.id, user.email) for user in users]
    org = Organization.query.filter_by(id=org_id).first()

    if form.validate_on_submit():
        org.name = form.name.data
        org.data_dir = form.data_dir.data
        users = []

        for user_id in form.users.data:
            user = User.quuery.filter_by(id=user_id).first()
            users.append(user)

        org.users = users
        session_commit()

        return redirect(url_for("admin.list_organizations"))

    return render_template("admin_panel/edit_organization.html", form=form, org=org)


@mod_admin.route("/delete_organization/<org_id>", methods=["GET", "POST"])
def delete_organization(org_id):
    org = Organization.query.filter_by(id=org_id).first()
    session_delete(org)
    session_commit()

    return redirect(url_for("admin.list_organizations"))
