import os
import random
import shutil
from pathlib import Path

def create_datasets(json_dir, images_dir, output_dir, train_size=0, test_size=1000, val_size=0):
    """
    Создаёт обучающую, тестовую и валидационную выборки из исходных данных.
    
    Args:
        json_dir (str): Путь к директории с JSON-файлами.
        images_dir (str): Путь к директории с изображениями.
        output_dir (str): Путь к директории, где будут сохранены выборки.
        train_size (int): Размер обучающей выборки.
        test_size (int): Размер тестовой выборки.
        val_size (int): Размер валидационной выборки.
    """
    # Получаем список всех JSON-файлов
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    total_files = len(json_files)
    
    # Проверка достаточного количества файлов
    required_total = train_size + test_size + val_size
    if total_files < required_total:
        print(f"Недостаточно файлов для заданных размеров выборок. Всего файлов: {total_files}, требуется: {required_total}")
        return
    
    # Перемешиваем файлы случайным образом
    random.shuffle(json_files)
    
    # Разделяем файлы на выборки
    train_files = json_files[:train_size]
    test_files = json_files[train_size:train_size + test_size]
    val_files = json_files[train_size + test_size:train_size + test_size + val_size]
    
    assert len(set(train_files).intersection(set(test_files))) == 0, "Обучающая и тестовая выборки пересекаются!"
    assert len(set(train_files).intersection(set(val_files))) == 0, "Обучающая и валидационная выборки пересекаются!"
    assert len(set(test_files).intersection(set(val_files))) == 0, "Тестовая и валидационная выборки пересекаются!"
    
    def copy_files(file_list, dataset_type):
        json_output_dir = Path(output_dir) / dataset_type / 'json'
        images_output_dir = Path(output_dir) / dataset_type / 'images'
        json_output_dir.mkdir(parents=True, exist_ok=True)
        images_output_dir.mkdir(parents=True, exist_ok=True)
        
        for json_file in file_list:
            # Копируем JSON-файл
            json_src = Path(json_dir) / json_file
            json_dst = json_output_dir / json_file
            shutil.copy2(json_src, json_dst)
            
            # Предполагаем, что имя изображения совпадает с именем JSON-файла, но с другим расширением
            image_filename = json_file.replace('.json', '.png')  # Измените расширение, если необходимо
            image_src = Path(images_dir) / image_filename
            image_dst = images_output_dir / image_filename
            
            if image_src.exists():
                shutil.copy2(image_src, image_dst)
            else:
                print(f"Изображение не найдено для {json_file}: {image_src}")
    
    # Копируем файлы в соответствующие директории
    print("Копирование файлов обучающей выборки...")
    copy_files(train_files, 'train')
    print("Копирование файлов тестовой выборки...")
    copy_files(test_files, 'test')
    print("Копирование файлов валидационной выборки...")
    copy_files(val_files, 'validation')
    
    print("Разделение данных завершено.")

def main():
    JSON_DIR = "json_annotations"  # Директория с JSON-файлами
    IMAGES_DIR = "images"          # Директория с изображениями
    OUTPUT_DIR = "dataset_1000"         # Директория для сохранения выборок
    
    TRAIN_SIZE = 0
    TEST_SIZE = 1000
    VAL_SIZE = 0
    
    create_datasets(JSON_DIR, IMAGES_DIR, OUTPUT_DIR, TRAIN_SIZE, TEST_SIZE, VAL_SIZE)

if __name__ == "__main__":
    main()
