import streamlit as st
import json
import os
import importlib.util
from datetime import datetime, timedelta

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
    .stButton>button { background-color: #FFFFFF !important; color: #000 !important; font-weight: bold !important; width: 100%; border: 2px solid #00e6e6 !important; }
    .stButton>button:hover { background-color: #00e6e6 !important; }
    .card { background: #111; border: 1px solid #333; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 10px; }
    .card-lock { opacity: 0.3; }
    </style>
""", unsafe_allow_html=True)

# --- PANEL MAESTRO (ADMINISTRACIÓN) ---
def renderizar_panel_maestro():
    st.title("🛠️ PANEL MAESTRO - Gestión F5CO")
    if st.button("⬅️ VOLVER AL HUB"): 
        st.session_state.modulo_activo = "Lobby"
        st.rerun()

    db_u = cargar_json(ARCHIVO_USUARIOS)
    db_c = cargar_json(ARCHIVO_CUENTAS)
    
    id_usuario = st.selectbox("Seleccionar Usuario", options=list(db_u.keys()), 
                              format_func=lambda x: f"{db_u[x].get('username', 'S/N')} ({x})")
    
    if id_usuario:
        u_dat = db_u[id_usuario]
        c_dat = db_c.get(id_usuario, {"servicios_f5co": {"microservicios_especializados": {"activo": False}}})

        st.subheader(f"Gestión de {u_dat.get('username')}")
        col1, col2 = st.columns(2)
        
        with col1:
            estado_actual = u_dat.get('estado_cuenta', 'activa')
            nuevo_estado = st.selectbox("Estado de Cuenta", ["activa", "desactiva", "bloqueada"], 
                                        index=["activa", "desactiva", "bloqueada"].index(estado_actual))
            
            f_venc_str = u_dat.get('fecha_vencimiento', str(datetime.now().date()))
            nueva_fecha = st.date_input("Fecha Vencimiento", value=datetime.strptime(f_venc_str, '%Y-%m-%d'))
        
        with col2:
            st.write("--- Servicios F5CO ---")
            ms_esp = st.toggle("Microservicios Especializados (CACD)", 
                               value=c_dat.get('servicios_f5co', {}).get('microservicios_especializados', {}).get('activo', False))

        if st.button("💾 GUARDAR CAMBIOS MAESTROS"):
            db_u[id_usuario]['estado_cuenta'] = nuevo_estado
            db_u[id_usuario]['fecha_vencimiento'] = str(nueva_fecha)
            guardar_json(db_u, ARCHIVO_USUARIOS)
            
            if id_usuario not in db_c: db_c[id_usuario] = {"servicios_f5co": {"microservicios_especializados": {"activo": False}}}
            db_c[id_usuario]['servicios_f5co']['microservicios_especializados']['activo'] = ms_esp
            guardar_json(db_c, ARCHIVO_CUENTAS)
                
            st.success("Cambios aplicados.")
            st.rerun()

# --- LÓGICA DE LOGIN ---
if not st.session_state.autenticado and st.session_state.modulo_activo != "PanelMaestro":
    st.title("🚀 Portal Universo X")
    with st.form("login"):
        u_id = st.text_input("Número de Celular")
        u_pw = st.text_input("Clave", type="password")
        if st.form_submit_button("SINCRONIZAR"):
            db_u = cargar_json(ARCHIVO_USUARIOS)
            if u_id in db_u and str(db_u[u_id]["clave"]) == str(u_pw):
                if 'fecha_vencimiento' not in db_u[u_id]:
                    hoy = datetime.now().date()
                    db_u[u_id]['estado_cuenta'] = "activa"
                    db_u[u_id]['fecha_creacion'] = str(hoy)
                    db_u[u_id]['fecha_vencimiento'] = str(hoy + timedelta(days=15))
                    guardar_json(db_u, ARCHIVO_USUARIOS)
                
                st.session_state.autenticado = True
                st.session_state.user_id = u_id
                st.rerun()
            else: st.error("Datos incorrectos.")
    
    # Acceso Maestro desde fuera
    llave_m = st.text_input("Llave Administrativa", type="password")
    if llave_m == "10538":
        if st.button("ACCESO MAESTRO"): 
            st.session_state.modulo_activo = "PanelMaestro"
            st.rerun()

# --- INTERFAZ POST-LOGIN ---
elif st.session_state.modulo_activo == "PanelMaestro":
    renderizar_panel_maestro()

elif st.session_state.autenticado:
    u_id = st.session_state.user_id
    db_u = cargar_json(ARCHIVO_USUARIOS)
    user_info = db_u.get(u_id, {})
    
    # Validación de tiempo y estado
    f_venc = datetime.strptime(user_info.get('fecha_vencimiento', '2000-01-01'), '%Y-%m-%d').date()
    vencida = datetime.now().date() > f_venc
    inactiva = user_info.get('estado_cuenta') != "activa"

    st.sidebar.title(f"👤 {user_info.get('username')}")
    if st.sidebar.button("Cerrar Sesión"): 
        st.session_state.autenticado = False
        st.rerun()

    # Botón Maestro en sidebar
    if str(user_info.get('clave')) == "10538":
        if st.sidebar.button("🛠️ PANEL MAESTRO"):
            st.session_state.modulo_activo = "PanelMaestro"
            st.rerun()

    # Bloqueo por pago
    if (vencida or inactiva) and st.session_state.modulo_activo == "Lobby":
        st.error("🚨 CUENTA REQUIERE VALIDACIÓN")
        st.info("📲 Contactar a **3122204688** para pago y habilitación.")
        st.stop()

    if st.session_state.modulo_activo == "Lobby":
        st.title("🌌 Hub Central - Universo X")
        db_c = cargar_json(ARCHIVO_CUENTAS)
        permisos = db_c.get(u_id, {}).get('servicios_f5co', {})

        st.subheader("⚙️ Microservicios Operativos")
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.button("🚚 LOGÍSTICA"): st.session_state.modulo_activo = "1_Logistica.py"; st.rerun()
        with c2: 
            if st.button("🚜 MÁQUINAS"): st.session_state.modulo_activo = "2_Maquinas.py"; st.rerun()
        with c3: 
            if st.button("🍔 COCINA"): st.session_state.modulo_activo = "3_restaurante.py"; st.rerun()

        st.divider()
        st.subheader("🧬 Microservicios Especializados")
        ce1, ce2 = st.columns(2)
        if permisos.get('microservicios_especializados', {}).get('activo'):
            with ce1:
                if st.button("🐍 CACD (IA)"): st.session_state.modulo_activo = "x_cacd.py"; st.rerun()
            with ce2:
                if st.button("📊 DATA MINING"): st.info("Cargando...")
        else:
            st.markdown('<div class="card card-lock"><h3>🔒 ESPECIALIZADOS BLOQUEADOS</h3></div>', unsafe_allow_html=True)
    else:
        if st.sidebar.button("⬅️ REGRESAR AL HUB"): 
            st.session_state.modulo_activo = "Lobby"
            st.rerun()
        cargar_modulo(st.session_state.modulo_activo)