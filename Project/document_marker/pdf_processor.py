import os
from ocr_utils import extract_font_sizes, extract_blocks
from annotations import save_annotations_per_page
from visualization import visualize_annotations
from utils import convert_pdf_to_png

def process_pdfs(input_pdf_dir, output_json_dir, output_image_dir, image_dir):
    os.makedirs(output_json_dir, exist_ok=True)
    os.makedirs(output_image_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)

    for filename in os.listdir(input_pdf_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_pdf_dir, filename)
            print(f"\nОбработка документа: {pdf_path}")
            process_pdf(pdf_path, output_json_dir, output_image_dir, image_dir)
            print(f"Визуализация всех страниц документа завершена: {pdf_path}")

def process_pdf(pdf_path, output_json_dir, output_image_dir=None, image_dir=None):
    base_font_size = extract_font_sizes(pdf_path)
    if base_font_size is None:
        print(f"Не удалось определить базовый размер шрифта для документа '{pdf_path}'. Пропуск.")
        return

    annotations = extract_blocks(pdf_path, base_font_size)
    num_pages = len(annotations)

    for page_num in range(num_pages):
        # Конвертация страницы в PNG без разметки
        image_path = convert_pdf_to_png(pdf_path, image_dir, page_num) if image_dir else ""

        # Визуализация аннотаций и сохранение аннотированного изображения
        visualize_annotations(pdf_path, annotations, page_num, output_image_dir)

        # Получение размеров изображения
        image_width, image_height = get_image_dimensions(pdf_path, page_num)

        # Путь к JSON-файлу
        json_filename = os.path.join(output_json_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page_{page_num + 1}.json")

        # Сохранение аннотаций с информацией об изображении
        page_data = annotations.get(page_num, {})
        save_annotations_per_page(
            page_num=page_num,
            page_data=page_data,
            image_width=image_width,
            image_height=image_height,
            image_path=image_path if image_dir else "",
            output_path=json_filename
        )

def get_image_dimensions(pdf_path, page_num):
    import fitz
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num)
    pix = page.get_pixmap()
    image_width = pix.width
    image_height = pix.height
    doc.close()
    return image_width, image_height
