from pdfminer.layout import LTTextContainer, LTChar, LTTextLine, LAParams
from collections import Counter
from pdfminer.high_level import extract_pages
import csv
import glob
import os



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

def extract_chars(element, font_sizes):
    if isinstance(element, LTChar):
        font_size = round(element.size)
        font_sizes.append(font_size)
    elif isinstance(element, LTTextContainer) or isinstance(element, LTTextLine):
        for child in element:
            extract_chars(child, font_sizes)
    else:
        pass

def classify_title(element, base_font_size):
    font_sizes = []
    is_bold = False
    is_italic = False
    text_length = 0

    for text_line in element:
        if isinstance(text_line, LTTextLine):
            for char in text_line:
                if isinstance(char, LTChar):
                    font_sizes.append(round(char.size))
                    if "bold" in char.fontname.lower():
                        is_bold = True
                    if "italic" in char.fontname.lower():
                        is_italic = True
            text_length += len(text_line.get_text())

    if font_sizes:
        most_common_font_size = Counter(font_sizes).most_common(1)[0][0]
        if (most_common_font_size >= base_font_size + 2 and
                (is_bold or is_italic) and
                text_length < 100):
            return True
    return False

def detect_titles(pdf_path, base_font_size):
    titles = []
    for page_layout in extract_pages(pdf_path, laparams=LAParams()):
        for element in page_layout:
            if isinstance(element, LTTextContainer) and classify_title(element, base_font_size):
                titles.append({
                    "text": element.get_text(),
                    "x0": element.x0,
                    "y0": element.y0,
                    "x1": element.x1,
                    "y1": element.y1
                })
                print(f"Найден заголовок: '{element.get_text().strip()}' с координатами "
                      f"({element.x0}, {element.y0}, {element.x1}, {element.y1})")
    return titles

def get_pdf_files(directory):
    abs_directory = os.path.abspath(directory)
    pdf_files = glob.glob(os.path.join(abs_directory, "*.pdf")) + glob.glob(os.path.join(abs_directory, "*.PDF"))
    return pdf_files


directory = "pdf"
pdf_files = get_pdf_files(directory)
for pdf_file in pdf_files:
    base_filename = os.path.splitext(os.path.basename(pdf_file))[0]
    base_size = extract_font_sizes(pdf_file)
    print(f"Файл: {base_filename}.pdf,Базоаый размер шрифта {base_size}")