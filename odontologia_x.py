import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# --- CARGA DE DATOS ---
ARCHIVO_USUARIOS = "usuarios_x.json"

def cargar_json(ruta):
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return {}
    return {}

# --- ESTÉTICA MEJORADA (Sidebar con Datos Resaltados) ---
st.markdown("""
    <style>
    /* Fondo principal negro */
    .stApp { background-color: #000; color: #FFFFFF; }
    
    /* FORZAR LETRAS NEGRAS EN MENÚ SIDEBAR */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* RECUADRO DE DATOS DEL USUARIO (Sidebar) */
    .user-info-sidebar {
        background: #00e6e6;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 2px solid #000;
    }
    .user-info-sidebar b { color: #000 !important; }
    .user-info-sidebar span { color: #000 !important; display: block; font-size: 0.9em; }

    /* Caja de Bienvenida Premium */
    .welcome-box {
        background: linear-gradient(145deg, #001a1a, #004d4d);
        padding: 35px;
        border-radius: 20px;
        border: 2px solid #00e6e6;
        box-shadow: 0 10px 30px rgba(0, 230, 230, 0.2);
        margin-bottom: 30px;
        text-align: center;
    }
    .dr-name { color: #00e6e6; font-size: 32px; font-weight: 900; margin-bottom: 5px; }
    .instruction { 
        background-color: #00e6e6; 
        color: #000 !important; 
        padding: 8px 15px; 
        border-radius: 50px; 
        font-weight: bold;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

if 'acceso_maestro_odont' not in st.session_state:
    st.session_state.acceso_maestro_odont = False

def odontologia_main():
    u_id = st.session_state.get('user_id', 'S/N')
    db_u = cargar_json(ARCHIVO_USUARIOS)
    user_info = db_u.get(u_id, {})
    nombre_p = user_info.get('nombre_completo', 'Paciente')
    fecha_v = user_info.get('fecha_vencimiento', 'N/A')

    # --- DATOS EN SIDEBAR (OTRO COLOR) ---
    st.sidebar.markdown(f"""
    <div class="user-info-sidebar">
        <b>👤 PACIENTE:</b><br>
        <span>{nombre_p}</span>
        <hr style="border: 0.5px solid #000; margin: 8px 0;">
        <b>⏳ VENCE:</b><br>
        <span>{fecha_v}</span>
    </div>
    """, unsafe_allow_html=True)

    # --- BIENVENIDA ---
    st.markdown(f"""
    <div class="welcome-box">
        <div class="dr-name">Dra. Sol Rojas</div>
        <div style="color: #ccc; letter-spacing: 2px; margin-bottom: 15px;">CONSULTORIO ODONTOLÓGICO</div>
        <div style="color: #fff; font-size: 20px; margin-bottom: 20px;">¡Hola, <b>{nombre_p}</b>! Es un placer recibirte.</div>
        <div class="instruction">👈 Selecciona un módulo en el menú</div>
    </div>
    """, unsafe_allow_html=True)

    # --- NAVEGACIÓN ---
    st.sidebar.markdown("# 🏥 MENÚ")
    menu = st.sidebar.radio("", 
                            ["Mis Procedimientos", 
                             "Software de Cepillado", 
                             "Diseño de Sonrisa IA", 
                             "🔐 ACCESO PROFESIONAL"])

    if menu == "Mis Procedimientos":
        st.header("📂 Tu Historial Clínico")
        st.file_uploader("Subir foto de control", type=['jpg', 'png'], key="up")

    elif menu == "Software de Cepillado":
        st.header("🪥 Guía de Higiene")
        st.button("INICIAR ASISTENTE")

    elif menu == "Diseño de Sonrisa IA":
        st.header("🧬 Simulación Estética")
        st.file_uploader("Sube tu foto frontal", type=['jpg', 'png'], key="ia")

    elif menu == "🔐 ACCESO PROFESIONAL":
        if not st.session_state.acceso_maestro_odont:
            st.subheader("Área Restringida - Dra. Sol Rojas")
            with st.form("sol_key"):
                llave = st.text_input("Contraseña", type="password")
                if st.form_submit_button("INGRESAR"):
                    if llave == "sol27":
                        st.session_state.acceso_maestro_odont = True
                        st.rerun()
                    else: st.error("Llave incorrecta.")
        else:
            st.header("🌟 PANEL PROFESIONAL")
            st.dataframe(pd.DataFrame([{"ID": k, "Paciente": v.get('nombre_completo')} for k, v in db_u.items()]))
            if st.button("SALIR DEL PANEL"):
                st.session_state.acceso_maestro_odont = False
                st.rerun()

odontologia_main()