import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Matriz BCG por Familias - Menú", layout="wide")

st.title("📊 Generador de Matriz BCG por Categorías de Menú")
st.markdown("Selecciona una pestaña para administrar y analizar cada familia de platillos de forma independiente con sus propios promedios.")

# Definir las categorías solicitadas
categorias = [
    "DESAYUNOS", "QUESADILLAS", "ENTRADAS", "CALDOS", 
    "MARISCOS", "CARNES", "CHAROLAS DE CARNES", "CHAROLAS DE MARISCOS"
]

# Diccionario con datos base de ejemplo
datos_base = {
    "DESAYUNOS": [
        ("Huevos al gusto", 55.0, 120),
        ("Chilaquiles sencillos", 60.0, 180),
        ("Chilaquiles con carne", 45.0, 95)
    ],
    "QUESADILLAS": [
        ("Quesadilla de bistec", 50.0, 140),
        ("Quesadilla de queso", 65.0, 210),
        ("Quesadilla especial", 48.0, 85)
    ],
    "ENTRADAS": [
        ("Sopa de pan", 71.0, 40),
        ("Chile relleno pollo", 96.0, 185),
        ("Chile relleno puerco", 96.0, 67)
    ],
    "CALDOS": [
        ("Caldo de gallina", 63.0, 967),
        ("Caldo de guajolote", 37.0, 76),
        ("Cocido de res", 53.0, 103),
        ("Mondongo", 48.0, 388),
        ("Mole de gallina", 63.0, 226),
        ("Mole de guajolote", 44.0, 61)
    ],
    "MARISCOS": [
        ("Filete empanizado", 45.0, 110),
        ("Caldo de camarón", 52.0, 135),
        ("Mojarra frita", 40.0, 160)
    ],
    "CARNES": [
        ("Barbacoa de borrego", 42.0, 515),
        ("Asado de puerco", 58.0, 58),
        ("Bistec a la mexicana", 60.0, 130),
        ("Milanesa de pollo", 60.0, 228),
        ("Milanesa de res", 33.0, 38)
    ],
    "CHAROLAS DE CARNES": [
        ("Charola Parrillada Mixta", 38.0, 45),
        ("Charola Carnes Asadas", 35.0, 30)
    ],
    "CHAROLAS DE MARISCOS": [
        ("Charola Mariscos Especial", 42.0, 25),
        ("Charola Fritos del Mar", 40.0, 20)
    ]
}

# Crear las pestañas en la interfaz
pestanas = st.tabs(categorias)

for idx, cat in enumerate(categorias):
    with pestanas[idx]:
        st.subheader(f"📂 Familia: {cat}")
        st.markdown(f"Edita los platillos, costos y ventas específicos para **{cat}**. *(Puedes agregar filas con el botón '+' o borrar filas vacías seleccionándolas y presionando la tecla Supr/Backspace)*:")
        
        df_cat_inicial = pd.DataFrame(datos_base[cat], columns=["Producto", "Margen %", "Popularidad (Artículos Vendidos)"])
        
        # Editor interactivo
        df_cat_editado = st.data_editor(df_cat_inicial, num_rows="dynamic", key=f"editor_{cat}", use_container_width=True)
        
        if not df_cat_editado.empty:
            # LIMPIEZA AUTOMÁTICA: Eliminar filas donde el nombre del producto esté vacío, sea None o nulo
            df_cat_editado = df_cat_editado.dropna(subset=["Producto"])
            df_cat_editado = df_cat_editado[df_cat_editado["Producto"].astype(str).str.strip() != ""]
            
            # Asegurar que Margen y Popularidad sean numéricos
            df_cat_editado["Margen %"] = pd.to_numeric(df_cat_editado["Margen %"], errors="coerce").fillna(0)
            df_cat_editado["Popularidad (Artículos Vendidos)"] = pd.to_numeric(df_cat_editado["Popularidad (Artículos Vendidos)"], errors="coerce").fillna(0)

        if not df_cat_editado.empty:
            # Calcular promedios exclusivos de esta categoría limpia
            mean_x = df_cat_editado["Margen %"].mean()
            mean_y = df_cat_editado["Popularidad (Artículos Vendidos)"].mean()
            
            def clasificar_bcg(row, mx, my):
                if row["Margen %"] >= mx and row["Popularidad (Artículos Vendidos)"] >= my:
                    return "Estrella ⭐"
                elif row["Margen %"] < mx and row["Popularidad (Artículos Vendidos)"] >= my:
                    return "Vaca 🐮"
                elif row["Margen %"] >= mx and row["Popularidad (Artículos Vendidos)"] < my:
                    return "Interrogante ❓"
                else:
                    return "Perro 🐶"
            
            df_cat_editado["Cuadrante BCG"] = df_cat_editado.apply(lambda r: clasificar_bcg(r, mean_x, mean_y), axis=1)
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            col1.metric(f"Margen Promedio ({cat})", f"{mean_x:.2f}%")
            col2.metric(f"Popularidad Promedio ({cat})", f"{mean_y:.2f} arts.")
            
            st.dataframe(df_cat_editado, use_container_width=True)
            
            # Generar gráfica exclusiva
            st.markdown(f"### 📈 Gráfica BCG — {cat}")
            
            min_x, max_x = df_cat_editado["Margen %"].min(), df_cat_editado["Margen %"].max()
            if min_x == max_x:
                min_x -= 5
                max_x += 5
                
            min_y, max_y = 0, df_cat_editado["Popularidad (Artículos Vendidos)"].max()
            
            sub_x1 = (min_x + mean_x) / 2
            sub_x2 = (mean_x + max_x) / 2
            sub_y1 = (min_y + mean_y) / 2
            sub_y2 = (mean_y + max_y) / 2
            
            fig, ax = plt.subplots(figsize=(14, 9))
            
            ax.scatter(df_cat_editado["Margen %"], df_cat_editado["Popularidad (Artículos Vendidos)"], 
                       color='navy', s=120, edgecolors='white', linewidths=1.5, zorder=3)
            
            ax.axvline(mean_x, color='crimson', linestyle='--', linewidth=2, alpha=0.9, label=f'Promedio Margen ({mean_x:.1f}%)')
            ax.axhline(mean_y, color='crimson', linestyle='--', linewidth=2, alpha=0.9, label=f'Promedio Popularidad ({mean_y:.1f})')
            
            ax.axvline(sub_x1, color='gray', linestyle=':', linewidth=1, alpha=0.6)
            ax.axvline(sub_x2, color='gray', linestyle=':', linewidth=1, alpha=0.6)
            ax.axhline(sub_y1, color='gray', linestyle=':', linewidth=1, alpha=0.6)
            ax.axhline(sub_y2, color='gray', linestyle=':', linewidth=1, alpha=0.6)
            
            for i, row in df_cat_editado.iterrows():
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
            
            ax.set_title(f"Matriz BCG Independiente: {cat}", fontsize=15, fontweight='bold', pad=15)
            ax.set_xlabel("Margen %", fontsize=12, fontweight='bold')
            ax.set_ylabel("Popularidad (Artículos Vendidos)", fontsize=12, fontweight='bold')
            ax.grid(True, linestyle=':', alpha=0.6, zorder=0)
            ax.legend(loc='upper right', fontsize=10)
            
            ax.set_xlim(min_x - 8, max_x + 8)
            ax.set_ylim(-50, max_y * 1.15 if max_y > 0 else 100)
            
            st.pyplot(fig)
        else:
            st.info(f"Agrega al menos un platillo en la tabla de {cat} para ver sus métricas y gráfica.")
