import fitz
from pathlib import Path


def merge_blocks_by_column(blocks, column_threshold=50):
    """
    Объединяет текстовые блоки в каждой колонке.

    :param blocks: Список текстовых блоков.
    :param column_threshold: Пороговое значение для разделения колонок (в пикселях).
    :return: Список объединённых блоков.
    """
    # Сортируем блоки по X-координате (левый верхний угол)
    blocks = sorted(blocks, key=lambda b: b["bbox"][0])

    # Разделяем блоки на колонки
    columns = []
    current_column = [blocks[0]]

    for block in blocks[1:]:
        prev_block = current_column[-1]
        # Проверяем, находятся ли блоки в одной колонке (по горизонтальной близости)
        if block["bbox"][0] - prev_block["bbox"][2] < column_threshold:
            current_column.append(block)
        else:
            columns.append(current_column)
            current_column = [block]

    if current_column:
        columns.append(current_column)

    # Объединяем блоки в каждой колонке
    merged_blocks = []
    for column in columns:
        column = sorted(column, key=lambda b: b["bbox"][1])  # Сортируем блоки по Y-координате (по вертикали)
        merged_text = " ".join([block["lines"][0]["spans"][0]["text"] for block in column if "lines" in block])
        bbox = [
            min(block["bbox"][0] for block in column),  # Левый верхний угол X
            min(block["bbox"][1] for block in column),  # Левый верхний угол Y
            max(block["bbox"][2] for block in column),  # Правый нижний угол X
            max(block["bbox"][3] for block in column),  # Правый нижний угол Y
        ]
        merged_blocks.append({"text": merged_text, "bbox": bbox})

    return merged_blocks


def visualize_blocks_with_merging(pdf_path, output_path):
    """
    Визуализирует объединённые текстовые блоки зелёными рамками и сохраняет PDF.

    :param pdf_path: Путь к исходному PDF-файлу.
    :param output_path: Путь для сохранения визуализированного PDF.
    """
    doc = fitz.open(pdf_path)  # Открываем PDF

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Загружаем страницу
        blocks = page.get_text("dict")["blocks"]

        # Объединяем блоки по колонкам
        merged_blocks = merge_blocks_by_column(blocks)

        for block in merged_blocks:
            bbox = block["bbox"]  # Координаты объединённого блока
            x0, y0, x1, y1 = bbox
            # Рисуем зелёную рамку вокруг объединённого блока
            page.draw_rect(fitz.Rect(x0, y0, x1, y1), color=(0, 1, 0), width=1.0)

    # Сохраняем результат
    doc.save(output_path)
    print(f"Визуализированный PDF сохранён в: {output_path}")


# Пример использования
pdf_path = "pdf/doc_0.pdf"  # Путь к входному PDF
output_path = "output_visualized.pdf"  # Путь к сохранённому PDF

visualize_blocks_with_merging(pdf_path, output_path)
