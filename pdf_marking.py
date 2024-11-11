from pdfminer.layout import LTTextContainer, LTChar, LTTextLine, LAParams
from collections import Counter
from pdfminer.high_level import extract_pages
import csv
import glob

def load_font_sizes(csv_path):
    font_sizes = {}
    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                font_sizes[row['filename']] = int(row['base_font_size'])
    except Exception as e:
        print(f"Ошибка при загрузке истинных размеров шрифтов из {csv_path}: {e}")
    return font_sizes

def extract_font_sizes(pdf_path):
    font_sizes = []
    try:
        for page_layout in extract_pages(pdf_path, laparams=LAParams()):
            for element in page_layout:
                extract_chars(element, font_sizes)
    except Exception as e:
        print(f"Ошибка при обработке файла {pdf_path}: {e}")
        return None

    if not font_sizes:
        print(f"Не удалось найти размеры шрифтов в документе: {pdf_path}")
        return None

    size_counter = Counter(font_sizes)
    base_font_size, count = size_counter.most_common(1)[0]
    return base_font_size

