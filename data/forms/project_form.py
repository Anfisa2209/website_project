from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, FileField
from wtforms.validators import DataRequired


class ProjectForm(FlaskForm):
    name = StringField('Название проекта', validators=[DataRequired()])
    project_text = TextAreaField("Расскажите о проекте...", validators=[DataRequired()])
    image_photo = FileField('Добавьте фото')
    submit = SubmitField('Изменить')

    def __init__(self, photo_required=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if photo_required:
            self.image_photo.validators = [DataRequired()]
            self.submit.label.text = 'Добавить'
