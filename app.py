import streamlit as st
import pandas as pd

# ==========================================
# 1. КОНСТАНТИ ВЕРСІЇ (Оновлено алгоритм розрахунку)
# ==========================================
__version__ = "1.2.0"
__release_date__ = "2026-07-06"

# Налаштування сторінки Streamlit
st.set_page_config(page_title="Калькулятор процесів Клауса", layout="wide")

# ==========================================
# 2. ВІДОБРАЖЕННЯ ВЕРСІЇ В SIDEBAR
# ==========================================
st.sidebar.title("Навігація")
st.sidebar.markdown(f"**Поточна версія:** `{__version__}`")
st.sidebar.caption(f"Дата релізу: {__release_date__}")
st.sidebar.markdown("---")

# Додано нову сторінку "Допомога та методичні вказівки" в список
page = st.sidebar.radio(
    "Перейти до:", 
    ["Головний калькулятор", "Про програму & Історія змін", "Допомога та методичні вказівки"]
)

# ==========================================
# 3. ЛОГІКА ПЕРЕМИКАННЯ СТОРІНОК
# ==========================================
if page == "Головний калькулятор":
    
    # Зменшений кастомний заголовок за допомогою HTML (Виправлено відступи)
    st.markdown(
        "<h2 style='font-size: 28px; font-weight: bold; margin-bottom: 5px;'>"
        "Розрахунок матеріального балансу печі спалювання кислого газу"
        "</h2>", 
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='font-size: 18px; color: #555555; margin-top: 0px;'>"
        "Динамічна модель процесу Клауса з урахуванням надлишку повітря"
        "</p>", 
        unsafe_allow_html=True
    )
    st.markdown("---")

    # Блок вхідних даних
    st.header("Вхідні дані")

    col_v, col_a = st.columns(2)
    with col_v:
        v_vkh = st.number_input("Загальна об'ємна витрата кислого газу (Vвх), нм3/год", value=150.0, step=10.0, format="%.2f")
    with col_a:
        alpha = st.number_input("Коефіцієнт надлишку повітря (alpha)", value=1.05, min_value=1.00, max_value=1.50, step=0.01, format="%.2f")

    st.write("### Склад вихідного газу (% об.):")
    col1, col2 = st.columns(2)

    with col1:
        x_h2s = st.number_input("Вміст сірководню (H2S), %", value=34.70, step=1.0, format="%.2f")
        x_co2 = st.number_input("Вміст діоксиду вуглецю (CO2), %", value=50.00, step=1.0, format="%.2f")

    with col2:
        x_hcn = st.number_input("Вміст ціановодню (HCN), %", value=10.70, step=1.0, format="%.2f")
        x_h2o = st.number_input("Вміст водяної пари (H2O), %", value=4.60, step=1.0, format="%.2f")

    # Перевірка суми відсотків
    sum_pct = x_h2s + x_co2 + x_hcn + x_h2o

    if abs(sum_pct - 100.0) > 0.01:
        st.error(f"Помилка: Сума компонентів газу дорівнює {sum_pct}%, а повинна бути строго 100%!")
    else:
        st.success("Сума компонентів газу дорівнює 100%. Проводимо розрахунок...")
        st.markdown("---")
        
        # --- КОНСТАНТИ (Молярні маси) ---
        M_H2S = 34.08
        M_CO2 = 44.01
        M_HCN = 27.03
        M_H2O = 18.015
        M_O2 = 32.00
        M_N2 = 28.013
        M_SO2 = 64.06
        VM = 22.414  # Молярний об'єм
        
        # --- 1. РОЗРАХУНОК ПОТОКІВ НА ВХОДІ ---
        v_h2s_vkh = v_vkh * (x_h2s / 100.0)
        v_co2_vkh = v_vkh * (x_co2 / 100.0)
        v_hcn_vkh = v_vkh * (x_hcn / 100.0)
        v_h2o_vkh = v_vkh * (x_h2o / 100.0)
        
        g_h2s_vkh = v_h2s_vkh * M_H2S / VM
        g_co2_vkh = v_co2_vkh * M_CO2 / VM
        g_hcn_vkh = v_hcn_vkh * M_HCN / VM
        g_h2o_vkh = v_h2o_vkh * M_H2O / VM
        
        # --- 2. РОЗРАХУНОК ФАКТИЧНОГО ПОДОКУ ПОВІТРЯ (Базується на alpha) ---
        v_o2_teor_h2s = 0.5 * v_h2s_vkh
        v_o2_teor_hcn = 1.25 * v_hcn_vkh
        v_o2_teor_zag = v_o2_teor_h2s + v_o2_teor_hcn  # Теоретичний кисень для суміші
        
        v_o2_zag = v_o2_teor_zag * alpha  # Фактичний кисень, що подається
        v_air = v_o2_zag / 0.21
        v_n2_air = v_air * 0.79
        
        g_o2 = v_o2_zag * M_O2 / VM
        g_n2_air = v_n2_air * M_N2 / VM
        
        # --- 3. ДИНАМІЧНИЙ РОЗРАХУНОК ПОТОКІВ НА ВИХОДІ ---
        # Весь кисень витрачається повністю. Спочатку на HCN, залишок - на H2S.
        v_o2_for_h2s = v_o2_zag - v_o2_teor_hcn
        
        # Скільки H2S реально згорає до SO2 (на 1 моль SO2 йде 1.5 моля O2)
        v_h2s_burned = v_o2_for_h2s / 1.5
        
        # Об'єми речовин на виході
        v_h2s_vykh = v_h2s_vkh - v_h2s_burned
        v_so2_vykh = v_h2s_burned
        v_co2_vykh = v_co2_vkh + v_hcn_vkh
        v_n2_vykh = v_n2_air + (0.5 * v_hcn_vkh)
        v_h2o_vykh = v_h2o_vkh + v_h2s_burned + (0.5 * v_hcn_vkh)
        v_o2_vykh = 0.0  # Вільний кисень відсутній (повне згорання)
        
        # Маси речовин на виході
        g_h2s_vykh = v_h2s_vykh * M_H2S / VM
        g_so2_vykh = v_so2_vykh * M_SO2 / VM
        g_co2_vykh = v_co2_vykh * M_CO2 / VM
        g_n2_vykh = v_n2_vykh * M_N2 / VM
        g_h2o_vykh = v_h2o_vykh * M_H2O / VM
        g_o2_vykh = 0.0
        
        # --- СТВОРЕННЯ ТАБЛИЦІ МАТЕРІАЛЬНОГО БАЛАНСУ ---
        st.header("Результати розрахунку")
        
        # Прихід
        prikhod_data = {
            "Потік / Речовина": [
                "1. Кислий газ: H2S", "1. Кислий газ: CO2", "1. Кислий газ: HCN", "1. Кислий газ: H2O",
                "2. Повітря: O2", "2. Повітря: N2", "РАЗОМ ПРИХІД"
            ],
            "Об'єм, нм3/год": [v_h2s_vkh, v_co2_vkh, v_hcn_vkh, v_h2o_vkh, v_o2_zag, v_n2_air, (v_vkh + v_air)],
            "Маса, кг/год": [g_h2s_vkh, g_co2_vkh, g_hcn_vkh, g_h2o_vkh, g_o2, g_n2_air, (g_h2s_vkh + g_co2_vkh + g_hcn_vkh + g_h2o_vkh + g_o2 + g_n2_air)]
        }
        
        # Вихід
        vykhod_data = {
            "Потік / Речовина": [
                "3. Газ після peчі: H2S (залишок)", "3. Газ після печі: SO2", "3. Газ після печі: CO2", 
                "3. Газ після печі: N2", "3. Газ після печі: H2O", "3. Газ після печі: O2 (вільний)", "РАЗОМ ВИХІД"
            ],
            "Об'єм, нм3/год": [v_h2s_vykh, v_so2_vykh, v_co2_vykh, v_n2_vykh, v_h2o_vykh, v_o2_vykh, (v_h2s_vykh + v_so2_vykh + v_co2_vykh + v_n2_vykh + v_h2o_vykh + v_o2_vykh)],
            "Маса, кг/год": [g_h2s_vykh, g_so2_vykh, g_co2_vykh, g_n2_vykh, g_h2o_vykh, g_o2_vykh, (g_h2s_vykh + g_so2_vykh + g_co2_vykh + g_n2_vykh + g_h2o_vykh + g_o2_vykh)]
        }
        
        df_prikhod = pd.DataFrame(prikhod_data)
        df_vykhod = pd.DataFrame(vykhod_data)
        
        df_prikhod_formatted = df_prikhod.style.format({"Об'єм, нм3/год": "{:.2f}", "Маса, кг/год": "{:.2f}"})
        df_vykhod_formatted = df_vykhod.style.format({"Об'єм, нм3/год": "{:.2f}", "Маса, кг/год": "{:.2f}"})
        
        st.subheader("ПРИХІД балансу")
        st.dataframe(df_prikhod_formatted, use_container_width=True, hide_index=True)
        
        st.subheader("ВИХІД балансу")
        st.dataframe(df_vykhod_formatted, use_container_width=True, hide_index=True)
        
        # Вивід ключового співвідношення
        ratio = v_h2s_vykh / v_so2_vykh if v_so2_vykh != 0 else 0
        st.info(f"💡 Фактичне співвідношення H2S : SO2 на виході: **{ratio:.2f} : 1** (Теоретичний ідеал — 2.00 : 1)")

elif page == "Про програму & Історія змін":
    st.title("ℹ️ Про застосунок та історія оновлень")
    st.write(f"**Версія системи:** {__version__} від {__release_date__}")
    st.write("Ця програма призначена для автоматизації інженерних розрахунків.")
    st.markdown("---")
    
    try:
        with open("CHANGELOG.md", "r", encoding="utf-8") as f:
            changelog_content = f.read()
        st.markdown(changelog_content)
    except FileNotFoundError:
        st.warning("Файл CHANGELOG.md не знайдено.")

elif page == "Допомога та методичні вказівки":
    st.title("📖 Допомога та методичні вказівки")
    st.markdown("Цей розділ допоможе вам розібратися з принципом роботи калькулятора та закладеними математичними моделями.")
    st.markdown("---")

    with st.expander("📌 Як користуватися калькулятором (Інструкція)", expanded=True):
        st.write("""
        1. Перейдіть на сторінку **"Головний калькулятор"** через бокове меню навігації.
        2. У блоці **"Вхідні дані"** вкажіть загальну витрату газу ($V_{вх}$) та бажаний коефіцієнт надлишку повітря ($\\alpha$).
        3. Заповніть склад вихідного кислого газу у відсотках. **Зверніть увагу:** загальна сума часток компонентів ($H_2S, CO_2, HCN, H_2O$) повинна строго дорівнювати **100%**.
        4. Система автоматично прорахує матеріальний баланс (прихід та вихід потоків) в об'ємних ($нм^3/год$) та масових ($кг/год$) одиницях і відобразить підсумкові таблиці.
        """)

    with st.expander("🧪 Хімізм процесу та логіка розрахунку"):
        st.markdown("""
        Калькулятор моделює процес термічного спалювання компонентів кислого газу в печі Клауса. Математична модель базується на наступних стехіометричних рівняннях реакцій:
        
        * **Спалювання ціановодню ($HCN$):**
          $$2HCN + 2.5O_2 \\rightarrow 2CO_2 + N_2 + H_2O$$
          *На спалювання 1 моля HCN витрачається 1.25 моля кисню.*
        
        * **Окиснення сірководню ($H_2S$) до діоксиду сірки ($SO_2$):**
          $$H_2S + 1.5O_2 \\rightarrow SO_2 + H_2O$$
          *На утворення 1 моля $SO_2$ витрачається 1.5 моля кисню.*

        **Пріоритетність реакцій в моделі:**
        Програма використовує динамічний розподіл: спочатку весь кисень, що подається з повітрям (з урахуванням $\\alpha$), витрачається на повне вигоряння $HCN$. Залишок кисню спрямовується на окиснення $H_2S$ до $SO_2$.
        """)

    with st.expander("💡 Оцінка результатів (Співвідношення $H_2S : SO_2$)"):
        st.write("""
        Для оптимального перебігу подальшої каталітичної стадії процесу Клауса (отримання елементної сірки) ідеальним є співвідношення компонентів газу на виході з печі:
        **$H_2S : SO_2 = 2 : 1$**.
        
        Калькулятор автоматично розраховує фактичне співвідношення та підказує, наскільки воно близьке до теоретичного ідеалу. Регулюйте коефіцієнт надлишку повітря ($\\alpha$), щоб досягти необхідного балансу потоків.
        """)