import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, date

# --- CONFIGURACIÓN DEL UNIVERSO X ---
st.set_page_config(page_title="X - Seguridad Nivel 3", layout="wide", page_icon="🚀")

# Estética de la Colmena: Contraste Total y Visibilidad
st.markdown("""
    <style>
    .stApp { background-color: #0a0a1a; }
    html, body, [class*="st-text"], p, label, .stMarkdown, .stTabs [data-baseweb="tab"], 
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stWidgetLabel"], .stRadio label {
        color: #ffffff !important;
    }
    h1, h2, h3 { 
        color: #00e6e6 !important; 
        text-shadow: 0 0 10px rgba(0, 230, 230, 0.4); 
    }
    [data-testid="stSidebar"] {
        background-color: #111122 !important;
        border-right: 1px solid #00e6e6;
    }
    </style>
    """, unsafe_allow_html=True)

def cargar_usuarios():
    if os.path.exists("usuarios.json"):
        with open("usuarios.json", "r") as f:
            return json.load(f)
    return {}

def guardar_usuarios(usuarios):
    with open("usuarios.json", "w") as f:
        json.dump(usuarios, f, indent=4)

# --- SISTEMA DE AUTENTICACIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Acceso al Universo X")
        celular = st.text_input("Número de Celular (ID)", placeholder="Escribe tu celular...")
        clave = st.text_input("Clave de Seguridad", type="password")
        
        if st.button("Sincronizar Identidad"):
            users = cargar_usuarios()
            if celular in users and users[celular]['clave'] == clave:
                st.session_state.autenticado = True
                st.session_state.user_id = celular
                st.session_state.datos_usuario = users[celular]
                st.rerun()
            else:
                st.error("Identidad no reconocida.")

    # --- LLAVE MAESTRA Y RESTAURACIÓN (EL PANEL QUE TENÍAS) ---
    with st.expander("🛠 Soporte Técnico (Llave Maestra)"):
        clave_m = st.text_input("Código Maestro", type="password", key="m_key")
        if clave_m == "2131":
            st.subheader("Panel de Gestión de la Colmena")
            usuarios = cargar_usuarios()
            
            if usuarios:
                # 1. Opción para Restaurar Contraseña
                user_select = st.selectbox("Usuario a gestionar:", list(usuarios.keys()))
                nueva_pass = st.text_input("Asignar nueva clave:", type="password")
                if st.button("Actualizar Clave"):
                    usuarios[user_select]['clave'] = nueva_pass
                    guardar_usuarios(usuarios)
                    st.success(f"Clave de {user_select} actualizada.")
                
                st.divider()
                
                # 2. Visualización de Base de Datos
                data_admin = []
                for uid, info in usuarios.items():
                    data_admin.append({
                        "ID (Cel)": uid, "Nombre": info.get('nombre'),
                        "Expedición": info.get('expedicion'), "Clave": info.get('clave')
                    })
                st.table(pd.DataFrame(data_admin))
            else:
                st.info("No hay usuarios registrados.")

# --- PANEL DE CONTROL (COLMENA MODULAR) ---
else:
    u = st.session_state.datos_usuario
    st.sidebar.title(f"👤 {u['nombre']}")
    opciones = ["Inicio", "⚙️ Máquinas", "💻 Tecnología", "🚜 Agro-Pro", "🏦 F5CO"]
    seleccion = st.sidebar.radio("Navegar a:", opciones)
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    if seleccion == "Inicio":
        st.header(f"🌌 Centro de Mandos - Universo X")
        st.write(f"Bienvenido de nuevo, **{u['nombre']}**.")
    
    elif seleccion == "⚙️ Máquinas":
        try:
            from servicios import maquinas
            maquinas.ejecutar()
        except: st.warning("Módulo de Máquinas no detectado.")