from tools.service_files import return_files

SCHEME_LIST = [i.split("/")[-1].split('.')[0] for i in return_files('static/img/scheme')]
