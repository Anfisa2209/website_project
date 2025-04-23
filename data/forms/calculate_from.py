from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField, IntegerField, ColorField
from wtforms.validators import DataRequired, NumberRange


class CalculateFrom(FlaskForm):
    width = IntegerField('Ширина', validators=[DataRequired(),
                                               NumberRange(min=1500, max=15000,
                                                           message='Значение должно быть между %(min)s и %(max)s')])
    height = IntegerField('Длина', validators=[DataRequired(),
                                               NumberRange(min=2300, max=3000,
                                                           message='Значение должно быть между %(min)s и %(max)s')])
    materials = RadioField("Выберите материал",
                           choices=[
                               (1, "Дуб"),
                               (2, "Сосна"),
                               (3, "Лиственница")
                           ],
                           validators=[DataRequired()])
    steklopakets = RadioField("Выберите стеклопакет",
                              choices=[
                                  (1, "Однокамерный"),
                                  (2, "Двухкамерный"),
                              ],
                              validators=[DataRequired()])
    handle_color = RadioField("Выберите материал",
                              choices=[
                                  (1, "Серебро"),
                                  (2, "Бронза"),
                                  (3, "Белый"),
                                  (4, "Коричневый")
                              ],
                              validators=[DataRequired()])
    handle_models = RadioField("Выберите материал",
                               choices=[
                                   (1, "Односторонняя"),
                                   (2, "Двухсторонняя")
                               ],
                               validators=[DataRequired()])
    color = ColorField('Выберите цвет портала', default='#ffffff')

    calculate = SubmitField('Рассчитать')
