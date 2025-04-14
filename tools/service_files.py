import os

from requests import get

SERVER_URL = 'http://127.0.0.1:8080'


def return_files(path):
    # возвращает все файл из заданного пути
    if not os.path.exists(path):
        raise ValueError(f"Путь {path} не найден")
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
    # возвращает все комментарии под определенной схемой
    comments = []
    all_comments = get(f"{SERVER_URL}/api/comments").json()
    for comment in all_comments.get('comments'):
        if comment['scheme_name'] == scheme_name:
            user_id = comment['user_id']
            user = get(f"{SERVER_URL}/api/users/{user_id}").json()
            if user:
                com = comment
                com['user_name'] = user['users'][0]['name']
                comments.append(com)
    return comments
