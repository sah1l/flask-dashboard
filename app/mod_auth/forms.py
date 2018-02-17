from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo

from app import session_maker
from app.models import Organization


class LoginForm(FlaskForm):
    """
    Login Form
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
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
    organization = SelectField('Organization')
    submit = SubmitField('Submit')


class OrgCreateForm(FlaskForm):
    """
    Create form for an organization
    """
    name = StringField('Organization Name', validators=[DataRequired()])
    data_dir = StringField('Data directory', validators=[DataRequired()])
    users = SelectField('User')
