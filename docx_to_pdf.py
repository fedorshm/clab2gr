import os
import subprocess

def docx_to_pdf_converter(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".docx"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename.replace(".docx", ".pdf"))
            try:
                # Используем libre-ofice для конвертации
                #docker потребуется
                #sudo apt install libreoffice -y 
     
                subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', input_path, '--outdir', output_folder], check=True)
                print(f"Конвертировано: {input_path} -> {output_path}")
            except subprocess.CalledProcessError as e:
                print(f"Ошибка при конвертации файла {input_path}: {e}")

if __name__ == "__main__":
    input_folder = "docx"  
    output_folder = "pdf"   

    docx_to_pdf_converter(input_folder, output_folder)
    print("Конвертация завершена!")