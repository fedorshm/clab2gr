import os
import streamlit as st
from PIL import Image
import cv2
from ultralytics import YOLO
import pypdfium2 as pdfium
import json
import time 

TEMP_PDF_PATH = "temp_doc.pdf"
TEMP_PNG_DIR = "temp_pngs"
OUTPUT_PNG_DIR = "output_pngs"
MODEL_PATH = "best.pt"

custom_confidences = {
    0: 0.3,  # title
    1: 0.1,  # paragraph
    9: 0.15, # footer
    11: 0.1,  # formula
    10: 0.88, # footnote
    6: 0.9, # numbered_list
    7: 0.9  # marked_list
}

general_conf = 0.4
iou_threshold = 0.51

def convert_pdf_to_pngs(pdf_file_path, output_directory):
    pdf = pdfium.PdfDocument(pdf_file_path)
    png_paths = []
    os.makedirs(output_directory, exist_ok=True)
    
    for i in range(len(pdf)):
        page = pdf[i]
        pil_image = page.render(scale=2).to_pil()
        png_file_path = os.path.join(output_directory, f"page_{i+1}.png")
        pil_image.save(png_file_path)
        png_paths.append(png_file_path)
        
    return png_paths

def run_yolo_on_multiple_images(model_path, png_file_paths, output_directory):
    model = YOLO(model_path)
    os.makedirs(output_directory, exist_ok=True)
    
    if hasattr(model, 'names'):
        class_names = model.names
    else:
        raise ValueError("Модель не предоставляет названия классов")
    
    output_paths = []
    detections = []

    for png_file_path in png_file_paths:
        img = cv2.imread(png_file_path)
        results = model.predict(source=img, conf=general_conf, iou=iou_threshold, save=False)
        
        filtered_boxes = []
        for result in results:
            for box in result.boxes:
                cls = int(box.cls)
                conf = float(box.conf)

                if cls in custom_confidences:
                    if conf >= custom_confidences[cls]:
                        filtered_boxes.append(box)
                else:
                    if conf >= general_conf:
                        filtered_boxes.append(box)

            result.boxes = filtered_boxes

        result_image = results[0].plot()
        output_file_path = os.path.join(output_directory, f"processed_{os.path.basename(png_file_path)}")
        cv2.imwrite(output_file_path, result_image)
        output_paths.append(output_file_path)
        
        image_detections = []
        for box in filtered_boxes:
            class_id = int(box.cls)
            class_name = class_names.get(class_id, "Unknown")
            confidence = float(box.conf)
            box_details = box.xywh.numpy().tolist()

            details = {
                "class_id": class_id,
                "class_name": class_name,
                "confidence": confidence,
                "box": box_details
            }
            image_detections.append(details)

        detections.append({os.path.basename(png_file_path): image_detections})

    return output_paths, detections

def main():
    st.title("Распознавание объектов документа через YOLO")
    st.write("Загрузите документ формата PDF или PNG.")

    uploaded_file = st.file_uploader("Загрузка документа", type=["pdf", "png"])
    if uploaded_file is not None:
        start_time = time.time() 

        file_name = uploaded_file.name
        file_extension = os.path.splitext(file_name)[-1].lower()
        
        if file_extension == '.pdf':
            with open(TEMP_PDF_PATH, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            st.write("Конвертация документа в PNG...")
            png_paths = convert_pdf_to_pngs(TEMP_PDF_PATH, TEMP_PNG_DIR)
        
        elif file_extension == '.png':
            os.makedirs(TEMP_PNG_DIR, exist_ok=True)
            png_path = os.path.join(TEMP_PNG_DIR, "uploaded.png")
            with open(png_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            png_paths = [png_path]

        if png_paths:
            st.write("Обработка через YOLO...")
            output_paths, detections = run_yolo_on_multiple_images(MODEL_PATH, png_paths, OUTPUT_PNG_DIR)
            for output_path, detection in zip(output_paths, detections):
                st.image(Image.open(output_path), caption=f'Processed {os.path.basename(output_path)}', use_container_width=True)
                st.json(detection)
                json_str = json.dumps(detection, indent=4)
                st.download_button(
                    label="Скачать JSON",
                    data=json_str,
                    file_name=f"{os.path.splitext(os.path.basename(output_path))[0]}_detections.json",
                    mime="application/json"
                )

            end_time = time.time()  
            processing_time = end_time - start_time
            st.write(f"Время обработки: {processing_time:.2f} сек.")

        cleanup_temp_files()

def cleanup_temp_files():
    for dir_path in [TEMP_PNG_DIR, OUTPUT_PNG_DIR]:
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                st.error(f"Ошибка с удалением временного файла {file_path}: {e}")

    for path in [TEMP_PDF_PATH, TEMP_PNG_DIR, OUTPUT_PNG_DIR]:
        if os.path.isdir(path):
            try:
                os.rmdir(path)
            except OSError:
                pass

if __name__ == "__main__":
    main()
