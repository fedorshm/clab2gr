import os
import subprocess

def docx_to_pdf_converter(input_folder, output_folder, timeout=120):
    """
    Конвертирует файлы .docx в .pdf с помощью LibreOffice.

    :param input_folder: Папка с входными файлами .docx.
    :param output_folder: Папка для сохранения выходных файлов .pdf.
    :param timeout: Время в секундах для завершения конвертации одного файла.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".docx"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename.replace(".docx", ".pdf"))
            try:
                subprocess.run(
                    ['soffice', '--headless', '--convert-to', 'pdf', input_path, '--outdir', output_folder],
                    check=True,
                    timeout=timeout
                )
                print(f"Конвертировано: {input_path} -> {output_path}")
            except subprocess.TimeoutExpired:
                # Если превышен таймаут, выводим сообщение и продолжаем обработку
                print(f"Ошибка: Конвертация файла {input_path} превысила таймаут {timeout} секунд. Пропущено.")
            except subprocess.CalledProcessError as e:
                # Обработка других ошибок конвертации
                print(f"Ошибка при конвертации файла {input_path}: {e}")
