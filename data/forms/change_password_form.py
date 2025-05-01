from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Введите старый пароль',
                                 validators=[DataRequired(),
                                             Length(min=6, max=32,
                                                    message="Пароль должен быть от 6 до 32 символов")])
    new_password = PasswordField('Придумайте новый пароль',
                                 validators=[DataRequired(),
                                             Length(min=6, max=32,
                                                    message="Пароль должен быть от 6 до 32 символов")])
    repeat_new_password = PasswordField('Повторите новый пароль',
                                        validators=[DataRequired(),
                                                    Length(min=6, max=32,
                                                           message="Пароль должен быть от 6 до 32 символов")])
    submit = SubmitField('Изменить пароль')
