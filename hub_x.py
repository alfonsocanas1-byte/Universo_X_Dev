import streamlit as st
import json
import os
import importlib.util
from datetime import date, datetime

# --- CONFIGURACIÓN DEL UNIVERSO ---
st.set_page_config(page_title="Universo X - Central", layout="wide")

# Archivo de Base de Datos
ARCHIVO_USUARIOS = "usuarios_x.json"

# --- FUNCIONES DE PERSISTENCIA ---
def cargar_usuarios():
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return {}
    return {}

def guardar_usuarios(usuarios):
    with open(ARCHIVO_USUARIOS, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)

def cargar_modulo(nombre_archivo):
    ruta_completa = os.path.join(os.getcwd(), nombre_archivo)
    if os.path.exists(ruta_completa):
        spec = importlib.util.spec_from_file_location("modulo_dinamico", ruta_completa)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
    else:
        st.error(f"⚠️ El archivo '{nombre_archivo}' no se encuentra.")

# --- ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'modulo_activo' not in st.session_state:
    st.session_state.modulo_activo = "Lobby"

# --- ESTÉTICA DARK TOTAL ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2, h3, p, label { color: #FFFFFF !important; }
    .lobby-card { background-color: #111; border: 1px solid #333; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ACCESO ---
if not st.session_state.autenticado:
    st.title("🚀 Acceso al Universo X")
    tab_in, tab_reg = st.tabs(["INGRESAR", "CREAR CUENTA"])

    with tab_in:
        c_id = st.text_input("Número de Celular (ID)")
        c_pw = st.text_input("Código Secreto", type="password")
        if st.button("SINCRONIZAR"):
            users = cargar_usuarios()
            if c_id in users and users[c_id]["clave"] == c_pw:
                st.session_state.autenticado = True
                st.session_state.user_id = c_id
                st.rerun()
            else: st.error("Credenciales incorrectas.")

    with tab_reg:
        st.subheader("Registro de Nuevo Usuario")
        r_cel = st.text_input("Número Celular (ID)")
        r_pais = st.selectbox("País", ["Colombia", "España", "Otro"])
        r_nom = st.text_input("Nombre de Usuario")
        r_nac = st.date_input("Fecha de Nacimiento", value=date(2000, 1, 1))
        r_pw = st.text_input("Código Secreto", type="password")
        r_ind = st.text_input("Indicio de clave (Pista)")
        if st.button("REGISTRAR EN X"):
            db = cargar_usuarios()
            db[r_cel] = {
                "nombre": r_nom, "pais": r_pais, "nacimiento": str(r_nac),
                "clave": r_pw, "indicio": r_ind, "saldo": 0.0, "movimientos": []
            }
            guardar_usuarios(db)
            st.success("Usuario creado con éxito.")

# --- PANEL DE CONTROL ---
else:
    db = cargar_usuarios()
    u = db.get(st.session_state.user_id)
    
    st.sidebar.title(f"👤 {u['nombre']}")
    st.sidebar.write(f"💰 Saldo: ${u['saldo']:,}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False; st.rerun()

    if st.session_state.modulo_activo == "Lobby":
        st.title("🌌 Centro de Mandos - Lobby")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown('<div class="lobby-card"><h3>🚚 LOGÍSTICA</h3></div>', unsafe_allow_html=True)
            if st.button("ENTRAR", key="log"): st.session_state.modulo_activo = "1_Logistica.py"; st.rerun()
        with col2:
            st.markdown('<div class="lobby-card"><h3>🚜 MÁQUINAS</h3></div>', unsafe_allow_html=True)
            if st.button("ENTRAR", key="maq"): st.session_state.modulo_activo = "2_Maquinas.py"; st.rerun()
        with col3:
            st.markdown('<div class="lobby-card"><h3>🍔 RESTAURANTE</h3></div>', unsafe_allow_html=True)
            if st.button("ENTRAR", key="res"): st.session_state.modulo_activo = "3_restaurante.py"; st.rerun()
        with col4:
            st.markdown('<div style="background-color: #001f1f; border: 1px solid #00e6e6; padding: 20px; border-radius: 10px; text-align: center;"><h3>🏦 F5CO</h3></div>', unsafe_allow_html=True)
            if st.text_input("Llave F5CO", type="password") == "10538":
                if st.button("GESTIONAR"): st.session_state.modulo_activo = "F5CO"; st.rerun()

    elif st.session_state.modulo_activo == "F5CO":
        st.title("🏦 Panel Bancario F5CO")
        if st.button("⬅️ VOLVER"): st.session_state.modulo_activo = "Lobby"; st.rerun()
        
        t1, t2, t3 = st.tabs(["💰 CARGAR SALDO", "📊 CONSULTAR ESTADO", "👤 DATOS PERSONALES"])
        
        with t1: # 1. Cargar saldo solo con celular y monto
            target_id = st.text_input("Celular del Beneficiario")
            monto = st.number_input("Monto a Cargar ($)", min_value=0)
            if st.button("EJECUTAR TRANSACCIÓN"):
                if target_id in db:
                    db[target_id]["saldo"] += monto
                    db[target_id].setdefault("movimientos", []).append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Carga: +${monto:,}")
                    guardar_usuarios(db); st.success("Carga exitosa.")
                else: st.error("Usuario no existe.")

        with t2: # 2. Consultar saldo y movimientos
            search_id = st.text_input("Celular para Consultar Movimientos")
            if st.button("VER ESTADO DE CUENTA"):
                if search_id in db:
                    st.metric("Saldo Actual", f"${db[search_id]['saldo']:,}")
                    st.write("Últimos Movimientos:")
                    for mov in reversed(db[search_id].get("movimientos", [])): st.text(mov)
                else: st.error("Usuario no encontrado.")

        with t3: # 3. Consultar y Modificar Datos Personales
            edit_id = st.text_input("Celular para Gestión de Perfil")
            if edit_id in db:
                user_data = db[edit_id]
                new_nom = st.text_input("Nombre", value=user_data['nombre'])
                new_pais = st.selectbox("País", ["Colombia", "España", "Otro"], index=["Colombia", "España", "Otro"].index(user_data['pais']))
                new_ind = st.text_input("Indicio de Clave", value=user_data['indicio'])
                if st.button("ACTUALIZAR DATOS"):
                    db[edit_id].update({"nombre": new_nom, "pais": new_pais, "indicio": new_ind})
                    guardar_usuarios(db); st.success("Perfil actualizado.")
            elif edit_id: st.warning("ID no registrado.")
    else:
        if st.sidebar.button("⬅️ REGRESAR AL LOBBY"): st.session_state.modulo_activo = "Lobby"; st.rerun()
        cargar_modulo(st.session_state.modulo_activo)