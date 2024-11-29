import easyocr

BLOCK_COLORS = {
    "title": "red",
    "paragraph": "green",
    "table": "blue",
    "picture": "purple",
    "table_signature": "orange",
    "picture_signature": "cyan",
    "numbered_list": "magenta",
    "marked_list": "yellow",
    "header": "brown",
    "footer": "grey",
    "footnote": "pink",
    "formula": "olive",

    "unknown": "black"
}



# Инициализируем EasyOCR reader с поддержкой английского и русского языков
reader = easyocr.Reader(['la', 'en'])