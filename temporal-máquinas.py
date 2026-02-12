import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN DE RUTAS ---
FOLDER_PATH = "PROYECTOS_X"
MAQ_FILE = os.path.join(FOLDER_PATH, "maquinas_x.json")
FUEL_FILE = os.path.join(FOLDER_PATH, "tanqueos_x.json")

# --- SEGURIDAD: VERIFICAR LOGIN DEL HUB ---
if not st.session_state.get('llave_general', False):
    st.warning("⚠️ Acceso denegado. Por favor, inicia sesión en el Hub principal.")
    st.stop()

# --- ESTÉTICA DEL UNIVERSO ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    div.stButton > button { background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #4B4B4B !important; font-weight: bold; }
    .stExpander, div[data-testid="stForm"] { background-color: #0E1117 !important; border: 1px solid #30363D !important; border-radius: 10px; }
    .pedido-card { background-color: #1A1A1A; padding: 15px; border-radius: 10px; border-left: 5px solid #4B4B4B; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE DATOS ---
def cargar_datos(archivo, columnas):
    if os.path.exists(archivo):
        try: return pd.read_json(archivo)
        except: pass
    return pd.DataFrame(columns=columnas)

def guardar_datos(df, archivo):
    if not os.path.exists(FOLDER_PATH): os.makedirs(FOLDER_PATH)
    df.to_json(archivo, orient='records', indent=4)

st.title("⚙️ Micro-Universo: Máquinas")

# --- LÓGICA DE ACCESO Y TANQUEO ---
df_m = cargar_datos(MAQ_FILE, ["Placa", "Llave", "Propietario", "Datos", "Fecha"])

if 'maquina_autenticada' not in st.session_state:
    st.session_state.maquina_autenticada = None

if st.session_state.maquina_autenticada is None:
    tab1, tab2 = st.tabs(["🔑 Acceso por Placa", "🆕 Registro Nuevo"])
    
    with tab1:
        p_in = st.text_input("Placa", key="p_in").upper()
        k_in = st.text_input("Llave de Seguridad", type="password", key="k_in")
        if st.button("🔓 ABRIR PANEL"):
            match = df_m[(df_m["Placa"] == p_in) & (df_m["Llave"] == k_in)]
            if not match.empty:
                st.session_state.maquina_autenticada = p_in
                st.rerun()
            else: st.error("Placa o llave incorrecta.")

    with tab2:
        with st.form("reg_maq"):
            p_new = st.text_input("Nueva Placa").upper()
            k_new = st.text_input("Crear Llave", type="password")
            prop = st.text_input("Nombre Propietario")
            if st.form_submit_button("🛡️ RECLAMAR PLACA"):
                if p_new in df_m["Placa"].values: st.warning("La placa ya existe.")
                elif p_new and k_new:
                    nueva = pd.DataFrame([{"Placa": p_new, "Llave": k_new, "Propietario": prop, "Datos": "Inicial", "Fecha": datetime.now().strftime("%Y-%m-%d")}])
                    guardar_datos(pd.concat([df_m, nueva], ignore_index=True), MAQ_FILE)
                    st.success(f"Placa {p_new} registrada."); st.rerun()
else:
    placa_activa = st.session_state.maquina_autenticada
    st.success(f"Sesión Activa: **{placa_activa}**")
    
    col_acc1, col_acc2 = st.columns(2)
    with col_acc1:
        with st.form("form_tanqueo", clear_on_submit=True):
            st.write("### ⛽ Nuevo Tanqueo")
            odometro = st.number_input("Odómetro / Kilometraje Actual", min_value=0)
            galones = st.number_input("Galones Ingresados", min_value=0.0)
            if st.form_submit_button("⛽ GUARDAR"):
                df_t = cargar_datos(FUEL_FILE, ["ID", "Placa", "Odometro", "Galones", "Fecha"])
                nid = 1 if df_t.empty else int(df_t["ID"].max() + 1)
                nuevo_t = pd.DataFrame([{
                    "ID": nid, 
                    "Placa": placa_activa, 
                    "Odometro": odometro, 
                    "Galones": galones, 
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
                }])
                guardar_datos(pd.concat([df_t, nuevo_t], ignore_index=True), FUEL_FILE)
                st.success("Tanqueo registrado con éxito.")
    
    with col_acc2:
        st.write("### 📊 Historial de Tanqueos")
        df_t = cargar_datos(FUEL_FILE, ["ID", "Placa", "Odometro", "Galones", "Fecha"])
        hist = df_t[df_t["Placa"] == placa_activa]
        if not hist.empty:
            st.dataframe(hist.sort_values(by="ID", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("No hay registros previos.")

    if st.button("🔴 Cerrar Sesión de Placa"):
        st.session_state.maquina_autenticada = None
        st.rerun()

# --- ADMIN 0303 ---
st.divider()
llave_admin = st.text_input("Admin (0303)", type="password")
if llave_admin == "0303":
    st.write("#### Base Maestra de Placas")
    for i, row in df_m.iterrows():
        c1, c2 = st.columns([0.8, 0.2])
        with c1: st.markdown(f'<div class="pedido-card">🚗 {row["Placa"]} | 🔑 {row["Llave"]}</div>', unsafe_allow_html=True)
        with c2:
            if st.button("🗑️", key=f"del_{row['Placa']}"):
                guardar_datos(df_m.drop(i), MAQ_FILE); st.rerun()