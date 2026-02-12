import streamlit as st
import pandas as pd
import os
import json

# --- CONFIGURACIÓN DE RUTA PERMANENTE ---
FOLDER_PATH = "PROYECTOS_X"
DB_FILE = os.path.join(FOLDER_PATH, "usuarios_x.json")

# Configuración visual
st.set_page_config(page_title="Software X", page_icon="✖️", layout="wide")

def cargar_datos_permanentes():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_json(DB_FILE, dtype={'celular': str, 'password': str, 'expedicion': str})
        except:
            return pd.DataFrame(columns=['celular', 'nombre', 'expedicion', 'rol', 'password'])
    return pd.DataFrame(columns=['celular', 'nombre', 'expedicion', 'rol', 'password'])

if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.admin = False

# --- PANTALLA DE ACCESO ---
if not st.session_state.auth:
    st.title("Software X")
    
    # Selección de opciones (Sin barra de búsqueda interna)
    menu = st.selectbox("Seleccione una opción para continuar:", 
                        ["Ingresar", "Ingresar Admin", "Registrarse", "Recuperar Contraseña"])

    if menu == "Ingresar Admin":
        st.subheader("Acceso Administrativo")
        admin_pass = st.text_input("Contraseña Maestra", type="password")
        if st.button("ACCEDER AL PANEL"):
            if admin_pass == "2131":
                st.session_state.auth = True
                st.session_state.admin = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")

    elif menu == "Ingresar":
        st.subheader("Inicio de Sesión")
        cel_input = st.text_input("Número de celular")
        pass_input = st.text_input("Contraseña", type="password")
        
        if st.button("ENTRAR"):
            df = cargar_datos_permanentes()
            user = df[(df['celular'] == cel_input) & (df['password'] == pass_input)]
            if not user.empty:
                st.session_state.auth = True
                st.session_state.admin = False
                st.rerun()
            else:
                st.error("Datos incorrectos")

    elif menu == "Registrarse":
        st.subheader("Registro de Nuevo Usuario")
        with st.form("reg_form"):
            nom = st.text_input("Nombre completo")
            cel = st.text_input("Número de celular")
            # Cambio solicitado: Referencia de fecha AAAAMMDD
            exp = st.text_input("Expedición cédula (Referencia: AAAAMMDD)")
            pas = st.text_input("Contraseña")
            if st.form_submit_button("REGISTRAR"):
                df = cargar_datos_permanentes()
                nueva_fila = pd.DataFrame([[cel, nom, exp, 'usuario', pas]], columns=df.columns)
                df_final = pd.concat([df, nueva_fila], ignore_index=True)
                
                if not os.path.exists(FOLDER_PATH):
                    os.makedirs(FOLDER_PATH)
                
                df_final.to_json(DB_FILE, orient='records', indent=4)
                st.success("Registrado con éxito en el Universo X.")

# --- PANEL PRINCIPAL (POST-LOGIN) ---
else:
    st.sidebar.title("Navegación")
    st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.update({"auth": False, "admin": False}))
    
    if st.session_state.admin:
        with st.expander("🛡️ VER USUARIOS REGISTRADOS (ADMIN)"):
            df_usuarios = cargar_datos_permanentes()
            st.dataframe(df_usuarios)

    st.title("Universo Central X")
    st.write("Seleccione el sub-Universo al que desea acceder:")
    st.divider()

    # Layout de Sub-Universos
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🚚 Logística")
        if st.button("Abrir Logística_X"):
            st.info("Espacio listo para vincular código de logística_x")
            # Aquí irá: import logistica_x

    with col2:
        st.subheader("📦 Alacena")
        if st.button("Abrir Alacena_X"):
            st.info("Espacio listo para vincular código de alacena_x")
            # Aquí irá: import alacena_x

    with col3:
        st.subheader("🍽️ Restaurante")
        if st.button("Abrir Restaurante_X"):
            st.info("Espacio listo para vincular código de restaurante_x")
            # Aquí irá: import restaurante_x

    st.divider()
    st.write("Cada sub-Universo gestionará sus propias bases de datos independientes.")