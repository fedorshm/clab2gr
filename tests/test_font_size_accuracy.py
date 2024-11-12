import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pdf_marking import extract_font_sizes
import csv
from pdf_marking import extract_font_sizes
import glob


def load_font_sizes(csv_path):
    font_sizes = {}
    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                font_sizes[row['filename']] = int(row['base_font_size'])
    except Exception as e:
        print(f"Ошибка при загрузке истинных размеров шрифтов из {csv_path}: {e}")
    return font_sizes
def get_pdf_files(directory):
    abs_directory = os.path.abspath(directory)
    pdf_files = glob.glob(os.path.join(abs_directory, "*.pdf")) + glob.glob(os.path.join(abs_directory, "*.PDF"))
    return pdf_files

def compare_font_sizes(pdf_files, font_sizes):
    correct_predictions = 0
    total_predictions = 0

    for pdf_file in pdf_files:
        base_filename = os.path.splitext(os.path.basename(pdf_file))[0]
        base_size = extract_font_sizes(pdf_file)
        
        if base_size is None:
            print(f"Файл: {base_filename}.pdf, базовый размер шрифта не найден.")
            continue

        true_size = font_sizes.get(base_filename)
        
        if true_size is None:
            print(f"Файл: {base_filename}.pdf, истинный размер шрифта не найден в CSV.")
        else:
            total_predictions += 1
            if base_size == true_size:
                correct_predictions += 1
                print(f"Файл: {base_filename}.pdf, базовый размер шрифта: {base_size} совпадает с истинным значением.")
            else:
                print(f"Файл: {base_filename}.pdf, базовый размер шрифта: {base_size} не совпадает с истинным значением {true_size}.")

    if total_predictions > 0:
        accuracy = correct_predictions / total_predictions * 100
        print(f"\nТочность предсказания размеров шрифта: {accuracy:.2f}% ({correct_predictions} из {total_predictions} совпадений)")
    else:
        print("\nНет данных для расчета точности.")

def main():
    # Путь к директории с PDF-файлами и CSV-файлу с истинными значениями
    directory_path = "pdf"
    csv_path = "font_sizes.csv"

    # Загрузка истинных размеров шрифтов из CSV
    font_sizes = load_font_sizes(csv_path)

    # Получение списка PDF-файлов
    pdf_files = get_pdf_files(directory_path)

    # Сравнение размеров шрифтов, если PDF-файлы найдены
    if pdf_files and font_sizes:
        compare_font_sizes(pdf_files, font_sizes)
    else:
        print("Нет PDF-файлов или истинных значений для сравнения.")

if __name__ == "__main__":
    main()
