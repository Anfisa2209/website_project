from pathlib import Path
import sqlite3

# Путь к tools/sqlite.py
from requests import get

from tools.service_files import materials, handle_models, colors_ids, SERVER_URL

current_dir = Path(__file__).parent
db_path = current_dir.parent / "db" / "portal_data.db"

connect = sqlite3.connect(db_path, check_same_thread=False)
cursor = connect.cursor()


def return_scheme_id(scheme: str):
    # возвращает id схемы
    scheme = scheme.replace('F', '')
    try:
        scheme_id = cursor.execute('''SELECT id FROM Portals WHERE type = ?''', (scheme,)).fetchone()[0]
        return scheme_id
    except TypeError:
        return


def return_material_id(material: str):
    # возвращает id материала (дуб, сосна, итд)
    material = material.lower()
    material_id = cursor.execute('''SELECT id FROM Materials WHERE title = ?''', (material,)).fetchone()[0]
    return material_id


def return_min_max_size(scheme):
    # возвращает минимальный и максимальный размер для схемы
    scheme_id = return_scheme_id(scheme)

    if scheme_id:
        request = """SELECT width, height FROM PortalPrice WHERE id_portal = ?"""
        all_sizes = cursor.execute(request, (scheme_id,)).fetchall()
        min_size, max_size = all_sizes[0], all_sizes[-1]
        return min_size, max_size
    return


def return_price(portal_width, portal_height, scheme_id, material_id):
    request = """SELECT price FROM PortalPrice 
                WHERE ? <= width AND ? <= height AND 
                id_material = ? AND id_portal = ?"""
    try:
        price = cursor.execute(request, (portal_width, portal_height, material_id, scheme_id)).fetchone()[0]
        return price
    except TypeError:
        return


def calculate_total_price(data: dict):
    # Ключи: width, height, material, steklopakets: id, handle_color: id, handle_models: id, portal_color, scheme_id
    width, height, scheme_id, handle_model_id = data['width'], data['height'], data['scheme_id'], data['material']
    price = return_price(width, height, scheme_id, data['material'])
    total_price = 0
    glass_price = cursor.execute('SELECT price FROM Steklopaket WHERE id = ?', (data['steklopakets'],)).fetchone()[0]
    total_price += price + height * width * 0.8 / 1000000 * glass_price
    handle_number = cursor.execute('SELECT door_number FROM Portals WHERE id = ?', (scheme_id,)).fetchone()[0]
    total_price += 10000 * handle_number if handle_model_id == 2 else 0
    return int(total_price)


def add_order(data: dict):
    request = """INSERT INTO Orders
    (width, height, material_id, steklopaket_id, handle_color_id, handle_model_id, portal_color, scheme, price, user_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    cursor.execute(request, (*data.values(),))
    connect.commit()


def return_orders_by_user_id(user_id):
    request = """
    SELECT width, height, material_id, steklopaket_id, handle_color_id, handle_model_id, portal_color, price, scheme
    FROM Orders
    WHERE user_id = ?
    """
    orders = cursor.execute(request, (user_id,))
    if not orders:
        return []
    result = []
    for order in orders.fetchall():
        width, height, material_id, glass_id, handle_color_id, handle_model_id, portal_color, price, scheme = order
        material, handle_color, handle_model = materials[material_id], colors_ids[handle_color_id], handle_models[
            handle_model_id]
        glass = 'односторонний' if glass_id == 1 else 'двусторонний'
        result.append((width, height, material, glass, handle_color, handle_model, portal_color, scheme, price))
    return result


def return_all_orders():
    request = "SELECT * FROM Orders"
    orders = cursor.execute(request)
    if not orders:
        return []
    result = []
    for order in orders.fetchall():
        _, w, h, material_id, glass_id, handle_color_id, handle_model_id, portal_color, price, scheme, user_id = order
        material, handle_color, handle_model = materials[material_id], colors_ids[handle_color_id], handle_models[
            handle_model_id]
        glass = 'односторонний' if glass_id == 1 else 'двусторонний'
        user = get(f"{SERVER_URL}/api/users/{user_id}")
        if user.status_code != 200:
            user_name = 'Удаленный аккаунт'
        else:
            user_name = user.json()['users'][0]['name']
        result.append((user_name, w, h, material, glass, handle_color, handle_model, portal_color, scheme, price))
    return result


def popular_scheme():
    req = """SELECT scheme, COUNT(scheme) FROM Orders
            GROUP BY scheme
            ORDER BY COUNT(scheme) DESC"""
    res = cursor.execute(req).fetchall()
    return res