import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN DE DATOS ---
ARCHIVO_USUARIOS = "usuarios_x.json"

def cargar_json(ruta):
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return {}
    return {}

# --- ESTÉTICA ODONTOLOGÍA X ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: #FFFFFF; }
    .odont-card { background: #111; border-top: 4px solid #00e6e6; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .stButton>button { border-color: #00e6e6 !important; color: #fff !important; width: 100%; }
    /* Letras blancas para el menú lateral de odontología */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- ESTADO DE ACCESO PROFESIONAL ---
if 'acceso_maestro_odont' not in st.session_state:
    st.session_state.acceso_maestro_odont = False

def odontologia_main():
    # Recuperamos el ID del Hub
    u_id = st.session_state.get('user_id', 'S/N')
    db_u = cargar_json(ARCHIVO_USUARIOS)
    user_info = db_u.get(u_id, {})
    nombre_paciente = user_info.get('nombre_completo', 'Usuario')

    st.title("🦷 Ecosistema Odontológico X")
    st.write(f"Paciente: **{nombre_paciente}** | ID: {u_id}")

    # --- NAVEGACIÓN LATERAL (DISPONIBLE PARA TODOS) ---
    st.sidebar.markdown("### 🛠️ Módulos Disponibles")
    menu = st.sidebar.radio("", 
                            ["Mis Procedimientos", 
                             "Software de Cepillado", 
                             "Diseño de Sonrisa IA", 
                             "🔐 ACCESO PROFESIONAL"])

    # 1. MIS PROCEDIMIENTOS
    if menu == "Mis Procedimientos":
        st.header("📂 Mis Procedimientos y Seguimiento")
        st.info(f"Visualizando registros de: {nombre_paciente}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='odont-card'><h4>Subir Seguimiento</h4></div>", unsafe_allow_html=True)
            foto = st.file_uploader("Cargar foto de mi tratamiento", type=['jpg', 'png', 'jpeg'], key="user_proc")
            if foto:
                st.image(foto, caption="Imagen registrada en su historial")
        
        with col2:
            st.markdown("<div class='odont-card'><h4>Estatus Actual</h4></div>", unsafe_allow_html=True)
            st.success("✅ Próxima cita sugerida: Revisar con administración.")

    # 2. SOFTWARE DE CEPILLADO
    elif menu == "Software de Cepillado":
        st.header("🪥 Asistente de Higiene Bucal")
        st.write("Sigue el ritmo para un cepillado perfecto.")
        if st.button("INICIAR TEMPORIZADOR DE 2 MINUTOS"):
            st.info("⌛ Iniciando ciclo...")
            st.progress(0.4)
            st.write("Fase 1: Zona superior derecha (Molares)...")

    # 3. DISEÑO DE SONRISA IA
    elif menu == "Diseño de Sonrisa IA":
        st.header("🧬 Simulador IA de Sonrisa")
        st.write("Sube una foto frontal para analizar proporciones estéticas.")
        img_ia = st.file_uploader("Foto frontal sonriendo", type=['jpg', 'png'], key="ia_smile")
        if img_ia:
            st.image(img_ia)
            with st.spinner("IA analizando proporciones áureas..."):
                st.success("Análisis completo: Sugerencia de blanqueamiento y carillas en sectores 11 y 21.")

    # 4. ACCESO PROFESIONAL (LLAVE SOL27)
    elif menu == "🔐 ACCESO PROFESIONAL":
        if not st.session_state.acceso_maestro_odont:
            st.header("Validación Profesional")
            with st.form("llave_odont"):
                llave = st.text_input("Ingrese llave profesional", type="password")
                if st.form_submit_button("DESBLOQUEAR PANEL TOTAL"):
                    if llave == "sol27":
                        st.session_state.acceso_maestro_odont = True
                        st.success("Acceso Profesional Concedido.")
                        st.rerun()
                    else:
                        st.error("Llave incorrecta.")
        else:
            st.header("🌟 PANEL DE CONTROL TOTAL (SOL)")
            st.markdown("<div class='odont-card'><h4>Gestión Global de Pacientes</h4></div>", unsafe_allow_html=True)
            st.write("Registros en base de datos:")
            st.dataframe(pd.DataFrame([{"ID": k, "Nombre": v.get('nombre_completo')} for k, v in db_u.items()]))
            
            if st.button("CERRAR SESIÓN PROFESIONAL"):
                st.session_state.acceso_maestro_odont = False
                st.rerun()

import pandas as pd # Necesario para la tabla profesional
odontologia_main()