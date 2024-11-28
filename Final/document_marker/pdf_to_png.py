import fitz
import os

def convert_pdf_to_png(pdf_path, image_folder, page_num):

    os.makedirs(image_folder, exist_ok=True)
    pdf = fitz.open(pdf_path)
    page = pdf[page_num]
    pix = page.get_pixmap()
    image_path = os.path.join(image_folder, f"{os.path.basename(pdf_path)}_page_{page_num + 1}.png")
    pix.save(image_path)
    pdf.close()
    return image_path
