from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import login_required, current_user
from requests import get

from tools.service_files import SERVER_URL

admin_bp = Blueprint('admin', __name__, template_folder='templates', static_folder='static',
                     static_url_path='/admin/static', url_prefix='/admin')


@admin_bp.before_request
@login_required
def check_admin():
    if current_user.id != 1:
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


@admin_bp.route('/projects')
def projects():
    return 'projects'
