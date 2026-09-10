import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Calculadora Matriz BCG - Menú", layout="wide")

st.title("📊 Generador Automático de Matriz BCG por Categorías")
st.markdown("Administra tus platillos, asígnales una categoría y analiza el menú de forma global o filtrada.")

# Datos iniciales precargados con la columna "Categoría"
datos_iniciales = pd.DataFrame([
    ("Mole de guajolote", "Caldos y Moles", 44.0, 61),
    ("Caldo de guajolote", "Caldos y Moles", 37.0, 76),
    ("Barbacoa de borrego", "Carnes", 42.0, 515),
    ("Mole de gallina", "Caldos y Moles", 63.0, 226),
    ("Caldo de gallina", "Caldos y Moles", 63.0, 967),
    ("Ziguamut de conejo", "Especialidades", 94.0, 159),
    ("Asado de puerco", "Carnes", 58.0, 58),
    ("Mondongo", "Caldos y Moles", 48.0, 388),
    ("Chile de relleno pollo", "Entradas y Guisados", 96.0, 185),
    ("chile relleno puerco", "Entradas y Guisados", 96.0, 67),
    ("ziguamut de res", "Especialidades", 27.0, 63),
    ("Cocido de res", "Caldos y Moles", 53.0, 103),
    ("Albóndigas enchipotladas", "Entradas y Guisados", 41.0, 66),
    ("Bistec a la mexicana", "Carnes", 60.0, 130),
    ("Milanesa de puerco", "Carnes", 53.0, 23),
    ("Milanesa de res", "Carnes", 33.0, 38),
    ("Milanesa de pollo", "Carnes", 60.0, 228),
    ("Sopa de pan", "Entradas y Guisados", 71.0, 40),
    ("Enchiladas de pollo", "Antojitos", 25.0, 97),
    ("Taco de birra", "Antojitos", 15.0, 58)
], columns=["Producto", "Categoría", "Margen %", "Popularidad (Artículos Vendidos)"])

st.subheader("1. Edición de Datos y Familias de Platillos")
st.markdown("Puedes agregar nuevas filas, cambiar categorías libremente o editar valores directamente en la tabla.")
df_usuario = st.data_editor(datos_iniciales, num_rows="dynamic", use_container_width=True)

if not df_usuario.empty:
    # Barra lateral de filtros
    st.sidebar.header("🔍 Filtros de Análisis")
    categorias_disponibles = ["Todas las categorías"] + list(df_usuario["Categoría"].dropna().unique())
    categoria_seleccionada = st.sidebar.selectbox("Selecciona la categoría a visualizar:", categorias_disponibles)

    # Filtrar datos según la selección de la barra lateral
    if categoria_seleccionada != "Todas las categorías":
        df_filtrado = df_usuario[df_usuario["Categoría"] == categoria_seleccionada].copy()
        titulo_filtro = f"Categoría: {categoria_seleccionada}"
    else:
        df_filtrado = df_usuario.copy()
        titulo_filtro = "Menú Completo (Todas las Categorías)"

    if not df_filtrado.empty:
        mean_x = df_filtrado["Margen %"].mean()
        mean_y = df_filtrado["Popularidad (Artículos Vendidos)"].mean()

        def clasificar_bcg(row, mx, my):
            if row["Margen %"] >= mx and row["Popularidad (Artículos Vendidos)"] >= my:
                return "Estrella ⭐"
            elif row["Margen %"] < mx and row["Popularidad (Artículos Vendidos)"] >= my:
                return "Vaca 🐮"
            elif row["Margen %"] >= mx and row["Popularidad (Artículos Vendidos)"] < my:
                return "Interrogante ❓"
            else:
                return "Perro 🐶"

        df_filtrado["Cuadrante BCG"] = df_filtrado.apply(lambda r: clasificar_bcg(r, mean_x, mean_y), axis=1)

        st.subheader(f"2. Resultados y Clasificación — [{titulo_filtro}]")
        col1, col2 = st.columns(2)
        col1.metric("Margen Promedio", f"{mean_x:.2f}%")
        col2.metric("Popularidad Promedio", f"{mean_y:.2f} arts.")

        st.dataframe(df_filtrado, use_container_width=True)

        st.subheader(f"3. Visualización BCG — [{titulo_filtro}]")
        
        min_x, max_x = df_filtrado["Margen %"].min(), df_filtrado["Margen %"].max()
        # Si todos los elementos tienen el mismo margen, evitamos error de rango
        if min_x == max_x:
            min_x -= 5
            max_x += 5

        min_y, max_y = 0, df_filtrado["Popularidad (Artículos Vendidos)"].max()

        sub_x1 = (min_x + mean_x) / 2
        sub_x2 = (mean_x + max_x) / 2
        sub_y1 = (min_y + mean_y) / 2
        sub_y2 = (mean_y + max_y) / 2

        fig, ax = plt.subplots(figsize=(16, 11))
        
        ax.scatter(df_filtrado["Margen %"], df_filtrado["Popularidad (Artículos Vendidos)"], 
                   color='navy', s=120, edgecolors='white', linewidths=1.5, zorder=3)

        ax.axvline(mean_x, color='crimson', linestyle='--', linewidth=2, alpha=0.9, label=f'Promedio Margen ({mean_x:.1f}%)')
        ax.axhline(mean_y, color='crimson', linestyle='--', linewidth=2, alpha=0.9, label=f'Promedio Popularidad ({mean_y:.1f})')

        ax.axvline(sub_x1, color='gray', linestyle=':', linewidth=1, alpha=0.6)
        ax.axvline(sub_x2, color='gray', linestyle=':', linewidth=1, alpha=0.6)
        ax.axhline(sub_y1, color='gray', linestyle=':', linewidth=1, alpha=0.6)
        ax.axhline(sub_y2, color='gray', linestyle=':', linewidth=1, alpha=0.6)

        for i, row in df_filtrado.iterrows():
            prod = str(row["Producto"])
            ax.annotate(prod, 
                         (row["Margen %"], row["Popularidad (Artículos Vendidos)"]),
                         textcoords="offset points", 
                         xytext=(25, 20), 
                         ha='center', 
                         fontsize=9, 
                         fontweight='bold',
                         bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="darkgray", alpha=0.95),
                         arrowprops=dict(arrowstyle="->", color="crimson", lw=0.9, connectionstyle="arc3,rad=0"))

        ax.set_title(f"Matriz BCG: {titulo_filtro}", fontsize=16, fontweight='bold', pad=15)
        ax.set_xlabel("Margen %", fontsize=13, fontweight='bold')
        ax.set_ylabel("Popularidad (Artículos Vendidos)", fontsize=13, fontweight='bold')
        ax.grid(True, linestyle=':', alpha=0.6, zorder=0)
        ax.legend(loc='upper right', fontsize=10)
        
        ax.set_xlim(min_x - 8, max_x + 8)
        ax.set_ylim(-80, max_y * 1.15 if max_y > 0 else 100)

        st.pyplot(fig)
    else:
        st.warning("No hay platillos registrados para esta categoría.")
