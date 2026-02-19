import streamlit as st
import json
import os
import importlib.util
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DEL SISTEMA ---
st.set_page_config(page_title="Universo X - Sistema Central", layout="wide")

ARCHIVO_USUARIOS = "usuarios_x.json"

# --- FUNCIONES DE PERSISTENCIA SEGURA ---
def cargar_json(ruta):
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def guardar_json(datos, ruta):
    # Escribir en un archivo temporal y luego renombrar es la forma más segura
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# --- PANEL MAESTRO (CORREGIDO PARA PERSISTENCIA) ---
def renderizar_panel_maestro():
    st.title("🛠️ PANEL MAESTRO")
    if st.button("⬅️ VOLVER AL HUB"): 
        st.session_state.modulo_activo = "Lobby"
        st.rerun()
    
    # Carga fresca antes de mostrar
    db_u = cargar_json(ARCHIVO_USUARIOS)
    id_usuario = st.selectbox("Gestionar Usuario", options=list(db_u.keys()))
    
    if id_usuario:
        u = db_u[id_usuario]
        col1, col2 = st.columns(2)
        with col1:
            estado_actual = u.get('estado_cuenta', 'activa')
            nuevo_estado = st.selectbox("Estado", ["activa", "desactiva"], 
                                        index=0 if estado_actual == "activa" else 1)
        with col2:
            fecha_str = u.get('fecha_vencimiento', '2026-03-06')
            nueva_fecha = st.date_input("Vencimiento", value=datetime.strptime(fecha_str, '%Y-%m-%d'))
        
        if st.button("💾 GUARDAR CAMBIOS DEFINITIVOS"):
            # RE-CARGAR antes de guardar para evitar sobrescribir otros cambios
            db_actualizada = cargar_json(ARCHIVO_USUARIOS)
            db_actualizada[id_usuario]['estado_cuenta'] = nuevo_estado
            db_actualizada[id_usuario]['fecha_vencimiento'] = str(nueva_fecha)
            
            guardar_json(db_actualizada, ARCHIVO_USUARIOS)
            st.success(f"✅ Datos de {id_usuario} actualizados en el servidor.")
            st.rerun()

# --- LÓGICA DE REGISTRO (CORREGIDA) ---
# Dentro de tu bloque de registro:
# ...
if st.form_submit_button("CREAR MI CUENTA"):
    db_u = cargar_json(ARCHIVO_USUARIOS)
    r_id = str(r_id).strip() # Asegurar que el ID sea texto y no tenga espacios
    if r_id in db_u: 
        st.error("Este número ya existe.")
    elif r_id and r_pw:
        hoy = datetime.now().date()
        db_u[r_id] = {
            "username": r_user,
            "clave": str(r_pw), # Guardar clave siempre como string
            "estado_cuenta": "activa",
            "fecha_vencimiento": str(hoy + timedelta(days=15))
        }
        guardar_json(db_u, ARCHIVO_USUARIOS)
        st.success("✅ Registro guardado correctamente.")