import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Calculadora Matriz BCG - Menú", layout="wide")

st.title("📊 Generador Automático de Matriz BCG para Restaurante")
st.markdown("Ingresa o edita los datos de tus platillos directamente en la tabla. La gráfica y la clasificación se actualizarán al instante.")

# Datos iniciales precargados (puedes modificarlos libremente en la tabla)
datos_iniciales = pd.DataFrame([
    ("Mole de guajolote", 44.0, 61),
    ("Caldo de guajolote", 37.0, 76),
    ("Barbacoa de borrego", 42.0, 515),
    ("Mole de gallina", 63.0, 226),
    ("Caldo de gallina", 63.0, 967),
    ("Ziguamut de conejo", 94.0, 159),
    ("Asado de puerco", 58.0, 58),
    ("Mondongo", 48.0, 388),
    ("Chile de relleno pollo", 96.0, 185),
    ("chile relleno puerco", 96.0, 67),
    ("ziguamut de res", 27.0, 63),
    ("Cocido de res", 53.0, 103),
    ("Albóndigas enchipotladas", 41.0, 66),
    ("Bistec a la mexicana", 60.0, 130),
    ("Milanesa de puerco", 53.0, 23),
    ("Milanesa de res", 33.0, 38),
    ("Milanesa de pollo", 60.0, 228),
    ("Sopa de pan", 71.0, 40),
    ("Enchiladas de pollo", 25.0, 97),
    ("Taco de birra", 15.0, 58)
], columns=["Producto", "Margen %", "Popularidad (Artículos Vendidos)"])

# Editor de datos interactivo para tablet
st.subheader("1. Edición de Datos del Menú")
df_usuario = st.data_editor(datos_iniciales, num_rows="dynamic", use_container_width=True)

if not df_usuario.empty:
    # Cálculos automáticos
    mean_x = df_usuario["Margen %"].mean()
    mean_y = df_usuario["Popularidad (Artículos Vendidos)"].mean()

    # Función para clasificar automáticamente en los 4 cuadrantes BCG principales
    def clasificar_bcg(row, mx, my):
        if row["Margen %"] >= mx and row["Popularidad (Artículos Vendidos)"] >= my:
            return "Estrella ⭐"
        elif row["Margen %"] < mx and row["Popularidad (Artículos Vendidos)"] >= my:
            return "Vaca 🐮"
        elif row["Margen %"] >= mx and row["Popularidad (Artículos Vendidos)"] < my:
            return "Interrogante ❓"
        else:
            return "Perro 🐶"

    df_usuario["Cuadrante BCG"] = df_usuario.apply(lambda r: clasificar_bcg(r, mean_x, mean_y), axis=1)

    st.subheader("2. Resultados y Clasificación")
    col1, col2 = st.columns(2)
    col1.metric("Margen Promedio del Menú", f"{mean_x:.2f}%")
    col2.metric("Popularidad Promedio", f"{mean_y:.2f} arts.")

    # Mostrar tabla con clasificación
    st.dataframe(df_usuario, use_container_width=True)

    # Generar Gráfica
    st.subheader("3. Visualización de la Matriz BCG")
    
    min_x, max_x = df_usuario["Margen %"].min(), df_usuario["Margen %"].max()
    min_y, max_y = 0, df_usuario["Popularidad (Artículos Vendidos)"].max() * 1.05

    sub_x1 = (min_x + mean_x) / 2
    sub_x2 = (mean_x + max_x) / 2
    sub_y1 = (min_y + mean_y) / 2
    sub_y2 = (mean_y + max_y) / 2

    fig, ax = plt.subplots(figsize=(14, 9))
    ax.scatter(df_usuario["Margen %"], df_usuario["Popularidad (Artículos Vendidos)"], color='darkblue', s=80, zorder=3)

    # Ejes principales de promedios
    ax.axvline(mean_x, color='crimson', linestyle='--', linewidth=2, alpha=0.9, label=f'Promedio Margen ({mean_x:.1f}%)')
    ax.axhline(mean_y, color='crimson', linestyle='--', linewidth=2, alpha=0.9, label=f'Promedio Popularidad ({mean_y:.1f})')

    # Sub-cuadrantes
    ax.axvline(sub_x1, color='gray', linestyle=':', linewidth=1, alpha=0.6)
    ax.axvline(sub_x2, color='gray', linestyle=':', linewidth=1, alpha=0.6)
    ax.axhline(sub_y1, color='gray', linestyle=':', linewidth=1, alpha=0.6)
    ax.axhline(sub_y2, color='gray', linestyle=':', linewidth=1, alpha=0.6)

    # Etiquetas con conectores inteligentes básicos
    for i, row in df_usuario.iterrows():
        prod = str(row["Producto"])
        ax.annotate(prod, 
                     (row["Margen %"], row["Popularidad (Artículos Vendidos)"]),
                     textcoords="offset points", 
                     xytext=(20, 15), 
                     ha='center', 
                     fontsize=9, 
                     fontweight='bold',
                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="darkgray", alpha=0.9),
                     arrowprops=dict(arrowstyle="->", color="crimson", lw=0.8, connectionstyle="arc3,rad=0"))

    ax.set_title("Matriz BCG Dinámica: Margen vs. Popularidad", fontsize=15, fontweight='bold', pad=15)
    ax.set_xlabel("Margen %", fontsize=12, fontweight='bold')
    ax.set_ylabel("Popularidad", fontsize=12, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.5, zorder=0)
    ax.legend(loc='upper right', fontsize=10)
    ax.set_ylim(-50, max_y if max_y > 0 else 100)

    st.pyplot(fig)
