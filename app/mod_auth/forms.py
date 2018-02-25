from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField


class LoginForm(FlaskForm):
    """
    Login Form
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')
