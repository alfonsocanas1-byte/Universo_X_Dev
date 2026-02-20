import streamlit as st
import json
import os
import importlib.util
import pandas as pd  # Añadido para manejo de tablas
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DEL SISTEMA ---
st.set_page_config(page_title="Universo X - Sistema Central", layout="wide")

ARCHIVO_USUARIOS = "usuarios_x.json"

# --- FUNCIONES DE PERSISTENCIA SEGURA ---
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

# --- PANEL MAESTRO (ACTUALIZADO CON TABLA) ---
def renderizar_panel_maestro():
    st.title("🛠️ PANEL MAESTRO")
    if st.button("⬅️ VOLVER AL HUB"): 
        st.session_state.modulo_activo = "Lobby"
        st.rerun()
    
    # Pestañas para organizar el panel
    tab_gestion, tab_tabla = st.tabs(["👤 GESTIÓN INDIVIDUAL", "📊 BASE DE DATOS TOTAL"])

    with tab_gestion:
        db_u = cargar_json(ARCHIVO_USUARIOS)
        id_usuario = st.selectbox("Seleccionar Usuario para Editar", options=list(db_u.keys()))
        
        if id_usuario:
            u = db_u[id_usuario]
            col1, col2 = st.columns(2)
            with col1:
                nuevo_estado = st.selectbox("Estado de Cuenta", ["activa", "desactiva"], index=0 if u.get('estado_cuenta')=="activa" else 1)
            with col2:
                fecha_v = u.get('fecha_vencimiento', str(datetime.now().date()))
                nueva_fecha = st.date_input("Nueva Fecha Vencimiento", value=datetime.strptime(fecha_v, '%Y-%m-%d'))
            
            if st.button("💾 GUARDAR CAMBIOS DEFINITIVOS"):
                db_actualizada = cargar_json(ARCHIVO_USUARIOS)
                db_actualizada[id_usuario]['estado_cuenta'] = nuevo_estado
                db_actualizada[id_usuario]['fecha_vencimiento'] = str(nueva_fecha)
                guardar_json(db_actualizada, ARCHIVO_USUARIOS)
                st.success(f"✅ Usuario {id_usuario} actualizado.")
                st.rerun()

    with tab_tabla:
        st.subheader("📋 Registro Global de Usuarios")
        db_u = cargar_json(ARCHIVO_USUARIOS)
        if db_u:
            # Convertir el diccionario en una lista de filas para la tabla
            datos_tabla = []
            for id_cel, info in db_u.items():
                fila = {"Celular (ID)": id_cel}
                fila.update(info)
                datos_tabla.append(fila)
            
            df = pd.DataFrame(datos_tabla)
            # Reordenar columnas importantes al principio
            columnas = ["Celular (ID)", "username", "estado_cuenta", "fecha_vencimiento"] + \
                       [c for c in df.columns if c not in ["Celular (ID)", "username", "estado_cuenta", "fecha_vencimiento"]]
            
            st.dataframe(df[columnas], use_container_width=True, hide_index=True)
            st.download_button("📥 DESCARGAR BASE DE DATOS (CSV)", df.to_csv(index=False), "usuarios_universo_x.csv")
        else:
            st.warning("No hay usuarios registrados en la base de datos.")

# --- LÓGICA DE INTERFAZ PRINCIPAL ---
if not st.session_state.autenticado and st.session_state.modulo_activo != "PanelMaestro":
    st.title("🚀 Bienvenido al Universo X")
    tab_log, tab_reg = st.tabs(["🔐 INGRESAR", "📝 REGISTRARME"])

    with tab_log:
        with st.form("form_login"):
            u_id = st.text_input("Número de Celular")
            u_pw = st.text_input("Clave", type="password")
            if st.form_submit_button("SINCRONIZAR"):
                db_u = cargar_json(ARCHIVO_USUARIOS)
                if u_id in db_u and str(db_u[u_id]["clave"]) == str(u_pw):
                    st.session_state.autenticado = True
                    st.session_state.user_id = u_id
                    st.rerun()
                else: st.error("Datos incorrectos.")

    with tab_reg:
        with st.form("form_registro"):
            r_id = st.text_input("Número de Celular (ID)")
            r_user = st.text_input("Nombre de Usuario")
            r_pw = st.text_input("Clave", type="password")
            if st.form_submit_button("CREAR MI CUENTA"):
                db_u = cargar_json(ARCHIVO_USUARIOS)
                r_id = str(r_id).strip()
                if r_id in db_u: st.error("Este número ya existe.")
                elif r_id and r_pw:
                    hoy = datetime.now().date()
                    db_u[r_id] = {
                        "username": r_user,
                        "clave": str(r_pw),
                        "estado_cuenta": "activa",
                        "fecha_vencimiento": str(hoy + timedelta(days=15))
                    }
                    guardar_json(db_u, ARCHIVO_USUARIOS)
                    st.success("✅ Registro guardado. Ya puede ingresar.")
                else: st.warning("Complete los campos.")

    st.divider()
    if st.text_input("🔑 Acceso Maestro", type="password") == "10538":
        if st.button("ABRIR PANEL MAESTRO"):
            st.session_state.modulo_activo = "PanelMaestro"
            st.rerun()

elif st.session_state.modulo_activo == "PanelMaestro":
    renderizar_panel_maestro()

elif st.session_state.autenticado:
    u_id = st.session_state.user_id
    user = cargar_json(ARCHIVO_USUARIOS).get(u_id, {})
    
    st.sidebar.title(f"👤 {user.get('username')}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    if st.session_state.modulo_activo == "Lobby":
        st.title("🌌 Hub Central de Microservicios")
        
        # CATEGORÍAS
        st.subheader("⚙️ OPERACIONES")
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.button("🚚 LOGÍSTICA"): st.session_state.modulo_activo = "1_Logistica.py"; st.rerun()
        with c2: 
            if st.button("🚜 MÁQUINAS"): st.session_state.modulo_activo = "2_Maquinas.py"; st.rerun()
        with c3: 
            if st.button("🍔 RESTAURANTE"): st.info("Módulo en desarrollo...")

        st.divider()
        st.subheader("🧬 ESPECIALIZADOS Y SALUD")
        c4, c5, c6 = st.columns(3)
        with c4: 
            if st.button("🐍 CACD"): st.session_state.modulo_activo = "x_cacd.py"; st.rerun()
        with c5: 
            if st.button("🦷 ODONTOLOGÍA"): st.info("Módulo en desarrollo...")
        with c6: 
            if st.button("🌱 AGRO-PRO"): st.info("Módulo en desarrollo...")
            
    else:
        if st.sidebar.button("⬅️ VOLVER AL HUB"): 
            st.session_state.modulo_activo = "Lobby"
            st.rerun()
        cargar_modulo(st.session_state.modulo_activo)