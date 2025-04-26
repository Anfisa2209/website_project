from tools.service_files import return_files

SCHEME_LIST = [i.split("/")[-1].split('.')[0] for i in return_files('static/img/scheme')]
VIDEO_LIST = ['sA.mp4', 'sC.mp4', 'sE.mp4',  'sG.mp4', 'sL.mp4']
