import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN DE RUTAS ---
FOLDER_PATH = "PROYECTOS_X"
LOG_FILE = os.path.join(FOLDER_PATH, "pedidos_logistica.json")

# --- ESTÉTICA DARK TOTAL (NEGRO Y BLANCO) ---
st.markdown("""
    <style>
    /* Fondo total de la aplicación */
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Forzar color blanco en todos los textos */
    h1, h2, h3, h4, h5, h6, p, div, span, label, .stMarkdown { 
        color: #FFFFFF !important; 
    }
    
    /* Estilo para las Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] { 
        background-color: #000000; 
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1A1A1A !important;
        color: #888888 !important;
        border: 1px solid #333 !important;
        border-radius: 5px 5px 0px 0px;
        padding: 10px 20px !important;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom: 2px solid #FFFFFF !important;
        background-color: #333333 !important;
    }

    /* Inputs y Formularios */
    input, textarea, [data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 1px solid #4B4B4B !important;
    }

    /* Botones de acción */
    div.stButton > button {
        background-color: #000000 !important; 
        color: #FFFFFF !important;
        border: 1px solid #4B4B4B !important; 
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        border-color: #FFFFFF !important;
        box-shadow: 0px 0px 10px #FFFFFF;
    }

    /* Estilo de las Tablas (Dataframes) */
    div[data-testid="stDataFrame"] {
        background-color: #000000 !important;
        border: 1px solid #333 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CARGAR DATOS ---
def cargar_pedidos():
    columnas = ["ID", "Usuario", "Item", "Costo Unitario", "Costo Total", "Costo Servicio", "Comentarios", "Estado", "Fecha", "Activo"]
    if os.path.exists(LOG_FILE):
        try:
            df = pd.read_json(LOG_FILE)
            for col in columnas:
                if col not in df.columns:
                    df[col] = "Pendiente" if col == "Estado" else (0 if "Costo" in col else ("" if col != "Activo" else True))
            return df
        except: pass
    return pd.DataFrame(columns=columnas)

df_l = cargar_pedidos()

st.title("🚚 Tablero de Logística X")

# --- TABLAS PÚBLICAS POR ESTADO ---
st.write("### 📊 Control de Operaciones")
tab1, tab2, tab3 = st.tabs(["⏳ PENDIENTES", "🚧 EN PROCESO", "✅ FINALIZADOS"])

# Filtrar solo registros activos
df_vivos = df_l[df_l["Activo"] == True] if not df_l.empty else pd.DataFrame()

with tab1:
    pends = df_vivos[df_vivos["Estado"] == "Pendiente"]
    if not pends.empty:
        st.dataframe(pends[["ID", "Usuario", "Item", "Fecha"]], use_container_width=True, hide_index=True)
    else: st.info("No hay tareas pendientes en el Universo.")

with tab2:
    proc = df_vivos[df_vivos["Estado"] == "En Proceso"]
    if not proc.empty:
        st.dataframe(proc[["ID", "Usuario", "Item", "Fecha"]], use_container_width=True, hide_index=True)
    else: st.info("No hay nada en proceso actualmente.")

with tab3:
    fin = df_vivos[df_vivos["Estado"].isin(["Completado", "Cancelado"])]
    if not fin.empty:
        st.dataframe(fin[["ID", "Usuario", "Item", "Estado"]], use_container_width=True, hide_index=True)
    else: st.info("El historial de finalizados está limpio.")

# --- REGISTRO PÚBLICO ---
st.divider()
with st.expander("➕ REGISTRAR NUEVO PEDIDO"):
    with st.form("form_logistica", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            u = st.text_input("Usuario / Cliente")
            it = st.text_input("Descripción del Item")
        with col2:
            cu = st.number_input("Costo Unitario", min_value=0.0)
            cs = st.number_input("Costo Servicio", min_value=0.0)
        com = st.text_area("Comentarios / Observaciones")
        
        if st.form_submit_button("🚀 GUARDAR REGISTRO"):
            nid = 1 if df_l.empty else int(df_l["ID"].max() + 1)
            nuevo = pd.DataFrame([{
                "ID": nid, "Usuario": u, "Item": it, "Costo Unitario": cu, 
                "Costo Servicio": cs, "Costo Total": cu + cs, "Comentarios": com,
                "Estado": "Pendiente", "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "Activo": True
            }])
            pd.concat([df_l, nuevo], ignore_index=True).to_json(LOG_FILE, orient='records', indent=4)
            st.success("Sincronizado con el Universo.")
            st.rerun()

# --- GESTIÓN PRIVADA (5050) ---
st.divider()
if st.text_input("🔑 Administración Maestra", type="password") == "5050":
    st.subheader("📋 Gestión de Datos")
    if not df_vivos.empty:
        for idx, row in df_vivos.sort_values(by="ID", ascending=False).iterrows():
            with st.expander(f"⚙️ Gestión Pedido #{row['ID']} - {row['Usuario']}"):
                with st.form(key=f"edit_{row['ID']}"):
                    c1, c2 = st.columns(2)
                    new_u = c1.text_input("Editar Usuario", value=str(row['Usuario']))
                    new_est = c2.selectbox("Cambiar Estado", ["Pendiente", "En Proceso", "Completado", "Cancelado"], index=["Pendiente", "En Proceso", "Completado", "Cancelado"].index(row['Estado']))
                    new_com = st.text_area("Editar Comentarios", value=str(row['Comentarios']))
                    
                    col_b1, col_b2 = st.columns([0.8, 0.2])
                    if col_b1.form_submit_button("💾 ACTUALIZAR"):
                        df_l.at[idx, "Usuario"] = new_u
                        df_l.at[idx, "Estado"] = new_est
                        df_l.at[idx, "Comentarios"] = new_com
                        df_l.to_json(LOG_FILE, orient='records', indent=4)
                        st.rerun()
                    if col_b2.form_submit_button("🗑️"):
                        df_l.at[idx, "Activo"] = False
                        df_l.to_json(LOG_FILE, orient='records', indent=4)
                        st.rerun()