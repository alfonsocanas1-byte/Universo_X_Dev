import streamlit as st
import json
import os
import importlib.util
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DEL SISTEMA ---
st.set_page_config(page_title="Universo X - Sistema Central", layout="wide")

ARCHIVO_USUARIOS = "usuarios_x.json"

# --- FUNCIONES DE PERSISTENCIA SEGURA ---
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
            fecha_v = u.get('fecha_vencimiento', '2026-03-06')
            nueva_fecha = st.date_input("Vencimiento", value=datetime.strptime(fecha_v, '%Y-%m-%d'))
        
        if st.button("💾 GUARDAR CAMBIOS DEFINITIVOS"):
            db_actualizada = cargar_json(ARCHIVO_USUARIOS)
            db_actualizada[id_usuario]['estado_cuenta'] = nuevo_estado
            db_actualizada[id_usuario]['fecha_vencimiento'] = str(nueva_fecha)
            guardar_json(db_actualizada, ARCHIVO_USUARIOS)
            st.success("✅ Datos guardados.")
            st.rerun()

# --- LÓGICA DE INTERFAZ ---
if not st.session_state.autenticado and st.session_state.modulo_activo != "PanelMaestro":
    st.title("🚀 Bienvenido al Universo X")
    tab_log, tab_reg = st.tabs(["🔐 INGRESAR", "📝 REGISTRARME"])

    with tab_log:
        with st.form("form_login"):
            u_id = st.text_input("Número de Celular")
            u_pw = st.text_input("Clave", type="password")
            if st.form_submit_button("SINCRONIZAR"):
                db_u = cargar_json(ARCHIVO_USUARIOS)
                if u_id in db_u and str(db_u[u_id]["clave"]) == str(u_pw):
                    st.session_state.autenticado = True
                    st.session_state.user_id = u_id
                    st.rerun()
                else: st.error("Datos incorrectos.")

    with tab_reg:
        with st.form("form_registro"):
            r_id = st.text_input("Número de Celular (ID)")
            r_user = st.text_input("Nombre de Usuario")
            r_pw = st.text_input("Clave", type="password")
            # AQUÍ ESTABA EL ERROR: El botón ahora está dentro del 'with st.form'
            if st.form_submit_button("CREAR MI CUENTA"):
                db_u = cargar_json(ARCHIVO_USUARIOS)
                r_id = str(r_id).strip()
                if r_id in db_u: st.error("Este número ya existe.")
                elif r_id and r_pw:
                    hoy = datetime.now().date()
                    db_u[r_id] = {
                        "username": r_user,
                        "clave": str(r_pw),
                        "estado_cuenta": "activa",
                        "fecha_vencimiento": str(hoy + timedelta(days=15))
                    }
                    guardar_json(db_u, ARCHIVO_USUARIOS)
                    st.success("✅ Registro guardado. Ya puede ingresar.")
                else: st.warning("Complete los campos.")

    if st.text_input("🔑 Acceso Maestro", type="password") == "10538":
        if st.button("ABRIR PANEL"):
            st.session_state.modulo_activo = "PanelMaestro"
            st.rerun()

elif st.session_state.modulo_activo == "PanelMaestro":
    renderizar_panel_maestro()

elif st.session_state.autenticado:
    u_id = st.session_state.user_id
    user = cargar_json(ARCHIVO_USUARIOS).get(u_id, {})
    
    st.sidebar.title(f"👤 {user.get('username')}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    if st.session_state.modulo_activo == "Lobby":
        st.title("🌌 Hub Central")
        c1, c2, c3, c4 = st.columns(4)
        with c1: 
            if st.button("🚚 LOGÍSTICA"): st.session_state.modulo_activo = "1_Logistica.py"; st.rerun()
        with c2: 
            if st.button("🚜 MÁQUINAS"): st.session_state.modulo_activo = "2_Maquinas.py"; st.rerun()
        with c3: 
            if st.button("🐍 CACD"): st.session_state.modulo_activo = "x_cacd.py"; st.rerun()
        with c4:
            if st.button("🍔 RESTAURANTE"): st.info("Cargando...")
    else:
        if st.sidebar.button("⬅️ VOLVER AL HUB"): 
            st.session_state.modulo_activo = "Lobby"
            st.rerun()
        cargar_modulo(st.session_state.modulo_activo)