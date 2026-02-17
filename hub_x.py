import streamlit as st
import json
import os
import importlib.util
import random
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

# --- ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'modulo_activo' not in st.session_state: st.session_state.modulo_activo = "Lobby"
if 'precios' not in st.session_state: st.session_state.precios = {"Microservicio": 3000}

# --- ESTÉTICA DARK TOTAL ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: white; }
    .card { background: #111; border: 1px solid #333; padding: 20px; border-radius: 10px; text-align: center; }
    h1, h2, h3 { color: #00e6e6 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ACCESO ---
if not st.session_state.autenticado and st.session_state.modulo_activo not in ["F5CO", "X_Usuarios"]:
    st.title("🚀 Portal de Acceso - Universo X")
    
    col_acc1, col_acc2 = st.columns(2)
    with col_acc1:
        with st.expander("🔑 ACCESO ADMINISTRATIVO"):
            llave = st.text_input("Llave Maestra", type="password")
            if st.button("ENTRAR A GESTIÓN"):
                if llave == "10538":
                    st.session_state.modulo_activo = "X_Usuarios"
                    st.rerun()
    
    with col_acc2:
        with st.expander("🏦 ACCESO TESORERÍA F5CO"):
            llave_f5 = st.text_input("Llave F5CO", type="password")
            if st.button("ENTRAR A F5CO"):
                if llave_f5 == "10538":
                    st.session_state.modulo_activo = "F5CO"
                    st.rerun()

    # Login de Usuario Normal
    st.divider()
    c_id = st.text_input("Número de Celular (ID)")
    c_pw = st.text_input("Código Secreto", type="password")
    if st.button("SINCRONIZAR"):
        db_u = cargar_json(ARCHIVO_USUARIOS)
        if c_id in db_u and db_u[c_id]["clave"] == c_pw:
            st.session_state.autenticado = True
            st.session_state.user_id = c_id
            st.rerun()
        else: st.error("Acceso denegado.")

# --- MÓDULO: X USUARIOS (GESTIÓN DE IDENTIDAD) ---
elif st.session_state.modulo_activo == "X_Usuarios":
    st.title("👤 Microservicio: X Usuarios")
    if st.button("⬅️ VOLVER"): st.session_state.modulo_activo = "Lobby"; st.rerun()

    db_u = cargar_json(ARCHIVO_USUARIOS)
    t_del, t_edit = st.tabs(["🗑️ DESPLEGAR Y ELIMINAR", "✏️ EDICIÓN POR CELULAR"])

    with t_del:
        st.subheader("Listado Global de Identidades")
        if st.checkbox("Mostrar todos los usuarios"):
            for cel, info in db_u.items():
                c1, c2 = st.columns([0.8, 0.2])
                c1.write(f"**{info.get('nombre_completo')}** ({cel}) - {info.get('username')}")
                if c2.button("ELIMINAR", key=f"del_{cel}"):
                    del db_u[cel]
                    guardar_json(db_u, ARCHIVO_USUARIOS)
                    st.success(f"Usuario {cel} eliminado de Identidades. (Cuenta F5CO preservada)")
                    st.rerun()

    with t_edit:
        st.subheader("Buscador de Perfil")
        target = st.text_input("Digite celular exacto para editar")
        if target in db_u:
            with st.form("edit_perfil"):
                u = db_u[target]
                n_nom = st.text_input("Nombre Completo", value=u.get('nombre_completo'))
                n_usr = st.text_input("Username", value=u.get('username'))
                n_pais = st.text_input("País", value=u.get('pais', 'Colombia'))
                n_pw = st.text_input("Clave", value=u.get('clave'))
                n_ind = st.text_input("Indicio", value=u.get('indicio'))
                n_res = st.text_input("Respuesta Secreta", value=u.get('respuesta_secreta'))
                if st.form_submit_button("GUARDAR CAMBIOS"):
                    db_u[target].update({
                        "nombre_completo": n_nom, "username": n_usr, "pais": n_pais,
                        "clave": n_pw, "indicio": n_ind, "respuesta_secreta": n_res
                    })
                    guardar_json(db_u, ARCHIVO_USUARIOS)
                    st.success("Información personal actualizada.")
        elif target: st.warning("Usuario no encontrado en la base de datos personal.")

# --- MÓDULO: F5CO (TESORERÍA) ---
elif st.session_state.modulo_activo == "F5CO":
    st.title("🏦 Panel F5CO - Finanzas")
    if st.button("⬅️ VOLVER"): st.session_state.modulo_activo = "Lobby"; st.rerun()
    
    db_c = cargar_json(ARCHIVO_CUENTAS)
    # Aquí iría tu lógica de abonos y saldos (usando db_c)
    st.info("Gestión financiera activa vinculada a f5co_cuentas.json")

# --- LOBBY PRINCIPAL ---
else:
    db_u = cargar_json(ARCHIVO_USUARIOS)
    db_c = cargar_json(ARCHIVO_CUENTAS)
    u = db_u.get(st.session_state.user_id)
    c = db_c.get(st.session_state.user_id, {"saldo": 0.0})

    st.sidebar.title(f"👤 {u['username']}")
    st.sidebar.metric("Saldo F5CO", f"${c['saldo']:,}")
    if st.sidebar.button("Salir"): st.session_state.autenticado = False; st.rerun()

    st.title("🌌 Lobby Universo X")
    cols = st.columns(4)
    # Lista de servicios...