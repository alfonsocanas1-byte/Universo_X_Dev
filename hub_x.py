import streamlit as st
import json
import os
import importlib.util
from datetime import datetime

# --- CONFIGURACIÓN DEL SISTEMA ---
st.set_page_config(page_title="Universo X - Sistema Central", layout="wide")

ARCHIVO_USUARIOS = "usuarios_x.json"
ARCHIVO_CUENTAS = "cuentasx_f5co.json"

def cargar_json(ruta):
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return {}
    return {}

def guardar_json(datos, ruta):
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# --- PANEL MAESTRO (ADMINISTRACIÓN) ---
def renderizar_panel_maestro():
    st.divider()
    st.subheader("🛠️ PANEL MAESTRO - Gestión de F5CO")
    
    cuentas = cargar_json(ARCHIVO_CUENTAS)
    usuarios = cargar_json(ARCHIVO_USUARIOS)
    
    # Selector de usuario para editar
    id_usuario = st.selectbox("Seleccionar Usuario para Gestionar", options=list(cuentas.keys()), 
                              format_func=lambda x: f"{usuarios.get(x, {}).get('username')} ({x})")
    
    if id_usuario:
        user_data = cuentas[id_usuario]
        st.write(f"**Estado Actual:** {user_data['verificacion']['estado']}")
        
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            st.write("--- Permisos Especializados ---")
            esp_activo = st.toggle("Activar Microservicios Especializados (CACD/IA)", 
                                   value=user_data['servicios_f5co'].get('microservicios_especializados', {}).get('activo', False))
            
        with col_p2:
            st.write("--- Permisos Globales ---")
            blog_global = st.toggle("Bloqueo Global de Cuenta", 
                                    value=user_data.get('panel_maestro', {}).get('bloqueo_global', False))

        if st.button("💾 GUARDAR CAMBIOS DE MAESTRO"):
            cuentas[id_usuario]['servicios_f5co']['microservicios_especializados']['activo'] = esp_activo
            cuentas[id_usuario]['panel_maestro']['bloqueo_global'] = blog_global
            guardar_json(cuentas, ARCHIVO_CUENTAS)
            st.success("Permisos actualizados en el sistema F5CO.")
            st.rerun()

# --- LÓGICA DE NAVEGACIÓN ---
if not st.session_state.get('autenticado'):
    # ... (Tu código de Login aquí)
    pass
else:
    # Sidebar de usuario
    u_id = st.session_state.user_id
    u_info = cargar_json(ARCHIVO_USUARIOS).get(u_id, {})
    st.sidebar.title(f"👤 {u_info.get('username')}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    # DETECTOR DE MAESTRO: Si la clave es 10538, habilitamos el Panel Maestro en el Sidebar
    if u_info.get('clave') == "10538":
        with st.sidebar.expander("⭐ OPCIONES DE ADMINISTRADOR"):
            if st.button("ABRIR PANEL MAESTRO"):
                st.session_state.modulo_activo = "PanelMaestro"
                st.rerun()

    # --- RENDERIZADO DE MÓDULOS ---
    if st.session_state.modulo_activo == "PanelMaestro":
        if st.button("⬅️ VOLVER AL LOBBY"):
            st.session_state.modulo_activo = "Lobby"
            st.rerun()
        renderizar_panel_maestro()
        
    elif st.session_state.modulo_activo == "Lobby":
        st.title("🌌 Universo X - Central")
        # ... (Tu código actual del Lobby aquí)