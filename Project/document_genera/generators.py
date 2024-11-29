# generators.py

from faker import Faker
from mimesis import Generic
from mimesis.enums import Locale
import random
import sympy as sp
import matplotlib.pyplot as plt
from io import BytesIO
from docx.shared import Inches
from utils import roman_number
from config import locales
import os
import re
from config import reader  
from io import BytesIO
import matplotlib.pyplot as plt
import sympy as sp
import random
from mimesis import Text
from mimesis.locales import Locale
from io import BytesIO
from PIL import Image
import numpy as np
fake = Faker(list(locales.keys()))
generic = Generic(Locale.RU)

fake_en = Faker("en_US")
fake_ru = Faker("ru_RU")
text_en = Text(Locale.EN)
text_ru = Text(Locale.RU)

def generate_realistic_data():
    """
    Генерирует содержимое для ячейки таблицы с использованием mimesis.
    """
    data_type = random.choice(['name', 'date', 'number', 'address', 'company', 'number'])
    
    if data_type == 'name':
        return generic.person.full_name()
    elif data_type == 'date':
        return generic.datetime.date().strftime('%d.%m.%Y')  
    elif data_type == 'number':
        return str(random.randint(1, 1000))
    elif data_type == 'address':
        return generic.address.address()
    elif data_type == 'company':
        return generic.finance.company()
    elif data_type == 'number':
        return random.randint(1000)
    else:
        return generic.text.text(quantity=1)

def generate_formula_image():
    import random
    import sympy as sp
    from io import BytesIO
    import matplotlib.pyplot as plt

    # Основные математические символы и функции
    symbols_dict = {
        'variables': sp.symbols('x y z a b c'),
        'constants': [sp.pi, sp.E],
        'functions': [sp.sin, sp.cos, sp.exp, sp.log, sp.sqrt]
    }

    def random_symbol():
        return random.choice(list(symbols_dict['variables']) + symbols_dict['constants'])

    def random_expression(depth=0):
        if depth > 2 or random.choice([True, False]):
            expr = random_symbol()
            if random.choice([True, False]):
                func = random.choice(symbols_dict['functions'])
                expr = func(expr)
            return expr
        else:
            left = random_expression(depth + 1)
            right = random_expression(depth + 1)

            operator = random.choice(['+', '-', '*', '/', '**'])
            if operator == '/':
                # Проверка, чтобы избежать ошибок при создании sp.Rational
                if any(isinstance(arg, (sp.Basic, sp.Function)) for arg in [left, right]):
                    # Используем обычное деление, если аргументы содержат выражения
                    return left / (right + sp.Integer(1))
                else:
                    # Создаем sp.Rational для простых чисел
                    return sp.Rational(left, right + sp.Integer(1))
            elif operator == '**':
                exponent = random.randint(2, 3)
                return left ** exponent
            elif operator == '+':
                return left + right
            elif operator == '-':
                return left - right
            elif operator == '*':
                return left * right
            else:
                return left

    # Генерация выражения с минимальным количеством символов
    while True:
        expr = random_expression()
        latex_formula = sp.latex(expr)
        if len(latex_formula.replace('\\', '').replace('{', '').replace('}', '')) >= 3:
            break

    # Создание изображения
    plt.figure(figsize=(1.7 * 3, 0.7))
    plt.text(0.5, 0.5, f"${latex_formula}$", fontsize=27, ha='center', va='center')
    plt.axis('off')

    image_stream = BytesIO()
    plt.savefig(image_stream, format='png', bbox_inches='tight', pad_inches=0.1, transparent=True)
    plt.close()
    image_stream.seek(0)

    return image_stream


def test_formula_recognition(image_stream):
    """
    Проверяет, распознается ли формула в изображении.
    """
    from PIL import Image

    image = Image.open(image_stream)
    image.save("test_formula.png")  # Временный файл для отладки

    try:
        result = reader.readtext("test_formula.png")
        recognized_text = " ".join([text for _, text, _ in result])
        os.remove("test_formula.png")  # Удаляем временный файл
        return recognized_text
    except Exception as e:
        print(f"Ошибка распознавания формулы: {e}")
        os.remove("test_formula.png")
        return ""

def generate_formula_image_with_check():
    """
    Генерирует изображение формулы, которая гарантированно распознается EasyOCR.
    """
    max_attempts = 10
    for _ in range(max_attempts):
        image_stream = generate_formula_image()
        recognized_text = test_formula_recognition(image_stream)

        if len(recognized_text.strip()) > 0:
            return image_stream

    raise ValueError("Не удалось создать распознаваемую формулу после нескольких попыток.")
def roman_number(n):
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ''
    for i in range(len(val)):
        count = int(n / val[i])
        roman_num += syb[i] * count
        n -= val[i] * count
    return roman_num


def generate_chart():
    """
    Генерирует случайный график и сохраняет его как файл `temp_img_chart.png`.
    Возвращает путь к сохранённому изображению.
    """
    # Генерация случайного заголовка
    title = random.choice([fake_ru.sentence(), fake_en.sentence()])
    title = " ".join(title.split()[:5])  # Ограничиваем заголовок 5 словами

    # Расширенный список типов графиков
    chart_types = [
        'line', 'bar', 'scatter', 'pie', 'histogram',
        'box', 'area', 'heatmap', 'radar', 'bubble', 'stacked_bar',
        'violin', 'polar', '3d', 'density', 'step', 'errorbar', 'barh'
    ]
    chart_type = random.choice(chart_types)
    scale = random.uniform(1, 3)
    fig_width = 6 * scale  # Увеличено для более сложных графиков
    fig_height = 4 * scale
    plt.figure(figsize=(fig_width, fig_height))

    if chart_type == 'line':
        num_lines = random.randint(1, 3)  # Несколько линий
        x = np.linspace(0, 10, 100)
        for i in range(num_lines):
            y = np.sin(x + i) + np.random.normal(0, 0.1, 100)
            plt.plot(x, y, label=f"Line {i+1}")
        plt.title(title)
        plt.legend()

    elif chart_type == 'bar':
        num_categories = random.randint(3, 7)
        categories = [f"Cat{i}" for i in range(1, num_categories + 1)]
        values = np.random.randint(10, 100, size=num_categories)
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, num_categories))
        plt.bar(categories, values, color=colors)
        plt.title(title)

    elif chart_type == 'scatter':
        num_series = random.randint(1, 3)
        for i in range(num_series):
            x = np.random.rand(50) * 10
            y = np.random.rand(50) * 10
            sizes = np.random.randint(20, 200, size=50)
            colors = np.random.rand(50)
            plt.scatter(x, y, s=sizes, c=colors, alpha=0.5, cmap='coolwarm', label=f"Series {i+1}")
        plt.title(title)
        plt.legend()

    elif chart_type == 'pie':
        num_slices = random.randint(3, 6)
        sizes = np.random.randint(10, 50, size=num_slices)
        labels = [f"Part{i}" for i in range(1, num_slices + 1)]
        explode = [0.05] * num_slices  # Незначительное отделение секторов
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, explode=explode, shadow=True)
        plt.title(title)

    elif chart_type == 'histogram':
        num_bins = random.randint(10, 30)
        data = np.random.normal(loc=random.uniform(20, 80), scale=random.uniform(5, 15), size=500)
        plt.hist(data, bins=num_bins, color='skyblue', alpha=0.7, edgecolor='black')
        plt.title(title)

    elif chart_type == 'box':
        num_boxes = random.randint(3, 6)
        data = [np.random.normal(loc=random.uniform(0, 100), scale=random.uniform(1, 20), size=100) for _ in range(num_boxes)]
        plt.boxplot(data, vert=True, patch_artist=True, labels=[f"Box{i}" for i in range(1, num_boxes + 1)],
                    boxprops=dict(facecolor='lightgreen'))
        plt.title(title)

    elif chart_type == 'area':
        num_series = random.randint(1, 3)
        x = np.linspace(0, 10, 100)
        for i in range(num_series):
            y = (np.sin(x + i) + 1) * np.random.uniform(0.5, 1.5)
            plt.fill_between(x, y, alpha=0.3, label=f"Series {i+1}")
            plt.plot(x, y, label=f"Line {i+1}")
        plt.title(title)
        plt.legend()

    elif chart_type == 'heatmap':
        data_size = random.randint(5, 15)
        data = np.random.rand(data_size, data_size)
        plt.imshow(data, cmap='hot', interpolation='nearest')
        plt.colorbar()
        plt.title(title)

    elif chart_type == 'radar':
        categories = [f"Metric{i}" for i in range(1, 6)]
        num_vars = len(categories)

        values = np.random.randint(1, 10, size=num_vars).tolist()
        values += values[:1]  # Повторяем первый элемент для замыкания круга

        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]

        ax = plt.subplot(111, polar=True)
        ax.plot(angles, values, linewidth=1, linestyle='solid', label="Radar Chart")
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        plt.title(title, y=1.1)
        plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))

    elif chart_type == 'bubble':
        x = np.random.rand(100) * 100
        y = np.random.rand(100) * 100
        sizes = np.random.rand(100) * 1000
        colors = np.random.rand(100)
        plt.scatter(x, y, s=sizes, c=colors, alpha=0.6, cmap='plasma')
        plt.title(title)
        plt.colorbar(label='Color Scale')

    elif chart_type == 'stacked_bar':
        num_groups = random.randint(3, 6)
        num_categories = random.randint(2, 4)
        categories = [f"Group{i}" for i in range(1, num_groups + 1)]
        data = np.random.randint(5, 50, size=(num_categories, num_groups))
        bottom = np.zeros(num_groups)
        for i in range(num_categories):
            plt.bar(categories, data[i], bottom=bottom, label=f"Category {i+1}")
            bottom += data[i]
        plt.title(title)
        plt.legend()

    elif chart_type == 'violin':
        num_violin = random.randint(3, 6)
        data = [np.random.normal(loc=random.uniform(0, 100), scale=random.uniform(5, 15), size=200) for _ in range(num_violin)]
        plt.violinplot(data, showmeans=True, showmedians=True)
        plt.title(title)
        plt.xticks(range(1, num_violin + 1), [f"Violin{i}" for i in range(1, num_violin + 1)])

    elif chart_type == 'polar':
        theta = np.linspace(0, 2 * np.pi, 100)
        r = np.abs(np.sin(theta) * np.cos(theta)) * 100
        plt.subplot(111, polar=True)
        plt.plot(theta, r, color='purple')
        plt.fill(theta, r, color='purple', alpha=0.3)
        plt.title(title, va='bottom')

    elif chart_type == '3d':
        from mpl_toolkits.mplot3d import Axes3D  # Импортируем внутри условия
        ax = plt.axes(projection='3d')
        x = np.random.rand(100) * 10
        y = np.random.rand(100) * 10
        z = np.random.rand(100) * 10
        dx = dy = np.ones(100) * 0.1
        dz = np.random.rand(100) * 10
        ax.bar3d(x, y, np.zeros(100), dx, dy, dz, color='cyan', alpha=0.6)
        plt.title(title)

    elif chart_type == 'density':
        from scipy.stats import gaussian_kde  # Импортируем внутри условия
        x = np.random.randn(1000)
        y = np.random.randn(1000)
        density = gaussian_kde([x, y])
        xi, yi = np.mgrid[x.min():x.max():100j, y.min():y.max():100j]
        zi = density(np.vstack([xi.flatten(), yi.flatten()]))
        plt.pcolormesh(xi, yi, zi.reshape(xi.shape), shading='auto', cmap='viridis')
        plt.colorbar()
        plt.title(title)

    elif chart_type == 'step':
        x = np.linspace(0, 10, 100)
        y = np.random.randint(0, 100, size=100).cumsum()
        plt.step(x, y, where='mid', label='Step Chart', color='brown')
        plt.title(title)
        plt.legend()

    elif chart_type == 'errorbar':
        x = np.linspace(0, 10, 10)
        y = np.sin(x) + np.random.normal(0, 0.1, len(x))
        yerr = np.random.uniform(0.1, 0.3, size=len(x))
        plt.errorbar(x, y, yerr=yerr, fmt='o', label='Error Bars', color='red', ecolor='lightgray', elinewidth=3, capsize=0)
        plt.title(title)
        plt.legend()

    elif chart_type == 'barh':
        num_categories = random.randint(3, 7)
        categories = [f"Cat{i}" for i in range(1, num_categories + 1)]
        values = np.random.randint(10, 100, size=num_categories)
        colors = plt.cm.Pastel1(np.linspace(0, 1, num_categories))
        plt.barh(categories, values, color=colors)
        plt.title(title)

    else:
        # Default line chart if unknown type
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        plt.plot(x, y, label="Default Line Chart", color='blue')
        plt.title(title)
        plt.legend()

    # Путь для временного файла
    temp_img_path = "temp_img_chart.png"

    # Сохранение графика в файл
    plt.savefig(temp_img_path, format='png', bbox_inches='tight')
    plt.close()

    return temp_img_path