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
            try:
                return json.load(f)
            except:
                return {}
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
if 'precios' not in st.session_state:
    st.session_state.precios = {"General": 10000, "Micro": 3000}

# --- ESTÉTICA DARK TOTAL ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2, h3, p, label { color: #FFFFFF !important; }
    .lobby-card {
        background-color: #111;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ACCESO Y REGISTRO ---
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
                st.error("Credenciales incorrectas.")

    with tab_reg:
        st.subheader("Registro de Nuevo Usuario")
        r_cel = st.text_input("Número Celular (ID)")
        r_pais = st.selectbox("País", ["Colombia", "España", "Otro"])
        r_nom = st.text_input("Nombre de Usuario")
        r_nac = st.date_input("Fecha de Nacimiento", min_value=date(1940, 1, 1), value=date(2000, 1, 1))
        r_pw = st.text_input("Código Secreto (Password)", type="password")
        r_ind = st.text_input("Indicio de clave (Pista)")

        if st.button("REGISTRAR EN X"):
            if r_cel and r_pw and r_nom:
                db = cargar_usuarios()
                if r_cel in db:
                    st.warning("Este celular ya está registrado.")
                else:
                    db[r_cel] = {
                        "nombre": r_nom,
                        "pais": r_pais,
                        "nacimiento": str(r_nac),
                        "clave": r_pw,
                        "indicio": r_ind,
                        "saldo": 0.0
                    }
                    guardar_usuarios(db)
                    st.success("¡Usuario creado con éxito! Ya puedes ingresar.")
            else:
                st.error("Completa los campos obligatorios.")

# --- PANEL DE CONTROL (LOBBY Y MÓDULOS) ---
else:
    # Actualizar datos del usuario desde el archivo en cada carga para ver el saldo real
    db_actual = cargar_usuarios()
    u = db_actual.get(st.session_state.user_id, st.session_state.datos_usuario)
    
    # Sidebar de Navegación
    st.sidebar.title(f"👤 {u['nombre']}")
    st.sidebar.write(f"📍 {u['pais']}")
    st.sidebar.write(f"💰 Saldo: ${u['saldo']:,}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.modulo_activo = "Lobby"
        st.rerun()

    if st.session_state.modulo_activo == "Lobby":
        st.title("🌌 Centro de Mandos - Lobby")
        st.divider()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown('<div class="lobby-card"><h3>🚚 LOGÍSTICA</h3></div>', unsafe_allow_html=True)
            if st.button("ENTRAR", key="log"):
                st.session_state.modulo_activo = "1_Logistica.py"; st.rerun()

        with col2:
            st.markdown('<div class="lobby-card"><h3>🚜 MÁQUINAS</h3></div>', unsafe_allow_html=True)
            if st.button("ENTRAR", key="maq"):
                st.session_state.modulo_activo = "2_Maquinas.py"; st.rerun()

        with col3:
            st.markdown('<div class="lobby-card"><h3>🐍 CACD</h3></div>', unsafe_allow_html=True)
            if st.button("ENTRAR", key="cacd"):
                st.session_state.modulo_activo = "x_cacd.py"; st.rerun()

        with col4:
            st.markdown('<div style="background-color: #001f1f; border: 1px solid #00e6e6; padding: 20px; border-radius: 10px; text-align: center;"><h3>🏦 F5CO</h3></div>', unsafe_allow_html=True)
            f5_llave = st.text_input("Llave F5CO", type="password")
            if st.button("GESTIONAR"):
                if f5_llave == "10538":
                    st.session_state.modulo_activo = "F5CO"; st.rerun()
                else:
                    st.error("Llave incorrecta.")

    elif st.session_state.modulo_activo == "F5CO":
        st.title("🏦 Panel Bancario F5CO")
        if st.button("⬅️ VOLVER AL LOBBY"):
            st.session_state.modulo_activo = "Lobby"; st.rerun()
        
        tab_carga, tab_precios = st.tabs(["💰 CARGA DE SALDO", "⚙️ CONFIGURACIÓN"])
        
        with tab_carga:
            target_id = st.text_input("ID Celular del Usuario")
            monto_efectivo = st.number_input("Monto Recibido ($)", min_value=0, step=1000)
            if st.button("APLICAR CARGA"):
                db = cargar_usuarios()
                if target_id in db:
                    db[target_id]["saldo"] += monto_efectivo
                    guardar_usuarios(db)
                    st.success(f"Carga exitosa. Nuevo saldo de {db[target_id]['nombre']}: ${db[target_id]['saldo']:,}")
                else:
                    st.error("Usuario no encontrado.")

        with tab_precios:
            st.subheader("Precios de Suscripción")
            st.session_state.precios["General"] = st.number_input("Suscripción General (Trimestral)", value=st.session_state.precios["General"])
            st.session_state.precios["Micro"] = st.number_input("Suscripción Microservicio (Trimestral)", value=st.session_state.precios["Micro"])
            st.info(f"Precios actuales guardados en la sesión.")

    else:
        # Carga de módulos externos
        if st.sidebar.button("⬅️ REGRESAR AL LOBBY"):
            st.session_state.modulo_activo = "Lobby"; st.rerun()
        cargar_modulo(st.session_state.modulo_activo)