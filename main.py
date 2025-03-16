import os

from flask import Flask, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    astronaut_id = StringField('ID астронавта', validators=[DataRequired()])
    astronaut_password = PasswordField('Пароль астронавта', validators=[DataRequired()])
    cap_id = StringField('ID капитана', validators=[DataRequired()])
    cap_password = PasswordField('Пароль капитана', validators=[DataRequired()])
    submit = SubmitField('Доступ')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def return_files(path):
    if not os.path.exists(path):
        raise ValueError(f"Путь {path} не найден")
    file_list = []
    for currentdir, dirs, files in os.walk(path):
        for file in files:
            file_list.append(f'{path}/{file}')
    return file_list


def create_tuple(data, n=2):
    result = []
    while data:
        result.append(tuple(data[:n]))
        del data[:n]
    return result


@app.route('/')
def index():
    css_file = url_for('static', filename='css/main_page.css')
    scheme_images = [i.split("/")[-1] for i in return_files('static/img/scheme')]
    pair_images = create_tuple(scheme_images)
    links = create_tuple(['http://127.0.0.1:8080/scheme/' + letter for letter in ['A', 'C', 'E', 'G', 'L']])
    hs_info = open('static/infos/hs_info', encoding='utf-8').read()
    return render_template('projects_page.html',
                           title='Главная страница',
                           css_url=css_file,
                           scheme_images=pair_images,
                           hs_info=hs_info,
                           links=links)


@app.route('/scheme/<image_id>')
def scheme_details(image_id):
    try:
        css_file = url_for('static', filename='css/scheme.css')
        image_list = ['/'.join(i.split("/")[1:]) for i in return_files(f'static/img/carousel/{image_id}')]
        return render_template('details.html', title=f'Схема {image_id}', css_url=css_file, image_id=image_id,
                               image_list=image_list)
    except Exception:
        css_file = url_for('static', filename='css/style.css')

        return render_template('error.html', image_id=image_id, title='Ошибка', css_url=css_file)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
