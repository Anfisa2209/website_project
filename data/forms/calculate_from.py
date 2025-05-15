from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from wtforms_components import ColorField


class CalculateFrom(FlaskForm):
    width = IntegerField('Ширина', validators=[DataRequired()])
    height = IntegerField('Длина', validators=[DataRequired(message="Обязательное поле"),
                                               NumberRange(min=2100, max=3000,
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
    handle_color = RadioField("Выберите цвет",
                              choices=[
                                  (1, "Серебро"),
                                  (2, "Бронза"),
                                  (3, "Белый"),
                                  (4, "Коричневый")
                              ],
                              validators=[DataRequired()])
    handle_models = RadioField("Выберите модель ручки",
                               choices=[
                                   (1, "Односторонняя"),
                                   (2, "Двухсторонняя")
                               ],
                               validators=[DataRequired()])
    color = ColorField('Выберите цвет портала', default='#ffffff')

    calculate = SubmitField('Рассчитать')

    def __init__(self, scheme_limits=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if scheme_limits:
            self.width.validators = [
                DataRequired(message="Обязательное поле"),
                NumberRange(
                    min=scheme_limits['min_width'],
                    max=scheme_limits['max_width'],
                    message=f"Ширина должна быть между {scheme_limits['min_width']} и {scheme_limits['max_width']} мм"
                )
            ]
