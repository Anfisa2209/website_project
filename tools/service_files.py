import os

SERVER_URL = 'http://127.0.0.1:8080'


def return_files(path):
    if not os.path.exists(path):
        raise ValueError(f"Путь {path} не найден")
    file_list = []
    for currentdir, dirs, files in os.walk(path):
        for file in files:
            file_list.append(f'{path}/{file}')
    return file_list


def create_tuple(data, n=2):
    result = []
    while data:
        result.append(tuple(data[:n]))
        del data[:n]
    return result
