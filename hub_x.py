import streamlit as st
import json
import os
import importlib.util
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DEL SISTEMA ---
st.set_page_config(page_title="Universo X - Sistema Central", layout="wide")

ARCHIVO_USUARIOS = "usuarios_x.json"

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

# --- ESTÉTICA DARK PREMIUM Y LETRAS BLANCAS SIDEBAR ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: #FFFFFF; }
    /* Forzar letras blancas en el Sidebar */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] span {
        color: #FFFFFF !important;
    }
    h1, h2, h3, label { color: #00e6e6 !important; }
    .stButton>button { background-color: #111 !important; color: #fff !important; border: 1px solid #333 !important; height: 55px; width: 100%; }
    .stButton>button:hover { border-color: #00e6e6 !important; color: #00e6e6 !important; }
    .card-title { font-size: 1.1rem; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 5px; color: #00e6e6; }
    </style>
""", unsafe_allow_html=True)

# --- PANEL MAESTRO ---
def renderizar_panel_maestro():
    st.title("🛠️ PANEL MAESTRO")
    if st.button("⬅️ VOLVER AL HUB"): 
        st.session_state.modulo_activo = "Lobby"
        st.rerun()
    
    tab_gestion, tab_tabla = st.tabs(["👤 EDICIÓN DE USUARIOS", "📊 BASE DE DATOS"])

    with tab_gestion:
        db_u = cargar_json(ARCHIVO_USUARIOS)
        id_usuario = st.selectbox("Seleccionar Celular (ID) para editar", options=list(db_u.keys()))
        
        if id_usuario:
            u = db_u[id_usuario]
            col1, col2 = st.columns(2)
            with col1:
                nuevo_nombre = st.text_input("Nombre Completo", value=u.get('nombre_completo', ''))
                nuevo_user = st.text_input("Username", value=u.get('username', ''))
                nuevo_pais = st.text_input("País", value=u.get('pais', 'Colombia'))
                nueva_clave = st.text_input("Clave de Acceso", value=u.get('clave', ''))
            with col2:
                nueva_nac = st.text_input("Fecha Nacimiento", value=u.get('nacimiento', '1992-01-01'))
                nuevo_indicio = st.text_input("Indicio de Clave", value=u.get('indicio', ''))
                nuevo_estado = st.selectbox("Estado", ["activa", "desactiva"], index=0 if u.get('estado_cuenta')=="activa" else 1)
                fecha_v = u.get('fecha_vencimiento', str(datetime.now().date()))
                nueva_fecha = st.date_input("Vencimiento", value=datetime.strptime(fecha_v, '%Y-%m-%d'))
            
            if st.button("💾 GUARDAR CAMBIOS"):
                db_actualizada = cargar_json(ARCHIVO_USUARIOS)
                db_actualizada[id_usuario].update({
                    "nombre_completo": nuevo_nombre, "username": nuevo_user, "pais": nuevo_pais,
                    "clave": nueva_clave, "nacimiento": nueva_nac, "indicio": nuevo_indicio,
                    "estado_cuenta": nuevo_estado, "fecha_vencimiento": str(nueva_fecha)
                })
                guardar_json(db_actualizada, ARCHIVO_USUARIOS)
                st.success("✅ Datos actualizados.")
                st.rerun()

    with tab_tabla:
        db_u = cargar_json(ARCHIVO_USUARIOS)
        if db_u:
            df = pd.DataFrame([{"Celular": k, **v} for k, v in db_u.items()])
            st.dataframe(df, use_container_width=True, hide_index=True)

# --- INTERFAZ PRINCIPAL (LOGIN Y REGISTRO) ---
if not st.session_state.autenticado and st.session_state.modulo_activo != "PanelMaestro":
    st.title("🚀 Bienvenido al Universo X")
    
    tab_login, tab_registro = st.tabs(["🔐 INGRESAR", "📝 REGISTRARME"])

    with tab_login:
        with st.form("login"):
            u_id = st.text_input("Número de Celular")
            u_pw = st.text_input("Clave", type="password")
            if st.form_submit_button("INGRESAR AL HUB"):
                db_u = cargar_json(ARCHIVO_USUARIOS)
                if u_id in db_u and str(db_u[u_id]["clave"]) == str(u_pw):
                    st.session_state.autenticado = True
                    st.session_state.user_id = u_id
                    st.rerun()
                else: st.error("Acceso incorrecto. Verifique sus datos.")

    with tab_registro:
        with st.form("registro"):
            r_id = st.text_input("Número de Celular (Será su ID)")
            r_nombre = st.text_input("Nombre Completo")
            r_user = st.text_input("Nombre de Usuario")
            r_pw = st.text_input("Definir Clave", type="password")
            r_indicio = st.text_input("Indicio de clave (opcional)")
            
            if st.form_submit_button("CREAR MI CUENTA"):
                db_u = cargar_json(ARCHIVO_USUARIOS)
                r_id = r_id.strip()
                if r_id in db_u:
                    st.error("Este número ya se encuentra registrado.")
                elif r_id and r_pw and r_nombre:
                    hoy = datetime.now().date()
                    db_u[r_id] = {
                        "nombre_completo": r_nombre,
                        "username": r_user,
                        "pais": "Colombia",
                        "nacimiento": "1992-01-01",
                        "clave": r_pw,
                        "indicio": r_indicio,
                        "estado_cuenta": "activa",
                        "fecha_creacion": str(hoy),
                        "fecha_vencimiento": str(hoy + timedelta(days=15))
                    }
                    guardar_json(db_u, ARCHIVO_USUARIOS)
                    st.success("✅ ¡Registro exitoso! Ya puede ingresar con sus datos en la pestaña anterior.")
                else:
                    st.warning("Por favor complete los campos obligatorios.")

    st.divider()
    if st.text_input("🔑 Maestro", type="password") == "10538":
        if st.button("ABRIR PANEL"):
            st.session_state.modulo_activo = "PanelMaestro"; st.rerun()

elif st.session_state.modulo_activo == "PanelMaestro":
    renderizar_panel_maestro()

elif st.session_state.autenticado:
    u_id = st.session_state.user_id
    user = cargar_json(ARCHIVO_USUARIOS).get(u_id, {})
    
    # --- SIDEBAR CON LETRAS BLANCAS ---
    st.sidebar.markdown(f"""
    <div style="background-color: #111; padding: 15px; border-radius: 10px; border-left: 5px solid #00e6e6; margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 1.2em;">👤 {user.get('nombre_completo', 'Usuario')}</h2>
        <p style="margin: 8px 0; font-size: 0.9em;"><b>📞 Celular:</b> {u_id}</p>
        <p style="margin: 5px 0; font-size: 0.9em;"><b>⏳ Vence:</b> {user.get('fecha_vencimiento')}</p>
        <p style="margin: 0; font-size: 0.8em; opacity: 0.7;">@{user.get('username')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False; st.rerun()

    if user.get('clave') == "10538":
        if st.sidebar.button("🛠️ PANEL MAESTRO"):
            st.session_state.modulo_activo = "PanelMaestro"; st.rerun()

    if st.session_state.modulo_activo == "Lobby":
        st.title("🌌 Hub Central de Microservicios")
        
        # CATEGORÍA 1: OPERACIONES
        st.markdown("<div class='card-title'>⚙️ OPERACIONES</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.button("🚚 LOGÍSTICA"): st.session_state.modulo_activo = "1_Logistica.py"; st.rerun()
        with c2: 
            if st.button("🚜 MÁQUINAS"): st.session_state.modulo_activo = "2_Maquinas.py"; st.rerun()
        with c3: 
            if st.button("🍔 RESTAURANTE"): st.session_state.modulo_activo = "3_restaurante.py"; st.rerun()

        # CATEGORÍA 2: SALUD Y SUMINISTROS
        st.markdown("<div class='card-title'>📦 SALUD Y SUMINISTROS</div>", unsafe_allow_html=True)
        c4, c5, c6 = st.columns(3)
        with c4: 
            if st.button("🛒 ALACENA / MERCADO"): st.info("Próximamente...")
        with c5: 
            if st.button("🌱 AGRO-PRO"): st.info("Próximamente...")
        with c6: 
            if st.button("🦷 ODONTOLOGÍA"): st.info("Próximamente...")

        # CATEGORÍA 3: ESPECIALIZADO Y CONTENIDO
        st.divider()
        col_esp, col_con = st.columns(2)
        with col_esp:
            st.markdown("<div class='card-title'>🧬 ESPECIALIZADO</div>", unsafe_allow_html=True)
            if st.button("🐍 CACD (IA OFÍDICA)"): st.session_state.modulo_activo = "x_cacd.py"; st.rerun()
        with col_con:
            st.markdown("<div class='card-title'>💎 CONTENIDO</div>", unsafe_allow_html=True)
            c_ga, c_dt = st.columns(2)
            with c_ga: 
                if st.button("🎨 GALERÍA ARTE"): st.info("Cargando Galería...")
            with c_dt: 
                if st.button("📑 DESCARGABLES"): st.info("Abriendo Biblioteca...")
    else:
        if st.sidebar.button("⬅️ VOLVER AL HUB"): 
            st.session_state.modulo_activo = "Lobby"; st.rerun()
        cargar_modulo(st.session_state.modulo_activo)