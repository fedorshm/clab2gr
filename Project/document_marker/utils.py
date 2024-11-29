import fitz
import os
import logging
import numpy as np
from sklearn.cluster import KMeans
import numpy as np
import re
from docx.shared import Pt
from PIL import Image


def determine_column_boundaries(blocks, num_columns, page_width, column_threshold=5):
    """
    Определяет границы колонок на основе позиций блоков.
    """
    if num_columns <= 1:
        return [(0, page_width)]

    # Извлекаем центры блоков по оси X
    x_centers = sorted([ (block['bbox'][0] + block['bbox'][2]) / 2 for block in blocks])

    # Преобразуем в numpy массив
    x_centers_np = np.array(x_centers).reshape(-1, 1)

    # Проверяем, что число точек больше или равно числу кластеров
    n_samples = len(x_centers_np)
    n_clusters = min(num_columns, n_samples)

    if n_clusters <= 1:
        # Если число кластеров 1 или меньше, возвращаем одну колонку
        return [(0, page_width)]

    # Выполняем кластеризацию с обновленным числом кластеров
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(x_centers_np)

    # Остальной код без изменений
    labels = kmeans.labels_
    cluster_centers = kmeans.cluster_centers_

    # Определяем границы колонок
    column_boundaries = []
    for i in range(n_clusters):
        cluster_points = x_centers_np[labels == i]
        min_x = cluster_points.min() - column_threshold
        max_x = cluster_points.max() + column_threshold
        min_x = max(min_x, 0)
        max_x = min(max_x, page_width)
        column_boundaries.append((min_x, max_x))

    # Сортируем границы колонок по возрастанию координаты X
    column_boundaries.sort(key=lambda x: x[0])

    return column_boundaries



def extract_chars(block, font_sizes):

    spans = block.get('spans', [])
    for span in spans:
        font_size = span.get('size')
        if font_size:
            font_sizes.append(round(font_size))

def get_average_font_size(block, base_font_size):
    """
    Вычисляет средний размер шрифта блока.
    
    :param block: Блок разметки документа.
    :param base_font_size: Базовый размер шрифта, используется как значение по умолчанию.
    :return: Средний размер шрифта.
    """
    font_sizes = []
    extract_chars(block, font_sizes)
    if font_sizes:
        return sum(font_sizes) / len(font_sizes)
    else:
        return base_font_size

def convert_pdf_to_png(pdf_path, image_folder, page_num):
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

def overlap(bbox1, bbox2):
    """
    Проверяет, пересекаются ли два прямоугольника.
    """
    x0_1, y0_1, x1_1, y1_1 = bbox1
    x0_2, y0_2, x1_2, y1_2 = bbox2

    return not (x1_1 < x0_2 or x0_1 > x1_2 or y1_1 < y0_2 or y0_1 > y1_2)

def determine_column_boundaries(blocks, num_columns, page_width):
    if num_columns <= 1:
        return [0, page_width]

    x_coords = sorted(list(set([block['bbox'][0] for block in blocks])))
    gaps = []
    for i in range(len(x_coords) - 1):
        gap = x_coords[i+1] - x_coords[i]
        if gap > 0: # Добавляем только положительные зазоры
            gaps.append(gap)
        else:
            logging.warning(f"Обнаружен отрицательный зазор: {gap}. Пропускаем.")

    gaps.sort(reverse=True)
    column_boundaries = [0]
    for i in range(min(num_columns - 1, len(gaps))):
        # Находим индекс самой правой x-координаты ПЕРЕД зазором.
        # Это предотвращает попытку доступа к индексу за пределами списка.
        try:
            idx = next(j for j in range(len(x_coords) - 1) if x_coords[j+1] - x_coords[j] == gaps[i])
            column_boundaries.append(x_coords[idx + 1]) # Используем правую границу зазора
        except StopIteration:
            logging.error(f"Зазор {gaps[i]} не найден в x_coords. Пропускаем.")
            continue

    column_boundaries.append(page_width)
    return column_boundaries


def assign_blocks_to_columns(blocks, column_boundaries):
    """Назначает блоки к соответствующим колонкам."""
    columns = {}
    for block in blocks:
        x0 = block['bbox'][0]
        for i in range(len(column_boundaries) - 1):
            if column_boundaries[i] <= x0 < column_boundaries[i+1]:
                col_num = i
                if col_num not in columns:
                    columns[col_num] = []
                columns[col_num].append(block)
                break
    return columns


def merge_blocks(blocks, base_font_size, orientation, page_height, num_columns):
    if not blocks:
        return []
    
    # Определяем границы колонок
    page_width = max(block['bbox'][2] for block in blocks) if blocks else 0
    column_boundaries = determine_column_boundaries(blocks, num_columns, page_width)

    # Назначаем блоки колонкам
    columns = assign_blocks_to_columns(blocks, column_boundaries)

    merged_blocks = []

    for col_num, col_blocks in columns.items():
        if not col_blocks:
            continue

        # Сортируем блоки в колонке сверху вниз
        col_blocks_sorted = sorted(col_blocks, key=lambda b: b['bbox'][1])
        merged_col = []
        current_group = []

        for block in col_blocks_sorted:
            block_type = block['type']

            # Если блок является изображением или формулой, добавляем его отдельно
            if block_type in ['picture', 'formula']:
                # Если есть текущая группа, добавляем её в merged_blocks
                if current_group:
                    merged_blocks.extend(current_group)
                    current_group = []
                # Добавляем изображение или формулу как отдельный блок
                merged_blocks.append(block)
                continue

            # Если текущей группы нет, начинаем новую
            if not current_group:
                current_group.append(block)
                continue

            last_block = current_group[-1]
            last_type = last_block['type']
            last_avg_font = get_average_font_size(last_block, base_font_size)
            current_avg_font = get_average_font_size(block, base_font_size)
            vertical_gap = block['bbox'][1] - last_block['bbox'][3]
            horizontal_gap = block['bbox'][0] - last_block['bbox'][2]

            vertical_gap = 0 if vertical_gap < 0 else vertical_gap

            # Проверка значительного различия в размере шрифта
            if max(last_avg_font, current_avg_font) == 0:
                font_difference = 0
            else:
                font_difference = abs(current_avg_font - last_avg_font) / max(last_avg_font, current_avg_font)

            if font_difference > 0.02:
                merged_blocks.extend(current_group)
                current_group = [block]
                continue

            # Порог для слияния
            threshold = max(last_avg_font, current_avg_font) * 1.2
            if last_type in ['marked_list', 'numbered_list'] and block_type == 'paragraph':
                threshold *= 0.2  # Меньший порог для параграфа после списка

            if last_type == ['marked_list'] and block_type == ['marked_list']:
                threshold = Pt(14)
            
            if last_type == ['numbered_list'] and block_type == ['numbered_list']:
                threshold = Pt(14)

            if last_type and block_type == 'paragraph':
                threshold *= 2

            if last_type and block_type == 'title':
                threshold *= 2.5

            if block_type == 'footnote':
                threshold *= 2.5

            # Условие слияния: только если типы одинаковые или параграф следует за списком
            if (block_type == last_type) or \
               (last_type in ['marked_list', 'numbered_list'] and block_type == 'paragraph'):
                if (vertical_gap < threshold or horizontal_gap > 0):
                    # Объединяем блоки
                    new_bbox = [
                        min(last_block['bbox'][0], block['bbox'][0]),
                        min(last_block['bbox'][1], block['bbox'][1]),
                        max(last_block['bbox'][2], block['bbox'][2]),
                        max(last_block['bbox'][3], block['bbox'][3])
                    ]
                    merged_text = f"{last_block.get('text', '')} {block.get('text', '')}".strip()
                    # Обновляем последний блок в текущей группе
                    current_group[-1]['bbox'] = new_bbox
                    current_group[-1]['text'] = merged_text
                else:
                    merged_blocks.extend(current_group)
                    current_group = [block]
            else:
                merged_blocks.extend(current_group)
                current_group = [block]

        # Добавляем оставшиеся блоки в текущей группе
        if current_group:
            merged_blocks.extend(current_group)

    # Теперь добавим логику для объединения блоков, если один находится внутри другого
    def is_inside(inner_block, outer_block):
        """ Проверка, если блок `inner_block` полностью внутри блока `outer_block` """
        return (inner_block['bbox'][0] >= outer_block['bbox'][0] and
                inner_block['bbox'][1] >= outer_block['bbox'][1] and
                inner_block['bbox'][2] <= outer_block['bbox'][2] and
                inner_block['bbox'][3] <= outer_block['bbox'][3])

    # Объединение вложенных блоков
    final_blocks = []
    for block in merged_blocks:
        merged = False
        for idx, final_block in enumerate(final_blocks):
            if final_block['type'] == block['type'] and is_inside(block, final_block):
                # Если текущий блок внутри другого, объединяем
                new_bbox = [
                    min(final_block['bbox'][0], block['bbox'][0]),
                    min(final_block['bbox'][1], block['bbox'][1]),
                    max(final_block['bbox'][2], block['bbox'][2]),
                    max(final_block['bbox'][3], block['bbox'][3])
                ]
                merged_text = f"{final_block.get('text', '')} {block.get('text', '')}".strip()
                final_blocks[idx]['bbox'] = new_bbox
                final_blocks[idx]['text'] = merged_text
                merged = True
                break
        if not merged:
            final_blocks.append(block)

    # Присваиваем метки "того, кто больше" по площади
    for idx, block in enumerate(final_blocks):
        if 'bbox' in block:
            block_width = block['bbox'][2] - block['bbox'][0]
            block_height = block['bbox'][3] - block['bbox'][1]
            block_area = block_width * block_height
            block['area'] = block_area

    # Сортируем все объединённые блоки по позиции на странице (сверху вниз, слева направо)
    return sorted(final_blocks, key=lambda b: (b['bbox'][1], b['bbox'][0]))


def refine_formula_bbox(image_path):
    """
    Уточняет границы формулы на изображении, где фон белый, а текст чёрный.
    """
    image = Image.open(image_path).convert('L')  # Преобразуем в градации серого
    np_image = np.array(image)

    # Инвертируем изображение: теперь формула белая на чёрном фоне
    inverted_image = 255 - np_image

    # Определяем пороговое значение
    threshold = 50  # Можете настроить порог при необходимости
    binary_image = (inverted_image > threshold).astype(np.uint8) * 255

    # Находим координаты ненулевых пикселей
    coords = np.column_stack(np.where(binary_image > 0))
    if coords.size == 0:
        # Если символы не найдены, возвращаем исходные размеры
        return 0, 0, image.width, image.height

    # Вычисляем границы (x_min, y_min, x_max, y_max)
    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)

    return x_min, y_min, x_max, y_max