from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    email = EmailField('Логин / Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(),
                                                   Length(min=6, max=32,
                                                          message="Пароль должен быть от 6 до 32 символов")])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField('Войти')
