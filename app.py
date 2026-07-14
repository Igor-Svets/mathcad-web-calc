import streamlit as st
import pandas as pd
import math

# ==========================================
# 1. КОНСТАНТИ ВЕРСІЇ
# ==========================================
__version__ = "1.3.0"
__release_date__ = "2026-07-14"

# Налаштування сторінки Streamlit
st.set_page_config(page_title="Калькулятор процесів Клауса", layout="wide")

# ==========================================
# 2. ВІДОБРАЖЕННЯ ВЕРСІЇ В SIDEBAR
# ==========================================
st.sidebar.title("Навігація")
st.sidebar.markdown(f"**Поточна версія:** `{__version__}`")
st.sidebar.caption(f"Дата релізу: {__release_date__}")
st.sidebar.markdown("---")

# Список сторінок
page = st.sidebar.radio(
    "Перейти до:", 
    ["Головний калькулятор", "Про програму & Історія змін", "Допомога та методичні вказівки"]
)

# ==========================================
# 3. ЛОГІКА ПЕРЕМИКАННЯ СТОРІНОК
# ==========================================
if page == "Головний калькулятор":
    
    # Заголовок
    st.markdown(
        "<h2 style='font-size: 28px; font-weight: bold; margin-bottom: 5px;'>"
        "Розрахунок матеріального балансу печі спалювання кислого газу"
        "</h2>", 
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='font-size: 18px; color: #555555; margin-top: 0px;'>"
        "Динамічна модель процесу Клауса з урахуванням хімічної рівноваги та надлишку повітря"
        "</p>", 
        unsafe_allow_html=True
    )
    st.markdown("---")

    # Блок вхідних даних
    st.header("Вхідні дані")

    col_v, col_a, col_t = st.columns(3)
    with col_v:
        v_vkh = st.number_input("Загальна об'ємна витрата кислого газу (Vвх), нм3/год", value=150.0, step=10.0, format="%.2f")
    with col_a:
        alpha = st.number_input("Коефіцієнт надлишку повітря (alpha)", value=1.00, min_value=1.00, max_value=1.50, step=0.01, format="%.2f")
    with col_t:
        T2 = st.number_input("Температура в паливній камері печі (T2), K", value=1373.15, min_value=1000.0, max_value=1800.0, step=10.0, format="%.2f")

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
        
        # --- КОНСТАНТИ (Молярні маси, кг/кмоль) ---
        M_H2S = 34.08
        M_CO2 = 44.01
        M_HCN = 27.03
        M_H2O = 18.015
        M_O2 = 32.00
        M_N2 = 28.013
        M_SO2 = 64.06
        M_S2 = 64.12
        VM = 22.414  # Молярний об'єм газу за н.у.
        R = 8.3144   # Універсальна газова стала, Дж/(моль*К)
        
        # --- 1. РОЗРАХУНОК ПОТОКІВ НА ВХОДІ ---
        v_h2s_vkh = v_vkh * (x_h2s / 100.0)
        v_co2_vkh = v_vkh * (x_co2 / 100.0)
        v_hcn_vkh = v_vkh * (x_hcn / 100.0)
        v_h2o_vkh = v_vkh * (x_h2o / 100.0)
        
        g_h2s_vkh = v_h2s_vkh * M_H2S / VM
        g_co2_vkh = v_co2_vkh * M_CO2 / VM
        g_hcn_vkh = v_hcn_vkh * M_HCN / VM
        g_h2o_vkh = v_h2o_vkh * M_H2O / VM
        
        # --- 2. РОЗРАХУНОК ФАКТИЧНОГО ПОТОКУ ПОВІТРЯ (Стадія А) ---
        v_o2_teor_h2s = 0.5 * v_h2s_vkh
        v_o2_teor_hcn = 1.25 * v_hcn_vkh
        v_o2_teor_zag = v_o2_teor_h2s + v_o2_teor_hcn
        
        v_o2_zag = v_o2_teor_zag * alpha  # Кисень, що подається
        v_air = v_o2_zag / 0.21
        v_n2_air = v_air * 0.79
        
        g_o2 = v_o2_zag * M_O2 / VM
        g_n2_air = v_n2_air * M_N2 / VM
        
        # --- 3. МАТЕРІАЛЬНИЙ БАЛАНС ПІСЛЯ СТАДІЇ А (Горіння до рівноваги Клауса) ---
        v_o2_for_h2s = v_o2_zag - v_o2_teor_hcn
        v_h2s_burned = v_o2_for_h2s / 1.5
        
        # Вихідні об'єми речовин на Стадії А (Проміжні потоки)
        v_h2s_stA = v_h2s_vkh - v_h2s_burned
        v_so2_stA = v_h2s_burned
        v_co2_stA = v_co2_vkh + v_hcn_vkh
        v_n2_stA = v_n2_air + (0.5 * v_hcn_vkh)
        v_h2o_stA = v_h2o_vkh + v_h2s_burned + (0.5 * v_hcn_vkh)
        v_o2_stA = 0.0
        
        # Проміжні маси речовин на Стадії А
        g_h2s_stA = v_h2s_stA * M_H2S / VM
        g_so2_stA = v_so2_stA * M_SO2 / VM
        g_co2_stA = v_co2_stA * M_CO2 / VM
        g_n2_stA = v_n2_stA * M_N2 / VM
        g_h2o_stA = v_h2o_stA * M_H2O / VM
        g_o2_stA = 0.0
        
        # Переведення в мольні витрати для термодинаміки (кмоль/год)
        N_H2S = v_h2s_stA / VM
        N_SO2 = v_so2_stA / VM
        N_CO2 = v_co2_stA / VM
        N_N2 = v_n2_stA / VM
        N_H2O = v_h2o_stA / VM
        
        # --- 4. ТЕРМОДИНАМІЧНИЙ РОЗРАХУНОК КОНСТАНТИ РІВНОВАГИ ---
        # Термодинамічні константи утворення за 298.15 K [кДж/моль]
        dH_298 = {"H2S": -20.6, "SO2": -296.8, "S2": 128.6, "H2O": -241.8}
        dG_298 = {"H2S": -33.6, "SO2": -300.2, "S2": 79.7, "H2O": -228.6}
        
        # Розрахунок дельт для реакції: 2H2S + SO2 <-> 1.5 S2 + 2H2O
        dH_reak = (2 * dH_298["H2O"] + 1.5 * dH_298["S2"]) - (2 * dH_298["H2S"] + dH_298["SO2"])  # кДж/моль
        dG_reak = (2 * dG_298["H2O"] + 1.5 * dG_298["S2"]) - (2 * dG_298["H2S"] + dG_298["SO2"])  # кДж/моль
        
        # Константа при 298.15 K
        K_298 = math.exp(-(dG_reak * 1000) / (R * 298.15))
        
        # Константа при робочій температурі T2 за рівнянням Ван-Тгоффа
        K_T2 = K_298 * math.exp(-((dH_reak * 1000) / R) * (1.0 / T2 - 1.0 / 298.15))
        
        # --- 5. ЧИСЕЛЬНИЙ РОЗВ'ЯЗУВАЧ РІВНОВАГИ КЛАУСА (Метод бісекції) ---
        # Визначаємо границі для ступеня конверсії H2S (x)
        x_max = 1.0
        if N_H2S > 0:
            x_max = min(1.0, (2.0 * N_SO2) / N_H2S)
            
        a, b = 0.0, x_max - 1e-7
        x_sol = 0.0
        
        # Функція нев'язки закону діючих мас (f(x) = 0)
        def f_eq(x):
            n_H2S = N_H2S * (1.0 - x)
            n_SO2 = N_SO2 - 0.5 * N_H2S * x
            n_S2 = 0.75 * N_H2S * x
            n_H2O = N_H2O + N_H2S * x
            N_tot = n_H2S + n_SO2 + n_S2 + n_H2O + N_CO2 + N_N2
            
            if n_H2S <= 0 or n_SO2 <= 0:
                return float('inf')
                
            # ЗДМ: K_T2 = (P_S2^1.5 * P_H2O^2) / (P_H2S^2 * P_SO2), за P = 1.0 атм
            val = ((n_S2**1.5) * (n_H2O**2.0)) / ((n_H2S**2.0) * n_SO2 * (N_tot**0.5))
            return val - K_T2

        # Обчислення кореня
        if N_H2S > 0 and N_SO2 > 0:
            for _ in range(100):
                c = (a + b) / 2.0
                val_c = f_eq(c)
                if abs(val_c) < 1e-6 or (b - a) < 1e-7:
                    x_sol = c
                    break
                if val_c < 0:
                    a = c
                else:
                    b = c
            else:
                x_sol = (a + b) / 2.0
        else:
            x_sol = 0.0

        # --- 6. ОБЧИСЛЕННЯ РІВНОВАЖНИХ ПОТОКІВ НА ВИХОДІ (Стадія Б) ---
        n_H2S_eq = N_H2S * (1.0 - x_sol)
        n_SO2_eq = N_SO2 - 0.5 * N_H2S * x_sol
        n_S2_eq = 0.75 * N_H2S * x_sol
        n_H2O_eq = N_H2O + N_H2S * x_sol
        
        # Об'єми на виході Стадії Б (нм3/год)
        v_h2s_vykh = n_H2S_eq * VM
        v_so2_vykh = n_SO2_eq * VM
        v_s2_vykh = n_S2_eq * VM
        v_h2o_vykh = n_H2O_eq * VM
        v_co2_vykh = v_co2_stA
        v_n2_vykh = v_n2_stA
        v_o2_vykh = 0.0
        
        # Маси на виході Стадії Б (кг/год)
        g_h2s_vykh = v_h2s_vykh * M_H2S / VM
        g_so2_vykh = v_so2_vykh * M_SO2 / VM
        g_s2_vykh = v_s2_vykh * M_S2 / VM
        g_co2_vykh = v_co2_vykh * M_CO2 / VM
        g_n2_vykh = v_n2_vykh * M_N2 / VM
        g_h2o_vykh = v_h2o_vykh * M_H2O / VM
        g_o2_vykh = 0.0
        
        # ==========================================
        # 7. ВІДОБРАЖЕННЯ РЕЗУЛЬТАТІВ НА ЕКРАНІ
        # ==========================================
        st.header("Результати розрахунку")
        
        # Таблиця 1: ПРИХІД
        prikhod_data = {
            "Потік / Речовина": [
                "1. Кислий газ: H2S", "1. Кислий газ: CO2", "1. Кислий газ: HCN", "1. Кислий газ: H2O",
                "2. Повітря: O2", "2. Повітря: N2", "РАЗОМ ПРИХІД"
            ],
            "Об'єм, нм3/год": [v_h2s_vkh, v_co2_vkh, v_hcn_vkh, v_h2o_vkh, v_o2_zag, v_n2_air, (v_vkh + v_air)],
            "Маса, кг/год": [g_h2s_vkh, g_co2_vkh, g_hcn_vkh, g_h2o_vkh, g_o2, g_n2_air, (g_h2s_vkh + g_co2_vkh + g_hcn_vkh + g_h2o_vkh + g_o2 + g_n2_air)]
        }
        
        # Таблиця 2: ПРОМІЖНИЙ ВИХІД СТАДІЇ А (Без Клауса)
        vykhod_stA_data = {
            "Потік / Речовина": [
                "3. Газ після печі: H2S (залишок)", "3. Газ після печі: SO2", "3. Газ після печі: CO2", 
                "3. Газ після печі: N2", "3. Газ після печі: H2O", "3. Газ після печі: O2 (вільний)", "РАЗОМ ВИХІД"
            ],
            "Об'єм, нм3/год": [v_h2s_stA, v_so2_stA, v_co2_stA, v_n2_stA, v_h2o_stA, v_o2_stA, (v_h2s_stA + v_so2_stA + v_co2_stA + v_n2_stA + v_h2o_stA)],
            "Маса, кг/год": [g_h2s_stA, g_so2_stA, g_co2_stA, g_n2_stA, g_h2o_stA, g_o2_stA, (g_h2s_stA + g_so2_stA + g_co2_stA + g_n2_stA + g_h2o_stA)]
        }
        
        # Таблиця 3: КІНЦЕВИЙ ВИХІД СТАДІЇ Б (З урахуванням рівноваги Клауса)
        vykhod_stB_data = {
            "Потік / Речовина": [
                "3. Газ після печі: H2S (залишок)", "3. Газ після печі: SO2", "3. Газ після печі: S2 (сірка димер)",
                "3. Газ після печі: CO2", "3. Газ після печі: N2", "3. Газ після печі: H2O", 
                "3. Газ після печі: O2 (вільний)", "РАЗОМ ВИХІД"
            ],
            "Об'єм, нм3/год": [
                v_h2s_vykh, v_so2_vykh, v_s2_vykh, v_co2_vykh, v_n2_vykh, v_h2o_vykh, v_o2_vykh, 
                (v_h2s_vykh + v_so2_vykh + v_s2_vykh + v_co2_vykh + v_n2_vykh + v_h2o_vykh + v_o2_vykh)
            ],
            "Маса, кг/год": [
                g_h2s_vykh, g_so2_vykh, g_s2_vykh, g_co2_vykh, g_n2_vykh, g_h2o_vykh, g_o2_vykh, 
                (g_h2s_vykh + g_so2_vykh + g_s2_vykh + g_co2_vykh + g_n2_vykh + g_h2o_vykh + g_o2_vykh)
            ]
        }
        
        df_prikhod = pd.DataFrame(prikhod_data)
        df_vykhod_stA = pd.DataFrame(vykhod_stA_data)
        df_vykhod_stB = pd.DataFrame(vykhod_stB_data)
        
        # Форматування чисел до 2 знаків
        df_prikhod_fmt = df_prikhod.style.format({"Об'єм, нм3/год": "{:.2f}", "Маса, кг/год": "{:.2f}"})
        df_vykhod_stA_fmt = df_vykhod_stA.style.format({"Об'єм, нм3/год": "{:.2f}", "Маса, кг/год": "{:.2f}"})
        df_vykhod_stB_fmt = df_vykhod_stB.style.format({"Об'єм, нм3/год": "{:.2f}", "Маса, кг/год": "{:.2f}"})
        
        # 1. Відображення таблиці ПРИХОДУ
        st.subheader("ПРИХІД балансу")
        st.dataframe(df_prikhod_fmt, use_container_width=True, hide_index=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. Відображення таблиці СТАДІЇ А
        st.subheader("ВИХІД балансу (без урахування реакції Клауса) — Стадія А")
        st.dataframe(df_vykhod_stA_fmt, use_container_width=True, hide_index=True)
        
        # Співвідношення H2S : SO2 на стадії А
        ratio_stA = v_h2s_stA / v_so2_stA if v_so2_stA != 0 else 0
        st.info(f"💡 Фактичне співвідношення H2S : SO2 після горіння (до реакції Клауса): **{ratio_stA:.2f} : 1** (Теоретичний ідеал — 2.00 : 1)")
        st.markdown("<hr style='border:1px solid #ddd'>", unsafe_allow_html=True)
        
        # 3. Термодинамічні параметри та таблиця СТАДІЇ Б
        st.subheader("ВИХІД балансу з урахуванням реакції Клауса (Рівноважний склад) — Стадія Б")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric(label="Константа рівноваги (KT2)", value=f"{K_T2:.4f}")
        with col_res2:
            st.metric(label="Рівноважний ступінь конверсії H2S (x)", value=f"{x_sol * 100:.2f} %")
        with col_res3:
            ratio_stB = v_h2s_vykh / v_so2_vykh if v_so2_vykh != 0 else 0
            st.metric(label="Фактичне співвідношення H2S : SO2", value=f"{ratio_stB:.2f} : 1", delta=f"{ratio_stB - 2.0:.2f} від ідеалу")
            
        st.dataframe(df_vykhod_stB_fmt, use_container_width=True, hide_index=True)
        st.success("🎉 Термодинамічний прорахунок виконано успішно. Враховано утворення газуватої сірки S2 та виділення додаткової водяної пари!")
        
        # --- 4. ЗВЕДЕНА ТАБЛИЦЯ ПОРІВНЯННЯ «ВХІД ⇄ ВИХІД» ---
        st.markdown("<hr style='border:1.5px solid #4CAF50'>", unsafe_allow_html=True)
        st.subheader("📊 Зведена таблиця порівняння матеріального балансу (Вхід ⇄ Вихід)")
        
        # Готуємо дані порівняння компонентів
        comparison_data = {
            "Компонент": [
                "Сірководень (H2S)", 
                "Діоксид сірки (SO2)", 
                "Елементна сірка (S2)", 
                "Діоксид вуглецю (CO2)", 
                "Азот (N2)", 
                "Вода / Водяна пара (H2O)", 
                "Кисень (O2)", 
                "Ціановодень (HCN)",
                "РАЗОМ ПОТОКИ"
            ],
            "Вхід: Об'єм, нм3/год": [v_h2s_vkh, 0.0, 0.0, v_co2_vkh, v_n2_air, v_h2o_vkh, v_o2_zag, v_hcn_vkh, (v_vkh + v_air)],
            "Вихід: Об'єм, нм3/год": [v_h2s_vykh, v_so2_vykh, v_s2_vykh, v_co2_vykh, v_n2_vykh, v_h2o_vykh, v_o2_vykh, 0.0, (v_h2s_vykh + v_so2_vykh + v_s2_vykh + v_co2_vykh + v_n2_vykh + v_h2o_vykh + v_o2_vykh)],
            "Вхід: Маса, кг/год": [g_h2s_vkh, 0.0, 0.0, g_co2_vkh, g_n2_air, g_h2o_vkh, g_o2, g_hcn_vkh, (g_h2s_vkh + g_co2_vkh + g_hcn_vkh + g_h2o_vkh + g_o2 + g_n2_air)],
            "Вихід: Маса, кг/год": [g_h2s_vykh, g_so2_vykh, g_s2_vykh, g_co2_vykh, g_n2_vykh, g_h2o_vykh, g_o2_vykh, 0.0, (g_h2s_vykh + g_so2_vykh + g_s2_vykh + g_co2_vykh + g_n2_vykh + g_h2o_vykh + g_o2_vykh)]
        }
        
        df_comparison = pd.DataFrame(comparison_data)
        df_comparison_fmt = df_comparison.style.format({
            "Вхід: Об'єм, нм3/год": "{:.2f}",
            "Вихід: Об'єм, нм3/год": "{:.2f}",
            "Вхід: Маса, кг/год": "{:.2f}",
            "Вихід: Маса, кг/год": "{:.2f}"
        })
        
        st.dataframe(df_comparison_fmt, use_container_width=True, hide_index=True)
        st.caption("Примітка: Ціановодень (HCN) повністю руйнується у термічній стадії, а вільний кисень (O2) витрачається на окиснення.")

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
    st.markdown("Цей розділ допоможе вам розібратися з принципом роботи калькулятора.")
    st.markdown("---")

    with st.expander("📌 Як користуватися калькулятором (Інструкція)", expanded=True):
        st.write("""
        1. Перейдіть на сторінку **"Головний калькулятор"** через бокове меню навігації.
        2. У блоці **"Вхідні дані"** вкажіть загальну витрату газу ($V_{вх}$), бажаний коефіцієнт надлишку повітря ($\\alpha$) та робочу температуру печі ($T_2$).
        3. Заповніть склад вихідного кислого газу у відсотках. **Зверніть увагу:** загальна сума часток компонентів ($H_2S, CO_2, HCN, H_2O$) повинна строго дорівнювати **100%**.
        4. Система автоматично прорахує матеріальний баланс (прихід та вихід потоків) в об'ємних ($нм^3/год$) та масових ($кг/год$) одиницях і відобразить підсумкові таблиці з урахуванням реакції Клауса.
        """)

    # --- НОВИЙ БЛОК ДЛЯ ВІДКРИТТЯ ТА ЗАВАНТАЖЕННЯ PDF ---
    st.subheader("🧪 Хімізм та макрокінетика процесів у печі")
    st.write("Ви можете завантажити оригінальний документ з описом усіх 14 хімічних реакцій або розгорнути його для перегляду прямо на цій сторінці.")

    import base64
    try:
        # Зчитуємо файл один раз для обох функцій
        with open("Реакції.pdf", "rb") as pdf_file:
            pdf_data = pdf_file.read()
        
        # 1. Кнопка для скачування
        st.download_button(
            label="📥 Завантажити методичні вказівки (PDF)",
            data=pdf_data,
            file_name="Реакції_в_печі_Клауса.pdf",
            mime="application/pdf"
        )
        
        # 2. Кнопка-чекбокс для вбудованого перегляду
        if st.checkbox("👁️ Переглянути документ онлайн не завантажуючи"):
            base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            
    except FileNotFoundError:
        st.error("⚠️ Файл 'Реакції.pdf' не знайдено. Будь ласка, завантажте файл у папку з програмою під назвою 'Реакції.pdf'.")

    # Співвідношення H2S/SO2 залишаємо як швидку підказку
    with st.expander("💡 Оцінка результатів (Співвідношення H2S : SO2)"):
        st.write("""
        Для оптимального перебігу подальшої каталітичної стадії процесу Клауса (отримання елементної сірки) ідеальним є співвідношення компонентів газу на виході з печі:
        **$H_2S : SO_2 = 2 : 1$**.
        """)

    with st.expander("🧪 Хімізм процесу та розрахунок рівноваги (Термодинаміка)"):
        st.markdown("""
        Калькулятор моделює процес термічного спалювання компонентів кислого газу в печі Клауса. Розрахунок штучно розділено на дві послідовні умовні стадії:
        
        ##### :orange[Стадія А: Первинне горіння та деструкція HCN]
        * **Спалювання ціановодню ($HCN$):**
          $$2HCN + 2.5O_2 \\rightarrow 2CO_2 + N_2 + H_2O$$
        * **Окиснення сірководню ($H_2S$) до діоксиду сірки ($SO_2$):**
          $$H_2S + 1.5O_2 \\rightarrow SO_2 + H_2O$$

        ##### :orange[Стадія Б: Оборотна реакція Клауса]
        При температурах понад 1000 K сірка існує у формі газоподібного димеру $S_2$:
        $$2H_2S_{(г)} + SO_{2(г)} \\leftrightarrow \\frac{3}{2}S_{2(г)} + 2H_2O_{(г)}$$
        
        Константа рівноваги при температурі $T_2$ розраховується за інтегральним рівнянням Ван-Тгоффа:
        $$K_{T2} = K_{298} \\cdot \\exp\\left[-\\frac{\\Delta H_{298}^\\circ \\cdot 1000}{R} \\cdot \\left(\\frac{1}{T_2} - \\frac{1}{298.15}\\right)\\right]$$
        
        Рівноважний стан системи описується законом діючих мас через парціальні тиски компонентів (загальний тиск у печі $P = 1.0$ атм):
        $$K_{T2} = \\frac{\\left(P_{S2}\\right)^{1.5} \\cdot \\left(P_{H2O}\\right)^2}{\\left(P_{H2S}\\right)^2 \\cdot P_{SO2}}$$
        
        Ступінь конверсії $x$ знаходиться чисельним розв'язанням критеріального рівняння нев'язки на проміжку $x \\in [0, 1)$.
        """)

    with st.expander("💡 Оцінка результатів (Співвідношення $H_2S : SO_2$)"):
        st.write("""
        Для оптимального перебігу подальшої каталітичної стадії процесу Клауса (отримання елементної сірки) ідеальним є співвідношення компонентів газу на виході з печі:
        **$H_2S : SO_2 = 2 : 1$**.
        
        Калькулятор автоматично розраховує фактичне співвідношення та підказує, наскільки воно близьке до теоретичного ідеалу. Завдяки термодинамічному розрахунку рівноваги ви отримуєте точний вміст вільної сірки ($S_2$), яка утворюється безпосередньо у газовій фазі печі.
        """)