import streamlit as st
import os
import importlib.util

# --- CONFIGURACIÓN DEL UNIVERSO ---
st.set_page_config(page_title="Universo X - Desarrollo", layout="wide")

# --- ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'modulo_activo' not in st.session_state:
    st.session_state.modulo_activo = "Lobby"

# --- FUNCIONES DE NAVEGACIÓN ---
def cargar_modulo(nombre_archivo):
    path = os.path.join(os.getcwd(), nombre_archivo)
    spec = importlib.util.spec_from_file_location("modulo", path)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)

# --- ESTÉTICA DARK TOTAL ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2, h3, h4, p, label, .stMarkdown { color: #FFFFFF !important; }
    
    .lobby-card {
        background-color: #1A1A1A;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 10px;
    }
    
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
    st.markdown("<h1 style='text-align: center;'>✖️ SISTEMA CENTRAL X (DEV)</h1>", unsafe_allow_html=True)
    st.write("---")
    col_l, col_c, col_r = st.columns([1, 1, 1])
    with col_c:
        llave_master = st.text_input("Llave de Activación", type="password")
        if st.button("DESBLOQUEAR UNIVERSO"):
            if llave_master == "2222":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Acceso denegado.")

# --- LOBBY DE MICROSERVICIOS ---
elif st.session_state.modulo_activo == "Lobby":
    st.title("Hub - Universo X [Desarrollo]")
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="lobby-card"><h3>🚚 LOGÍSTICA</h3><p>Panel operativo de flota.</p></div>', unsafe_allow_html=True)
        if st.button("ENTRAR A LOGÍSTICA"):
            st.session_state.modulo_activo = "1_Logistica.py"
            st.rerun()

    with col2:
        st.markdown('<div class="lobby-card"><h3>🚜 MÁQUINAS</h3><p>Gestión de combustible y foro.</p></div>', unsafe_allow_html=True)
        if st.button("ENTRAR A MÁQUINAS"):
            st.session_state.modulo_activo = "2_Maquinas.py"
            st.rerun()

    with col3:
        st.markdown('<div class="lobby-card"><h3>🍳 RESTAURANTE</h3><p>Cocina Gourmet.</p></div>', unsafe_allow_html=True)
        if st.button("ENTRAR A COCINA"):
            st.session_state.modulo_activo = "3_restaurante.py"
            st.rerun()

    st.sidebar.button("🚪 APAGAR", on_click=lambda: st.session_state.update({"autenticado": False, "modulo_activo": "Lobby"}))

# --- CARGA DINÁMICA DE MÓDULOS ---
else:
    if st.sidebar.button("⬅️ SALIR AL LOBBY"):
        st.session_state.modulo_activo = "Lobby"
        st.rerun()
    
    try:
        cargar_modulo(st.session_state.modulo_activo)
    except Exception as e:
        st.error(f"Error cargando el módulo {st.session_state.modulo_activo}: {e}")