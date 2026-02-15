import streamlit as st
import os
import importlib.util

# --- CONFIGURACIÓN DEL UNIVERSO ---
st.set_page_config(page_title="Universo X - Lobby", layout="wide")

# --- ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'modulo_activo' not in st.session_state:
    st.session_state.modulo_activo = "Lobby"

# --- FUNCIÓN DE CARGA SEGURA ---
def cargar_modulo(nombre_archivo):
    ruta_completa = os.path.join(os.getcwd(), nombre_archivo)
    if os.path.exists(ruta_completa):
        spec = importlib.util.spec_from_file_location("modulo_dinamico", ruta_completa)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
    else:
        st.error(f"⚠️ El archivo '{nombre_archivo}' no se encuentra en la raíz.")

# --- ESTÉTICA DARK ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2, h3, h4, p, label { color: #FFFFFF !important; }
    .lobby-card {
        background-color: #1A1A1A; border: 1px solid #333; padding: 20px;
        border-radius: 15px; text-align: center; min-height: 180px; margin-bottom: 10px;
    }
    div.stButton > button {
        background-color: #000000 !important; color: #FFFFFF !important;
        border: 1px solid #4B4B4B !important; font-weight: bold; width: 100%; border-radius: 10px;
    }
    div.stButton > button:hover { border-color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ACCESO MAESTRO ---
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>✖️ SISTEMA CENTRAL X</h1>", unsafe_allow_html=True)
    col_c = st.columns([1, 1, 1])[1]
    with col_c:
        llave = st.text_input("Llave de Activación", type="password")
        if st.button("DESBLOQUEAR UNIVERSO"):
            if llave == "2222":
                st.session_state.autenticado = True
                st.rerun()

# --- LOBBY: LOS CUATRO PILARES ---
elif st.session_state.modulo_activo == "Lobby":
    st.title("Welcome to the Hub - Universo X")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="lobby-card"><h3>🚚 LOGÍSTICA</h3><p>Gestión de pedidos.</p></div>', unsafe_allow_html=True)
        if st.button("ENTRAR A LOGÍSTICA"):
            st.session_state.modulo_activo = "1_Logistica.py"; st.rerun()

    with col2:
        st.markdown('<div class="lobby-card"><h3>🚜 MÁQUINAS</h3><p>Control de flota.</p></div>', unsafe_allow_html=True)
        if st.button("ENTRAR A MÁQUINAS"):
            st.session_state.modulo_activo = "2_Maquinas.py"; st.rerun()

    with col3:
        st.markdown('<div class="lobby-card"><h3>🍳 COCINA</h3><p>Pedidos gourmet.</p></div>', unsafe_allow_html=True)
        if st.button("ENTRAR A COCINA"):
            st.session_state.modulo_activo = "3_restaurante.py"; st.rerun()

    with col4:
        st.markdown('<div class="lobby-card"><h3>🐍 CACD</h3><p>Reporte médico ofídico.</p></div>', unsafe_allow_html=True)
        if st.button("ENTRAR A CACD"):
            st.session_state.modulo_activo = "x_cacd.py"; st.rerun()

    st.sidebar.button("🚪 APAGAR", on_click=lambda: st.session_state.update({"autenticado": False, "modulo_activo": "Lobby"}))

# --- CARGA DEL MÓDULO ---
else:
    if st.sidebar.button("⬅️ VOLVER AL LOBBY"):
        st.session_state.modulo_activo = "Lobby"; st.rerun()
    cargar_modulo(st.session_state.modulo_activo)