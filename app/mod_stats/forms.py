from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField


class CustomizeStatsForm(FlaskForm):
    organization = SelectField('Select Office', coerce=int)
    submit = SubmitField("Submit")
