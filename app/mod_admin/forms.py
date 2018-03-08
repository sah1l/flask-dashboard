from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, PasswordField, BooleanField, widgets
from wtforms.validators import DataRequired, Email, EqualTo, Length

from app.models import Organization, User


class UserInfoForm(FlaskForm):
    """
    Edit user form

    Fields:

    - username (string field)
    - is_admin (checkbox)
    - organizations (select multiple field)
    """
    username = StringField('Username', validators=[DataRequired()])
    is_admin = BooleanField('Is Admin', default=False)
    organizations = SelectMultipleField('Organizations',
                                        widget=widgets.TableWidget(with_table_tag=True),
                                        option_widget=widgets.CheckboxInput(),
                                        coerce=int)
    submit = SubmitField('Update')


class EmailForm(FlaskForm):
    """
    Edit email form

    Fields:

    -email (string field)
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update email')


class PasswordForm(FlaskForm):
    """
    Edit password form

    Fields:

    - type password (password field)
    - retype password (password field)
    """
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update password')


class UserCreateForm(UserInfoForm, EmailForm, PasswordForm):
    """
    Registration form for new user.

    Consists of UserInfoForm, EmailForm, PasswordForm and personal submit button.
    Custom validation.
    """
    submit = SubmitField('Add user')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        """
        Checks if user exists already (by email)

        :return: If the user exists already, return False, else True
        """
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(email=self.email.data).first()

        if user:
            self.email.errors.append("This email is already taken.")
            return False

        return True


class OrgInfoForm(FlaskForm):
    """
    Edit Organization information form

    Field:

    - name (string field)
    - data directory (string field)
    - users (select multiple field)
    - submit button
    """
    name = StringField('Organization Name', validators=[DataRequired()])
    data_dir = StringField('Data directory', validators=[DataRequired()])
    users = SelectMultipleField('Users',
                                widget=widgets.TableWidget(with_table_tag=True),
                                option_widget=widgets.CheckboxInput(),
                                coerce=int)
    submit = SubmitField('Save')


class OrgCreateForm(OrgInfoForm):
    """
    Create form for organization

    Custom validation
    """

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.org = None

    def validate(self):
        """
        Checks if Organization name and data directory are valid
        :return: True if both fields are valid, False if name or data directory are not valid
        """
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        org = Organization.query.filter_by(name=self.name.data).first()
        if org:
            self.name.errors.append("An organization with this name exists already.")
            return False

        org = Organization.query.filter_by(data_dir=self.data_dir.data).first()
        if org:
            self.data_dir.errors.append("Please choose another directory.")
            return False

        return True