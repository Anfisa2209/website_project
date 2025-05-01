import os

import requests.exceptions
from requests import get

SERVER_URL = 'http://127.0.0.1:8080'

handle_models = {1: 'односторонняя', 2: 'двухсторонняя'}
colors_ids = {1: "серебро", 2: "бронза", 3: "белый", 4: 'коричневый'}
materials = {1: "дуб", 2: "сосна", 3: "лиственница"}


def return_files(path):
    # возвращает все файл из заданного пути
    if not os.path.exists(path):
        return ['A', 'AF', 'C', 'CF', 'E', 'EF', 'G', 'L']
    file_list = []
    for currentdir, dirs, files in os.walk(path):
        for file in files:
            file_list.append(f'{path}/{file}')
    return file_list


def create_tuple(data, n=2):
    # возвращает список кортежей
    result = []
    while data:
        result.append(tuple(data[:n]))
        del data[:n]
    return result


def get_comments(scheme_name):
    # возвращает все комментарии под определенной схемой или все, если указать all
    try:
        comments = []
        all_comments = get(f"{SERVER_URL}/api/comments").json()
        for comment in all_comments.get('comments'):
            if comment['scheme_name'] == scheme_name or scheme_name == 'all':
                user_id = comment['user_id']
                try:
                    user = get(f"{SERVER_URL}/api/users/{user_id}").json()
                except requests.exceptions.JSONDecodeError:
                    continue  # если нет пользователя с таким айди, пропускаем комментарий
                if user:
                    com = comment
                    com['user_name'] = user['users'][0]['name']
                    comments.append(com)
        return comments
    except requests.exceptions.MissingSchema:
        return []
