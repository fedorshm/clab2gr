import json
import numpy as np

def convert_to_serializable(obj):
    """
    Рекурсивно преобразует неподдерживаемые JSON объекты в стандартные типы Python.
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    else:
        return obj

def save_annotations_per_page(page_num, page_data, image_width, image_height, image_path, output_path):
    if not page_data:
        return

    json_data = {
        "image_height": image_height,
        "image_width": image_width,
        "image_path": image_path,
    }

    for block_type, blocks in page_data.items():
        json_data[block_type] = [block['bbox'] for block in blocks]

    # Преобразование данных в сериализуемый формат
    json_data = convert_to_serializable(json_data)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    print(f"Аннотации сохранены в {output_path}")
