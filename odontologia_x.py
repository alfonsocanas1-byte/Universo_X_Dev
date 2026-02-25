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
    .odont-card { background: #111; border-top: 4px solid #00e6e6; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .stButton>button { border-color: #00e6e6 !important; color: #fff !important; }
    .sidebar .sidebar-content { background-image: linear-gradient(#2e7bcf,#2e7bcf); color: white; }
    </style>
""", unsafe_allow_html=True)

# --- ESTADO DE ACCESO ESPECIAL ---
if 'acceso_maestro_odont' not in st.session_state:
    st.session_state.acceso_maestro_odont = False

def odontologia_main():
    # Datos del usuario que viene del Hub
    u_id = st.session_state.get('user_id', 'S/N')
    db_u = cargar_json(ARCHIVO_USUARIOS)
    user_info = db_u.get(u_id, {})
    nombre_usuario = user_info.get('nombre_completo', 'Paciente')

    st.title("🦷 Ecosistema Odontológico X")
    st.write(f"Bienvenido/a, **{nombre_usuario}**")

    # --- NAVEGACIÓN LATERAL ---
    opciones = ["Mis Procedimientos", "Software de Cepillado", "Diseño de Sonrisa IA", "🔐 ACCESO PROFESIONAL"]
    menu = st.sidebar.radio("Módulos Disponibles", opciones)

    # 1. MIS PROCEDIMIENTOS
    if menu == "Mis Procedimientos":
        st.header("📂 Mis Procedimientos y Seguimiento")
        st.info(f"Visualizando registros de: {nombre_usuario}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='odont-card'><h4>Subir Seguimiento</h4></div>", unsafe_allow_html=True)
            foto = st.file_uploader("Cargar foto de mi tratamiento", type=['jpg', 'png'], key="user_proc")
            if foto:
                st.image(foto, caption="Imagen registrada en su historial")
        
        with col2:
            st.markdown("<div class='odont-card'><h4>Estatus Actual</h4></div>", unsafe_allow_html=True)
            st.success("✅ Próxima cita sugerida: Revisar con administración.")

    # 2. SOFTWARE DE CEPILLADO
    elif menu == "Software de Cepillado":
        st.header("🪥 Asistente de Higiene Bucal")
        st.write("Sigue el ritmo para un cepillado perfecto.")
        if st.button("INICIAR TEMPORIZADOR"):
            st.info("⌛ Iniciando ciclo de 2 minutos...")
            st.progress(0.3)
            st.write("Fase 1: Zona superior derecha...")

    # 3. DISEÑO DE SONRISA IA
    elif menu == "Diseño de Sonrisa IA":
        st.header("🧬 Simulador IA")
        st.write("Sube una foto de tu sonrisa para ver el potencial del diseño X.")
        img_ia = st.file_uploader("Foto frontal", type=['jpg', 'png'], key="ia_smile")
        if img_ia:
            st.image(img_ia)
            with st.spinner("IA analizando proporciones..."):
                st.success("Sugerencia IA: Blanqueamiento Grado 2 y ajuste estético leve.")

    # 4. ACCESO PROFESIONAL (LLAVE SOL27)
    elif menu == "🔐 ACCESO PROFESIONAL":
        if not st.session_state.acceso_maestro_odont:
            st.header("Validación de Credenciales")
            with st.form("llave_odont"):
                llave = st.text_input("Ingrese llave profesional", type="password")
                if st.form_submit_button("DESBLOQUEAR TODO"):
                    if llave == "sol27":
                        st.session_state.acceso_maestro_odont = True
                        st.success("Acceso Profesional Concedido. Ahora puede ver el Panel Total.")
                        st.rerun()
                    else:
                        st.error("Llave incorrecta.")
        else:
            st.header("🌟 PANEL DE CONTROL TOTAL (Sol / Maestro)")
            st.markdown("<div class='odont-card'><h4>Gestión de Pacientes</h4></div>", unsafe_allow_html=True)
            # Aquí Sol vería la lista de todos los pacientes del JSON
            st.write("Lista de pacientes registrados:")
            st.dataframe(list(db_u.keys()))
            
            if st.button("CERRAR SESIÓN PROFESIONAL"):
                st.session_state.acceso_maestro_odont = False
                st.rerun()

# Ejecutar
odontologia_main()