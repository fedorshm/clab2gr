from collections import OrderedDict
#Настройки частоты появдения блоков для стандартного документа
block_frequencies = {
    'paragraph': 40,
    'table': 15,
    'picture': 15,
    'numbered_list': 10,
    'marked_list': 10,
    'formula': 10
}
#Диапозоны отсупов документа
MARGIN_RANGES = {
    'left': (0.5, 2),  
    'right': (0.5, 2),  
    'top': (0.5, 1.5),  
    'bottom': (0.5, 1.5),  
}

# Языки для генерации данных
locales = OrderedDict([('en-US', 1), ('ru-RU', 2)])

