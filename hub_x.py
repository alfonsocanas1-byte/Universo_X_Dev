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
    .subs-info { background-color: #111; padding: 10px; border-radius: 5px; border-left: 3px solid #00e6e6; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- PANEL MAESTRO (FUNCIÓN DE RENDERIZADO) ---
def renderizar_panel_maestro():
    st.title("🛠️ PANEL MAESTRO - Control Total")
    if st.button("⬅️ VOLVER AL HUB / LOBBY"): 
        st.session_state.modulo_activo = "Lobby"
        st.rerun()

    db_u = cargar_json(ARCHIVO_USUARIOS)
    
    # Lista desplegable de usuarios registrados
    id_usuario = st.selectbox("Seleccionar Usuario para gestionar", options=list(db_u.keys()), 
                              format_func=lambda x: f"{db_u[x].get('username', 'Sin nombre')} ({x})")
    
    if id_usuario:
        u_dat = db_u[id_usuario]
        st.markdown(f"### Gestión de Cuenta: **{u_dat.get('username')}**")
        
        col1, col2 = st.columns(2)
        with col1:
            estado_actual = u_dat.get('estado_cuenta', 'activa')
            nuevo_estado = st.selectbox("Cambiar Estado de Cuenta", ["activa", "desactiva", "bloqueada"], 
                                        index=["activa", "desactiva", "bloqueada"].index(estado_actual))
        
        with col2:
            f_venc_str = u_dat.get('fecha_vencimiento', str(datetime.now().date()))
            nueva_fecha = st.date_input("Nueva Fecha de Vencimiento", value=datetime.strptime(f_venc_str, '%Y-%m-%d'))
        
        st.divider()
        if st.button("💾 APLICAR CAMBIOS MAESTROS"):
            db_u[id_usuario]['estado_cuenta'] = nuevo_estado
            db_u[id_usuario]['fecha_vencimiento'] = str(nueva_fecha)
            guardar_json(db_u, ARCHIVO_USUARIOS)
            st.success(f"✅ Los cambios para {id_usuario} han sido guardados en el sistema.")
            st.rerun()

# --- INTERFAZ DE ENTRADA (LOGIN / REGISTRO) ---
if not st.session_state.autenticado and st.session_state.modulo_activo != "PanelMaestro":
    st.title("🚀 Acceso al Universo X")
    t_log, t_reg = st.tabs(["🔐 INGRESAR", "📝 REGISTRARME"])

    with t_log:
        with st.form("login_form"):
            u_id = st.text_input("Número de Celular")
            u_pw = st.text_input("Clave", type="password")
            if st.form_submit_button("SINCRONIZAR"):
                db_u = cargar_json(ARCHIVO_USUARIOS)
                if u_id in db_u and str(db_u[u_id]["clave"]) == str(u_pw):
                    st.session_state.autenticado = True
                    st.session_state.user_id = u_id
                    st.rerun()
                else: st.error("Acceso denegado. Verifique sus credenciales.")

    with t_reg:
        with st.form("reg_form"):
            r_id = st.text_input("Número de Celular (ID)")
            r_user = st.text_input("Nombre de Usuario")
            r_pw = st.text_input("Definir Clave", type="password")
            if st.form_submit_button("CREAR MI CUENTA"):
                db_u = cargar_json(ARCHIVO_USUARIOS)
                if r_id in db_u: st.error("Este número ya existe.")
                elif r_id and r_pw:
                    hoy = datetime.now().date()
                    db_u[r_id] = {
                        "username": r_user,
                        "clave": r_pw,
                        "estado_cuenta": "activa",
                        "fecha_vencimiento": str(hoy + timedelta(days=15))
                    }
                    guardar_json(db_u, ARCHIVO_USUARIOS)
                    st.success("✅ Registro exitoso con 15 días de cortesía.")
                else: st.warning("Complete los campos obligatorios.")

    # Acceso administrativo externo
    st.write("---")
    master_key = st.text_input("🔒 Acceso de Administrador", type="password")
    if master_key == "10538":
        if st.button("ABRIR PANEL MAESTRO"):
            st.session_state.modulo_activo = "PanelMaestro"
            st.rerun()

# --- LÓGICA DE NAVEGACIÓN POST-LOGIN ---
elif st.session_state.modulo_activo == "PanelMaestro":
    renderizar_panel_maestro()

elif st.session_state.autenticado:
    u_id = st.session_state.user_id
    db_u = cargar_json(ARCHIVO_USUARIOS)
    user = db_u.get(u_id, {})

    # Cálculos de suscripción
    f_v = datetime.strptime(user.get('fecha_vencimiento', '2000-01-01'), '%Y-%m-%d').date()
    hoy = datetime.now().date()
    dias = (f_v - hoy).days
    
    # Barra lateral
    st.sidebar.title(f"👤 {user.get('username')}")
    st.sidebar.markdown(f"""
    <div class='subs-info'>
        <b>Estado:</b> {user.get('estado_cuenta', 'S/N').upper()}<br>
        <b>Vence:</b> {f_v.strftime('%d/%m/%Y')}<br>
        <b>Días:</b> <span style='color:{'#ff4b4b' if dias <= 3 else '#00e6e6'};'>{max(0, dias)}</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    # Si el usuario es el maestro (10538), mostrar botón administrativo
    if str(user.get('clave')) == "10538":
        if st.sidebar.button("🛠️ PANEL MAESTRO"):
            st.session_state.modulo_activo = "PanelMaestro"
            st.rerun()

    # Validación de bloqueo
    if (hoy > f_v or user.get('estado_cuenta') != "activa") and st.session_state.modulo_activo == "Lobby":
        st.error("🚨 SERVICIO SUSPENDIDO")
        st.info(f"Contactar por WhatsApp al **3122204688** para pago de suscripción.")
        st.stop()

    if st.session_state.modulo_activo == "Lobby":
        st.title("🌌 Hub Central - Universo X")
        c1, c2, c3, c4 = st.columns(4)
        with c1: 
            if st.button("🚚 LOGÍSTICA"): st.session_state.modulo_activo = "1_Logistica.py"; st.rerun()
        with c2: 
            if st.button("🚜 MÁQUINAS"): st.session_state.modulo_activo = "2_Maquinas.py"; st.rerun()
        with c3: 
            if st.button("🍔 COCINA"): st.session_state.modulo_activo = "3_restaurante.py"; st.rerun()
        with c4: 
            if st.button("🐍 CACD (IA)"): st.session_state.modulo_activo = "x_cacd.py"; st.rerun()
    else:
        if st.sidebar.button("⬅️ VOLVER AL HUB"): 
            st.session_state.modulo_activo = "Lobby"
            st.rerun()
        cargar_modulo(st.session_state.modulo_activo)