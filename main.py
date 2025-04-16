from flask import Flask, render_template, url_for, redirect, abort, request, flash
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from flask_restful import Api
from requests import get, post, delete, put

from api.comments.comment_resource import CommentsListResource, CommentsResource
from api.users.users_resource import UsersResource, UsersListResource
from data import db_session
from data.forms.calculate_from import CalculateFrom
from data.forms.comment_form import CommentForm
from data.forms.login_form import LoginForm
from data.forms.register_form import RegisterForm
from data.models.users import User
from tools.scheme_list import SCHEME_LIST
from tools.service_files import return_files, create_tuple, SERVER_URL, get_comments
from tools.sqlite import return_scheme_id

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

api_init = Api(app)
API_PREFIX = 'api'

api_init.add_resource(UsersResource, f'/{API_PREFIX}/users/<int:user_id>')
api_init.add_resource(UsersListResource, f'/{API_PREFIX}/users')
api_init.add_resource(CommentsListResource, f'/{API_PREFIX}/comments')
api_init.add_resource(CommentsResource, f'/{API_PREFIX}/comments/<int:comment_id>')

login_manager = LoginManager()
login_manager.init_app(app)


@app.context_processor
def inject_schemes():
    # Передаем список во все шаблоны
    return {"scheme_list": SCHEME_LIST, "css_url": url_for('static', filename='css/scheme.css')}


@login_manager.user_loader
def load_user(user_id):
    db_ses = db_session.create_session()
    return db_ses.get(User, user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/delete_comment/<int:comment_id>,<image_id>')
def delete_comment(comment_id, image_id):
    if delete(f'{SERVER_URL}/api/comments/{comment_id}').json().get("success"):
        flash('Комментарий удален')
        return redirect(f'/scheme/{image_id}')
    return


@app.route('/update_comment/<int:comment_id>', methods=['POST'])
def update_comment(comment_id):
    comment = get(f"{SERVER_URL}/api/comments/{comment_id}").json()
    if not comment.get('comments'):
        abort(404)
    if comment['comments'][0]['user_id'] != current_user.id:
        abort(403)
    comment = comment['comments'][0]
    new_text = request.form.get('text')
    user_id, scheme_name = comment['user_id'], comment['scheme_name']
    put(f'http://127.0.0.1:8080/api/comments/{comment_id}', json={'text': new_text,
                                                                  'user_id': user_id,
                                                                  'scheme_name': scheme_name})
    link = f'/scheme/{scheme_name}'
    return redirect(link)


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


@app.route('/scheme/<image_id>', methods=['GET', 'POST'])
def scheme_details(image_id):
    form = CommentForm()
    if request.method == 'POST' and form.validate_on_submit():
        post(f'{SERVER_URL}/api/comments', json={
            'scheme_name': image_id,
            "text": form.text.data,
            'user_id': current_user.id})
        return redirect(f'/scheme/{image_id}')
    comments = get_comments(image_id)
    css_file = url_for('static', filename='css/scheme.css')
    image_list = ['/'.join(i.split("/")[1:]) for i in return_files(f'static/img/carousel/{image_id}')]
    return render_template('details.html', title=f'Схема {image_id}', css_url=css_file, image_id=image_id,
                           image_list=image_list, comments=comments, form=form,
                           count_comments=len(comments))


@app.route('/calculate/<scheme>', methods=['GET', 'POST'])
def calculate(scheme):
    form = CalculateFrom()
    if form.validate_on_submit():
        ...
    if scheme == "scheme":  # если схему не выбрали и перешли через меню
        return render_template('calculate.html', scheme_id=scheme)
    data = {"scheme": scheme, "scheme_id": return_scheme_id(scheme), "form": form,
            'css_url': url_for('static', filename='css/calculate.css')}
    return render_template('calculate.html', **data)


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
        user = User(email=form.email.data, name=form.name.data)
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
