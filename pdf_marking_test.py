import os
import glob
import json
import re
from collections import defaultdict
from pdfminer.layout import LTTextContainer, LTChar
from collections import Counter

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTImage, LTChar, LTAnno

def extract_font_sizes(pdf_path):
    font_sizes = []

    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    for character in text_line:
                        if isinstance(character, LTChar):
                            font_size = round(character.size)
                            font_sizes.append(font_size)
    
    if not font_sizes:
        print("Не удалось найти размеры шрифтов в документе.")
        return None
    
    # Определяем наиболее часто используемый размер шрифта
    size_counter = Counter(font_sizes)
    base_font_size, count = size_counter.most_common(1)[0]
    return base_font_size



def extract_elements(pdf_path):
    elements = []
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                text = element.get_text().strip()
                if text:
                    x0, y0, x1, y1 = element.bbox
                    elements.append({
                        'type': 'text',
                        'text': text,
                        'coordinates': [x0, y0, x1, y1],
                        'font_size': get_average_font_size(element),
                        'is_bold': is_bold(element),
                        'is_italic': is_italic(element),
                        'alignment': get_alignment(element)
                    })
            elif isinstance(element, LTImage):
                x0, y0, x1, y1 = element.bbox
                elements.append({
                    'type': 'image',
                    'coordinates': [x0, y0, x1, y1]
                })
            # Можно добавить обработку других типов элементов при необходимости
    return elements

def get_average_font_size(textbox):
    font_sizes = []
    for line in textbox:
        for char in line:
            if isinstance(char, LTChar):
                font_sizes.append(char.size)
    return sum(font_sizes) / len(font_sizes) if font_sizes else 0

def is_bold(textbox):
    for line in textbox:
        for char in line:
            if isinstance(char, LTChar) and 'Bold' in char.fontname:
                return True
    return False

def is_italic(textbox):
    for line in textbox:
        for char in line:
            if isinstance(char, LTChar) and 'Italic' in char.fontname:
                return True
    return False

def get_alignment(textbox):
    # Определение выравнивания может быть сложным. Здесь упрощённый пример:
    # Если x0 близко к левому краю, то выравнивание по левому краю и т.д.
    page_width = textbox.page_width if hasattr(textbox, 'page_width') else 595  # Ширина A4 в points
    x0, y0, x1, y1 = textbox.bbox
    if x0 < page_width * 0.1:
        return 'LEFT'
    elif x1 > page_width * 0.9:
        return 'RIGHT'
    else:
        return 'CENTER'

def classify_elements(elements):
    classifications = defaultdict(list)

    for element in elements:
        if element['type'] == 'text':
            text = element['text']
            coordinates = element['coordinates']
            font_size = element.get('font_size', 0)
            is_bold_flag = element.get('is_bold', False)
            is_italic_flag = element.get('is_italic', False)
            alignment = element.get('alignment', 'LEFT')

            # Классификация заголовков
            if is_bold_flag and font_size > 14:
                classifications["title"].append(coordinates)
                
                continue

            # Классификация списков
            if re.match(r'^(\d+\.\s|•\s)', text):
                if text.startswith(tuple(f"{i}." for i in range(10))):
                    classifications["numbered_list"].append(coordinates)
                else:
                    classifications["marked_list"].append(coordinates)
                continue

            # Классификация подвалов и колонтитулов
            if coordinates[1] < 50:  # Примерное значение, зависит от размера страницы
                classifications["footer"].append(coordinates)
                continue
            elif coordinates[3] > (595 - 50):  # Пример для A4, верх страницы
                classifications["header"].append(coordinates)
                continue

            # Классификация формул (может потребовать дополнительных условий)
            if re.search(r'\$.*?\$', text):  # Пример поиска LaTeX-форматирования
                classifications["formula"].append(coordinates)
                continue

            # Остальной текст считаем параграфом
            classifications["paragraph"].append(coordinates)

        elif element['type'] == 'image':
            coordinates = element['coordinates']
            classifications["picture"].append(coordinates)

    return classifications

def find_table_signatures(classifications, elements):
    table_coords = classifications.get("table", [])
    for table in table_coords:
        # Ищем текстовый блок ниже таблицы
        table_bottom = table[1]
        for element in elements:
            if element['type'] == 'text':
                x0, y0, x1, y1 = element['coordinates']
                # Определяем, находится ли текст сразу под таблицей
                if abs(y0 - table_bottom) < 20:  # Пороговое значение, можно настроить
                    text = element['text']
                    if re.match(r'^(Таблица|Табл\.).*', text):
                        classifications["table_signature"].append(element['coordinates'])
    return classifications

def find_picture_signatures(classifications, elements):
    picture_coords = classifications.get("picture", [])
    for picture in picture_coords:
        # Ищем текстовый блок ниже или выше изображения
        picture_bottom = picture[1]
        picture_top = picture[3]
        for element in elements:
            if element['type'] == 'text':
                x0, y0, x1, y1 = element['coordinates']
                text = element['text']
                # Проверяем ниже изображения
                if abs(y0 - picture_bottom) < 20 and re.match(r'^(Рис\.|Рисунок).*', text):
                    classifications["picture_signature"].append(element['coordinates'])
                # Проверяем выше изображения
                elif abs(y1 - picture_top) < 20 and re.match(r'^(Рис\.|Рисунок).*', text):
                    classifications["picture_signature"].append(element['coordinates'])
    return classifications

def process_pdf(pdf_path):
    elements = extract_elements(pdf_path)
    initial_classifications = classify_elements(elements)
    final_classifications = find_table_signatures(initial_classifications, elements)
    final_classifications = find_picture_signatures(final_classifications, elements)
    

    return final_classifications

def process_all_pdfs(directory):
    results = {}
    
    pdf_files = glob.glob(os.path.join(directory, "*.pdf"))
    
    for pdf_file in pdf_files:
        print(f"Обрабатывается файл: {pdf_file}")

        classifications = process_pdf(pdf_file)
        
        # Определяем имя JSON-файла
        base_name = os.path.splitext(os.path.basename(pdf_file))[0]
        json_file = os.path.join(directory, f"{base_name}.json")
        
        # Сохраняем результаты в JSON-файл
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(classifications, f, indent=4, ensure_ascii=False)
        
        print(f"Результаты сохранены в: {json_file}\n")
    
    return results

if __name__ == "__main__":
    pdf_directory = 'pdf'  # Путь к директории с PDF-файлами
    #process_all_pdfs(pdf_directory)
    #def extract_base_font_size_from_docx(docx_path)
    # Пример использования
    pdf_files = glob.glob(os.path.join(pdf_directory, "*.pdf"))

   
    base_size = extract_font_sizes(pdf_file)
    for pdf_file in pdf_files:
        base_size = extract_font_sizes(pdf_file)
    if base_size:
        print(f"Базовый размер шрифта: {base_size} pt")