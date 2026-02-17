import streamlit as st
import os
import importlib.util
import pandas as pd

# --- CONFIGURACIÓN DEL UNIVERSO ---
st.set_page_config(page_title="Universo X - Lobby", layout="wide")

# --- ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'modulo_activo' not in st.session_state:
    st.session_state.modulo_activo = "Lobby"
if 'f5co_desbloqueado' not in st.session_state:
    st.session_state.f5co_desbloqueado = False

# Simulación de Precios (Mientras implementamos DB)
if 'precios' not in st.session_state:
    st.session_state.precios = {
        "Suscripción General": 10000,
        "Microservicio": 3000
    }

# --- FUNCIÓN DE CARGA SEGURA ---
def cargar_modulo(nombre_archivo):
    ruta_completa = os.path.join(os.getcwd(), nombre_archivo)
    if os.path.exists(ruta_completa):
        spec = importlib.util.spec_from_file_location("modulo_dinamico", ruta_completa)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
    else:
        st.error(f"⚠️ El archivo '{nombre_archivo}' no se encuentra en la raíz.")

# --- ESTÉTICA DARK TOTAL ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2, h3, h4, p, label { color: #FFFFFF !important; }
    .lobby-card {
        background-color: #1A1A1A; border: 1px solid #333;
        padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 10px;
    }
    .f5co-card {
        background-color: #001f1f; border: 1px solid #00e6e6;
        padding: 20px; border-radius: 10px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
if st.session_state.modulo_activo == "Lobby":
    st.title("🌌 Welcome to the Hub - Universo X")
    st.write(f"Precios Actuales: Gral ${st.session_state.precios['Suscripción General']} | Micro ${st.session_state.precios['Microservicio']} (Trimestral)")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="lobby-card"><h3>🚚 LOGÍSTICA</h3><p>Gestión de pedidos.</p></div>', unsafe_allow_html=True)
        if st.button("ENTRAR A LOGÍSTICA"):
            st.session_state.modulo_activo = "1_Logistica.py"; st.rerun()

    with col2:
        st.markdown('<div class="lobby-card"><h3>🚜 MÁQUINAS</h3><p>Control de flota.</p></div>', unsafe_allow_html=True)
        if st.button("ENTRAR A MÁQUINAS"):
            st.session_state.modulo_activo = "2_Maquinas.py"; st.rerun()

    with col3:
        st.markdown('<div class="f5co-card"><h3>🏦 F5CO</h3><p>Tesorería y Créditos.</p></div>', unsafe_allow_html=True)
        llave_f5co = st.text_input("Llave Maestra F5CO", type="password", key="llave_f5")
        if st.button("ACCEDER A FINANZAS"):
            if llave_f5co == "10538":
                st.session_state.modulo_activo = "F5CO"
                st.rerun()
            else:
                st.error("Llave incorrecta")

    with col4:
        st.markdown('<div class="lobby-card"><h3>🐍 CACD</h3><p>Reporte médico.</p></div>', unsafe_allow_html=True)
        if st.button("ENTRAR A CACD"):
            st.session_state.modulo_activo = "x_cacd.py"; st.rerun()

elif st.session_state.modulo_activo == "F5CO":
    st.title("🏦 Panel Bancario F5CO")
    if st.button("⬅️ VOLVER AL LOBBY"):
        st.session_state.modulo_activo = "Lobby"; st.rerun()
    
    tab1, tab2 = st.tabs(["💰 CARGA DE SALDOS", "⚙️ CONFIGURACIÓN DE PRECIOS"])

    with tab1:
        st.subheader("Maestro de Cargas (Dinero Virtual)")
        col_c1, col_c2 = st.columns(2)
        id_usuario = col_c1.text_input("ID del Usuario / Suscriptor")
        monto = col_c2.number_input("Monto Recibido (Efectivo)", min_value=0, step=1000)
        
        if st.button("💎 CONFIRMAR CARGA DE SALDO"):
            st.success(f"Se han abonado ${monto:,} al ID {id_usuario}. El usuario ya puede descontar de su plataforma.")

    with tab2:
        st.subheader("Ajuste de Tarifas Trimestrales")
        p_gral = st.number_input("Suscripción X General", value=st.session_state.precios["Suscripción General"])
        p_micro = st.number_input("Suscripción por Microservicio", value=st.session_state.precios["Microservicio"])
        
        if st.button("💾 ACTUALIZAR PRECIOS EN EL HUB"):
            st.session_state.precios["Suscripción General"] = p_gral
            st.session_state.precios["Microservicio"] = p_micro
            st.success("Precios actualizados para todo el sistema.")

else:
    # Carga de módulos externos (Logística, Máquinas, CACD)
    if st.sidebar.button("⬅️ REGRESAR AL HUB"):
        st.session_state.modulo_activo = "Lobby"; st.rerun()
    cargar_modulo(st.session_state.modulo_activo)