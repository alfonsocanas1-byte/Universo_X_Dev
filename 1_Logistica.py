import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN DE RUTAS ---
FOLDER_PATH = "PROYECTOS_X"
LOG_FILE = os.path.join(FOLDER_PATH, "pedidos_logistica.json")

# Asegurar que la carpeta existe
if not os.path.exists(FOLDER_PATH):
    os.makedirs(FOLDER_PATH)

# --- ESTÉTICA DARK TOTAL (NEGRO Y BLANCO) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2, h3, h4, h5, h6, p, div, span, label, .stMarkdown { color: #FFFFFF !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: #000000; gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1A1A1A !important;
        color: #888888 !important;
        border: 1px solid #333 !important;
        border-radius: 5px 5px 0px 0px;
        padding: 10px 20px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    .stExpander { background-color: #111111 !important; border: 1px solid #333 !important; }
    .stButton>button { width: 100%; background-color: #FFFFFF; color: #000000; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #CCCCCC; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIÓN DE CARGA DE DATOS (CORREGIDA) ---
def cargar_pedidos():
    columnas = ["ID", "Usuario", "Item", "Costo Unitario", "Costo Total", "Costo Servicio", "Comentarios", "Estado", "Fecha", "Activo"]
    if os.path.exists(LOG_FILE):
        try:
            df = pd.read_json(LOG_FILE)
            if df.empty:
                return pd.DataFrame(columns=columnas)
            # Asegurar que todas las columnas existan para evitar KeyErrors
            for col in columnas:
                if col not in df.columns:
                    if col == "Estado": df[col] = "Pendiente"
                    elif col == "Activo": df[col] = True
                    else: df[col] = 0 if "Costo" in col else ""
            return df
        except:
            return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

# Inicializar datos
df_l = cargar_pedidos()

# --- TÍTULO ---
st.title("📦 TABLERO DE LOGÍSTICA X")
st.write(f"Gestión de flujos de trabajo - {datetime.now().strftime('%d/%m/%Y')}")

# --- FORMULARIO DE NUEVO PEDIDO ---
with st.expander("➕ REGISTRAR NUEVO PEDIDO"):
    with st.form("form_nuevo_pedido", clear_on_submit=True):
        c1, c2 = st.columns(2)
        usuario = c1.text_input("Usuario / Cliente")
        item = c2.text_input("Item / Producto")
        
        c3, c4, c5 = st.columns(3)
        c_uni = c3.number_input("Costo Unitario", min_value=0.0)
        c_tot = c4.number_input("Costo Total", min_value=0.0)
        c_ser = c5.number_input("Costo Servicio", min_value=0.0)
        
        comentarios = st.text_area("Comentarios Iniciales")
        
        if st.form_submit_button("REGISTRAR EN LOGÍSTICA"):
            nuevo_id = int(df_l["ID"].max() + 1) if not df_l.empty else 1
            nuevo_registro = {
                "ID": nuevo_id,
                "Usuario": usuario,
                "Item": item,
                "Costo Unitario": c_uni,
                "Costo Total": c_tot,
                "Costo Servicio": c_ser,
                "Comentarios": comentarios,
                "Estado": "Pendiente",
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Activo": True
            }
            df_l = pd.concat([df_l, pd.DataFrame([nuevo_registro])], ignore_index=True)
            df_l.to_json(LOG_FILE, indent=4)
            st.success("Pedido registrado exitosamente")
            st.rerun()

# --- FILTRADO PARA PESTAÑAS ---
# Usamos una copia segura para evitar errores si está vacío
df_vivos = df_l[df_l["Activo"] == True] if not df_l.empty else pd.DataFrame(columns=df_l.columns)

t1, t2, t3 = st.tabs(["⏳ PENDIENTES", "⚙️ EN PROCESO", "✅ FINALIZADOS"])

def mostrar_pedidos(dataframe, estado):
    sub_df = dataframe[dataframe["Estado"] == estado]
    if sub_df.empty:
        st.info(f"No hay pedidos en estado: {estado}")
    else:
        for _, row in sub_df.iterrows():
            with st.container():
                st.markdown(f"""
                **#{row['ID']} | {row['Usuario']}** 📦 {row['Item']} | 💰 ${row['Costo Total']}  
                📝 {row['Comentarios']}
                """)
                st.divider()

with t1: mostrar_pedidos(df_vivos, "Pendiente")
with t2: mostrar_pedidos(df_vivos, "En Proceso")
with t3: mostrar_pedidos(df_vivos, "Completado")

# --- GESTIÓN ADMINISTRATIVA (PASSWORD: 5050) ---
st.divider()
if st.text_input("🔑 Administración Maestra", type="password") == "5050":
    st.subheader("📋 Gestión de Datos")
    if not df_vivos.empty:
        for idx, row in df_vivos.sort_values(by="ID", ascending=False).iterrows():
            with st.expander(f"⚙️ Gestión Pedido #{row['ID']} - {row['Usuario']}"):
                with st.form(key=f"edit_{row['ID']}"):
                    c1, c2 = st.columns(2)
                    new_u = c1.text_input("Editar Usuario", value=str(row['Usuario']))
                    
                    # Asegurar índice correcto del selectbox
                    estados_posibles = ["Pendiente", "En Proceso", "Completado", "Cancelado"]
                    try:
                        idx_est = estados_posibles.index(row['Estado'])
                    except:
                        idx_est = 0
                        
                    new_est = c2.selectbox("Cambiar Estado", estados_posibles, index=idx_est)
                    new_com = st.text_area("Editar Comentarios", value=str(row['Comentarios']))
                    
                    col_b1, col_b2 = st.columns([0.8, 0.2])
                    if col_b1.form_submit_button("💾 ACTUALIZAR"):
                        df_l.at[idx, "Usuario"] = new_u
                        df_l.at[idx, "Estado"] = new_est
                        df_l.at[idx, "Comentarios"] = new_com
                        df_l.to_json(LOG_FILE, indent=4)
                        st.success("Actualizado")
                        st.rerun()
                    
                    if col_b2.form_submit_button("🗑️"):
                        df_l.at[idx, "Activo"] = False
                        df_l.to_json(LOG_FILE, indent=4)
                        st.warning("Archivado")
                        st.rerun()
    else:
        st.write("No hay datos activos para gestionar.")