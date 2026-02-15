import streamlit as st
from datetime import datetime

# --- SEGURIDAD INTERNA DEL MÓDULO ---
if 'cacd_desbloqueado' not in st.session_state:
    st.session_state.cacd_desbloqueado = False

# --- PANTALLA DE ACCESO CACD ---
if not st.session_state.cacd_desbloqueado:
    st.markdown("<h2 style='text-align: center; color: #FFFFFF;'>🔒 Acceso Restringido - CACD</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("Sistema de Registro de Accidentes Ofídicos")
        cedula_input = st.text_input("Ingrese los 5 primeros números de la cédula", type="password")
        if st.button("DESBLOQUEAR FORMULARIO"):
            if cedula_input == "10254":
                st.session_state.cacd_desbloqueado = True
                st.rerun()
            else:
                st.error("Llave incorrecta. Acceso denegado.")

# --- FORMULARIO MÉDICO (Solo se muestra si la llave es correcta) ---
else:
    st.markdown("<h1 style='text-align: center; color: #FFFFFF;'>🐍 Reporte Clínico de Accidente Ofídico</h1>", unsafe_allow_html=True)
    
    if st.sidebar.button("🔒 CERRAR SESIÓN MÉDICA"):
        st.session_state.cacd_desbloqueado = False
        st.rerun()

    # --- 1. INFORMACIÓN DEL PACIENTE ---
    st.subheader("1. Información del Paciente")
    c1, c2 = st.columns(2)
    with c1:
        nombre = st.text_input("Nombre Completo")
        documento = st.text_input("Documento de Identidad")
        edad = st.number_input("Edad", min_value=0, max_value=120)
    with c2:
        genero = st.selectbox("Género", ["Hombre", "Mujer", "Otro"])
        ocupacion = st.text_input("Ocupación")

    st.divider()

    # --- 2. DETALLES DEL ACCIDENTE ---
    st.subheader("2. Detalles del Accidente")
    c3, c4 = st.columns(2)
    with c3:
        fecha_accidente = st.date_input("Fecha del Accidente", value=datetime.now())
        hora_accidente = st.time_input("Hora del Accidente")
        lugar = st.text_input("Lugar del Accidente (Municipio/Vereda)")
    with c4:
        serpiente_traida = st.radio("¿La serpiente fue traída?", ["Sí", "No"])
        nombre_popular = st.text_input("Nombre popular de la serpiente")
        sitio_mordedura = st.text_input("Sitio anatómico de la mordedura")

    st.text_area("Descripción de la serpiente y estado inicial del paciente")

    st.divider()

    # --- 3. HALLAZGOS Y SÍNTOMAS ---
    st.subheader("3. Grado de Envenenamiento y Manifestaciones")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("**Hallazgos Locales:**")
        st.checkbox("Dolor")
        st.checkbox("Edema")
        st.checkbox("Hemorragia local")
        st.checkbox("Equimosis")
        st.checkbox("Necrosis")
    
    with col_b:
        st.write("**Manifestaciones Sistémicas:**")
        st.checkbox("Fiebre")
        st.checkbox("Malestar general")
        st.checkbox("Emesis")
        st.checkbox("Hematuria")
        st.checkbox("Hemorragia SNC")

    st.divider()

    if st.button("💾 GUARDAR REPORTE EN UNIVERSO X"):
        st.success(f"Reporte de {nombre} registrado exitosamente.")
        st.balloons()