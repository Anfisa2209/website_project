import os
import shutil

from flask import Blueprint, render_template, redirect, abort, flash
from flask_login import login_required, current_user
from requests import get, post, put, delete
from werkzeug.utils import secure_filename

from data.forms.edit_text_form import EditTextForm
from data.forms.project_form import ProjectForm
from tools.scheme_list import TEXTS_LIST, SCHEME_LIST
from tools.service_files import SERVER_URL
from tools.sqlite import return_all_orders, popular_scheme

admin_bp = Blueprint('admin', __name__, template_folder='templates', static_folder='static',
                     static_url_path='/admin/static', url_prefix='/admin')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def add_new_project(form):
    name, text, file = form.name.data, form.project_text.data, form.image_photo.data
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        #  создается папка с фотографиями, которому присваивается айди названия проекта
        project_id = post(f"{SERVER_URL}/api/projects", json={'name': name}).json().get('projects')[0]['id']
        directory = f'./static/img/projects/project_{project_id}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        filepath = os.path.join(directory, filename)
        file.save(filepath)

        with open(f'./static/infos/projects_text/project_{project_id}.txt', mode='w', encoding='utf8') as text_file:
            text_file.write(text)
        return 1
    return


# @admin_bp.before_request
# @login_required
# def check_admin():
#     if not current_user.is_admin:
#         abort(403)


@admin_bp.route('/')
def dashboard():
    orders_list = return_all_orders()
    diagram_data = [['Схема', 'Количество']] + popular_scheme()
    return render_template('admin_orders.html', orders_list=orders_list, diagram_data=diagram_data)


@admin_bp.route('/users')
def users():
    users_list = get(f"{SERVER_URL}/api/users").json()
    if not users_list.get('users'):
        return abort(404)
    return render_template('users.html', users_list=users_list['users'])


@admin_bp.route('/comments')
def comments():
    # так как уже есть страница с комментариями, просто переходим туда
    return redirect('/comments')


@admin_bp.route('/texts')
def texts():
    return render_template('text_list.html', texts_list=TEXTS_LIST)


@admin_bp.route('/edit_text/<link>', methods=['GET', 'POST'])
def edit_texts(link):
    original_link = link
    if original_link in SCHEME_LIST:
        file_path = f'schemes_text/{original_link}'
    else:
        file_path = original_link
    full_path = os.path.join('./static/infos', f'{file_path}.txt')
    try:
        with open(full_path, encoding='utf-8') as f:
            file_text = f.read()
    except FileNotFoundError:
        flash("Файл не найден", 'danger')
        return redirect('/admin')

    form = EditTextForm()

    if form.validate_on_submit():
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(form.text.data)
            flash('Текст успешно сохранён', 'success')
            return redirect('/admin')
        except Exception as e:
            flash(f'Ошибка при записи файла: {str(e)}', 'danger')
    form.text.data = file_text
    return render_template('edit_text.html', form=form, text_about=TEXTS_LIST[link])


@admin_bp.route('/projects')
def projects():
    # все что можно сделать с проектами
    return render_template('project_option.html')


@admin_bp.route('/add_project', methods=['GET', 'POST'])
def add_project():
    form = ProjectForm()
    if form.validate_on_submit():
        if add_new_project(form):
            flash('Новый проект добавлен', 'success')
            return redirect('/admin')
        else:
            flash('Недопустимый тип файла', 'info')
            return render_template('add_project.html', form=form)
    return render_template('add_project.html', form=form)


@admin_bp.route('/edit_project')
def edit_project():
    projects_list = get(f"{SERVER_URL}/api/projects").json().get('projects')
    return render_template('edit_project_list.html', projects_list=projects_list)


@admin_bp.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project_by_id(project_id):
    form = ProjectForm(photo_required=False)
    project = get(f"{SERVER_URL}/api/projects/{project_id}")
    if project.status_code != 200:
        abort(404)
    if form.validate_on_submit():
        result = put(f"{SERVER_URL}/api/projects/{project_id}", json={'name': form.name.data})
        with open(f'./static/infos/projects_text/project_{project_id}.txt', mode='w', encoding='utf8') as text_file:
            text_file.write(form.project_text.data)
        file = form.image_photo.data
        if file:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                #  добавляет фото в существующую папку
                directory = f'./static/img/projects/project_{project_id}'
                if not os.path.exists(directory):
                    os.makedirs(directory)
                filepath = os.path.join(directory, filename)
                file.save(filepath)
            else:
                flash('Недопустимый тип файла', 'info')
                return render_template('add_project.html', form=form)
        if result.status_code == 200:
            flash('Изменения успешно внесены', 'success')
            return redirect('/admin')
    project_name = project.json()['projects'][0]['name']
    form.name.data = project_name
    form.project_text.data = open(f'./static/infos/projects_text/project_{project_id}.txt', encoding='utf8').read()
    return render_template('add_project.html', form=form, project_id=project_id)


@admin_bp.route('/delete_project/<int:project_id>')
def delete_project(project_id):
    project = get(f"{SERVER_URL}/api/projects/{project_id}")
    if project.status_code != 200:
        abort(404)
    project_name = project.json()['projects'][0]['name']

    result = delete(f"{SERVER_URL}/api/projects/{project_id}")
    if result.status_code == 200:
        # Пути к файлам и папкам
        img_dir = f'./static/img/projects/project_{project_id}'
        txt_file = f'./static/infos/projects_text/project_{project_id}.txt'

        try:
            # Удаляем папку с изображениями (если существует)
            if os.path.exists(img_dir):
                shutil.rmtree(img_dir)

            if os.path.exists(txt_file):
                os.remove(txt_file)

            flash(f'Проект "{project_name.capitalize()}" успешно удалён', 'info')
        except Exception as e:
            flash(f'Ошибка при удалении файлов: {str(e)}', 'danger')

        return redirect('/admin')

    flash(f'Не удалось удалить проект {project_name}', 'danger')
    return redirect('/admin')
