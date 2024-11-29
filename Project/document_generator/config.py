from collections import OrderedDict

import easyocr
# Настройки частоты появления блоков для стандартного документа
block_frequencies = {
    'paragraph': 55,
    'table': 10,
    'picture': 10,
    'numbered_list': 5,
    'marked_list': 5,
    'formula': 10,
    'title' : 5  
}
# Диапазоны отступов
margin_ranges = {
    'left': (0.5, 1.5),
    'right': (0.5, 1.5),
    'top': (1.2, 1.3),
    'bottom': (1.2, 1.3)
}
# Языки для генерации данных
locales = OrderedDict([('en-US', 1), ('ru-RU', 2)])
reader = easyocr.Reader(['la', 'en'])