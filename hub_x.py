import streamlit as st
import json
import os
import importlib.util
from datetime import date

# --- CONFIGURACIÓN DEL UNIVERSO ---
st.set_page_config(page_title="Universo X - Sistema Central", layout="wide")

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

# --- ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'modulo_activo' not in st.session_state:
    st.session_state.modulo_activo = "Lobby"
if 'precios' not in st.session_state:
    st.session_state.precios = {"General": 10000, "Micro": 3000}

# --- ESTÉTICA DARK TOTAL ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    h1, h2, h3, p, label { color: #FFFFFF !important; }
    .stTextInput>div>div>input { background-color: #1A1A1A; color: white; border: 1px solid #333; }
    .lobby-card { background-color: #111; border: 1px solid #333; padding: 20px; border-radius: 10px; text-align: center; }
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
                st.session_state.datos_usuario = users[c_id]
                st.rerun()
            else:
                st.error("Credenciales no reconocidas.")

    with tab_reg:
        st.subheader("Nuevo Registro de Usuario")
        reg_cel = st.text_input("Número Celular (Este será tu ID)")
        reg_pais = st.selectbox("País", ["Colombia", "España", "Otro"])
        reg_nom = st.text_input("Nombre de Usuario")
        reg_nac = st.date_input("Fecha de Nacimiento", min_value=date(1940, 1, 1))
        reg_pw = st.text_input("Definir Código Secreto", type="password")
        reg_ind = st.text_input("Indicio de tu código (Pista)")

        if st.button("DAR DE ALTA EN X"):
            if reg_cel and reg_pw and reg_nom:
                usuarios = cargar_usuarios()
                if reg_cel in usuarios:
                    st.warning("Este ID ya existe.")
                else:
                    usuarios[reg_cel] = {
                        "nombre": reg_nom,
                        "pais": reg_pais,
                        "nacimiento": str(reg_nac),
                        "clave": reg_pw,
                        "indicio": reg_ind,
                        "saldo": 0.0,  # Campo solicitado
                        "rol": "Usuario"
                    }
                    guardar_usuarios(usuarios)
                    st.success("Cuenta creada. Ahora puedes ingresar.")
            else:
                st.error("Por favor completa los datos obligatorios.")

# --- PANEL DE CONTROL (POST-LOGIN) ---
else:
    u = st.session_state.datos_usuario
    
    if st.session_state.modulo_activo == "Lobby":
        st.title(f"🌌 Lobby - Bienvenido {u['nombre']}")
        st.sidebar.write(f"💰 Saldo: ${u['saldo']:,}")
        
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="lobby-card"><h3>🚚 Logística</h3></div>', unsafe_allow_html=True)
            if st.button("ENTRAR", key="btn_log"):
                st.session_state.modulo_activo = "1_Logistica.py"; st.rerun()
        
        with col2:
            st.markdown('<div class="lobby-card"><h3>🏦 F5CO</h3></div>', unsafe_allow_html=True)
            f5_pass = st.text_input("Llave F5CO", type="password")
            if st.button("ACCEDER"):
                if f5_pass == "10538":
                    st.session_state.modulo_activo = "F5CO"; st.rerun()

    elif st.session_state.modulo_activo == "F5CO":
        st.title("🏦 Panel F5CO - Tesorería")
        if st.button("⬅️ REGRESAR"):
            st.session_state.modulo_activo = "Lobby"; st.rerun()
        
        t1, t2 = st.tabs(["💰 CARGA DE SALDO", "⚙️ PRECIOS"])
        
        with t1:
            id_dest = st.text_input("ID de Usuario (Celular)")
            monto = st.number_input("Monto en Efectivo", min_value=0)
            if st.button("CONFIRMAR ABONO"):
                db = cargar_usuarios()
                if id_dest in db:
                    db[id_dest]["saldo"] += monto
                    guardar_usuarios(db)
                    st.success(f"Abono de ${monto} exitoso para {db[id_dest]['nombre']}")
                else:
                    st.error("Usuario no encontrado.")