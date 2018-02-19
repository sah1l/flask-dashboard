from flask import Blueprint, request, flash, redirect, url_for, render_template
from flask_login import current_user

from app import session_maker
from app.models import Organization
from app.mod_auth.models import User
from app.mod_auth.forms import UserRegistrationForm, OrgCreateForm

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
    session = session_maker()
    form = UserRegistrationForm()
    orgs = session.query(Organization).all()
    empty_choice = [(0, " " * 10)]
    form.organizations.choices = empty_choice + [(org.id, org.name) for org in orgs]
    if form.validate_on_submit():
        # additional validation on uniqueness subject
        user = session.query(User).filter_by(email=form.email.data).first()
        if user:
            form.email.errors.append("There'is already a user with this email. Please, choose another one.")
            return render_template("admin_panel/create_user.html", form=form)

        orgs = session.query(Organization).filter_by(id=form.organizations.data).all()  # temporary solution, fix this
        user = User(username=form.username.data,
                    email=form.email.data,
                    is_admin=form.is_admin.data,
                    organizations=orgs
                    )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        session.close()
        return redirect(url_for("admin.show_panel"))
    else:
        print('not valid')
    return render_template('admin_panel/create_user.html', form=form)


@mod_admin.route("/edit_user/<user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    form = UserRegistrationForm()
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
            user.organization = form.organization.data
            session.add(user)
            session.commit()
            session.close()
            return redirect(url_for("admin.show_panel"))
        else:
            return render_template("admin_panel/edit_user.html", form=form, user=user)


@mod_admin.route("/delete_user/<user_id>", methods=["GET", "POST"])
def delete_user(user_id):
    session = session_maker()
    session.query(User).filter_by(id=user_id).delete()
    session.commit()
    session.close()
    return redirect(url_for("admin.show_panel"))


@mod_admin.route("/list_organizations", methods=["GET"])
def list_organizations():
    session = session_maker()
    orgs = session.query(Organization).all()
    session.close()
    return render_template("admin_panel/list_organizations.html", orgs=orgs)


@mod_admin.route("/add_organization", methods=["GET", "POST"])
def add_organization():
    session = session_maker()
    form = OrgCreateForm()
    users = session.query(User).all()
    empty_choice = [(0, " " * 10)]
    form.users.choices = empty_choice + [(user.id, user.email) for user in users]
    if form.validate_on_submit():
        users = session.query(User).filter_by(id=form.users.data).all()  # fix this, temporary solution
        org = Organization(name=form.name.data,
                           data_dir=form.data_dir.data,
                           users=users)
        session.add(org)
        session.commit()
        session.close()
        return redirect(url_for("admin.add_organization"))
    else:
        print('errors in add org')
    return render_template("admin_panel/create_organization.html", form=form)


@mod_admin.route("/edit_organization/<org_id>", methods=["GET", "POST"])
def edit_organization(org_id):
    pass


@mod_admin.route("/delete_organization/<org_id>", methods=["GET", "POST"])
def delete_organization(org_id):
    pass
