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

# --- ESTÉTICA DE ALTO CONTRASTE (Letras Negras Reales) ---
st.markdown("""
    <style>
    /* Fondo principal negro */
    .stApp { background-color: #000; color: #FFFFFF; }
    
    /* FORZAR LETRAS NEGRAS EN SIDEBAR */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        color: #000000 !important;
        font-weight: 700 !important;
    }

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
    .patient-welcome { color: #ffffff; font-size: 20px; margin-bottom: 20px; }
    .instruction { 
        background-color: #00e6e6; 
        color: #000 !important; 
        padding: 8px 15px; 
        border-radius: 50px; 
        font-weight: bold;
        display: inline-block;
    }

    /* Tarjetas de módulos */
    .odont-card { background: #111; border-left: 5px solid #00e6e6; padding: 20px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

if 'acceso_maestro_odont' not in st.session_state:
    st.session_state.acceso_maestro_odont = False

def odontologia_main():
    u_id = st.session_state.get('user_id', 'S/N')
    db_u = cargar_json(ARCHIVO_USUARIOS)
    user_info = db_u.get(u_id, {})
    nombre_paciente = user_info.get('nombre_completo', 'Paciente')

    # --- DISEÑO DE BIENVENIDA ---
    st.markdown(f"""
    <div class="welcome-box">
        <div class="dr-name">Dra. Sol Rojas</div>
        <div style="color: #ccc; letter-spacing: 2px; margin-bottom: 15px;">CONSULTORIO ODONTOLÓGICO</div>
        <div class="patient-welcome">¡Hola, <b>{nombre_paciente}</b>! Es un placer recibirte.</div>
        <div class="instruction">👈 Accede a los módulos en la barra de la izquierda</div>
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
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='odont-card'><h4>Evolución</h4><p>Sube tus fotos de control aquí.</p></div>", unsafe_allow_html=True)
            st.file_uploader("Subir imagen", type=['jpg', 'png'], key="up")
        with col2:
            st.markdown("<div class='odont-card'><h4>Próximos Pasos</h4><p>Consulta tu estado actual.</p></div>", unsafe_allow_html=True)
            st.success("Tratamiento en curso.")

    elif menu == "Software de Cepillado":
        st.header("🪥 Guía de Higiene")
        if st.button("INICIAR ASISTENTE"):
            st.info("⌛ Iniciando cronómetro profesional...")

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
            st.write("Base de Datos de Pacientes:")
            st.dataframe(pd.DataFrame([{"ID": k, "Paciente": v.get('nombre_completo')} for k, v in db_u.items()]))
            if st.button("SALIR DEL PANEL"):
                st.session_state.acceso_maestro_odont = False
                st.rerun()

odontologia_main()