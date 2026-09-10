import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Matriz BCG por Familias", layout="wide")

st.title("📊 Generador de Matriz BCG por Categorías de Menú")
st.markdown("Pega tus datos directamente desde Excel (`Ctrl + V`) en las tablas de cada categoría.")

# Definir las categorías
categorias = [
    "DESAYUNOS", "QUESADILLAS", "ENTRADAS", "CALDOS", 
    "MARISCOS", "CARNES", "CHAROLAS DE CARNES", "CHAROLAS DE MARISCOS"
]

# Datos base iniciales mínimos
datos_base_iniciales = {
    "DESAYUNOS": [("Huevos al gusto", 55.0, 120), ("Chilaquiles sencillos", 60.0, 180)],
    "QUESADILLAS": [("Quesadilla de bistec", 50.0, 140), ("Quesadilla de queso", 65.0, 210)],
    "ENTRADAS": [("Sopa de pan", 71.0, 40), ("Chile relleno pollo", 96.0, 185)],
    "CALDOS": [("Caldo de gallina", 63.0, 967), ("Cocido de res", 53.0, 103)],
    "MARISCOS": [("Filete empanizado", 45.0, 110), ("Mojarra frita", 40.0, 160)],
    "CARNES": [("Barbacoa de borrego", 42.0, 515), ("Milanesa de pollo", 60.0, 228)],
    "CHAROLAS DE CARNES": [("Charola Parrillada Mixta", 38.0, 45)],
    "CHAROLAS DE MARISCOS": [("Charola Mariscos Especial", 42.0, 25)]
}

# --- INICIALIZAR MEMORIA DE SESIÓN ---
if "dataframes" not in st.session_state:
    st.session_state.dataframes = {}
    for cat in categorias:
        st.session_state.dataframes[cat] = pd.DataFrame(
            datos_base_iniciales[cat], 
            columns=["Producto", "Margen %", "Popularidad (Artículos Vendidos)"]
        )

# Crear las pestañas
pestanas = st.tabs(categorias)

for idx, cat in enumerate(categorias):
    with pestanas[idx]:
        st.subheader(f"📂 Familia: {cat}")
        st.markdown(f"Selecciona las celdas en tu Excel, copia (`Ctrl + C`), haz clic en la tabla de abajo y pega (`Ctrl + V`).")
        
        # Tabla interactiva optimizada para copiado y pegado directo
        df_cat_editado = st.data_editor(
            st.session_state.dataframes[cat], 
            num_rows="dynamic", 
            key=f"editor_{cat}", 
            use_container_width=True
        )
        
        if df_cat_editado is not None:
            st.session_state.dataframes[cat] = df_cat_editado.copy()

        df_actual = st.session_state.dataframes[cat]

        # Limpieza básica de datos vacíos
        if not df_actual.empty:
            df_actual = df_actual.dropna(subset=["Producto"])
            df_actual = df_actual[df_actual["Producto"].astype(str).str.strip() != ""]
            
            df_actual["Margen %"] = pd.to_numeric(df_actual["Margen %"], errors="coerce").fillna(0)
            df_actual["Popularidad (Artículos Vendidos)"] = pd.to_numeric(df_actual["Popularidad (Artículos Vendidos)"], errors="coerce").fillna(0)

        if not df_actual.empty and len(df_actual) > 0:
            mean_x = df_actual["Margen %"].mean()
            mean_y = df_actual["Popularidad (Artículos Vendidos)"].mean()
            
            def clasificar_bcg(row, mx, my):
                if row["Margen %"] >= mx and row["Popularidad (Artículos Vendidos)"] >= my:
                    return "Estrella ⭐"
                elif row["Margen %"] < mx and row["Popularidad (Artículos Vendidos)"] >= my:
                    return "Vaca 🐮"
                elif row["Margen %"] >= mx and row["Popularidad (Artículos Vendidos)"] < my:
                    return "Interrogante ❓"
                else:
                    return "Perro 🐶"
            
            df_actual["Cuadrante BCG"] = df_actual.apply(lambda r: clasificar_bcg(r, mean_x, mean_y), axis=1)
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            col1.metric(f"Margen Promedio ({cat})", f"{mean_x:.2f}%")
            col2.metric(f"Popularidad Promedio ({cat})", f"{mean_y:.2f} arts.")
            
            st.dataframe(df_actual, use_container_width=True)
            
            # --- GRÁFICA BCG ---
            st.markdown(f"### 📈 Gráfica BCG — {cat}")
            
            min_x, max_x = df_actual["Margen %"].min(), df_actual["Margen %"].max()
            if min_x == max_x:
                min_x -= 5
                max_x += 5
                
            min_y, max_y = 0, df_actual["Popularidad (Artículos Vendidos)"].max()
            
            sub_x1 = (min_x + mean_x) / 2
            sub_x2 = (mean_x + max_x) / 2
            sub_y1 = (min_y + mean_y) / 2
            sub_y2 = (mean_y + max_y) / 2
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            xlim_min, xlim_max = min_x - 8, max_x + 8
            ylim_min, ylim_max = -50, max_y * 1.15 if max_y > 0 else 100
            
            ax.set_xlim(xlim_min, xlim_max)
            ax.set_ylim(ylim_min, ylim_max)
            
            # Marcas de agua BCG tradicionales correctas
            ax.text((xlim_min + mean_x) / 2, (mean_y + ylim_max) / 2, "VACA", 
                    fontsize=35, fontweight='bold', ha='center', va='center', alpha=0.08, color='gray', zorder=0)
            ax.text((mean_x + xlim_max) / 2, (mean_y + ylim_max) / 2, "ESTRELLA", 
                    fontsize=35, fontweight='bold', ha='center', va='center', alpha=0.08, color='gray', zorder=0)
            ax.text((xlim_min + mean_x) / 2, (ylim_min + mean_y) / 2, "PERRO", 
                    fontsize=35, fontweight='bold', ha='center', va='center', alpha=0.08, color='gray', zorder=0)
            ax.text((mean_x + xlim_max) / 2, (ylim_min + mean_y) / 2, "INTERROGANTE", 
                    fontsize=30, fontweight='bold', ha='center', va='center', alpha=0.08, color='gray', zorder=0)
            
            # Puntos y líneas
            ax.scatter(df_actual["Margen %"], df_actual["Popularidad (Artículos Vendidos)"], 
                       color='navy', s=120, edgecolors='white', linewidths=1.5, zorder=3)
            
            ax.axvline(mean_x, color='crimson', linestyle='--', linewidth=2.5, alpha=0.9, zorder=2)
            ax.axhline(mean_y, color='crimson', linestyle='--', linewidth=2.5, alpha=0.9, zorder=2)
            
            for i, row in df_actual.iterrows():
                prod = str(row["Producto"])
                ax.annotate(prod, 
                             (row["Margen %"], row["Popularidad (Artículos Vendidos)"]),
                             textcoords="offset points", 
                             xytext=(20, 15), 
                             ha='center', 
                             fontsize=9, 
                             fontweight='bold',
                             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="darkgray", alpha=0.9),
                             arrowprops=dict(arrowstyle="->", color="crimson", lw=0.8),
                             zorder=4)
            
            ax.set_title(f"Matriz BCG: {cat}", fontsize=14, fontweight='bold', pad=12)
            ax.set_xlabel("Margen %", fontsize=11, fontweight='bold')
            ax.set_ylabel("Popularidad (Artículos Vendidos)", fontsize=11, fontweight='bold')
            ax.grid(True, linestyle=':', alpha=0.4, zorder=1)
            
            st.pyplot(fig)
        else:
            st.info(f"Agrega o pega datos en la tabla de {cat} para ver la gráfica.")
