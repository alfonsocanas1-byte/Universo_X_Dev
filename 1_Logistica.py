import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN DE RUTAS ---
FOLDER_PATH = "PROYECTOS_X"
LOG_FILE = os.path.join(FOLDER_PATH, "pedidos_logistica.json")

if not os.path.exists(FOLDER_PATH):
    os.makedirs(FOLDER_PATH)

# --- FUNCIONES DE DATOS ---
def cargar_pedidos():
    if os.path.exists(LOG_FILE):
        try:
            return pd.read_json(LOG_FILE)
        except:
            return pd.DataFrame(columns=["ID", "Fecha", "Usuario", "Estado", "Comentarios"])
    return pd.DataFrame(columns=["ID", "Fecha", "Usuario", "Estado", "Comentarios"])

# --- ESTÉTICA INTERNA ---
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab"] {
        background-color: #1A1A1A !important;
        color: #888888 !important;
        border: 1px solid #333 !important;
        padding: 10px 20px !important;
    }
    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom: 2px solid #FFFFFF !important;
    }
    .pedido-card {
        background-color: #111;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4B4B4B;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULO ---
st.title("🚚 OPERACIONES LOGÍSTICAS")

# Cargar datos
df_l = cargar_pedidos()

tab1, tab2 = st.tabs(["📝 Nuevo Pedido", "📊 Seguimiento de Flota"])

with tab1:
    st.subheader("Registrar Solicitud")
    with st.form("nuevo_pedido"):
        u = st.text_input("Usuario / Responsable")
        c = st.text_area("Descripción del pedido o ruta")
        if st.form_submit_button("ENVIAR A LOGÍSTICA"):
            if u and c:
                nuevo_id = int(df_l["ID"].max() + 1) if not df_l.empty else 1001
                nuevo_p = {
                    "ID": nuevo_id,
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Usuario": u,
                    "Estado": "Pendiente",
                    "Comentarios": c
                }
                df_l = pd.concat([df_l, pd.DataFrame([nuevo_p])], ignore_index=True)
                df_l.to_json(LOG_FILE, indent=4)
                st.success(f"Pedido #{nuevo_id} registrado en el Universo.")
            else:
                st.warning("Por favor completa los campos.")

with tab2:
    st.subheader("Estado de Operaciones")
    df_vivos = df_l[df_l["Estado"] != "Cancelado"]
    
    if not df_vivos.empty:
        for _, row in df_vivos.sort_values(by="ID", ascending=False).iterrows():
            st.markdown(f"""
            <div class="pedido-card">
                <div style="display: flex; justify-content: space-between;">
                    <b>#{row['ID']} - {row['Usuario']}</b>
                    <span style="color: {'#FFA500' if row['Estado'] == 'Pendiente' else '#00FF00'};">● {row['Estado']}</span>
                </div>
                <div style="font-size: 0.9em; color: #AAA; margin-top: 5px;">{row['Comentarios']}</div>
                <div style="font-size: 0.7em; color: #555; margin-top: 5px;">📅 {row['Fecha']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay operaciones activas.")

# --- GESTIÓN MAESTRA (5050) ---
st.divider()
with st.expander("🔑 ACCESO ADMINISTRACIÓN"):
    clave = st.text_input("Llave Administrativa", type="password")
    if clave == "5050":
        st.subheader("Panel de Gestión")
        if not df_l.empty:
            for idx, row in df_l.iterrows():
                with st.form(f"edit_{row['ID']}"):
                    st.write(f"Pedido #{row['ID']}")
                    new_est = st.selectbox("Cambiar Estado", ["Pendiente", "En Proceso", "Completado", "Cancelado"], 
                                         index=["Pendiente", "En Proceso", "Completado", "Cancelado"].index(row['Estado']))
                    if st.form_submit_button(f"ACTUALIZAR #{row['ID']}"):
                        df_l.at[idx, "Estado"] = new_est
                        df_l.to_json(LOG_FILE, indent=4)
                        st.rerun()