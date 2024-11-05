import pypdfium2 as pdfium
from PIL import Image
import os

def extract_images_from_pdf():
    pdf_folder = 'pdf'
    image_folder = 'image'
    
    if not os.path.exists(pdf_folder):
        print(f"Папка '{pdf_folder}' не существует.")
        return
    
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
        print(f"Создана папка '{image_folder}'.")
    
    pdf_files = os.listdir(pdf_folder)
    if not pdf_files:
        print(f"В папке '{pdf_folder}' нет PDF-файлов.")
        return
    
    for pdf_file in pdf_files:
        if not pdf_file.lower().endswith('.pdf'):
            print(f"Файл '{pdf_file}' не является PDF. Пропускаем.")
            continue
        
        pdf_path = os.path.join(pdf_folder, pdf_file)
        print(f"Обработка файла: {pdf_path}")
        
        try:
            pdf = pdfium.PdfDocument(pdf_path)
            n_pages = len(pdf)
            print(f"Количество страниц в документе: {n_pages}")
            
            for page_number in range(n_pages):
                try:
                    page = pdf.get_page(page_number)
                    pil_image = page.render(scale=300/72).to_pil()
                    image_name = f"{os.path.splitext(pdf_file)[0]}_{page_number + 1}.png"
                    image_path = os.path.join(image_folder, image_name)
                    pil_image.save(image_path)
                    print(f"Сохранено изображение: {image_path}")
                    page.close()
                except Exception as e:
                    print(f"Ошибка при обработке страницы {page_number + 1} в '{pdf_file}': {e}")
            
            pdf.close()
        except Exception as e:
            print(f"Не удалось открыть PDF-файл '{pdf_file}': {e}")


extract_images_from_pdf()