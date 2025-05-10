from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class EditTextForm(FlaskForm):
    text = TextAreaField(validators=[DataRequired()])

    submit = SubmitField('Сохранить')
