import streamlit as st
import json
import os
import importlib.util
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DEL SISTEMA ---
st.set_page_config(page_title="Universo X - Sistema Central", layout="wide")

ARCHIVO_USUARIOS = "usuarios_x.json"
ARCHIVO_CUENTAS = "cuentasx_f5co.json"

# --- FUNCIONES DE PERSISTENCIA ---
def cargar_json(ruta):
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return {}
    return {}

def guardar_json(datos, ruta):
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def cargar_modulo(nombre_archivo):
    ruta = os.path.join(os.getcwd(), nombre_archivo)
    if os.path.exists(ruta):
        spec = importlib.util.spec_from_file_location("mod", ruta)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
    else: st.error(f"⚠️ Módulo {nombre_archivo} no encontrado.")

# --- ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'modulo_activo' not in st.session_state: st.session_state.modulo_activo = "Lobby"
if 'user_id' not in st.session_state: st.session_state.user_id = None

# --- ESTÉTICA DARK PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: #FFFFFF; }
    h1, h2, h3, p, label { color: #00e6e6 !important; }
    .stButton>button { background-color: #111 !important; color: #fff !important; border: 1px solid #333 !important; height: 60px; font-size: 18px; }
    .stButton>button:hover { border-color: #00e6e6 !important; color: #00e6e6 !important; }
    .card-title { font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- PANEL MAESTRO ---
def renderizar_panel_maestro():
    st.title("🛠️ PANEL MAESTRO")
    if st.button("⬅️ VOLVER AL HUB"): 
        st.session_state.modulo_activo = "Lobby"
        st.rerun()
    
    db_u = cargar_json(ARCHIVO_USUARIOS)
    id_usuario = st.selectbox("Gestionar Usuario", options=list(db_u.keys()))
    
    if id_usuario:
        u = db_u[id_usuario]
        col1, col2 = st.columns(2)
        with col1:
            nuevo_estado = st.selectbox("Estado", ["activa", "desactiva"], index=0 if u.get('estado_cuenta')=="activa" else 1)
        with col2:
            nueva_fecha = st.date_input("Vencimiento", value=datetime.strptime(u.get('fecha_vencimiento', '2026-03-06'), '%Y-%m-%d'))
        
        if st.button("💾 GUARDAR CAMBIOS"):
            db_u[id_usuario]['estado_cuenta'] = nuevo_estado
            db_u[id_usuario]['fecha_vencimiento'] = str(nueva_fecha)
            guardar_json(db_u, ARCHIVO_USUARIOS)
            st.success("Usuario actualizado.")

# --- INTERFAZ ---
if not st.session_state.autenticado and st.session_state.modulo_activo != "PanelMaestro":
    st.title("🚀 Universo X")
    u_id = st.text_input("Celular (ID)")
    u_pw = st.text_input("Clave", type="password")
    if st.button("INGRESAR"):
        db_u = cargar_json(ARCHIVO_USUARIOS)
        if u_id in db_u and str(db_u[u_id]["clave"]) == str(u_pw):
            st.session_state.autenticado = True
            st.session_state.user_id = u_id
            st.rerun()
    
    st.divider()
    m_key = st.text_input("🔑 Acceso Maestro", type="password")
    if m_key == "10538" and st.button("ABRIR PANEL"):
        st.session_state.modulo_activo = "PanelMaestro"
        st.rerun()

elif st.session_state.modulo_activo == "PanelMaestro":
    renderizar_panel_maestro()

elif st.session_state.autenticado:
    # Sidebar
    u_id = st.session_state.user_id
    user = cargar_json(ARCHIVO_USUARIOS).get(u_id, {})
    st.sidebar.title(f"👤 {user.get('username')}")
    if user.get('clave') == "10538":
        if st.sidebar.button("🛠️ PANEL MAESTRO"):
            st.session_state.modulo_activo = "PanelMaestro"
            st.rerun()
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    if st.session_state.modulo_activo == "Lobby":
        st.title("🌌 Hub Central de Microservicios")

        # 1. MICROSERVICIOS OPERATIVOS
        st.markdown("<div class='card-title'>⚙️ OPERACIONES</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.button("🚚 LOGÍSTICA"): st.session_state.modulo_activo = "1_Logistica.py"; st.rerun()
        with c2: 
            if st.button("🚜 MÁQUINAS"): st.session_state.modulo_activo = "2_Maquinas.py"; st.rerun()
        with c3: 
            if st.button("🍔 RESTAURANTE"): st.session_state.modulo_activo = "3_restaurante.py"; st.rerun()

        # 2. NUEVOS SERVICIOS
        st.divider()
        st.markdown("<div class='card-title'>📦 SUMINISTROS Y SALUD</div>", unsafe_allow_html=True)
        c4, c5, c6 = st.columns(3)
        with c4: 
            if st.button("🛒 ALACENA / MERCADO"): st.info("Módulo Alacena en desarrollo...")
        with c5: 
            if st.button("🌱 AGRO-PRO"): st.info("Módulo Agro-Pro en desarrollo...")
        with c6: 
            if st.button("🦷 ODONTOLOGÍA"): st.info("Módulo Odontología en desarrollo...")

        # 3. ESPECIALIZADOS Y CONTENIDO
        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("<div class='card-title'>🧬 ESPECIALIZADO</div>", unsafe_allow_html=True)
            if st.button("🐍 CACD (IA OFÍDICA)"): st.session_state.modulo_activo = "x_cacd.py"; st.rerun()
        with col_b:
            st.markdown("<div class='card-title'>💎 CONTENIDO</div>", unsafe_allow_html=True)
            ca, cb = st.columns(2)
            with ca: 
                if st.button("🎨 GALERÍA ARTE"): st.info("Cargando Galería...")
            with cb: 
                if st.button("📑 DESCARGABLES"): st.info("Abriendo Biblioteca Técnica...")
    else:
        if st.sidebar.button("⬅️ VOLVER AL HUB"): 
            st.session_state.modulo_activo = "Lobby"
            st.rerun()
        cargar_modulo(st.session_state.modulo_activo)