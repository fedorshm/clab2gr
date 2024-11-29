import os
import json
import shutil
from pathlib import Path
from itertools import combinations

def scale_bounding_box(box, scale_x, scale_y):
    """
    Масштабирование координат бокса.

    Args:
        box (list): [x1, y1, x2, y2]
        scale_x (float): Масштаб по оси X
        scale_y (float): Масштаб по оси Y

    Returns:
        list: [x1_new, y1_new, x2_new, y2_new]
    """
    x1, y1, x2, y2 = box
    return [x1 * scale_x, y1 * scale_y, x2 * scale_x, y2 * scale_y]

def boxes_overlap(box1, box2):
    """
    Проверка пересечения двух боксов.

    Args:
        box1 (list): [x1, y1, x2, y2]
        box2 (list): [x1, y1, x2, y2]

    Returns:
        bool: True если бокс1 пересекается с бокс2, иначе False
    """
    # Распаковываем координаты
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2

    # Проверка пересечения
    return not (x1_max <= x2_min or x2_max <= x1_min or
                y1_max <= y2_min or y2_max <= y1_min)

def process_json_file(json_path, target_height_landscape=2550, target_width_landscape=3301,
                     target_height_portrait=3301, target_width_portrait=2550):
    """
    Обработка одного JSON-файла: исправление размеров и масштабирование координат.

    Args:
        json_path (str): Путь к JSON-файлу
        target_height_landscape (int): Новая высота для альбомной ориентации
        target_width_landscape (int): Новая ширина для альбомной ориентации
        target_height_portrait (int): Новая высота для портретной ориентации
        target_width_portrait (int): Новая ширина для портретной ориентации

    Returns:
        bool: True если файл успешно обработан и не содержит пересечений, иначе False
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Ошибка при чтении {json_path}: {e}")
        return False
    except Exception as e:
        print(f"Не удалось открыть {json_path}: {e}")
        return False

    original_height = data.get("image_height", None)
    original_width = data.get("image_width", None)

    if original_height is None or original_width is None:
        print(f"Отсутствуют 'image_height' или 'image_width' в {json_path}. Пропуск файла.")
        return False

    # Определение ориентации изображения
    if original_width > original_height:
        # Альбомная ориентация
        new_height, new_width = target_height_landscape, target_width_landscape
    else:
        # Портретная ориентация
        new_height, new_width = target_height_portrait, target_width_portrait

    # Вычисление масштабов
    scale_x = new_width / original_width
    scale_y = new_height / original_height

    # Проверка сохранения соотношения сторон
    aspect_ratio_original = original_width / original_height
    aspect_ratio_target = new_width / new_height
    if not abs(aspect_ratio_original - aspect_ratio_target) < 1e-4:
        print(f"Предупреждение: Соотношение сторон в {json_path} изменится после масштабирования.")

    # Исправление размеров изображения
    data["image_height"] = new_height
    data["image_width"] = new_width

    # Список всех боксов для проверки пересечений
    all_boxes = []

    # Проход по всем ключам, содержащим боксы
    for cls in data.keys():
        if cls in ["image_height", "image_width", "image_path"]:
            continue
        boxes = data.get(cls, [])
        scaled_boxes = []
        for box in boxes:
            if len(box) != 4:
                print(f"Некорректные координаты в {json_path} для класса '{cls}': {box}. Пропуск бокса.")
                continue
            scaled_box = scale_bounding_box(box, scale_x, scale_y)
            scaled_boxes.append(scaled_box)
            all_boxes.append(scaled_box)
        data[cls] = scaled_boxes  # Обновление координат

    # Проверка на пересечения
    for box1, box2 in combinations(all_boxes, 2):
        if boxes_overlap(box1, box2):
            print(f"Пересечение боксов в файле {json_path}. Удаление файла.")
            try:
                os.remove(json_path)
                print(f"Файл удалён: {json_path}")
            except Exception as e:
                print(f"Не удалось удалить файл {json_path}: {e}")
            return False  # Файл удалён из-за пересечений

    # Если пересечений нет, сохраняем исправленный JSON
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Файл обработан успешно: {json_path}")
        return True
    except Exception as e:
        print(f"Не удалось сохранить исправленный JSON для {json_path}: {e}")
        return False

def create_backup(json_dir, backup_dir):
    """
    Создание резервной копии всех JSON-файлов.

    Args:
        json_dir (str): Директория с исходными JSON-файлами
        backup_dir (str): Директория для резервных копий
    """
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    print(f"Создание резервных копий JSON-файлов в {backup_dir}...")

    json_files = list(Path(json_dir).glob("*.json"))
    if not json_files:
        print(f"В директории {json_dir} не найдено JSON-файлов.")
        return

    for json_file in json_files:
        try:
            backup_path = Path(backup_dir) / json_file.name
            if not backup_path.exists():
                shutil.copy2(json_file, backup_path)
                print(f"Создана резервная копия: {backup_path}")
            else:
                print(f"Резервная копия уже существует: {backup_path}")
        except Exception as e:
            print(f"Не удалось создать резервную копию для {json_file}: {e}")

def main():
    JSON_DIR = "json_annotations"  # Директория с JSON-файлами
    BACKUP_DIR = "json_annotations_backup"  # Директория для резервных копий
    TARGET_HEIGHT_LANDSCAPE = 2550
    TARGET_WIDTH_LANDSCAPE = 3301
    TARGET_HEIGHT_PORTRAIT = 3301
    TARGET_WIDTH_PORTRAIT = 2550

    # Создание резервной копии
    create_backup(JSON_DIR, BACKUP_DIR)

    # Получение списка всех JSON-файлов
    json_files = list(Path(JSON_DIR).glob("*.json"))
    if not json_files:
        print(f"В директории {JSON_DIR} не найдено JSON-файлов.")
        return

    success_count = 0
    delete_count = 0
    for json_file in json_files:
        result = process_json_file(
            str(json_file),
            target_height_landscape=TARGET_HEIGHT_LANDSCAPE,
            target_width_landscape=TARGET_WIDTH_LANDSCAPE,
            target_height_portrait=TARGET_HEIGHT_PORTRAIT,
            target_width_portrait=TARGET_WIDTH_PORTRAIT
        )
        if result:
            success_count += 1
        else:
            delete_count += 1

    print("\n=== Результаты обработки ===")
    print(f"Всего обработано файлов: {len(json_files)}")
    print(f"Успешно обработано: {success_count}")
    print(f"Удалено из-за пересечений или ошибок: {delete_count}")

if __name__ == "__main__":
    main()
