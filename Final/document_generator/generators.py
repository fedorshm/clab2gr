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

fake = Faker(list(locales.keys()))
generic = Generic(Locale.RU)

def generate_realistic_data():
    """
    Генерирует содержимое для ячейки таблицы с использованием mimesis.
    """
    data_type = random.choice(['name', 'date', 'number', 'address', 'company'])
    
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
    else:
        return generic.text.text(quantity=random.randint(1))

def generate_formula_image():
    symbols_dict = {
        'variables': sp.symbols('x y z a b c'),
        'greek': sp.symbols('alpha beta gamma delta epsilon theta lambda mu nu sigma phi psi omega chi'),
        'constants': [sp.pi, sp.E],
        'functions': [sp.sin, sp.cos, sp.exp, sp.log, sp.sqrt, sp.tan, sp.cot, sp.sec, sp.csc, sp.sinh, sp.cosh, sp.tanh],
    }

    def random_symbol():
        category = random.choice(['variables', 'greek', 'constants'])
        if category == 'constants':
            return random.choice(symbols_dict['constants'])
        else:
            return random.choice(symbols_dict[category]) 

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
            if operator == '+':
                return left + right
            elif operator == '-':
                return left - right
            elif operator == '*':
                return left * right
            elif operator == '/':
                right = right + sp.Integer(1)
                return left / right
            elif operator == '**':
                exponent = random.randint(2, 3)
                return left ** exponent
            else:
                return left

    while True:
        expr = random_expression()
        num_symbols = len(expr.free_symbols)
        num_constants = len(expr.atoms(sp.pi)) + len(expr.atoms(sp.E))
        num_total = num_symbols + num_constants
        if num_total >= 3:
            break

    latex_formula = sp.latex(expr)

    plt.figure(figsize=(5, 1.5))
    plt.text(0.5, 0.5, f"${latex_formula}$", fontsize=20, ha='center', va='center')
    plt.axis('off')

    image_stream = BytesIO()
    plt.savefig(image_stream, format='png', bbox_inches='tight', pad_inches=0.1, transparent=True)
    plt.close()
    image_stream.seek(0)

    return image_stream

def roman_number(n):
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ''
    for i in range(len(val)):
        count = int(n / val[i])
        roman_num += syb[i] * count
        n -= val[i] * count
    return roman_num
