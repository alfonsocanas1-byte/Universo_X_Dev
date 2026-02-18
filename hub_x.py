import streamlit as st
import json
import os
import importlib.util
from datetime import datetime

# --- CONFIGURACIÓN DEL SISTEMA ---
st.set_page_config(page_title="Universo X - Sistema Central", layout="wide")

ARCHIVO_USUARIOS = "usuarios_x.json"
ARCHIVO_CUENTAS = "cuentasx_f5co.json"

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
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
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
    .stButton>button { background-color: #FFFFFF !important; color: #000 !important; font-weight: bold !important; width: 100%; border: 2px solid #00e6e6 !important; }
    .stButton>button:hover { background-color: #00e6e6 !important; }
    .card { background: #111; border: 1px solid #333; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- ACCESO Y PANEL MAESTRO ---
if not st.session_state.autenticado and st.session_state.modulo_activo != "Panel_Maestro":
    st.title("🚀 Portal de Sincronización X")
    c1, c2 = st.columns([2, 1])
    with c1:
        with st.form("login"):
            u_id = st.text_input("Número de Celular")
            u_pw = st.text_input("Clave", type="password")
            if st.form_submit_button("SINCRONIZAR"):
                db_u = cargar_json(ARCHIVO_USUARIOS)
                if u_id in db_u and db_u[u_id]["clave"] == u_pw:
                    # Registro automático en F5CO si no existe
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
                    st.session_state.autenticado = True; st.session_state.user_id = u_id; st.rerun()
                else: st.error("Acceso denegado.")
    with c2:
        if st.text_input("Llave Administrativa", type="password") == "10538":
            if st.button("ABRIR PANEL MAESTRO"): st.session_state.modulo_activo = "Panel_Maestro"; st.rerun()

elif st.session_state.modulo_activo == "Panel_Maestro":
    st.title("🛠️ Gestión de Microservicios F5CO")
    if st.button("⬅️ VOLVER AL HUB"): st.session_state.modulo_activo = "Lobby"; st.rerun()
    db_c = cargar_json(ARCHIVO_CUENTAS)
    for cid, info in db_c.items():
        with st.expander(f"👤 {info['identidad']} ({cid})"):
            c1, c2, c3 = st.columns(3)
            # Control de estados para los microservicios y plataformas
            ms = c1.checkbox("Microservicios (Log/Maq/Rest/CACD)", value=info['servicios_f5co']['microservicios']['activo'], key=f"ms_{cid}")
            pd = c2.checkbox("Plataforma Descargables", value=info['servicios_f5co']['plataforma_descargables']['activo'], key=f"pd_{cid}")
            ga = c3.checkbox("Galería de Arte", value=info['servicios_f5co']['galeria_arte']['activo'], key=f"ga_{cid}")
            if st.button(f"ACTUALIZAR {cid}"):
                db_c[cid]['servicios_f5co']['microservicios']['activo'] = ms
                db_c[cid]['servicios_f5co']['plataforma_descargables']['activo'] = pd
                db_c[cid]['servicios_f5co']['galeria_arte']['activo'] = ga
                guardar_json(db_c, ARCHIVO_CUENTAS); st.success("Permisos guardados.")

# --- LOBBY PRINCIPAL ---
else:
    cuenta = cargar_json(ARCHIVO_CUENTAS).get(st.session_state.user_id, {})
    permisos = cuenta.get('servicios_f5co', {})
    
    st.sidebar.title(f"👤 {cuenta.get('identidad', 'Usuario X')}")
    if st.sidebar.button("Cerrar Sesión"): st.session_state.autenticado = False; st.rerun()

    if st.session_state.modulo_activo == "Lobby":
        st.title("🌌 Hub Central - Universo X")
        
        # SECCIÓN 1: MICROSERVICIOS OPERATIVOS (LOGÍSTICA, MÁQUINAS, RESTAURANTE, CACD)
        st.subheader("⚙️ Microservicios Operativos")
        if permisos.get('microservicios', {}).get('activo'):
            c1, c2, c3, c4 = st.columns(4)
            # Lista de archivos que actúan como microservicios [cite: 1, 2, 13, 14]
            mods = [("🚚 LOGÍSTICA", "1_Logistica.py", c1), ("🚜 MÁQUINAS", "2_Maquinas.py", c2), 
                    ("🍔 RESTAURANTE", "3_restaurante.py", c3), ("🐍 CACD", "x_cacd.py", c4)]
            for n, f, col in mods:
                with col:
                    st.markdown(f'<div class="card"><h3>{n}</h3></div>', unsafe_allow_html=True)
                    if st.button(f"ENTRAR", key=f): st.session_state.modulo_activo = f; st.rerun()
        else:
            st.warning("🔒 Microservicios bloqueados. Requiere verificación F5CO.")
            st.markdown('<div class="card" style="opacity:0.3"><h3>SERVICIOS DESACTIVADOS</h3><p>Verificación de número pendiente.</p></div>', unsafe_allow_html=True)

        st.divider()

        # SECCIÓN 2: PLATAFORMAS ADICIONALES (DESCARGABLES Y GALERÍA)
        st.subheader("💎 Plataformas de Contenido")
        ca, cb = st.columns(2)
        
        with ca:
            # Control dinámico basado en permisos de f5co [cite: 12]
            if permisos.get('plataforma_descargables', {}).get('activo'):
                st.markdown('<div class="card" style="border-color:#00e6e6"><h3>📑 DESCARGABLES</h3></div>', unsafe_allow_html=True)
                if st.button("ACCEDER A BIBLIOTECA"): st.info("Cargando archivos...")
            else:
                st.markdown('<div class="card" style="opacity:0.3"><h3>🔒 DESCARGABLES</h3></div>', unsafe_allow_html=True)
        
        with cb:
            if permisos.get('galeria_arte', {}).get('activo'):
                st.markdown('<div class="card" style="border-color:#00e6e6"><h3>🎨 GALERÍA DE ARTE</h3></div>', unsafe_allow_html=True)
                if st.button("VISITAR EXPOSICIÓN"): st.info("Cargando Galería...")
            else:
                st.markdown('<div class="card" style="opacity:0.3"><h3>🔒 GALERÍA</h3></div>', unsafe_allow_html=True)
    else:
        if st.sidebar.button("⬅️ REGRESAR AL HUB"): st.session_state.modulo_activo = "Lobby"; st.rerun()
        cargar_modulo(st.session_state.modulo_activo)