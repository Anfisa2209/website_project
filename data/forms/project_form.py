from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, FileField
from wtforms.validators import DataRequired


class ProjectForm(FlaskForm):
    name = StringField('Название проекта', validators=[DataRequired()])
    project_text = TextAreaField("Расскажите о новом проекте...", validators=[DataRequired()])
    image_photo = FileField('Добавьте фото', validators=[DataRequired()])
    submit = SubmitField('Добавить')
