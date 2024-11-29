
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import random

def apply_paragraph_format(paragraph, base_font_size, is_multicolumn=False):
    """
    Применяет форматирование к параграфу.

    :param paragraph: объект параграфа
    :param base_font_size: базовый размер шрифта
    :param is_multicolumn: флаг, указывающий, находится ли параграф в многоколоночной секции
    """
    paragraph_format = paragraph.paragraph_format
    if random.choice([True, False]):
        paragraph_format.first_line_indent = Pt(35.5)
    else:
        paragraph_format.first_line_indent = None

    paragraph_format.left_indent = Pt(0)
    paragraph_format.right_indent = Pt(0)    

    # Если текст в колонках, чаще выравниваем по ширине
    alignment_weights = [0.7, 0.1, 0.1, 0.1] if is_multicolumn else [0.3, 0.3, 0.2, 0.2]

    paragraph_format.alignment = random.choices(
        [WD_ALIGN_PARAGRAPH.JUSTIFY, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.RIGHT],
        weights=alignment_weights,
        k=1
    )[0]

def apply_run_format(run, base_font_size):
    """
    Применяет форматирование к запуску текста.

    :param run: объект запуска текста
    :param base_font_size: базовый размер шрифта
    """
    run.font.size = Pt(base_font_size)
    run.font.name = random.choice(['Times New Roman', 'Arial', 'Calibri', 'Verdana'])

def apply_title_format(paragraph, base_font_size, num=1):
    """
    Применяет форматирование к заголовку.

    :param paragraph: объект параграфа
    :param base_font_size: базовый размер шрифта
    :param num: номер заголовка (1 для основного, 2 для подзаголовка и т.д.)
    """
    run = paragraph.runs[0]
    run.font.italic = random.choice([True, False])

    if run.font.italic:
        run.font.bold = random.choice([True, False])
    else:
        run.font.bold = True
    if num == 1:
        title_font_size = base_font_size + random.choice([2, 3, 4, 5])
    elif num == 2:
        title_font_size = base_font_size + random.choice([2, 3])
    else:
        title_font_size = base_font_size + random.choice([1, 2])

    run.font.size = Pt(title_font_size)

    paragraph.alignment = random.choices(
        [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.RIGHT],
        weights=[0.6, 0.2, 0.2],
        k=1
    )[0]

