import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN DE RUTA ---
FOLDER_PATH = "PROYECTOS_X"
DB_FILE = os.path.join(FOLDER_PATH, "usuarios_x.json")

# Configuración de página con el estilo del Universo
st.set_page_config(page_title="Lector de Datos X", page_icon="🔍", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    h1, h2, h3, p, span, label { color: #FFFFFF !important; }
    .stDataFrame { background-color: #1A1C23; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔍 Lector del Universo X")
st.write("Visualización directa del archivo `usuarios_x.json` en tiempo real.")

if os.path.exists(DB_FILE):
    try:
        # Cargamos los datos forzando que celular y expedición sean texto
        df = pd.read_json(DB_FILE, dtype={'celular': str, 'expedicion': str})
        
        # Resumen rápido
        st.metric("Total de Usuarios", len(df))
        
        # Buscador rápido
        busqueda = st.text_input("Filtrar por nombre o celular:")
        if busqueda:
            df = df[df['nombre'].str.contains(busqueda, case=False) | df['celular'].str.contains(busqueda)]

        # Mostrar la tabla
        st.dataframe(df, use_container_width=True)
        
        # Botón para descargar en Excel (CSV)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Base de Datos",
            data=csv,
            file_name='usuarios_x_backup.csv',
            mime='text/csv',
        )

    except Exception as e:
        st.error(f"Error al leer la base de datos: {e}")
else:
    st.warning(f"No se encontró el archivo en la ruta: {DB_FILE}")