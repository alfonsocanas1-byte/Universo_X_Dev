import streamlit as st
import json
import os
import base64
import importlib.util
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DEL SISTEMA ---
st.set_page_config(page_title="Universo X - Sistema Central", layout="wide")

ARCHIVO_USUARIOS = "usuarios_x.json"
ARCHIVO_CUENTAS = "cuentasx_f5co.json"  # Vinculación con el nuevo sistema F5CO
ARCHIVO_PREREGISTRO = "preregistro_descargables.json"

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

# --- ESTÉTICA DARK PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: #FFFFFF; }
    h1, h2, h3, p, label { color: #00e6e6 !important; }
    .stButton>button {
        color: #000 !important;
        background-color: #FFFFFF !important;
        border: 2px solid #00e6e6 !important;
        font-weight: bold !important;
        width: 100%;
    }
    .stButton>button:hover { background-color: #00e6e6 !important; color: #000 !important; }
    .card { background: #111; border: 1px solid #333; padding: 20px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ACCESO Y REGISTRO F5CO ---
if not st.session_state.autenticado and st.session_state.modulo_activo not in ["Panel_Maestro", "F5CO_Publico"]:
    st.title("🚀 Portal de Acceso - Universo X")
    
    col_login, col_master = st.columns([2, 1])
    
    with col_login:
        with st.form("login_x"):
            st.subheader("Sincronización de Usuario")
            u_id = st.text_input("Número de Celular")
            u_pw = st.text_input("Clave de Acceso", type="password")
            
            if st.form_submit_button("SINCRONIZAR"):
                db_u = cargar_json(ARCHIVO_USUARIOS)
                if u_id in db_u and db_u[u_id]["clave"] == u_pw:
                    # Al loguear, verificamos si existe en F5CO, si no, lo creamos
                    db_c = cargar_json(ARCHIVO_CUENTAS)
                    if u_id not in db_c:
                        db_c[u_id] = {
                            "identidad": db_u[u_id]["username"],
                            "verificacion": {"metodo": "WhatsApp", "estado": "Pendiente", "fecha": str(datetime.now().date())},
                            "servicios_f5co": {
                                "microservicios": {"activo": False},
                                "plataforma_descargables": {"activo": False},
                                "galeria_arte": {"activo": False}
                            }
                        }
                        guardar_json(db_c, ARCHIVO_CUENTAS)
                    
                    st.session_state.autenticado = True
                    st.session_state.user_id = u_id
                    st.rerun()
                else:
                    st.error("Datos incorrectos.")

    with col_master:
        st.subheader("Acceso Maestro")
        llave = st.text_input("Llave Administrativa", type="password")
        if st.button("CONFIGURAR SISTEMA"):
            if llave == "10538":
                st.session_state.modulo_activo = "Panel_Maestro"
                st.rerun()

# --- PANEL MAESTRO (GESTIÓN DE MICROSERVICIOS) ---
elif st.session_state.modulo_activo == "Panel_Maestro":
    st.title("🛠️ Panel Maestro de Servicios")
    if st.button("⬅️ VOLVER AL HUB"): st.session_state.modulo_activo = "Lobby"; st.rerun()
    
    db_c = cargar_json(ARCHIVO_CUENTAS)
    for cid, info in db_c.items():
        with st.expander(f"👤 Usuario: {info['identidad']} ({cid})"):
            c1, c2, c3 = st.columns(3)
            # Modificación de estados en tiempo real
            ms = c1.checkbox("Microservicios", value=info['servicios_f5co']['microservicios']['activo'], key=f"ms_{cid}")
            pd = c2.checkbox("Descargables", value=info['servicios_f5co']['plataforma_descargables']['activo'], key=f"pd_{cid}")
            ga = c3.checkbox("Galería Arte", value=info['servicios_f5co']['galeria_arte']['activo'], key=f"ga_{cid}")
            
            if st.button(f"ACTUALIZAR PERMISOS {cid}"):
                db_c[cid]['servicios_f5co']['microservicios']['activo'] = ms
                db_c[cid]['servicios_f5co']['plataforma_descargables']['activo'] = pd
                db_c[cid]['servicios_f5co']['galeria_arte']['activo'] = ga
                guardar_json(db_c, ARCHIVO_CUENTAS)
                st.success("Permisos actualizados.")

# --- LOBBY PRINCIPAL ---
else:
    # Verificamos permisos del usuario actual
    cuenta = cargar_json(ARCHIVO_CUENTAS).get(st.session_state.user_id, {})
    permisos = cuenta.get('servicios_f5co', {})

    st.sidebar.title(f"👤 {cuenta.get('identidad', 'Usuario X')}")
    if st.sidebar.button("Cerrar Sesión"): st.session_state.autenticado = False; st.rerun()

    if st.session_state.modulo_activo == "Lobby":
        st.title("🌌 Lobby Universo X")
        
        # FILA 1: SERVICIOS BASE
        c1, c2, c3, c4 = st.columns(4)
        with c1: 
            st.markdown('<div class="card"><h3>🚚 LOGÍSTICA</h3></div>', unsafe_allow_html=True)
            if st.button("ENTRAR", key="log"): st.session_state.modulo_activo = "1_Logistica.py"; st.rerun()
        with c2: 
            st.markdown('<div class="card"><h3>🚜 MÁQUINAS</h3></div>', unsafe_allow_html=True)
            if st.button("ENTRAR", key="maq"): st.session_state.modulo_activo = "2_Maquinas.py"; st.rerun()
        with c3: 
            st.markdown('<div class="card"><h3>🍔 COCINA</h3></div>', unsafe_allow_html=True)
            if st.button("ENTRAR", key="res"): st.session_state.modulo_activo = "3_restaurante.py"; st.rerun()
        with c4: 
            st.markdown('<div class="card"><h3>🐍 CACD</h3></div>', unsafe_allow_html=True)
            if st.button("ENTRAR", key="snk"): st.session_state.modulo_activo = "x_cacd.py"; st.rerun()

        # FILA 2: MICROSERVICIOS F5CO (Condicionales)
        st.divider()
        st.subheader("💎 Microservicios y Plataformas F5CO")
        cf1, cf2, cf3 = st.columns(3)
        
        with cf1:
            if permisos.get('microservicios', {}).get('activo'):
                st.markdown('<div class="card" style="border-color:#00e6e6"><h3>⚙️ MICROSERVICIOS</h3></div>', unsafe_allow_html=True)
                if st.button("ACCEDER"): st.info("Habilitando Microservicios...")
            else:
                st.markdown('<div class="card" style="opacity:0.3"><h3>🔒 MICROSERVICIOS</h3></div>', unsafe_allow_html=True)
        
        with cf2:
            if permisos.get('plataforma_descargables', {}).get('activo'):
                st.markdown('<div class="card" style="border-color:#00e6e6"><h3>📑 DESCARGABLES</h3></div>', unsafe_allow_html=True)
                if st.button("VER ÁLBUM"): st.info("Abriendo Plataforma de Descargables...")
            else:
                st.markdown('<div class="card" style="opacity:0.3"><h3>🔒 DESCARGABLES</h3></div>', unsafe_allow_html=True)
                
        with cf3:
            if permisos.get('galeria_arte', {}).get('activo'):
                st.markdown('<div class="card" style="border-color:#00e6e6"><h3>🎨 GALERÍA ARTE</h3></div>', unsafe_allow_html=True)
                if st.button("ENTRAR"): st.info("Cargando Galería de Arte...")
            else:
                st.markdown('<div class="card" style="opacity:0.3"><h3>🔒 GALERÍA ARTE</h3></div>', unsafe_allow_html=True)

    else:
        if st.sidebar.button("⬅️ REGRESAR AL HUB"): st.session_state.modulo_activo = "Lobby"; st.rerun()
        cargar_modulo(st.session_state.modulo_activo)