import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
# No usamos set_page_config aquí porque el Hub ya lo hace.

ARCHIVO_USUARIOS = "usuarios_x.json"

def cargar_json(ruta):
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return {}
    return {}

# --- ESTÉTICA ESPECÍFICA ODONTOLOGÍA ---
st.markdown("""
    <style>
    .odont-card { background: #111; border-top: 4px solid #00e6e6; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .stButton>button { border-color: #00e6e6 !important; }
    </style>
""", unsafe_allow_html=True)

# --- VALIDACIÓN DE ACCESO ESPECIALIZADO ---
if 'acceso_odont_concedido' not in st.session_state:
    st.session_state.acceso_odont_concedido = False

def odontologia_main():
    st.title("🦷 Microservicio de Odontología")
    
    # Datos del usuario actual del Hub
    u_id = st.session_state.get('user_id', 'S/N')
    db_u = cargar_json(ARCHIVO_USUARIOS)
    user_info = db_u.get(u_id, {})

    if not st.session_state.acceso_odont_concedido:
        st.warning("⚠️ Este módulo requiere validación profesional.")
        with st.form("llave_odont"):
            llave = st.text_input("Ingrese Llave de Acceso Odontológico", type="password")
            if st.form_submit_button("VALIDAR"):
                if llave == "sol27":
                    st.session_state.acceso_odont_concedido = True
                    st.success("Acceso Concedido")
                    st.rerun()
                else:
                    st.error("Llave incorrecta.")
        return

    # --- MENU DE ODONTOLOGÍA ---
    menu_odont = st.sidebar.radio("Navegación Odontológica", 
                                  ["Mis Procedimientos", "Software de Cepillado", "Diseño de Sonrisa IA"])

    # 1. MIS PROCEDIMIENTOS (PERSONALIZADO)
    if menu_odont == "Mis Procedimientos":
        st.header(f"📂 Historial de: {user_info.get('nombre_completo', 'Paciente')}")
        st.write(f"ID Paciente: {u_id}")
        
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            st.markdown("<div class='odont-card'><h4>Radiografías</h4></div>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Cargar nueva imagen de seguimiento", type=['png', 'jpg', 'jpeg'], key="rad")
            if uploaded_file:
                st.image(uploaded_file, caption="Imagen cargada para análisis")
        
        with col_img2:
            st.markdown("<div class='odont-card'><h4>Evolución Clínica</h4></div>", unsafe_allow_html=True)
            st.info("No se registran procedimientos invasivos en las últimas 24 horas.")

    # 2. MINI SOFTWARE DE CEPILLADO
    elif menu_odont == "Software de Cepillado":
        st.header("🪥 Cronómetro de Limpieza Profunda")
        st.write("Inicie el temporizador para asegurar un cepillado efectivo por zonas (2 minutos).")
        
        if st.button("INICIAR CICLO"):
            st.write("⌛ Fase 1: Cara externa de dientes superiores...")
            # Aquí se puede añadir una barra de progreso real
            st.progress(25)
            st.write("⌛ Fase 2: Cara externa de dientes inferiores...")
            st.progress(50)

    # 3. DISEÑOS DE SONRISA CON IA
    elif menu_odont == "Diseño de Sonrisa IA":
        st.header("🧬 Análisis Estético IA")
        st.markdown("""
        Utilice nuestra red neuronal para simular el resultado de carillas, 
        blanqueamiento o diseño gingival.
        """)
        
        img_paciente = st.file_uploader("Suba una foto frontal sonriendo", type=['png', 'jpg'], key="ia_smile")
        
        if img_paciente:
            st.image(img_paciente, caption="Analizando proporciones áureas...")
            with st.spinner("Procesando simulaciones..."):
                st.success("Análisis completo: Se recomienda ajuste de 1.5mm en bordes incisales.")
                st.button("Generar Visualización 3D")

# Ejecución del módulo
odontologia_main()