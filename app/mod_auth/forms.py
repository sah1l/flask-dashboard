from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from app import session_maker
from app.models import Organization
from app.mod_auth.models import User


class LoginForm(FlaskForm):
    """
    Login Form
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class UserRegistrationForm(FlaskForm):
    """
    Registration form for new user
    """
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Is Admin', default=False)
    organizations = SelectField('Organization', coerce=int)
    # organizations = QuerySelectField(query_factory=Organization.objects.all,
    #                                  get_pk=lambda u: u.id,
    #                                  get_label=lambda u: u.username)
    submit = SubmitField('Add user')


class OrgCreateForm(FlaskForm):
    """
    Create form for an organization
    """
    name = StringField('Organization Name', validators=[DataRequired()])
    data_dir = StringField('Data directory', validators=[DataRequired()])
    users = SelectField('User', coerce=int)
    submit = SubmitField('Add organization')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.org = None

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        session = session_maker()
        org = session.query(Organization).filter_by(name=self.name.data).first()
        if org:
            self.name.errors.append("An organization with this name exists already.")
            session.close()
            return False

        org = session.query(Organization).filter_by(data_dir=self.data_dir.data).first()
        if org:
            self.data_dir.errors.append("Please choose another directory.")
            session.close()
            return False

        session.close()
        return True
