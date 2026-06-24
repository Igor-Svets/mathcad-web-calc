import math
import streamlit as str

# Назва та заголовок програми
str.set_page_config(page_title="Калькулятор Mathcad", page_icon="🧮")
str.title("Знаходження суми коренів двох чисел")
str.write("Перенесено з Mathcad у Python за допомогою Streamlit")

str.markdown("---")

# Блок введення вихідних даних (Inputs)
str.subheader("Вхідні дані")

# Створюємо поля для введення чисел (з дефолтними значеннями як на скриншоті)
a = str.number_input("Введіть число a", value=100.0, step=1.0)
b = str.number_input("Введіть число b", value=25.0, step=1.0)

str.markdown("---")

# Блок розрахунку та виведення результату (Outputs)
str.subheader("Результат розрахунку")

# Перевірка, щоб числа не були від'ємними (бо корінь з від'ємного числа дасть помилку)
if a >= 0 and b >= 0:
    # Сама формула (як у Маткаді: c = sqrt(a) + sqrt(b))
    c = math.sqrt(a) + math.sqrt(b)

    # Красиве виведення результату
    str.success(f"Результат c = {c}")

    # Відображення формули у красивому математичному вигляді
    str.latex(rf"c = \sqrt{{{a}}} + \sqrt{{{b}}} = {c}")
else:
    str.error(
        "Помилка: Числа повинні бути більшими або дорівнювати 0 для обчислення квадратного кореня!"
    )