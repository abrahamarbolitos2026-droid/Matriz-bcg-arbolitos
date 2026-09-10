import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Matriz BCG Restaurante", layout="wide")

st.title("📊 Generador de Matriz BCG por Categorías de Menú")
st.markdown("Edita, copia/pega tus datos (Ctrl+V) y genera la Matriz BCG de Restaurante Los Arbolitos. **Tus datos se guardan automáticamente en la sesión.**")

# Definir las categorías solicitadas
categorias = [
    "DESAYUNOS", "QUESADILLAS", "ENTRADAS", "CALDOS", 
    "MARISCOS", "CARNES", "CHAROLAS DE CARNES", "CHAROLAS DE MARISCOS"
]

# Datos base iniciales (solo para el primer inicio)
datos_base_iniciales = {
    "DESAYUNOS": [("Huevos al gusto", 55.0, 120), ("Chilaquiles sencillos", 60.0, 180)],
    "QUESADILLAS": [("Quesadilla de bistec", 50.0, 140)],
    "ENTRADAS": [("Sopa de pan", 71.0, 40), ("Chile relleno pollo", 96.0, 185)],
    "CALDOS": [("Caldo de gallina", 63.0, 967)],
    "MARISCOS": [("Filete empanizado", 45.0, 110)],
    "CARNES": [("Barbacoa de borrego", 42.0, 515), ("Asado de puerco", 58.0, 58)],
    "CHAROLAS DE CARNES": [("Charola Parrillada Mixta", 38.0, 45)],
    "CHAROLAS DE MARISCOS": [("Charola Mariscos Especial", 42.0, 25)]
}

# --- SISTEMA DE PERSISTENCIA DE DATOS (GUARDADO AUTOMÁTICO) ---
if "menu_data" not in st.session_state:
    st.session_state.menu_data = {}
    for cat in categorias:
        st.session_state.menu_data[cat] = pd.DataFrame(
            datos_base_iniciales.get(cat, []), 
            columns=["Producto", "Margen %", "Popularidad (Artículos Vendidos)"]
        )

# Crear las pestañas en la interfaz
pestanas = st.tabs(categorias)

for idx, cat in enumerate(categorias):
    with pestanas[idx]:
        st.subheader(f"📂 Familia: {cat}")
        st.markdown(f"Edita directamente, **copia y pega celdas desde Excel** (`Ctrl + V`) en la tabla de abajo. Tus cambios se guardan solos.")
        
        # Editor interactivo enlazado al session_state
        df_cat_editado = st.data_editor(
            st.session_state.menu_data[cat], 
            num_rows="dynamic", 
            key=f"editor_{cat}", 
            use_container_width=True
        )
        
        # Actualizar la sesión de inmediato con los cambios del usuario
        if df_cat_editado is not None:
            st.session_state.menu_data[cat] = df_cat_editado

        # Obtener el DataFrame actual para los cálculos
        df_actual = st.session_state.menu_data[cat]

        # LIMPIEZA AUTOMÁTICA DE DATOS
        if not df_actual.empty:
            df_actual = df_actual.dropna(subset=["Producto"])
            df_actual = df_actual[df_actual["Producto"].astype(str).str.strip() != ""]
            
            # Asegurar tipos numéricos
            df_actual["Margen %"] = pd.to_numeric(df_actual["Margen %"], errors="coerce").fillna(0)
            df_actual["Popularidad (Artículos Vendidos)"] = pd.to_numeric(df_actual["Popularidad (Artículos Vendidos)"], errors="coerce").fillna(0)

        if not df_actual.empty and len(df_actual) > 0:
            # Calcular promedios principales
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
            
            # Generar gráfica BCG
            st.markdown(f"### 📈 Gráfica BCG — {cat}")
            
            min_x, max_x = df_actual["Margen %"].min(), df_actual["Margen %"].max()
            if min_x == max_x: min_x -= 5; max_x += 5
            
            min_y, max_y = 0, df_actual["Popularidad (Artículos Vendidos)"].max()
            if max_y == 0: max_y = 100 # Evitar error si no hay ventas
            
            # Cálculo de sub-promedios para los 4 cuadrantes
            sub_x1 = (min_x + mean_x) / 2
            sub_x2 = (mean_x + max_x) / 2
            sub_y1 = (min_y + mean_y) / 2
            sub_y2 = (mean_y + max_y) / 2
            
            # Panel superior con promedios en NEGRITAS
            st.info(f"📌 **Promedios Principales (Líneas rojas):** Margen = **{mean_x:.1f}%** | Popularidad = **{mean_y:.1f}**\n\n"
                    f"🔹 **Líneas de Sub-cuadrantes (Azul punteado):** Dividen la matriz en 4 zonas.")
            
            fig, ax = plt.subplots(figsize=(14, 10))
            
            xlim_min, xlim_max = min_x - 8, max_x + 8
            ylim_min, ylim_max = -50, max_y * 1.15 
            
            ax.set_xlim(xlim_min, xlim_max)
            ax.set_ylim(ylim_min, ylim_max)
            
            # --- MARCAS DE AGUA DISCRETAS POR CUADRANTE (FONDO) ---
            # VACA: Izquierda (Margen bajo), Arriba (Popularidad alta)
            ax.text((xlim_min + mean_x) / 2, (mean_y + ylim_max) / 2, "VACA", 
                    fontsize=40, fontweight='bold', ha='center', va='center', alpha=0.08, color='gray', zorder=0)
            # ESTRELLA: Derecha (Margen alto), Arriba (Popularidad alta)
            ax.text((mean_x + xlim_max) / 2, (mean_y + ylim_max) / 2, "ESTRELLA", 
                    fontsize=40, fontweight='bold', ha='center', va='center', alpha=0.08, color='gray', zorder=0)
            # PERRO: Izquierda (Margen bajo), Abajo (Popularidad baja)
            ax.text((xlim_min + mean_x) / 2, (ylim_min + mean_y) / 2, "PERRO", 
                    fontsize=40, fontweight='bold', ha='center', va='center', alpha=0.08, color='gray', zorder=0)
            # INTERROGANTE: Derecha (Margen alto), Abajo (Popularidad baja)
            ax.text((mean_x + xlim_max) / 2, (ylim_min + mean_y) / 2, "INTERROGANTE", 
                    fontsize=35, fontweight='bold', ha='center', va='center', alpha=0.08, color='gray', zorder=0)
            
            # Puntos de dispersión
            ax.scatter(df_actual["Margen %"], df_actual["Popularidad (Artículos Vendidos)"], 
                       color='navy', s=120, edgecolors='white', linewidths=1.5, zorder=3)
            
            # 1. Líneas principales (Destacadas en color carmesí / rojo fuerte) - AHORA VISIBLES
            ax.axvline(mean_x, color='crimson', linestyle='--', linewidth=2.5, alpha=0.9, zorder=2)
            ax.axhline(mean_y, color='crimson', linestyle='--', linewidth=2.5, alpha=0.9, zorder=2)
            
            # 2. Líneas de sub-cuadrantes (Destacan sutilmente en color azul pizarra con puntos)
            sub_color = '#4682B4' # Steel Blue
            ax.axvline(sub_x1, color=sub_color, linestyle=':', linewidth=1.5, alpha=0.7, zorder=2)
            ax.axvline(sub_x2, color=sub_color, linestyle=':', linewidth=1.5, alpha=0.7, zorder=2)
            ax.axhline(sub_y1, color=sub_color, linestyle=':', linewidth=1.5, alpha=0.7, zorder=2)
            ax.axhline(sub_y2, color=sub_color, linestyle=':', linewidth=1.5, alpha=0.7, zorder=2)
            
            # Configurar marcas (Ticks) en los ejes X e Y
            current_xticks = list(ax.get_xticks())
            for val in [mean_x, sub_x1, sub_x2]:
                if round(val, 1) not in [round(x, 1) for x in current_xticks]:
                    current_xticks.append(val)
            ax.set_xticks(sorted(current_xticks))
            
            current_yticks = list(ax.get_yticks())
            for val in [mean_y, sub_y1, sub_y2]:
                if round(val, 1) not in [round(y, 1) for y in current_yticks]:
                    current_yticks.append(val)
            ax.set_yticks(sorted(current_yticks))
            
            plt.xticks(rotation=45, fontsize=9)
            
            # Resaltar etiquetas numéricas de los promedios en los ejes
            for label in ax.get_xticklabels():
                try:
                    val_text = float(label.get_text())
                    if np.isclose(val_text, mean_x, atol=0.1):
                        label.set_fontweight('bold')
                        label.set_color('crimson')
                except ValueError: pass

            for label in ax.get_yticklabels():
                try:
                    val_text = float(label.get_text())
                    if np.isclose(val_text, mean_y, atol=0.1):
                        label.set_fontweight('bold')
                        label.set_color('crimson')
                except ValueError: pass

            # Anotaciones de productos
            for i, row in df_actual.iterrows():
                prod = str(row["Producto"])
                ax.annotate(prod, 
                             (row["Margen %"], row["Popularidad (Artículos Vendidos)"]),
                             textcoords="offset points", 
                             xytext=(25, 20), 
                             ha='center', 
                             fontsize=9, 
                             fontweight='bold',
                             bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="darkgray", alpha=0.95),
                             arrowprops=dict(arrowstyle="->", color="crimson", lw=0.9, connectionstyle="arc3,rad=0"),
                             zorder=4)
            
            # Título dinámico y etiquetas
            ax.set_title(f"Matriz BCG: {cat}", fontsize=15, fontweight='bold', pad=15)
            ax.set_xlabel("Margen %", fontsize=12, fontweight='bold')
            ax.set_ylabel("Popularidad (Artículos Vendidos)", fontsize=12, fontweight='bold')
            ax.grid(True, linestyle=':', alpha=0.4, zorder=1)
            
            st.pyplot(fig)
        else:
            st.info(f"Agrega o pega al menos un platillo en la tabla de {cat} para ver sus métricas y gráfica.")
