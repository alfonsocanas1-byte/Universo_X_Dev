import streamlit as st
import json
import os
import importlib.util
import pandas as pd
from datetime import date, datetime, timedelta

# --- CONFIGURACIÓN DEL UNIVERSO ---
st.set_page_config(page_title="Universo X - Hub Central", layout="wide")

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

# --- ACCESO INICIAL ---
if not st.session_state.autenticado and st.session_state.modulo_activo not in ["F5CO", "X_Usuarios"]:
    st.title("🚀 Portal de Acceso - Universo X")
    
    col_acc1, col_acc2 = st.columns(2)
    with col_acc1:
        with st.expander("🔑 GESTIÓN DE IDENTIDAD (X Usuarios)"):
            llave_u = st.text_input("Llave Administrativa", type="password", key="k_u")
            if st.button("ENTRAR A USUARIOS"):
                if llave_u == "10538":
                    st.session_state.modulo_activo = "X_Usuarios"
                    st.rerun()
    
    with col_acc2:
        with st.expander("🏦 BANCO CENTRAL (F5CO)"):
            llave_f = st.text_input("Llave de Tesorería", type="password", key="k_f")
            if st.button("ENTRAR A FINANZAS"):
                if llave_f == "10538":
                    st.session_state.modulo_activo = "F5CO"
                    st.rerun()

    st.divider()
    st.subheader("Ingreso de Suscriptores")
    c_id = st.text_input("Número de Celular (ID)")
    c_pw = st.text_input("Código Secreto", type="password")
    if st.button("SINCRONIZAR"):
        db_u = cargar_json(ARCHIVO_USUARIOS)
        if c_id in db_u and db_u[c_id]["clave"] == c_pw:
            st.session_state.autenticado = True
            st.session_state.user_id = c_id
            st.rerun()
        else: st.error("Acceso denegado.")

# --- MÓDULO: X USUARIOS ---
elif st.session_state.modulo_activo == "X_Usuarios":
    st.title("👤 Gestión: X Usuarios")
    if st.button("⬅️ VOLVER AL PORTAL"): st.session_state.modulo_activo = "Lobby"; st.session_state.autenticado = False; st.rerun()
    db_u = cargar_json(ARCHIVO_USUARIOS)
    t_del, t_edit = st.tabs(["🗑️ ELIMINAR USUARIOS", "✏️ EDITAR PERFIL"])
    
    with t_del:
        if st.checkbox("Desplegar usuarios para eliminación"):
            for cel, info in db_u.items():
                c1, c2 = st.columns([0.8, 0.2])
                c1.write(f"**{info.get('nombre_completo')}** ({cel})")
                if c2.button("BORRAR", key=f"del_{cel}"):
                    del db_u[cel]
                    guardar_json(db_u, ARCHIVO_USUARIOS)
                    st.success("Identidad eliminada."); st.rerun()

    with t_edit:
        target = st.text_input("Digite celular para editar")
        if target in db_u:
            with st.form("edit_u"):
                u_dat = db_u[target]
                n_nom = st.text_input("Nombre", value=u_dat.get('nombre_completo'))
                n_usr = st.text_input("Username", value=u_dat.get('username'))
                if st.form_submit_button("ACTUALIZAR"):
                    db_u[target].update({"nombre_completo": n_nom, "username": n_usr})
                    guardar_json(db_u, ARCHIVO_USUARIOS); st.success("Guardado.")

# --- MÓDULO: F5CO ---
elif st.session_state.modulo_activo == "F5CO":
    st.title("🏦 Tesorería F5CO")
    if st.button("⬅️ VOLVER AL PORTAL"): st.session_state.modulo_activo = "Lobby"; st.session_state.autenticado = False; st.rerun()
    st.info("Sistema de saldos vinculado a f5co_cuentas.json")

# --- LOBBY CON MICROSERVICIOS SELECCIONADOS ---
else:
    db_u = cargar_json(ARCHIVO_USUARIOS)
    db_c = cargar_json(ARCHIVO_CUENTAS)
    u = db_u.get(st.session_state.user_id)
    # Si no existe la cuenta, simulamos saldo 0 para no romper el Lobby
    c = db_c.get(st.session_state.user_id, {"saldo": 0.0, "suscripciones": {}})

    st.sidebar.title(f"👤 {u.get('username', 'Usuario')}")
    st.sidebar.metric("Saldo Disponible", f"${c.get('saldo', 0.0):,}")
    if st.sidebar.button("Cerrar Sesión"): st.session_state.autenticado = False; st.rerun()

    st.title("🌌 Lobby Universo X")
    st.write("Servicios Profesionales Activos")
    
    col1, col2, col3 = st.columns(3)
    servs = [
        ("🚚 Logística", "1_Logistica.py", col1),
        ("🚜 Máquinas", "2_Maquinas.py", col2),
        ("🍔 Restaurante", "3_restaurante.py", col3)
    ]

    for nom, file, columna in servs:
        with columna:
            st.markdown(f'<div class="card"><h3>{nom}</h3></div>', unsafe_allow_html=True)
            costo = st.session_state.precios["Microservicio"]
            
            # Lógica de Acceso/Suscripción
            acceso = False
            if nom in c.get("suscripciones", {}):
                f_pago = datetime.strptime(c["suscripciones"][nom], "%Y-%m-%d")
                if datetime.now() < f_pago + timedelta(days=90): acceso = True

            if acceso:
                if st.button(f"ENTRAR A {nom.upper()}", key=f"go_{nom}"):
                    st.session_state.modulo_activo = file; st.rerun()
            else:
                if st.button(f"PAGAR 90 DÍAS (${costo:,})", key=f"pay_{nom}"):
                    if c["saldo"] >= costo:
                        # Descontar del archivo de cuentas
                        db_c.setdefault(st.session_state.user_id, {"saldo": 0.0, "suscripciones": {}, "movimientos": []})
                        db_c[st.session_state.user_id]["saldo"] -= costo
                        db_c[st.session_state.user_id]["suscripciones"][nom] = str(date.today())
                        guardar_json(db_c, ARCHIVO_CUENTAS)
                        st.success("Suscripción exitosa."); st.rerun()
                    else: st.error("Saldo insuficiente en F5CO.")

    # Pie de página o retorno de módulos
    if st.session_state.modulo_activo != "Lobby":
        if st.sidebar.button("⬅️ REGRESAR AL HUB"):
            st.session_state.modulo_activo = "Lobby"; st.rerun()
        cargar_modulo(st.session_state.modulo_activo)