import streamlit as st
import json
import os
import importlib.util
import random
import pandas as pd
from datetime import date, datetime, timedelta

# --- CONFIGURACIÓN DEL UNIVERSO ---
st.set_page_config(page_title="Universo X - Sistema Central", layout="wide")

ARCHIVO_USUARIOS = "usuarios_x.json"

# --- FUNCIONES DE PERSISTENCIA ---
def cargar_usuarios():
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return {}
    return {}

def guardar_usuarios(usuarios):
    with open(ARCHIVO_USUARIOS, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)

def cargar_modulo(nombre_archivo):
    ruta = os.path.join(os.getcwd(), nombre_archivo)
    if os.path.exists(ruta):
        spec = importlib.util.spec_from_file_location("mod", ruta)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
    else: st.error(f"⚠️ Módulo {nombre_archivo} no encontrado.")

# --- ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'modulo_activo' not in st.session_state: st.session_state.modulo_activo = "Lobby"
if 'precios' not in st.session_state:
    st.session_state.precios = {"Microservicio": 3000}

# --- ESTÉTICA ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: white; }
    .card { background: #111; border: 1px solid #333; padding: 20px; border-radius: 10px; text-align: center; }
    h1, h2, h3 { color: #00e6e6 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ACCESO Y REGISTRO ---
if not st.session_state.autenticado and st.session_state.modulo_activo != "F5CO":
    st.title("🚀 Portal de Acceso - Universo X")
    
    # Botón de Acceso Directo a F5CO
    with st.expander("🔑 ACCESO ADMINISTRATIVO F5CO"):
        f5_direct = st.text_input("Llave Maestra", type="password", key="direct_f5")
        if st.button("ENTRAR A TESORERÍA"):
            if f5_direct == "10538":
                st.session_state.modulo_activo = "F5CO"
                st.rerun()
            else: st.error("Llave incorrecta")

    t1, t2 = st.tabs(["INGRESAR", "CREAR CUENTA VIRTUAL"])

    with t1:
        c_id = st.text_input("Número de Celular (ID)", key="login_id")
        c_pw = st.text_input("Código Secreto", type="password", key="login_pw")
        if st.button("SINCRONIZAR"):
            db = cargar_usuarios()
            if c_id in db and db[c_id]["clave"] == c_pw:
                st.session_state.autenticado = True
                st.session_state.user_id = c_id
                st.rerun()
            else: st.error("Credenciales incorrectas.")

    with t2:
        st.subheader("Formulario de Apertura F5CO")
        col_a, col_b = st.columns(2)
        r_cel = col_a.text_input("Número Celular (ID)")
        r_nom = col_b.text_input("Nombre y Apellido")
        r_usr = col_a.text_input("Nombre de Usuario")
        r_nac = col_b.date_input("Fecha de Nacimiento", value=date(2000, 1, 1))
        r_pw  = col_a.text_input("Definir Código Secreto", type="password")
        r_ind = col_b.text_input("Indicio de pregunta")
        r_res = col_a.text_input("Respuesta Secreta")

        if st.button("REGISTRAR EN EL SISTEMA"):
            if r_cel and r_pw and r_res:
                db = cargar_usuarios()
                if r_cel in db: st.warning("El celular ya está registrado.")
                else:
                    n_cuenta = f"X-{random.randint(100000, 999999)}"
                    db[r_cel] = {
                        "nombre_completo": r_nom, "username": r_usr, "nacimiento": str(r_nac),
                        "clave": r_pw, "indicio": r_ind, "respuesta_secreta": r_res,
                        "cuenta_f5co": n_cuenta, "saldo": 0.0, "movimientos": [], "suscripciones": {}
                    }
                    guardar_usuarios(db)
                    st.success(f"Cuenta {n_cuenta} creada.")
            else: st.error("Por favor completa los campos obligatorios.")

# --- PANEL F5CO (GESTIÓN TOTAL) ---
elif st.session_state.modulo_activo == "F5CO":
    st.title("🏦 F5CO - Control Central de Usuarios")
    if st.button("⬅️ VOLVER AL INICIO"):
        st.session_state.modulo_activo = "Lobby"
        st.session_state.autenticado = False
        st.rerun()
    
    db = cargar_usuarios()
    tab1, tab2, tab3 = st.tabs(["💰 CARGAR ABONO", "📊 MOVIMIENTOS", "👤 GESTIÓN DE USUARIOS (EDITAR)"])
    
    with tab1:
        tid = st.text_input("Celular Beneficiario")
        amt = st.number_input("Monto Recibido ($)", min_value=0, step=1000)
        if st.button("APLICAR ABONO"):
            if tid in db:
                db[tid]["saldo"] += amt
                db[tid]["movimientos"].append({"tipo": "Abono Efectivo", "monto": amt, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")})
                guardar_usuarios(db); st.success("Abono cargado."); st.rerun()
            else: st.error("Usuario no encontrado.")

    with tab2:
        sid = st.text_input("Consultar Celular")
        if sid in db:
            st.write(f"### Estado de Cuenta: {db[sid].get('nombre_completo', 'N/A')}")
            st.metric("Saldo Actual", f"${db[sid].get('saldo', 0.0):,}")
            df_movs = pd.DataFrame(db[sid].get("movimientos", []))
            if not df_movs.empty: st.table(df_movs.iloc[::-1])

    with tab3:
        st.subheader("Editor Maestro de usuarios_x.json")
        lista_usuarios = list(db.keys())
        user_select = st.selectbox("Seleccione el usuario a editar", ["Seleccionar..."] + lista_usuarios)
        
        if user_select != "Seleccionar...":
            u_data = db[user_select]
            st.info(f"Editando ID: {user_select} | Cuenta: {u_data.get('cuenta_f5co')}")
            
            with st.form("master_edit"):
                col1, col2 = st.columns(2)
                new_nom = col1.text_input("Nombre Completo", value=u_data.get('nombre_completo', ''))
                new_usr = col2.text_input("Username", value=u_data.get('username', ''))
                new_clave = col1.text_input("Clave Secreta", value=u_data.get('clave', ''))
                new_saldo = col2.number_input("Saldo Manual", value=float(u_data.get('saldo', 0.0)))
                new_indicio = col1.text_input("Indicio Clave", value=u_data.get('indicio', ''))
                new_res = col2.text_input("Respuesta Secreta", value=u_data.get('respuesta_secreta', ''))
                
                if st.form_submit_button("💾 GUARDAR CAMBIOS EN JSON"):
                    db[user_select].update({
                        "nombre_completo": new_nom, "username": new_usr,
                        "clave": new_clave, "saldo": new_saldo,
                        "indicio": new_indicio, "respuesta_secreta": new_res
                    })
                    guardar_usuarios(db)
                    st.success("Archivo actualizado correctamente.")
                    st.rerun()

# --- INTERFAZ LOBBY ---
else:
    db = cargar_usuarios()
    u = db.get(st.session_state.user_id)
    
    nombre_mostrar = u.get('username', u.get('nombre_completo', 'Usuario X'))
    st.sidebar.title(f"👤 {nombre_mostrar}")
    st.sidebar.write(f"💳 Cuenta: **{u.get('cuenta_f5co', 'Sin Cuenta')}**")
    st.sidebar.metric("Saldo F5CO", f"${u.get('saldo', 0.0):,}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False; st.rerun()

    if st.session_state.modulo_activo == "Lobby":
        st.title("🌌 Lobby de Microservicios")
        cols = st.columns(4)
        servicios = [("🚚 Logística", "1_Logistica.py"), ("🚜 Máquinas", "2_Maquinas.py"), 
                     ("🍔 Restaurante", "3_restaurante.py"), ("🐍 CACD", "x_cacd.py")]

        for i, (nom, file) in enumerate(servicios):
            with cols[i]:
                st.markdown(f'<div class="card"><h3>{nom}</h3></div>', unsafe_allow_html=True)
                costo = st.session_state.precios["Microservicio"]
                acceso = False
                if nom in u.get("suscripciones", {}):
                    f_pago = datetime.strptime(u["suscripciones"][nom], "%Y-%m-%d")
                    if datetime.now() < f_pago + timedelta(days=90): acceso = True

                if acceso:
                    if st.button(f"ENTRAR", key=f"btn_{i}"):
                        st.session_state.modulo_activo = file; st.rerun()
                else:
                    if st.button(f"SUSCRIBIR - ${costo:,}", key=f"buy_{i}"):
                        if u["saldo"] >= costo:
                            db[st.session_state.user_id]["saldo"] -= costo
                            db[st.session_state.user_id]["suscripciones"][nom] = str(date.today())
                            db[st.session_state.user_id]["movimientos"].append({
                                "tipo": f"Suscripción {nom}", "monto": -costo, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
                            })
                            guardar_usuarios(db); st.rerun()
    else:
        if st.sidebar.button("⬅️ VOLVER AL LOBBY"):
            st.session_state.modulo_activo = "Lobby"; st.rerun()
        cargar_modulo(st.session_state.modulo_activo)