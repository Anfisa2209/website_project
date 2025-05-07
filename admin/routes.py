import os

from flask import Blueprint, render_template, redirect, abort, flash
from flask_login import login_required, current_user
from requests import get, post
from werkzeug.utils import secure_filename

from data.forms.project_form import ProjectForm
from tools.service_files import SERVER_URL, return_dirs

admin_bp = Blueprint('admin', __name__, template_folder='templates', static_folder='static',
                     static_url_path='/admin/static', url_prefix='/admin')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@admin_bp.before_request
@login_required
def check_admin():
    if not current_user.is_admin:
        abort(403)


@admin_bp.route('/')
def dashboard():
    return render_template('index.html')


@admin_bp.route('/users')
def users():
    users_list = get(f"{SERVER_URL}/api/users").json()
    if not users_list.get('users'):
        return abort(404)
    return render_template('users.html', users_list=users_list['users'])


@admin_bp.route('/comments')
def comments():
    users_list = get(f"{SERVER_URL}/api/users").json()
    if not users_list.get('users'):
        return abort(404)
    return 'comments'


@admin_bp.route('/texts')
def texts():
    return 'texts'


@admin_bp.route('/add_project', methods=['GET', 'POST'])
def add_project():
    form = ProjectForm()
    if form.validate_on_submit():
        name, text, file = form.name.data, form.project_text.data, form.image_photo.data
        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)
            project_number = len(return_dirs('./static/img/projects')) + 1
            directory = f'./static/img/projects/project_{project_number}'
            if not os.path.exists(directory):
                os.makedirs(directory)
            filepath = os.path.join(directory, filename)
            file.save(filepath)
            post(f"{SERVER_URL}/api/projects", json={'name': name}).json()
            with open(f'./static/infos/projects_text/project_{project_number}.txt', mode='w') as text_file:
                text_file.write(text)
            return redirect('/admin')
        else:
            flash('Недопустимый тип файла')
        return name
    return render_template('add_project.html', form=form)
