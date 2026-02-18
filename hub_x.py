import streamlit as st
import json
import os
import importlib.util
from datetime import datetime

# --- CONFIGURACIÓN DEL SISTEMA ---
st.set_page_config(page_title="Universo X - Sistema Central", layout="wide")

ARCHIVO_USUARIOS = "usuarios_x.json"
ARCHIVO_CUENTAS = "cuentasx_f5co.json"

def cargar_json(ruta):
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return {}
    return {}

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

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    .card {
        background-color: #1A1A1A; border: 1px solid #444;
        padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 10px;
    }
    .card-spec { border-color: #ff00ff; box-shadow: 0px 0px 10px #ff00ff33; }
    .card-lock { opacity: 0.4; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
if not st.session_state.autenticado:
    # (Aquí iría tu lógica de login actual)
    st.title("🌌 Acceso al Universo X")
    user = st.text_input("Usuario (ID)")
    pin = st.text_input("PIN", type="password")
    if st.button("INGRESAR"):
        db = cargar_json(ARCHIVO_USUARIOS)
        if user in db and db[user]['clave'] == pin:
            st.session_state.autenticado = True
            st.session_state.user_id = user
            st.rerun()

elif st.session_state.modulo_activo != "Lobby":
    if st.sidebar.button("⬅️ VOLVER AL HUB"):
        st.session_state.modulo_activo = "Lobby"
        st.rerun()
    cargar_modulo(st.session_state.modulo_activo)

else:
    # --- LOBBY PRINCIPAL ---
    cuentas = cargar_json(ARCHIVO_CUENTAS)
    permisos = cuentas.get(st.session_state.user_id, {}).get('servicios_f5co', {})
    
    st.title("🌌 Universo X - Panel de Control")
    st.divider()

    # SECCIÓN 1: OPERACIONES ESTÁNDAR
    st.subheader("🚚 Operaciones Base")
    c1, c2, c3 = st.columns(3)
    servicios_base = [
        ("LOGÍSTICA", "1_Logistica.py", c1),
        ("MÁQUINAS", "2_Maquinas.py", c2),
        ("COCINA", "3_restaurante.py", c3)
    ]
    
    for nombre, archivo, col in servicios_base:
        with col:
            st.markdown(f'<div class="card"><h3>{nombre}</h3></div>', unsafe_allow_html=True)
            if st.button(f"ENTRAR", key=archivo):
                st.session_state.modulo_activo = archivo
                st.rerun()

    st.divider()

    # SECCIÓN 2: MICROSERVICIOS ESPECIALIZADOS (IA & CACD)
    st.subheader("🧬 Microservicios Especializados")
    ce1, ce2 = st.columns(2)
    
    is_especializado = permisos.get('microservicios_especializados', {}).get('activo', False)

    with ce1:
        if is_especializado:
            st.markdown('<div class="card card-spec"><h3>🐍 CACD (IA Ofídica)</h3><p>Análisis Predictivo Activado</p></div>', unsafe_allow_html=True)
            if st.button("INICIAR PROTOCOLO CACD"):
                st.session_state.modulo_activo = "x_cacd.py"
                st.rerun()
        else:
            st.markdown('<div class="card card-lock"><h3>🔒 CACD BLOQUEADO</h3><p>Requiere Nivel Especializado</p></div>', unsafe_allow_html=True)

    with ce2:
        if is_especializado:
            st.markdown('<div class="card card-spec"><h3>📊 DATA MINING</h3><p>Consultoría de Datos X</p></div>', unsafe_allow_html=True)
            if st.button("VER REPORTES"): st.info("Cargando base de datos...")
        else:
            st.markdown('<div class="card card-lock"><h3>🔒 DATA MINING</h3><p>Acceso Restringido</p></div>', unsafe_allow_html=True)

    st.divider()

    # SECCIÓN 3: PLATAFORMAS DE CONTENIDO
    st.subheader("💎 Contenido & Documentación")
    ca, cb = st.columns(2)
    with ca:
        if permisos.get('plataforma_descargables', {}).get('activo'):
            if st.button("📑 BIBLIOTECA TÉCNICA"): st.info("Abriendo...")
        else: st.markdown('<div class="card card-lock"><h4>🔒 DESCARGABLES</h4></div>', unsafe_allow_html=True)
    with cb:
        if permisos.get('galeria_arte', {}).get('activo'):
            if st.button("🎨 GALERÍA DE ARTE"): st.info("Cargando...")
        else: st.markdown('<div class="card card-lock"><h4>🔒 GALERÍA</h4></div>', unsafe_allow_html=True)