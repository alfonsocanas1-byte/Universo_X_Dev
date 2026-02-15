import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Software X", layout="centered")

DB_FILE = "usuarios_x.csv"

if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=['celular', 'nombre', 'expedicion', 'rol', 'password']).to_csv(DB_FILE, index=False)

if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.admin = False

if not st.session_state.auth:
    st.title("Software X")
    opcion = st.selectbox("Menú", ["Ingresar", "Registrarse", "Recuperar Contraseña"])

    if opcion == "Registrarse":
        with st.form("f_reg"):
            n = st.text_input("Nombre completo")
            c = st.text_input("Celular")
            e = st.text_input("Expedición cédula")
            p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("REGISTRAR"):
                df = pd.read_csv(DB_FILE)
                nuevo = pd.DataFrame([[c, n, e, 'usuario', p]], columns=df.columns)
                pd.concat([df, nuevo], ignore_index=True).to_csv(DB_FILE, index=False)
                st.success("Registrado. Cambia a 'Ingresar' para entrar.")

    elif opcion == "Ingresar":
        u = st.text_input("Celular / Admin")
        p = st.text_input("Contraseña", type="password")
        if st.button("ENTRAR"):
            if u == "2131" and p == "2131":
                st.session_state.auth, st.session_state.admin = True, True
                st.rerun()
            else:
                df = pd.read_csv(DB_FILE)
                user = df[(df['celular'].astype(str) == u) & (df['password'].astype(str) == p)]
                if not user.empty:
                    st.session_state.auth, st.session_state.admin = True, False
                    st.rerun()
                else: st.error("Datos incorrectos")

    elif opcion == "Recuperar Contraseña":
        c_v = st.text_input("Celular")
        e_v = st.text_input("Expedición")
        n_p = st.text_input("Nueva Clave", type="password")
        if st.button("CAMBIAR"):
            df = pd.read_csv(DB_FILE)
            mask = (df['celular'].astype(str) == c_v) & (df['expedicion'].astype(str) == e_v)
            if not df[mask].empty:
                df.loc[mask, 'password'] = n_p
                df.to_csv(DB_FILE, index=False)
                st.success("Clave actualizada")
            else: st.error("No coinciden los datos")

else:
    st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.update({"auth": False}))
    if st.session_state.admin:
        st.header("ADMINISTRADOR")
        st.dataframe(pd.read_csv(DB_FILE))
    
    st.header("Seleccione Destino")
    c1, c2 = st.columns(2)
    if c1.button("MÁQUINAS", use_container_width=True): st.info("Entrando a Máquinas...")
    if c2.button("LOGÍSTICA", use_container_width=True): st.info("Entrando a Logística...")