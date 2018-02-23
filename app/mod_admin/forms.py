from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, PasswordField, BooleanField, widgets
from wtforms.validators import DataRequired, Email, EqualTo, Length

from app import session_maker
from app.models import Organization
from app.mod_auth.models import User


class UserCreateForm(FlaskForm):
    """
    Registration form for new user
    """
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Is Admin', default=False)
    organizations = SelectMultipleField('Organizations',
                                        widget=widgets.TableWidget(with_table_tag=True),
                                        option_widget=widgets.CheckboxInput(),
                                        coerce=int)
    # organizations = QuerySelectField(query_factory=Organization.objects.all,
    #                                  get_pk=lambda u: u.id,
    #                                  get_label=lambda u: u.username)
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        session = session_maker()
        user = session.query(User).filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("This email is already taken.")
            session.close()
            return False

        return True


class UserEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    is_admin = BooleanField('Is Admin', default=False)
    organizations = SelectMultipleField('Organizations',
                                        widget=widgets.TableWidget(with_table_tag=True),
                                        option_widget=widgets.CheckboxInput(),
                                        coerce=int)
    submit = SubmitField('Save')

class OrgCreateForm(FlaskForm):
    """
    Create form for an organization
    """
    name = StringField('Organization Name', validators=[DataRequired()])
    data_dir = StringField('Data directory', validators=[DataRequired()])
    users = SelectMultipleField('Users',
                                widget=widgets.TableWidget(with_table_tag=True),
                                option_widget=widgets.CheckboxInput(),
                                coerce=int)
    submit = SubmitField('Save')

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