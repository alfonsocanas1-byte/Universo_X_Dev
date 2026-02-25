import streamlit as st
import json
import os
import importlib.util
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DEL SISTEMA ---
st.set_page_config(page_title="Universo X - Sistema Central", layout="wide")

ARCHIVO_USUARIOS = "usuarios_x.json"

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

# --- ESTÉTICA PREMIUM (Letras Blancas y Dark Mode) ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: #FFFFFF; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] span {
        color: #FFFFFF !important;
    }
    h1, h2, h3, label { color: #00e6e6 !important; }
    .stButton>button { background-color: #111 !important; color: #fff !important; border: 1px solid #333 !important; height: 50px; width: 100%; }
    .stButton>button:hover { border-color: #00e6e6 !important; color: #00e6e6 !important; }
    .card-title { font-size: 1.1rem; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 5px; color: #00e6e6; }
    </style>
""", unsafe_allow_html=True)

# --- PANEL MAESTRO ---
def renderizar_panel_maestro():
    st.title("🛠️ PANEL MAESTRO")
    if st.button("⬅️ VOLVER AL HUB"): 
        st.session_state.modulo_activo = "Lobby"; st.rerun()
    
    db_u = cargar_json(ARCHIVO_USUARIOS)
    id_usuario = st.selectbox("Gestionar Usuario", options=list(db_u.keys()))
    
    if id_usuario:
        u = db_u[id_usuario]
        col1, col2 = st.columns(2)
        with col1:
            nuevo_estado = st.selectbox("Estado", ["activa", "desactiva"], index=0 if u.get('estado_cuenta')=="activa" else 1)
        with col2:
            fecha_v = u.get('fecha_vencimiento', str(datetime.now().date()))
            nueva_fecha = st.date_input("Vencimiento", value=datetime.strptime(fecha_v, '%Y-%m-%d'))
        
        if st.button("💾 GUARDAR CAMBIOS"):
            db_u[id_usuario]['estado_cuenta'] = nuevo_estado
            db_u[id_usuario]['fecha_vencimiento'] = str(nueva_fecha)
            guardar_json(db_u, ARCHIVO_USUARIOS)
            st.success("Actualizado.")
            st.rerun()

# --- LOGIN / REGISTRO ---
if not st.session_state.autenticado and st.session_state.modulo_activo != "PanelMaestro":
    st.title("🚀 Bienvenido al Universo X")
    t_login, t_reg = st.tabs(["🔐 INGRESAR", "📝 REGISTRARME"])

    with t_login:
        with st.form("f_login"):
            u_id = st.text_input("Celular")
            u_pw = st.text_input("Clave", type="password")
            if st.form_submit_button("ENTRAR"):
                db = cargar_json(ARCHIVO_USUARIOS)
                if u_id in db and str(db[u_id]["clave"]) == str(u_pw):
                    st.session_state.autenticado = True
                    st.session_state.user_id = u_id
                    st.rerun()
                else: st.error("Datos incorrectos.")

    with t_reg:
        with st.form("f_reg"):
            r_id = st.text_input("Número de Celular")
            r_nom = st.text_input("Nombre Completo")
            r_pw = st.text_input("Clave", type="password")
            if st.form_submit_button("CREAR CUENTA"):
                db = cargar_json(ARCHIVO_USUARIOS)
                if r_id in db: st.error("Ya registrado.")
                else:
                    db[r_id] = {
                        "nombre_completo": r_nom, "username": r_nom.split()[0],
                        "clave": r_pw, "estado_cuenta": "activa",
                        "fecha_vencimiento": str(datetime.now().date() + timedelta(days=15))
                    }
                    guardar_json(db, ARCHIVO_USUARIOS)
                    st.success("¡Listo! Ya puedes ingresar.")

    if st.text_input("🔑 Maestro", type="password") == "10538":
        if st.button("ABRIR PANEL"):
            st.session_state.modulo_activo = "PanelMaestro"; st.rerun()

# --- CONTENIDO AUTENTICADO ---
elif st.session_state.modulo_activo == "PanelMaestro":
    renderizar_panel_maestro()

elif st.session_state.autenticado:
    u_id = st.session_state.user_id
    user = cargar_json(ARCHIVO_USUARIOS).get(u_id, {})
    
    # Sidebar unificado
    st.sidebar.markdown(f"""
    <div style="background-color: #111; padding: 15px; border-radius: 10px; border-left: 5px solid #00e6e6;">
        <h2 style="margin: 0;">👤 {user.get('nombre_completo')}</h2>
        <p>⏳ Vence: {user.get('fecha_vencimiento')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False; st.rerun()

    if st.session_state.modulo_activo == "Lobby":
        st.title("🌌 Hub Central")
        
        # OPERACIONES
        st.markdown("<div class='card-title'>⚙️ OPERACIONES</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🚚 LOGÍSTICA"): st.session_state.modulo_activo = "1_Logistica.py"; st.rerun()
        with col2:
            if st.button("🚜 METEORO: MAQ Y TEC"): st.session_state.modulo_activo = "2_Maquinas.py"; st.rerun()
        with col3:
            if st.button("🍔 RESTAURANTE"): st.session_state.modulo_activo = "3_restaurante.py"; st.rerun()

        # SALUD Y SUMINISTROS (Aquí activamos Odontología)
        st.markdown("<div class='card-title'>📦 SALUD Y SUMINISTROS</div>", unsafe_allow_html=True)
        col4, col5, col6 = st.columns(3)
        with col4: st.button("🛒 ALACENA")
        with col5: st.button("🌱 AGRO-PRO")
        with col6:
            if st.button("🦷 ODONTOLOGÍA"): 
                st.session_state.modulo_activo = "odontologia_x.py"
                st.rerun()
    else:
        if st.sidebar.button("⬅️ VOLVER AL HUB"): 
            st.session_state.modulo_activo = "Lobby"; st.rerun()
        cargar_modulo(st.session_state.modulo_activo)