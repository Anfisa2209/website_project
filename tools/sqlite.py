from pathlib import Path
import sqlite3

# Путь к tools/sqlite.py
current_dir = Path(__file__).parent
db_path = current_dir.parent / "db" / "portal_data.db"

connect = sqlite3.connect(db_path, check_same_thread=False)
cursor = connect.cursor()


def return_scheme_id(scheme: str):
    # возвращает id схемы
    scheme = scheme.replace('F', '')
    scheme_id = cursor.execute('''SELECT id FROM Portals WHERE type = ?''', (scheme,)).fetchone()[0]
    return scheme_id


def return_material_id(material: str):
    # возвращает id материала (дуб, сосна, итд)
    material = material.lower()
    material_id = cursor.execute('''SELECT id FROM Materials WHERE type = ?''', (material,)).fetchone()[0]
    return material_id


def return_min_max_size(scheme):
    # возвращает минимальный и максимальный размер для схемы
    scheme_id = return_scheme_id(scheme)
    request = """SELECT width, height FROM PortalPrice WHERE id_portal = ?"""
    all_sizes = cursor.execute(request, (scheme_id,)).fetchall()
    min_size, max_size = all_sizes[0], all_sizes[-1]
    return min_size, max_size


def return_price(portal_width, portal_height, scheme_id, material_id):
    request = '''SELECT price FROM PortalPrice WHERE type = ?'''
    # price = cursor.execute(request, (width, height, scheme_id, material_id)).fetchone()[0]
