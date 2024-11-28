from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import random

def apply_paragraph_format(paragraph, base_font_size, cell):
    paragraph_format = paragraph.paragraph_format
    if random.choice([True, False]):
        paragraph_format.first_line_indent = Pt(35.5)
    else:
        paragraph_format.first_line_indent = None

    if cell is not None: 
        paragraph_format.alignment = random.choices(
        [WD_ALIGN_PARAGRAPH.JUSTIFY, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.RIGHT],
        weights=[0.8, 0.1, 0.1, 0],
        k=1
        )[0]
    else:
        paragraph_format.alignment = random.choices(
            [WD_ALIGN_PARAGRAPH.JUSTIFY, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.RIGHT],
            weights=[0.6, 0.2, 0.3, 0.1],
            k=1
        )[0]

def apply_run_format(run, base_font_size):
    run.font.size = Pt(base_font_size)
    run.font.name = random.choice(['Times New Roman', 'Arial', 'Calibri', 'Verdana'])

def apply_title_format(paragraph, base_font_size, number):
    run = paragraph.runs[0]
    run.font.italic = random.choice([True, False])

    if run.font.italic:
        run.font.bold = random.choice([True, False])
    else:
        run.font.bold = True
    if number == 1:
        title_font_size = base_font_size + random.choice([2, 3, 4, 5])
    else:
        title_font_size = base_font_size + random.choice([2, 3])

    run.font.size = Pt(title_font_size)

    paragraph.alignment = random.choices(
        [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.RIGHT],
        weights=[0.6, 0.2, 0.2],
        k=1
    )[0]
