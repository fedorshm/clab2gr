#pip install -r requirements.txt

#ubuntu
#sudo apt update
#sudo apt install libreoffice -y

import os
from docx_to_pdf import docx_to_pdf_converter 
from pdf_processor import process_pdfs

def main():
    input_docx_dir = "docx"              # Папка с DOCX-документами
    converted_pdf_dir = "pdf"  # Папка для сохранения конвертированных PDF
    output_json_dir = "json_annotations"
    output_image_dir = "annotated_images"
    image_dir = "images"

    # Конвертация DOCX в PDF
    print("Начало конвертации DOCX в PDF...")
    docx_to_pdf_converter(input_docx_dir, converted_pdf_dir, timeout=180)
    print("Конвертация DOCX в PDF завершена.")

    #  Обработка конвертированных PDF
    print("\nНачало обработки PDF-документов...")
    process_pdfs(converted_pdf_dir, output_json_dir, output_image_dir, image_dir)
    print("Обработка PDF-документов завершена.")

    print("\nВсе операции успешно завершены.")

if __name__ == "__main__":
    main()
