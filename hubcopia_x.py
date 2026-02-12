import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import importlib.util

# --- CONFIGURACIÓN DEL UNIVERSO ---
st.set_page_config(page_title="Universo X - Lobby", layout="wide")

FOLDER_PATH = "PROYECTOS_X"
USUARIOS_FILE = os.path.join(FOLDER_PATH, "usuariosllave_x.json")

if not os.path.exists(FOLDER_PATH):
    os.makedirs(FOLDER_PATH)

# --- ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'modulo_activo' not in st.session_state:
    st.session_state.modulo_activo = "Lobby"
# Para que 2_Maquinas.py no bloquee el acceso
if 'llave_general' not in st.session_state:
    st.session_state.llave_general = False

# --- FUNCIONES DE NAVEGACIÓN ---
def cargar_modulo(nombre_archivo):
    path = os.path.join(os.getcwd(), nombre_archivo)
    spec = importlib.util.spec_from_file_location("modulo", path)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)

def cargar_usuarios():
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, "r") as f:
            try: return json.load(f)
            except: return {}
    return {}

# --- ESTÉTICA DARK TOTAL ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2, h3, h4, p, label, .stMarkdown { color: #FFFFFF !important; }
    
    /* Tarjetas del Lobby */
    .lobby-card {
        background-color: #1A1A1A;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        transition: 0.3s;
    }
    
    /* Botones */
    div.stButton > button {
        background-color: #000000 !important; 
        color: #FFFFFF !important;
        border: 1px solid #4B4B4B !important; 
        font-weight: bold;
        width: 100%;
        border-radius: 10px;
    }
    div.stButton > button:hover { border-color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- PANTALLA DE ACCESO MAESTRO ---
if not st.session_state.autenticado:
    st.title("✖️ SISTEMA CENTRAL X")
    col_l, col_c, col_r = st.columns([1, 1, 1])
    with col_c:
        llave_master = st.text_input("Llave de Activación", type="password")
        if st.button("DESBLOQUEAR UNIVERSO"):
            if llave_master == "2222":
                st.session_state.autenticado = True
                st.session_state.llave_general = True
                st.rerun()
            else:
                st.error("Acceso denegado.")

# --- LOBBY DE MICROSERVICIOS ---
elif st.session_state.modulo_activo == "Lobby":
    st.title("Welcome to the Hub - Universo X")
    st.write("Selecciona el microservicio al que deseas acceder:")
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="lobby-card"><h3>🚚 LOGÍSTICA</h3><p>Gestión de pedidos y servicios.</p></div>', unsafe_allow_html=True)
        if st.button("ENTRAR A LOGÍSTICA"):
            st.session_state.modulo_activo = "1_Logistica.py"
            st.rerun()

    with col2:
        st.markdown('<div class="lobby-card"><h3>🚜 MÁQUINAS</h3><p>Control de flota y combustible.</p></div>', unsafe_allow_html=True)
        if st.button("ENTRAR A MÁQUINAS"):
            st.session_state.modulo_activo = "2_Maquinas.py"
            st.rerun()

    with col3:
        st.markdown('<div class="lobby-card"><h3>⚙️ GESTIÓN</h3><p>Usuarios y llaves de acceso.</p></div>', unsafe_allow_html=True)
        if st.button("CONFIGURACIÓN X"):
            st.session_state.modulo_activo = "Configuracion"
            st.rerun()

    st.sidebar.button("🚪 APAGAR SISTEMA", on_click=lambda: st.session_state.update({"autenticado": False}))

# --- CARGA DINÁMICA DE MÓDULOS ---
elif st.session_state.modulo_activo == "Configuracion":
    if st.button("⬅️ VOLVER AL LOBBY"):
        st.session_state.modulo_activo = "Lobby"
        st.rerun()
    
    st.header("⚙️ Gestión de Accesos")
    opcion = st.radio("Acción:", ["Registrar Nueva Llave", "Tabla Privada (1991)"], horizontal=True)
    
    if opcion == "Registrar Nueva Llave":
        with st.form("reg"):
            c = st.text_input("Celular")
            k = st.text_input("Llave", type="password")
            if st.form_submit_button("REGISTRAR"):
                # Aquí iría tu función guardar_vinculo
                st.success("Usuario registrado.")
                
    elif opcion == "Tabla Privada (1991)":
        pw = st.text_input("Llave Privada", type="password")
        if pw == "1991":
            db = cargar_usuarios()
            st.dataframe(pd.DataFrame.from_dict(db, orient='index'), use_container_width=True)

else:
    # Este bloque carga 1_Logistica.py o 2_Maquinas.py
    if st.sidebar.button("⬅️ SALIR AL LOBBY"):
        st.session_state.modulo_activo = "Lobby"
        st.rerun()
    
    try:
        cargar_modulo(st.session_state.modulo_activo)
    except Exception as e:
        st.error(f"Error cargando el módulo: {e}")