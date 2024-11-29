import fitz
import os

from collections import Counter
from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTChar, LTTextContainer, LTTextLine

from classify import classify_block
from utils import overlap, merge_blocks


def is_multicolumn_document(blocks, page_width, column_threshold=3):
    """
    Определяет количество колонок в документе.
    
    :param blocks: Список блоков, содержащих 'bbox'.
    :param page_width: Ширина страницы.
    :param column_threshold: Минимальное горизонтальное расстояние между колонками для их распознавания.
    :return: 0 для одноколоночных, 2 для двухколоночных, 3 для трёхколоночных документов.
    """
    # Извлекаем начальные x-координаты блоков
    x_positions = sorted(block['bbox'][0] for block in blocks)
    
    # Находим все значительные промежутки между блоками
    large_gaps = [
        x_positions[i+1] - x_positions[i]
        for i in range(len(x_positions) - 1)
        if x_positions[i+1] - x_positions[i] > column_threshold
    ]
    
    num_large_gaps = len(large_gaps)
    
    if num_large_gaps == 0:
        return 0  # Одноколоночный
    elif num_large_gaps == 1:
        return 2  # Двухколоночный
    elif num_large_gaps >= 2:
        return 3  # Трёхколоночный или более
    
    return 0  # По умолчанию одноколоночный

def extract_font_sizes(pdf_path):
    """
    Извлекает размеры шрифтов из PDF-документа с использованием pdfminer.
    """
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
    print(f"Базовый размер шрифта: {base_font_size} (используется {count} раз)")

    return base_font_size

def extract_chars(element, font_sizes):
    """
    Рекурсивно извлекает размеры шрифтов из элементов разметки.
    """
    if isinstance(element, LTChar):
        font_size = round(element.size)
        font_sizes.append(font_size)
    elif isinstance(element, (LTTextContainer, LTTextLine)):
        for child in element:
            extract_chars(child, font_sizes)

def convert_pdf_to_png(pdf_path, image_folder, page_num):
    """
    Конвертирует указанную страницу PDF в PNG-изображение без разметки.
    Возвращает путь к сохраненному изображению.
    """
    import pypdfium2 as pdfium

    try:
        pdf = pdfium.PdfDocument(pdf_path)
        if page_num < 0 or page_num >= len(pdf):
            print(f"Неверный номер страницы: {page_num}. В документе {len(pdf)} страниц.")
            return None

        page = pdf.get_page(page_num)
        pil_image = page.render(scale=300/72).to_pil()
        base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        image_name = f"{base_filename}_page_{page_num + 1}.png"
        image_path = os.path.join(image_folder, image_name)
        pil_image.save(image_path)
        print(f"Сохранено простое изображение: {image_path}")
        page.close()
        pdf.close()
        return image_path
    except Exception as e:
        print(f"Не удалось конвертировать страницу {page_num + 1} из '{pdf_path}': {e}")
        return None

def extract_blocks(pdf_path, base_font_size=12.0):
    """
    Извлекает и классифицирует блоки из PDF с использованием базового размера шрифта.
    Возвращает структуру данных в соответствии с требуемым JSON-форматом.
    """



    doc = fitz.open(pdf_path)
    classified_data = {}

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        page_height = page.rect.height
        page_width = page.rect.width
        orientation = get_page_orientation(pdf_path, page_num) 
        page_classified = {}

        # Определяем количество колонок на странице
        num_columns = is_multicolumn_document(blocks, page_width)
        

        # Детектирование таблиц
        tables = page.find_tables()
        table_bboxes = []
        for tbl in tables:
            try:
                bbox = tbl.bbox  
                table_bbox = [round(coord, 2) for coord in bbox]
                table_bboxes.append(table_bbox)
                page_classified.setdefault("table", []).append({
                    "bbox": table_bbox,
                })
            except AttributeError as e:
                continue

        # Фильтрация блоков (исключаем пересекающиеся с таблицами)
        filtered_blocks = []
        for block in blocks:
            if block['type'] == 1:
                # Для изображений добавляем в фильтрованные блоки
                filtered_blocks.append(block)
            else:
                # Для текстовых блоков проверяем пересечение с таблицами
                if not any(overlap(block['bbox'], tbl_bbox) for tbl_bbox in table_bboxes):
                    filtered_blocks.append(block)

        # Сортируем блоки по позиции на странице (сверху вниз, слева направо)
        filtered_blocks_sorted = sorted(filtered_blocks, key=lambda b: (b['bbox'][1], b['bbox'][0]))

        # Классифицируем блоки и создаём структуру данных
        classified_blocks = []
        for block in filtered_blocks_sorted:
            block_type, bbox, text = classify_block(doc, block, page_height, base_font_size, orientation)
            classified_blocks.append({
                "type": block_type,
                "bbox": bbox,
                "text": text 
            })

        # Объединяем блоки с учётом количества колонок
        merged_blocks = merge_blocks(classified_blocks, base_font_size, orientation, page_height, num_columns)

        # Добавляем объединённые блоки в page_classified
        for block in merged_blocks:
            block_type = block['type']
            bbox = block['bbox']
            page_classified.setdefault(block_type, []).append({
                "bbox": bbox
            })

        classified_data[page_num] = page_classified

    doc.close()
    return classified_data



def get_page_orientation(pdf_path, page_number=0):
    import fitz

    doc = fitz.open(pdf_path)
    if page_number < 0 or page_number >= len(doc):
        print(f"Неверный номер страницы: {page_number}. В документе {len(doc)} страниц.")
        doc.close()
        return None

    page = doc.load_page(page_number)
    width, height = page.rect.width, page.rect.height
    doc.close()

    return "horizontal" if width > height else "vertical"
