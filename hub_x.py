import streamlit as st
import json
import os
import base64
import importlib.util
import pandas as pd
from datetime import date, datetime, timedelta

# --- CONFIGURACIÓN DEL UNIVERSO ---
st.set_page_config(page_title="Universo X - Sistema Central", layout="wide")

ARCHIVO_USUARIOS = "usuarios_x.json"
ARCHIVO_CUENTAS = "f5co_cuentas.json"

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

# --- FUNCIÓN VISUALIZADOR PDF (UBICADO EN RAÍZ) ---
def mostrar_pdf(nombre_archivo):
    # BUSCA DIRECTAMENTE EN LA RAÍZ DEL PROYECTO (Universo_X_Dev)
    ruta_pdf = os.path.join(os.getcwd(), nombre_archivo)
    
    if os.path.exists(ruta_pdf):
        with open(ruta_pdf, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else: 
        # MENSAJE DE ERROR PARA CONFIRMAR LA RUTA EN PANTALLA
        st.error(f"⚠️ El PDF no está en la raíz del proyecto. Buscado en: {ruta_pdf}")

# --- ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'modulo_activo' not in st.session_state: st.session_state.modulo_activo = "Lobby"

# --- ESTÉTICA DARK TOTAL ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: #FFFFFF; }
    label, p, span, div, .stMarkdown, .stSubheader, .stTitle, .stHeader { color: #FFFFFF !important; }
    /* Letras negras exclusivas para el Sidebar según solicitud */
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] div {
        color: #000000 !important;
    }
    .card { background: #111; border: 1px solid #333; padding: 20px; border-radius: 10px; text-align: center; }
    h1, h2, h3 { color: #00e6e6 !important; }
    input { background-color: #1A1A1A !important; color: #FFFFFF !important; border: 1px solid #444 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- PORTAL DE ACCESO ---
if not st.session_state.autenticado and st.session_state.modulo_activo not in ["F5CO", "X_Usuarios"]:
    st.title("🚀 Portal de Acceso - Universo X")
    col_a, col_b = st.columns(2)
    with col_a:
        with st.expander("🔑 GESTIÓN DE IDENTIDAD (X Usuarios)"):
            if st.text_input("Llave Administrativa", type="password", key="ka_u") == "10538":
                if st.button("ENTRAR A USUARIOS"): st.session_state.modulo_activo = "X_Usuarios"; st.rerun()
    with col_b:
        with st.expander("🏦 BANCO CENTRAL (F5CO)"):
            if st.text_input("Llave de Tesorería", type="password", key="ka_f") == "10538":
                if st.button("ENTRAR A FINANZAS"): st.session_state.modulo_activo = "F5CO"; st.rerun()
    st.divider()
    c_id = st.text_input("Número de Celular (ID)")
    c_pw = st.text_input("Código Secreto", type="password")
    if st.button("SINCRONIZAR"):
        db_u = cargar_json(ARCHIVO_USUARIOS)
        if c_id in db_u and db_u[c_id]["clave"] == c_pw:
            st.session_state.autenticado, st.session_state.user_id = True, c_id
            st.rerun()
        else: st.error("Acceso denegado.")

# --- MÓDULO X USUARIOS (EDITOR MAESTRO) ---
elif st.session_state.modulo_activo == "X_Usuarios":
    st.title("👤 Editor Maestro de usuarios_x.json")
    if st.button("⬅️ VOLVER AL PORTAL"): 
        st.session_state.modulo_activo = "Lobby"
        st.session_state.autenticado = False
        st.rerun()
    
    db_u = cargar_json(ARCHIVO_USUARIOS)
    t1, t2 = st.tabs(["🗑️ ELIMINAR IDENTIDADES", "✏️ GESTIÓN DE USUARIOS (EDITAR)"])
    
    with t1:
        if st.checkbox("Desplegar usuarios para eliminación"):
            for cel, info in db_u.items():
                c1, c2 = st.columns([0.8, 0.2])
                c1.write(f"**{info.get('nombre_completo')}** ({cel})")
                if c2.button("BORRAR", key=f"d_{cel}"):
                    del db_u[cel]
                    guardar_json(db_u, ARCHIVO_USUARIOS); st.rerun()

    with t2:
        target = st.selectbox("Seleccione el usuario a editar", options=list(db_u.keys()))
        if target:
            u_d = db_u[target]
            st.info(f"Editando ID: {target} | Cuenta: {u_d.get('cuenta_f5co', 'None')}")
            with st.form("ed_maestro"):
                col1, col2 = st.columns(2)
                n_nom = col1.text_input("Nombre Completo", value=u_d.get('nombre_completo'))
                n_usr = col2.text_input("Username", value=u_d.get('username'))
                n_pw = col1.text_input("Clave Secreta", value=u_d.get('clave'))
                n_saldo = col2.number_input("Saldo Manual", value=float(u_d.get('saldo', 0.0)))
                n_ind = col1.text_input("Indicio Clave", value=u_d.get('indicio'))
                n_res = col2.text_input("Respuesta Secreta", value=u_d.get('respuesta_secreta'))
                if st.form_submit_button("💾 GUARDAR"):
                    db_u[target].update({"nombre_completo": n_nom, "username": n_usr, "clave": n_pw, "saldo": n_saldo, "indicio": n_ind, "respuesta_secreta": n_res})
                    guardar_json(db_u, ARCHIVO_USUARIOS); st.success("Cambios aplicados."); st.rerun()

# --- MÓDULO F5CO ---
elif st.session_state.modulo_activo == "F5CO":
    st.title("🏦 Tesorería F5CO")
    if st.button("⬅️ VOLVER"): st.session_state.modulo_activo = "Lobby"; st.session_state.autenticado = False; st.rerun()
    st.info("Bóveda financiera vinculada a f5co_cuentas.json")

# --- LOBBY Y CONOCIMIENTO ---
else:
    db_u = cargar_json(ARCHIVO_USUARIOS)
    db_c = cargar_json(ARCHIVO_CUENTAS)
    u = db_u.get(st.session_state.user_id, {})
    c = db_c.get(st.session_state.user_id, {"saldo": 0.0, "suscripciones": {}})

    st.sidebar.title(f"👤 {u.get('username', 'Usuario')}")
    st.sidebar.metric("Saldo Disponible", f"${c.get('saldo', 0.0):,}")
    if st.sidebar.button("Cerrar Sesión"): st.session_state.autenticado = False; st.rerun()

    if st.session_state.modulo_activo == "Lobby":
        st.title("🌌 Lobby Universo X")
        c1, c2, c3 = st.columns(3)
        servs = [("🚚 Logística", "1_Logistica.py", c1), ("🚜 Máquinas", "2_Maquinas.py", c2), ("🍔 Restaurante", "3_restaurante.py", c3)]
        for n, f, col in servs:
            with col:
                st.markdown(f'<div class="card"><h3>{n}</h3></div>', unsafe_allow_html=True)
                acc = False
                if n in c.get("suscripciones", {}):
                    if datetime.now() < datetime.strptime(c["suscripciones"][n], "%Y-%m-%d") + timedelta(days=90): acc = True
                if acc:
                    if st.button(f"ENTRAR", key=f"g_{n}"): st.session_state.modulo_activo = f; st.rerun()
                else:
                    if st.button(f"PAGAR (90 DÍAS)", key=f"p_{n}"):
                        if c["saldo"] >= 3000:
                            db_c.setdefault(st.session_state.user_id, {"saldo": 0.0, "suscripciones": {}})
                            db_c[st.session_state.user_id]["saldo"] -= 3000
                            db_c[st.session_state.user_id]["suscripciones"][n] = str(date.today())
                            guardar_json(db_c, ARCHIVO_CUENTAS); st.rerun()
                        else: st.error("Saldo insuficiente.")

        st.divider()
        st.header("📚 CONOCIMIENTO TÉCNICO")
        col_p, col_i = st.columns([0.7, 0.3])
        with col_i:
            st.info("📖 Manual de Aceite Hidráulico")
            if st.button("🔓 ABRIR PDF"): st.session_state.ver_pdf = True
        with col_p:
            if st.session_state.get('ver_pdf'):
                mostrar_pdf("aceite_hidraulico.pdf")
    else:
        if st.sidebar.button("⬅️ REGRESAR AL HUB"): st.session_state.modulo_activo = "Lobby"; st.rerun()
        cargar_modulo(st.session_state.modulo_activo)