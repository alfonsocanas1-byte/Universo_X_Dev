import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time

# --- CONFIGURACIÓN DE RUTAS ---
FOLDER_PATH = "PROYECTOS_X"
LOG_FILE = os.path.join(FOLDER_PATH, "pedidos_logistica.json")

st.set_page_config(page_title="Universo X", page_icon="✖️", layout="wide")

# --- ESTÉTICA DEL UNIVERSO ---
def aplicar_tema_oscuro():
    st.markdown("""
        <style>
        .stApp { background-color: #0E1117; color: #FFFFFF; }
        h1, h2, h3, p, span, label, .stMarkdown { color: #FFFFFF !important; }
        
        div.stButton > button {
            background-color: #000000 !important; 
            color: #FFFFFF !important;
            border: 1px solid #4B4B4B !important; 
            border-radius: 5px !important;
            width: 100%;
            font-weight: bold;
        }
        
        /* Cuadros de Estado Rápidos */
        .status-box {
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            margin-bottom: 10px;
            border: 1px solid #4B4B4B;
        }
        .st-pendiente { background-color: #2E3136; color: #ADB5BD; }
        .st-proceso { background-color: #856404; color: #FFEEBA; }
        .st-completado { background-color: #155724; color: #D4EDDA; }
        
        .pedido-card {
            background-color: #1A1A1A;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #4B4B4B;
            margin-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

aplicar_tema_oscuro()

def cargar_pedidos():
    if os.path.exists(LOG_FILE):
        try: return pd.read_json(LOG_FILE)
        except: return pd.DataFrame(columns=["ID", "Usuario", "Items", "Costo Total", "Estado", "Fecha"])
    return pd.DataFrame(columns=["ID", "Usuario", "Items", "Costo Total", "Estado", "Fecha"])

def guardar_pedidos(df):
    if not os.path.exists(FOLDER_PATH): os.makedirs(FOLDER_PATH)
    df.to_json(LOG_FILE, orient='records', indent=4)

if 'llave_general' not in st.session_state: st.session_state.llave_general = False
if 'vista' not in st.session_state: st.session_state.vista = "menu"
if 'maestra_activa' not in st.session_state: st.session_state.maestra_activa = False

if not st.session_state.llave_general:
    st.title("✖️ Sistema Central X")
    llave = st.text_input("Llave General", type="password", key=f"acceso_{int(time.time()/60)}")
    if st.button("INGRESAR AL UNIVERSO"):
        if llave == "2222":
            st.session_state.llave_general = True
            st.rerun()
        else: st.error("Llave incorrecta.")

else:
    col_t, col_l = st.columns([0.8, 0.2])
    with col_t: st.title("✖️ Universo Central X")
    with col_l:
        if st.button("🔴 Salir"):
            st.session_state.llave_general = False
            st.session_state.vista = "menu"
            st.session_state.maestra_activa = False
            st.rerun()

    st.divider()

    if st.session_state.vista == "menu":
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🚚 Logística", use_container_width=True):
                st.session_state.vista = "logistica"
                st.rerun()
        with c2: st.button("⚙️ Máquinas", use_container_width=True)
        with c3: st.button("🍽️ Restaurante", use_container_width=True)

    elif st.session_state.vista == "logistica":
        st.subheader("🚚 Logística - Sebastián")
        if st.button("⬅️ Volver"):
            st.session_state.vista = "menu"
            st.rerun()

        # --- NUEVO: CUADROS DE ESTADO POR ID ---
        df_resumen = cargar_pedidos()
        if not df_resumen.empty:
            st.write("**Resumen de Pedidos Activos:**")
            # Mostrar los últimos 5 pedidos de forma horizontal/cuadros
            cols_res = st.columns(5) 
            for i, row in df_resumen.sort_values(by="ID", ascending=False).head(5).iterrows():
                with cols_res[df_resumen.index.get_loc(i) % 5]:
                    clase = "st-pendiente"
                    if row['Estado'] == "En Proceso": clase = "st-proceso"
                    elif row['Estado'] == "Completado": clase = "st-completado"
                    
                    st.markdown(f"""
                        <div class="status-box {clase}">
                            ID: {row['ID']}<br>{row['Estado']}
                        </div>
                    """, unsafe_allow_html=True)
        
        st.divider()

        with st.expander("➕ NUEVO PEDIDO", expanded=False):
            with st.form("form_registro", clear_on_submit=True):
                cliente = st.text_input("Celular Cliente")
                prods = st.text_area("Productos")
                monto = st.number_input("Costo $", min_value=0.0)
                if st.form_submit_button("🚀 GUARDAR"):
                    df = cargar_pedidos()
                    nid = 1 if df.empty else int(df["ID"].max() + 1)
                    nuevo = pd.DataFrame([{"ID": nid, "Usuario": cliente, "Items": prods, "Costo Total": monto, "Estado": "Pendiente", "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M")}])
                    guardar_pedidos(pd.concat([df, nuevo], ignore_index=True))
                    st.success("Guardado."); st.rerun()

        st.divider()
        st.write("### 🔒 Zona Maestra")
        col_m1, col_m2 = st.columns([0.7, 0.3])
        with col_m1:
            maestra = st.text_input("Llave Maestra", type="password", key="maestra_key")
        with col_m2:
            if st.button("EJECUTAR"):
                if maestra == "5050":
                    st.session_state.maestra_activa = True
                else:
                    st.error("Clave Incorrecta")
                    st.session_state.maestra_activa = False

        if st.session_state.maestra_activa:
            df_hist = cargar_pedidos()
            if not df_hist.empty:
                for i, row in df_hist.sort_values(by="ID", ascending=False).iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div class="pedido-card">
                            <strong>🆔 ID: {row['ID']}</strong> | 📅 {row['Fecha']}<br>
                            <strong>👤 Cliente:</strong> {row['Usuario']}<br>
                            <strong>📦 Items:</strong> {row['Items']}<br>
                            <strong>💰 Total:</strong> ${row['Costo Total']} | <strong>Status:</strong> {row['Estado']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        with st.expander(f"📝 Editar Pedido #{row['ID']}"):
                            n_u = st.text_input("Usuario", value=str(row['Usuario']), key=f"u_{row['ID']}")
                            n_i = st.text_area("Items", value=str(row['Items']), key=f"i_{row['ID']}")
                            n_m = st.number_input("Monto", value=float(row['Costo Total']), key=f"m_{row['ID']}")
                            n_e = st.selectbox("Estado", ["Pendiente", "En Proceso", "Completado", "Cancelado"], 
                                             index=["Pendiente", "En Proceso", "Completado", "Cancelado"].index(row['Estado']), key=f"e_{row['ID']}")
                            
                            if st.button("💾 Actualizar", key=f"btn_{row['ID']}"):
                                df_hist.at[i, "Usuario"], df_hist.at[i, "Items"], df_hist.at[i, "Costo Total"], df_hist.at[i, "Estado"] = n_u, n_i, n_m, n_e
                                guardar_pedidos(df_hist)
                                st.success("Actualizado"); st.rerun()