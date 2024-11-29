import re
import os
from collections import Counter
import numpy as np
from config import reader, BLOCK_COLORS
from utils import refine_formula_bbox
from PIL import Image

def is_title(block, text, max_font, base_font_size):
    font_sizes = []
    is_bold = False
    is_italic = False
    text_length = 0

    for line in block.get('lines', []):
        for span in line.get('spans', []):
            font_sizes.append(round(span['size']))
            if "bold" in span['font'].lower():
                is_bold = True
            if "italic" in span['font'].lower():
                is_italic = True
            text_length += len(span['text'])

    if font_sizes:
        most_common_font_size = Counter(font_sizes).most_common(1)[0][0]
        if (most_common_font_size >= base_font_size + 2 and
                (is_bold or is_italic) and
                text_length < 100):
            return True
    return False

def is_header(block, y0, page_height, orientation):
    if orientation == "vertical":
        top_threshold = page_height * 0.05
    elif orientation == "horizontal":
        top_threshold = page_height * 0.07
    else:
        return False

    return y0 < top_threshold

def is_formula_image(image_path):

    try:
        with Image.open(image_path) as img:
            width, height = img.size 
            print(f"SIZE{width}x{height}")
             # Извлекаем размеры изображения в пикселях
            if (width / height) > 3: 
                return True
            else:
                return False
    except Exception as e:
        print(f"Ошибка обработки изображения: {e}")
        return False
    
def is_footer(block, y1, page_height, orientation):
    if orientation == "vertical":
        bottom_threshold = page_height * 0.95
    elif orientation == "horizontal":
        bottom_threshold = page_height * 0.93
    else:
        return False

    return y1 > bottom_threshold

def is_numbered_list(block, base_font_size, text):
    if not text:
        return False

    numbered_list_patterns = [
        r'^\d+\.', r'^\d+\)', r'^[IVXLCDM]+\.', r'^[IVXLCDM]+\)',
        r'^[ivxlcdm]+\)', r'^[A-Z]\.', r'^[A-Z]\)', r'^[a-z]\.',
        r'^[a-z]\)', r'^[ivxlcdm]+\.' 
    ]

    is_numbered = any(re.match(pattern, text) for pattern in numbered_list_patterns)
    if not is_numbered:
        return False

    spans = block.get('spans', [])
    if spans:
        avg_font = sum(span['size'] for span in spans) / len(spans)
        if abs(avg_font - base_font_size) > 0:
            return False

    return True

def is_marked_list(block, base_font_size, text):
    text = text.lower()
    if not text:
        return False

    if text[0] in ['•', '○', '■', '–', '*', '→']:
        spans = block.get('spans', [])
        return True
    return False

def is_footnote(block, base_font_size, text):
    if not text:
        return False

    footnote_patterns = [
        r'^_{10,}$',  
        r'^\d+\s*\^', 
    ]

    superscript_digits = {'⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹'}

    superscript = text[0] in superscript_digits
    matches_pattern = any(re.search(pattern, text) for pattern in footnote_patterns)

    if superscript or matches_pattern:
        spans = block.get('spans', [])
        if spans:
            avg_font = sum(span['size'] for span in spans) / len(spans)
            if abs(avg_font - base_font_size) < 2:
                return True
        else:
            return True

    return False

def is_table_signature(block, text):
    text = text.lower()
    if not text:
        return False

    signature_patterns = [
        r'\bтабл\.?\s*\d+[-–—]?',       
        r'\bтаблица\s*\d+[-–—]?'        
    ]

    for pattern in signature_patterns:
        if re.search(pattern, text):
            return True
    return False

def is_picture_signature(block, text):
    text = text.lower()
    if not text:
        return False

    signature_patterns = [
        r'(?:^|[^а-яёa-z0-9])рис\.?\s*\d+',      
        r'(?:^|[^а-яёa-z0-9])рисунок\s*\d+'      
    ]

    for pattern in signature_patterns:
        if re.search(pattern, text):
            return True
    return False

def classify_block(doc, block, page_height, base_font_size, orientation):
    """
    Классифицирует блок в PDF-документе и уточняет координаты, если это формула.
    """
    block_type = "unknown"
    bbox = block['bbox']  # Координаты блока на странице
    x0_page, y0_page, x1_page, y1_page = bbox
    text = extract_text_from_block(block)

    if block['type'] == 0:  # Текстовые блоки
        spans = block.get('spans', [])
        font_sizes = [span['size'] for span in spans]
        max_font = max(font_sizes) if font_sizes else 0
        avg_font = sum(font_sizes) / len(font_sizes) if spans else 0

        # Определение типа текстового блока
        if is_title(block, text, max_font, base_font_size):
            block_type = "title"
        elif is_header(block, y0_page, page_height, orientation):
            block_type = "header"
        elif is_footer(block, y1_page, page_height, orientation):
            block_type = "footer"
        elif is_numbered_list(block, base_font_size, text):
            block_type = "numbered_list"
        elif is_marked_list(block, base_font_size, text):
            block_type = "marked_list"
        elif is_footnote(block, base_font_size, text):
            block_type = "footnote"
        elif is_table_signature(block, text):
            block_type = "table_signature"
        elif is_picture_signature(block, text):
            block_type = "picture_signature"
        else:
            block_type = "paragraph"

    elif block['type'] == 1:  # Изображения
        image_info = block.get('image')
        temp_image_path = "temp_image.png"

        try:
            if not image_info:
                block_type = "picture"
            else:
                # Извлечение изображения из блока
                if isinstance(image_info, dict):
                    xref = image_info.get('xref')
                    if xref is not None:
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image['image']
                    else:
                        image_bytes = image_info.get('image', b'')
                elif isinstance(image_info, bytes):
                    image_bytes = image_info
                else:
                    image_bytes = None

                if image_bytes:
                    with open(temp_image_path, "wb") as temp_img:
                        temp_img.write(image_bytes)

                    # Проверяем, является ли это формулой
                    if is_formula_image(temp_image_path):
                        block_type = "formula"
                        # Уточняем координаты формулы
                        x_min_img, y_min_img, x_max_img, y_max_img = refine_formula_bbox(temp_image_path)
                        with Image.open(temp_image_path) as img:
                            img_width, img_height = img.size

                        # Переводим координаты изображения в координаты страницы
                        x0_new = x0_page + (x_min_img / img_width) * (x1_page - x0_page)
                        y0_new = y0_page + (y_min_img / img_height) * (y1_page - y0_page)
                        x1_new = x0_page + (x_max_img / img_width) * (x1_page - x0_page)
                        y1_new = y0_page + (y_max_img / img_height) * (y1_page - y0_page)

                        # Обновляем bbox
                        bbox = [round(coord, 2) for coord in [x0_new, y0_new, x1_new, y1_new]]
                    else:
                        block_type = "picture"
                else:
                    block_type = "picture"

        except Exception as e:
            print(f"Ошибка при обработке изображения: {e}")
            block_type = "picture"
        finally:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

    return block_type, bbox, text





def extract_text_from_block(block):
    """
    Извлекает весь текст из блока, объединив текст из всех строк и фрагментов.
    """
    full_text = ""
    if block.get("type") == 0:  # Проверяем, что это текстовый блок
        # Сортируем строки по y0 (сверху вниз)
        sorted_lines = sorted(block.get("lines", []), key=lambda l: l['bbox'])
        for line in sorted_lines:
            # Сортируем spans по x0 (слева направо)
            sorted_spans = sorted(line.get("spans", []), key=lambda s: s['bbox'])
            for span in sorted_spans:
                text = span.get("text", "").strip()  # Извлекаем текст из каждого span
                if text:
                    full_text += text
    return full_text.strip()
