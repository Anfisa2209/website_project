from flask import Flask, render_template, url_for, redirect, abort, request, make_response
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from flask_restful import Api
from requests import get

from api.users.users_resource import UsersResource, UsersListResource
from data import db_session
from data.forms.login_form import LoginForm
from data.forms.register_form import RegisterForm
from data.users import User
from tools.service_files import return_files, create_tuple, SERVER_URL
from tools.scheme_list import SCHEME_LIST

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

api_init = Api(app)
api_init.add_resource(UsersResource, '/api/users/<int:user_id>')
api_init.add_resource(UsersListResource, '/api/users')

login_manager = LoginManager()
login_manager.init_app(app)



@app.context_processor
def inject_schemes():
    # Передаем список во все шаблоны
    return {"scheme_list": SCHEME_LIST}


@login_manager.user_loader
def load_user(user_id):
    db_ses = db_session.create_session()
    return db_ses.get(User, user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/')
def index():
    css_file = url_for('static', filename='css/main_page.css')
    scheme_images = [i.split("/")[-1] for i in return_files('static/img/scheme')]
    pair_images = create_tuple(scheme_images)
    hs_info = open('static/infos/hs_info', encoding='utf-8').read()
    return render_template('projects_page.html',
                           title='Главная страница',
                           css_url=css_file,
                           scheme_images=pair_images,
                           hs_info=hs_info)


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    css_file = url_for('static', filename='css/login.css')

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               email_message="Неправильный логин или пароль",
                               form=form, css_url=css_file)
    return render_template('login.html', title='Авторизация', form=form, css_url=css_file)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    css_file = url_for('static', filename='css/login.css')
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   password_message="Пароли не совпадают", css_url=css_file)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   email_message="Такой пользователь уже есть", css_url=css_file)
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user, remember=form.remember_me.data)
        return redirect('/')
    return render_template('register.html', css_url=css_file, title='Регистрация', form=form)


@app.route('/profile')
@login_required
def profile():
    user_id = current_user.id
    data = get(f"{SERVER_URL}/api/users/{user_id}").json()
    if not data.get('users'):
        return abort(404)
    email = data['users'][0]['email']
    return render_template('profile.html', css_url=url_for('static', filename='css/profile.css'), email=email)


def main():
    db_session.global_init('db/hs_portal.db')
    app.run(port=8080, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()
