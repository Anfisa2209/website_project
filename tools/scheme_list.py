from tools.service_files import return_files

SCHEME_LIST = [i.split("/")[-1].split('.')[0] for i in return_files('./static/img/scheme')]
VIDEO_LIST = {"A": 'https://www.youtube.com/embed/JQGyltY-ncY?si=Oh_7-Fw0rs6aXW5z',
              "C": 'https://www.youtube.com/embed/sIxVlZvt-ug?si=R4CjzOwWVJDcEgeD',
              "G": 'https://www.youtube.com/embed/yQgvUCz8vWc?si=vWPCL0cwgXKgaBz4',
              "E": 'https://www.youtube.com/embed/AlugOd69eZY?si=t_Jxx5QOTeMEoQuf',
              "L": 'https://www.youtube.com/embed/ZHlHF8iYk94?si=5fUEJf54EVY_Gu5c'}
TEXTS_LIST = {'about_creator': 'О создателе',
              'hs_info': 'На главной',
              'A': 'Схема A',
              'AF': 'Схема AF',
              'C': 'Схема C',
              'CF': 'Схема CF',
              'E': 'Схема E',
              'EF': 'Схема EF',
              'G': 'Схема G',
              'L': 'Схема L'}
