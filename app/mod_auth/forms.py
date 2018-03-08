from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email

from app.models import User


class LoginForm(FlaskForm):
    """
    Login Form for user
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        """
        Checks user's email
        If email does not exist, show an error
        :return:
        """
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(email=self.email.data).first()
        if not user:
            self.email.errors.append("This email is not registered.")
            return False

        return True
