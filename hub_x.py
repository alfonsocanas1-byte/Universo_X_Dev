import streamlit as st
import json
import os
import importlib.util
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Universo X - Microservicios Central", layout="wide")

ARCHIVO_USUARIOS = "usuarios_x.json"
ARCHIVO_CUENTAS = "cuentasx_f5co.json"

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
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    else: st.error(f"⚠️ Módulo {nombre_archivo} no encontrado.")

# --- ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'modulo_activo' not in st.session_state: st.session_state.modulo_activo = "Lobby"
if 'user_id' not in st.session_state: st.session_state.user_id = None

# --- INTERFAZ DARK PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: #FFFFFF; }
    h1, h2, h3, p, label { color: #00e6e6 !important; }
    .stButton>button { background-color: #FFFFFF !important; color: #000 !important; font-weight: bold !important; width: 100%; border: 2px solid #00e6e6 !important; }
    .stButton>button:hover { background-color: #00e6e6 !important; }
    .card { background: #111; border: 1px solid #333; padding: 15px; border-radius: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN Y PANEL MAESTRO ---
if not st.session_state.autenticado and st.session_state.modulo_activo != "Panel_Maestro":
    st.title("🚀 Portal F5CO - Sincronización")
    c_login, c_master = st.columns([2, 1])
    
    with c_login:
        with st.form("login"):
            u_id = st.text_input("Celular (ID)")
            u_pw = st.text_input("Clave", type="password")
            if st.form_submit_button("SINCRONIZAR"):
                db_u = cargar_json(ARCHIVO_USUARIOS)
                if u_id in db_u and db_u[u_id]["clave"] == u_pw:
                    db_c = cargar_json(ARCHIVO_CUENTAS)
                    if u_id not in db_c: # Auto-registro en F5CO
                        db_c[u_id] = {"identidad": db_u[u_id]["username"], "servicios_f5co": {"microservicios": {"activo": False}, "plataforma_descargables": {"activo": False}, "galeria_arte": {"activo": False}}}
                        guardar_json(db_c, ARCHIVO_CUENTAS)
                    st.session_state.autenticado = True; st.session_state.user_id = u_id; st.rerun()
                else: st.error("Error de acceso.")
    
    with c_master:
        if st.text_input("Llave Administrativa", type="password") == "10538":
            if st.button("ABRIR PANEL MAESTRO"): st.session_state.modulo_activo = "Panel_Maestro"; st.rerun()

elif st.session_state.modulo_activo == "Panel_Maestro":
    st.title("🛠️ Panel Maestro - Gestión de Microservicios")
    if st.button("⬅️ VOLVER"): st.session_state.modulo_activo = "Lobby"; st.rerun()
    db_c = cargar_json(ARCHIVO_CUENTAS)
    for cid, info in db_c.items():
        with st.expander(f"👤 {info['identidad']} ({cid})"):
            # Aquí controlas si el Microservicio está activo
            ms_status = st.checkbox("Habilitar Microservicios (Logística, Máquinas, etc.)", value=info['servicios_f5co']['microservicios']['activo'], key=cid)
            if st.button(f"GUARDAR CAMBIOS {cid}"):
                db_c[cid]['servicios_f5co']['microservicios']['activo'] = ms_status
                guardar_json(db_c, ARCHIVO_CUENTAS); st.success("Actualizado.")

# --- LOBBY DE MICROSERVICIOS ---
else:
    cuenta = cargar_json(ARCHIVO_CUENTAS).get(st.session_state.user_id, {})
    permisos = cuenta.get('servicios_f5co', {})
    
    st.sidebar.title(f"👤 {cuenta.get('identidad', 'Usuario')}")
    if st.sidebar.button("Cerrar Sesión"): st.session_state.autenticado = False; st.rerun()

    if st.session_state.modulo_activo == "Lobby":
        st.title("🌌 Hub de Microservicios - Universo X")
        
        # Bloque condicional: Solo si 'microservicios' está activo
        if permisos.get('microservicios', {}).get('activo'):
            st.subheader("⚙️ Servicios Operativos Habilitados")
            c1, c2, c3, c4 = st.columns(4)
            servicios = [("🚚 LOGÍSTICA", "1_Logistica.py", c1), ("🚜 MÁQUINAS", "2_Maquinas.py", c2), 
                         ("🍔 COCINA", "3_restaurante.py", c3), ("🐍 CACD", "x_cacd.py", c4)]
            
            for nombre, archivo, col in servicios:
                with col:
                    st.markdown(f'<div class="card"><h3>{nombre}</h3></div>', unsafe_allow_html=True)
                    if st.button(f"ENTRAR", key=archivo): st.session_state.modulo_activo = archivo; st.rerun()
        else:
            st.warning("🔒 Microservicios bloqueados. Contacte al administrador para verificación por WhatsApp.")
            st.markdown('<div class="card" style="opacity:0.3"><h3>SERVICIOS DESACTIVADOS</h3><p>Verificación de número pendiente.</p></div>', unsafe_allow_html=True)

        # Otros servicios (Galería/Descargables)
        st.divider()
        col_g, col_d = st.columns(2)
        with col_g:
            if permisos.get('galeria_arte', {}).get('activo'):
                if st.button("🎨 GALERÍA DE ARTE"): st.info("Cargando Galería...")
            else: st.markdown('<div class="card" style="opacity:0.3"><h4>🎨 Galería (Bloqueada)</h4></div>', unsafe_allow_html=True)
    
    else:
        if st.sidebar.button("⬅️ REGRESAR AL HUB"): st.session_state.modulo_activo = "Lobby"; st.rerun()
        cargar_modulo(st.session_state.modulo_activo)