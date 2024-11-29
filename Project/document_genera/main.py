from document import create_document
import os

def main():

    for index in range(100):
        filename, base_font_size = create_document(index)
        base_filename = os.path.splitext(os.path.basename(filename))[0]
        
        print(f"Сгенерирован документ: {filename} ")

    print("Генерация документов завершена.")

if __name__ == "__main__":
    main()


