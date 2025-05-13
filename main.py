from flask import Flask, render_template, url_for, redirect, abort, request, flash
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from flask_restful import Api
from requests import post, put, delete

from admin.routes import admin_bp
from api.comments.comment_resource import CommentsListResource, CommentsResource
from api.projects.project_resource import ProjectsResource, ProjectsListResource
from api.users.users_resource import UsersResource, UsersListResource
from data import db_session
from data.forms.calculate_from import CalculateFrom
from data.forms.change_password_form import ChangePasswordForm
from data.forms.comment_form import CommentForm
from data.forms.login_form import LoginForm
from data.forms.register_form import RegisterForm
from data.models.users import User
from error import error_handlers
from tools.scheme_list import SCHEME_LIST, VIDEO_LIST
from tools.service_files import *
from tools.sqlite import return_scheme_id, return_min_max_size, calculate_total_price, add_order, \
    return_orders_by_user_id

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Максимальный размер файла
app.register_blueprint(admin_bp)

api_init = Api(app)
API_PREFIX = 'api'

error_handlers(app)

api_init.add_resource(UsersResource, f'/{API_PREFIX}/users/<int:user_id>')
api_init.add_resource(UsersListResource, f'/{API_PREFIX}/users')
api_init.add_resource(CommentsListResource, f'/{API_PREFIX}/comments')
api_init.add_resource(CommentsResource, f'/{API_PREFIX}/comments/<int:comment_id>')

api_init.add_resource(ProjectsListResource, f'/{API_PREFIX}/projects')
api_init.add_resource(ProjectsResource, f'/{API_PREFIX}/projects/<int:project_id>')

login_manager = LoginManager()
login_manager.init_app(app)


@app.context_processor
def inject():
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
    comment = get(f"{SERVER_URL}/{API_PREFIX}/comments/{comment_id}").json()
    if not comment.get('comments'):
        abort(404)
    user_id = comment['comments'][0]['user_id']
    if not current_user.is_admin and user_id != current_user.id:
        abort(403)
    if delete(f'{SERVER_URL}/{API_PREFIX}/comments/{comment_id}').json().get("success"):
        flash('Комментарий удален', 'success')
    else:
        flash('Не удалось удалить комментарий', 'danger')
    return redirect(f'/scheme/{image_id}')


@app.route('/update_comment/<int:comment_id>', methods=['POST'])
def update_comment(comment_id):
    comment = get(f"{SERVER_URL}/{API_PREFIX}/comments/{comment_id}").json()
    if not comment.get('comments'):
        abort(404)
    if comment['comments'][0]['user_id'] != current_user.id:
        abort(403)
    comment = comment['comments'][0]
    new_text = request.form.get('text')
    user_id, scheme_name = comment['user_id'], comment['scheme_name']
    put(f'{SERVER_URL}/{API_PREFIX}/comments/{comment_id}', json={'text': new_text,
                                                                  'user_id': user_id,
                                                                  'scheme_name': scheme_name})
    link = f'/scheme/{scheme_name}'
    flash('Комментарий изменён', 'success')
    return redirect(link)


@app.route('/')
def index():
    css_file = url_for('static', filename='css/main_page.css')
    scheme_images = [i.split("/")[-1] for i in return_files('static/img/scheme')]
    pair_images = create_tuple(scheme_images)
    hs_info = open('static/infos/hs_info.txt', encoding='utf-8').read()
    return render_template('projects_page.html',
                           title='Главная страница',
                           css_url=css_file,
                           scheme_images=pair_images,
                           hs_info=hs_info)


@app.route('/scheme/<image_id>', methods=['GET', 'POST'])
def scheme_details(image_id):
    if image_id not in SCHEME_LIST:
        abort(404)
    form = CommentForm()
    if request.method == 'POST' and form.validate_on_submit():
        post(f'{SERVER_URL}/api/comments', json={
            'scheme_name': image_id,
            "text": form.text.data,
            'user_id': current_user.id})
        return redirect(f'/scheme/{image_id}')
    comments = get_comments(image_id)
    css_file = url_for('static', filename='css/scheme.css')
    try:
        text_scheme = open(f'static/infos/schemes_text/{image_id}.txt', encoding='utf-8').read()
    except FileNotFoundError:
        text_scheme = "К сожалению, текста для это схемы у нас еще нет..."
    image_list = ['/'.join(i.split("/")[1:]) for i in return_files(f'static/img/carousel/{image_id}')]
    video_link = VIDEO_LIST.get(image_id, 'Video Not Found')
    data = {'title': f"Схема {image_id}", 'form': form,
            'css_url': css_file, 'image_id': image_id, 'image_list': image_list, 'video_link': video_link,
            'comments': comments, "count_comments": len(comments), 'text_scheme': text_scheme}
    return render_template('details.html', **data)


@app.route('/calculate/<scheme>', methods=['GET', 'POST'])
def calculate(scheme):
    if scheme == "scheme":  # если схему не выбрали и перешли через меню
        return render_template('calculate.html', scheme_id=scheme, form=CalculateFrom(), min_size=(), max_size=())
    if scheme not in SCHEME_LIST:
        abort(404)
    scheme_id = return_scheme_id(scheme)
    min_size, max_size = return_min_max_size(scheme)
    scheme_limits = {'min_width': min_size[0], 'max_width': max_size[0]} if scheme_id else None
    form = CalculateFrom(scheme_limits=scheme_limits)
    if form.validate_on_submit():
        form_data = {
            'width': int(form.width.data),
            'height': int(form.height.data),
            'material': int(form.materials.data),
            'steklopakets': int(form.steklopakets.data),
            'handle_color': int(form.handle_color.data),
            'handle_models': int(form.handle_models.data),
            'portal_color': str(form.color.data),
            'scheme_id': scheme_id
        }

        price = str(calculate_total_price(form_data)) + '₽'

        parameters = {"Ширина": form_data['width'], 'Длина': form_data['height'],
                      'Модель ручки': handle_models[form_data['handle_models']],
                      "Цвет ручки": colors_ids[form_data['handle_color']], "Материал": materials[form_data['material']],
                      "Цвет портал": form_data['portal_color']}
        data = {'parameters': parameters, 'scheme': scheme, 'price': price,
                'css_url': url_for('static', filename='css/calculated_result.css'), }
        if current_user.is_authenticated:
            order_data = form_data
            order_data['price'], order_data['scheme_id'], order_data['user_id'] = price, scheme, current_user.id
            add_order(order_data)
        return render_template('calculated_result.html', **data)

    data = {"title": f'расчет схемы {scheme}', "scheme": scheme, "scheme_id": scheme_id, "form": form,
            'css_url': url_for('static', filename='css/calculate.css'), 'min_size': min_size, 'max_size': max_size}
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
    return render_template('profile.html', css_url=url_for('static', filename='css/profile.css'), email=email,
                           title='Профиль')


@app.route('/profile/orders/<int:user_id>')
@login_required
def orders(user_id):
    if current_user.id != user_id:
        abort(403)
    orders_list = return_orders_by_user_id(current_user.id)
    css_file = url_for('static', filename='css/profile.css')
    return render_template("orders.html", css_url=css_file, orders_list=orders_list, title='Ваши расчеты')


@app.route('/change_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def change_password(user_id):
    if current_user.id != user_id:
        abort(403)
    form = ChangePasswordForm()
    if form.validate_on_submit():
        old_password, new_password, repeat_password = form.old_password.data, form.new_password.data, \
                                                      form.repeat_new_password.data
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(user_id == User.id)[0]
        if not user.check_password(old_password):
            return render_template('change_password.html', form=form,
                                   css_url=url_for('static', filename='css/login.css'),
                                   old_password_message='Неверный старый пароль')
        if new_password == old_password:
            return render_template('change_password.html', form=form,
                                   css_url=url_for('static', filename='css/login.css'),
                                   password_message='Это ваш текущий пароль, придумайте другой')
        if new_password != repeat_password:
            return render_template('change_password.html', form=form,
                                   css_url=url_for('static', filename='css/login.css'),
                                   password_message='Пароли не совпадают')
        user.set_password(new_password)
        db_sess.commit()
        flash('Пароль успешно изменён!', 'success')
        return redirect('/profile')

    return render_template('change_password.html', form=form, css_url=url_for('static', filename='css/login.css'))


@app.route('/delete_account/<int:user_id>', methods=['POST'])
@login_required
def delete_account(user_id):
    if current_user.id != user_id:
        abort(403)

    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)

    db_sess.delete(user)
    db_sess.commit()

    logout_user()
    flash('Ваш аккаунт был успешно удалён', 'info')
    return redirect('/')


@app.route('/about_us')
def about_us():
    about_creator_text = open('static/infos/about_creator.txt', encoding='utf8').read()
    return render_template('about_creator.html', about_creator_text=about_creator_text, title='О создателе')


@app.route('/comments')
def comments_list():
    comments = get_comments('all')
    return render_template('comments_list.html', comments=comments, title='Комментарии')


@app.route('/projects')
def projects():
    project_photo_path = './static/img/projects'
    # возвращает все директории в папке ./static/img/projects в порядке возрастании по айди
    photo_dirs_list = sorted(return_dirs(project_photo_path), key=lambda x: int(x[-1]))
    # возвращает все текст в папке ./static/infos/projects_text в порядке возрастании по айди
    text_files_list = sorted(return_files('./static/infos/projects_text'), key=lambda x: int(x.split('.txt')[0][-1]))

    projects_titles = get(f"{SERVER_URL}/api/projects").json().get('projects', [])
    css = url_for('static', filename='css/project_content.css')
    if not projects_titles:
        return render_template('projects.html', projects_dict=[], projects_titles=[],
                               project_text_dict=[], css_url=css, title='Проекты')
    # словарь с фотографиями для каждого проекта по айди
    projects_dict = {f'project_{project["id"]}': return_files(path) for path, project in
                     zip(photo_dirs_list, projects_titles)}

    # словарь с текстами для каждого проекта по айди
    project_text_dict = {}
    for path, project in zip(text_files_list, projects_titles):
        try:
            project_text_dict[f'project_{project["id"]}'] = open(path, encoding='utf-8').read()
        except FileNotFoundError:
            project_text_dict[f'project_{project["id"]}'] = 'Не смогли найти текст про этот проект, скоро исправим'
    return render_template('projects.html', projects_dict=projects_dict, projects_titles=projects_titles,
                           project_text_dict=project_text_dict,
                           css_url=css, title='Проекты')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


def main():
    db_session.global_init('db/hs_portal.db')
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
