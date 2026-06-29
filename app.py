import streamlit as st
import pandas as pd

# Налаштування сторінки
st.set_page_config(page_title="Баланс печі Клауса", layout="centered")

st.title("Розрахунок матеріального балансу печі спалювання кислого газу")
st.subheader("Процес Клауса з повним руйнуванням HCN")
st.markdown("---")

# Блок вхідних даних
st.header("Вхідні дані")

v_vkh = st.number_input("Загальна об'ємна витрата кислого газу (Vвх), нм3/год", value=150.0, step=10.0, format="%.2f")

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
    
    # Маси на вході
    g_h2s_vkh = v_h2s_vkh * M_H2S / VM
    g_co2_vkh = v_co2_vkh * M_CO2 / VM
    g_hcn_vkh = v_hcn_vkh * M_HCN / VM
    g_h2o_vkh = v_h2o_vkh * M_H2O / VM
    
    # --- 2. КИСЕНЬ ТА ПОВІТРЯ ---
    v_o2_h2s = 0.5 * v_h2s_vkh
    v_o2_hcn = 1.25 * v_hcn_vkh
    v_o2_zag = v_o2_h2s + v_o2_hcn
    
    v_air = v_o2_zag / 0.21
    v_n2_air = v_air * 0.79
    
    g_o2 = v_o2_zag * M_O2 / VM
    g_n2_air = v_n2_air * M_N2 / VM
    
    # --- 3. ПОТОКИ НА ВИХОДІ ---
    v_h2s_vykh = (2.0 / 3.0) * v_h2s_vkh
    v_so2_vykh = (1.0 / 3.0) * v_h2s_vkh
    v_co2_vykh = v_co2_vkh + v_hcn_vkh
    v_n2_vykh = v_n2_air + (0.5 * v_hcn_vkh)
    v_h2o_vykh = v_h2o_vkh + ((1.0 / 3.0) * v_h2s_vkh) + (0.5 * v_hcn_vkh)
    
    g_h2s_vykh = v_h2s_vykh * M_H2S / VM
    g_so2_vykh = v_so2_vykh * M_SO2 / VM
    g_co2_vykh = v_co2_vykh * M_CO2 / VM
    g_n2_vykh = v_n2_vykh * M_N2 / VM
    g_h2o_vykh = v_h2o_vykh * M_H2O / VM
    
    # --- СТВОРЕННЯ ТАБЛИЦІ МАТЕРІАЛЬНОГО БАЛАНСУ ---
    st.header("Результати розрахунку")
    
    # Дані для приходу
    prikhod_data = {
        "Потік / Речовина": [
            "1. Кислий газ: H2S", 
            "1. Кислий газ: CO2", 
            "1. Кислий газ: HCN", 
            "1. Кислий газ: H2O",
            "2. Повітря: O2", 
            "2. Повітря: N2",
            "РАЗОМ ПРИХІД"
        ],
        "Об'єм, нм3/год": [v_h2s_vkh, v_co2_vkh, v_hcn_vkh, v_h2o_vkh, v_o2_zag, v_n2_air, (v_vkh + v_air)],
        "Маса, кг/год": [g_h2s_vkh, g_co2_vkh, g_hcn_vkh, g_h2o_vkh, g_o2, g_n2_air, (g_h2s_vkh + g_co2_vkh + g_hcn_vkh + g_h2o_vkh + g_o2 + g_n2_air)]
    }
    
    # Дані для виходу
    vykhod_data = {
        "Потік / Речовина": [
            "3. Газ після печі: H2S (залишок)", 
            "3. Газ після печі: SO2", 
            "3. Газ після печі: CO2", 
            "3. Газ після печі: N2",
            "3. Газ после печі: H2O",
            "", # пустий рядок для вирівнювання
            "РАЗОМ ВИХІД"
        ],
        "Об'єм, нм3/год": [v_h2s_vykh, v_so2_vykh, v_co2_vykh, v_n2_vykh, v_h2o_vykh, 0.0, (v_h2s_vykh + v_so2_vykh + v_co2_vykh + v_n2_vykh + v_h2o_vykh)],
        "Маса, кг/год": [g_h2s_vykh, g_so2_vykh, g_co2_vykh, g_n2_vykh, g_h2o_vykh, 0.0, (g_h2s_vykh + g_so2_vykh + g_co2_vykh + g_n2_vykh + g_h2o_vykh)]
    }
    
    df_prikhod = pd.DataFrame(prikhod_data)
    df_vykhod = pd.DataFrame(vykhod_data)
    
    # Форматування для красивого відображення (2 знаки після коми)
    df_prikhod_formatted = df_prikhod.style.format({"Об'єм, нм3/год": "{:.2f}", "Маса, кг/год": "{:.2f}"})
    df_vykhod_formatted = df_vykhod.style.format({"Об'єм, нм3/год": "{:.2f}", "Маса, кг/год": "{:.2f}"})
    
    # Вивід таблиць у Streamlit
    st.subheader("ПРИХІД балансу")
    st.dataframe(df_prikhod_formatted, use_container_width=True, hide_index=True)
    
    st.subheader("ВИХІД балансу")
    st.dataframe(df_vykhod_formatted, use_container_width=True, hide_index=True)
    
    # Вивід ключового технологічного співвідношення
    ratio = v_h2s_vykh / v_so2_vykh if v_so2_vykh != 0 else 0
    st.info(f"💡 Співвідношення H2S : SO2 на виході становить {ratio:.2f} : 1 (Ідеал — 2.00 : 1)")