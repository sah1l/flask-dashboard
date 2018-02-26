import datetime
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, DateTimeField
from wtforms.validators import Optional


class CustomizeStatsForm(FlaskForm):
    organization = SelectField("Select Office", coerce=int)
    submit = SubmitField("Submit")


class CustomTimeSliceForm(FlaskForm):
    start_date = DateTimeField("Start date and time",
                               validators=[Optional()],
                               default=datetime.datetime.now().replace(hour=0, minute=0, second=0))
    end_date = DateTimeField("End date and time",
                             validators=[Optional()],
                             default=datetime.datetime.now().replace(hour=23, minute=59, second=59))
    submit = SubmitField("Submit")
