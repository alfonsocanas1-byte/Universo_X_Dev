import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import pytz

# --- CONFIGURACIÓN DE RUTAS ---
FOLDER_PATH = "PROYECTOS_X"
MAQ_FILE = os.path.join(FOLDER_PATH, "placa-llavesmaquinas.json")
FUEL_FILE = os.path.join(FOLDER_PATH, "tanqueos_x.json")
ZONA_HORARIA = pytz.timezone('America/Bogota')

# --- ESTÉTICA DARK TOTAL ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2, h3, p, label, .stMarkdown { color: #FFFFFF !important; }
    input, [data-baseweb="input"], [data-baseweb="select"] {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border: 1px solid #4B4B4B !important;
    }
    div.stButton > button, div.stFormSubmitButton > button {
        background-color: #000000 !important; 
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important; 
        font-weight: bold;
        width: 100% !important;
        border-radius: 5px;
    }
    .tanqueo-card {
        background-color: #111111;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .eficiencia-badge {
        background-color: #FFFFFF;
        color: #000000;
        padding: 2px 8px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 0.85em;
    }
    </style>
    """, unsafe_allow_html=True)

def cargar_json(ruta):
    if os.path.exists(ruta):
        with open(ruta, "r") as f:
            try: return json.load(f)
            except: return {} if "llave" in ruta else []
    return {} if "llave" in ruta else []

def guardar_json(data, ruta):
    with open(ruta, "w") as f:
        json.dump(data, f, indent=4)

st.title("🚜 GESTIÓN DE MAQUINARIA")

opcion = st.selectbox("Operación:", ["Validar para Tanqueo", "Vincular nueva placa-llave", "Panel Administrativo"])
st.divider()

# --- SECCIÓN 1: TANQUEO Y RENDIMIENTO ---
if opcion == "Validar para Tanqueo":
    if 'validado_tanqueo' not in st.session_state:
        st.session_state.validado_tanqueo = False

    if not st.session_state.validado_tanqueo:
        with st.form("login_tanqueo"):
            placa_in = st.text_input("Placa").upper().strip()
            llave_in = st.text_input("Llave", type="password").strip()
            if st.form_submit_button("INGRESAR"):
                db_m = cargar_json(MAQ_FILE)
                if placa_in in db_m and db_m[placa_in]['llave'] == llave_in:
                    st.session_state.validado_tanqueo = True
                    st.session_state.placa_activa = placa_in
                    st.rerun()
                else: st.error("Acceso denegado.")
    else:
        st.success(f"✅ Vehículo: {st.session_state.placa_activa}")
        tanqueos_all = cargar_json(FUEL_FILE)
        hist_placa = [t for t in tanqueos_all if t.get("Placa") == st.session_state.placa_activa]
        ultimo_odo = hist_placa[-1]["Odometro"] if hist_placa else 0
        
        with st.form("reg_fuel"):
            st.write("### Registrar Nuevo Tanqueo")
            gal = st.number_input("Galones Actuales", min_value=0.1, step=0.1)
            odo = st.number_input(f"Odómetro Actual (Anterior: {ultimo_odo})", min_value=float(ultimo_odo))
            
            if st.form_submit_button("💾 GUARDAR"):
                rend = round((odo - ultimo_odo) / gal, 2) if ultimo_odo > 0 else 0.0
                nuevo = {
                    "ID_Tanqueo": f"{st.session_state.placa_activa}-{datetime.now().strftime('%y%m%d%H%M')}",
                    "Placa": st.session_state.placa_activa,
                    "Galones": gal,
                    "Odometro": odo,
                    "Km_Galon": rend,
                    "Fecha": datetime.now(ZONA_HORARIA).strftime("%Y-%m-%d %H:%M")
                }
                tanqueos_all.append(nuevo)
                guardar_json(tanqueos_all, FUEL_FILE)
                st.success(f"¡Guardado! Rendimiento: {rend} km/gal")
                st.rerun()
        
        if st.button("🔴 CERRAR SESIÓN"):
            st.session_state.validado_tanqueo = False
            st.rerun()

        st.write("### 📊 Tu Historial de Rendimiento")
        for t in reversed(hist_placa):
            st.markdown(f"""
            <div class="tanqueo-card">
                <div style="display: flex; justify-content: space-between;">
                    <b>📅 {t['Fecha']}</b>
                    <span class="eficiencia-badge">{t.get('Km_Galon', 0.0)} km/gal</span>
                </div>
                <div style="font-size: 0.9em; color: #AAA;">⛽ {t['Galones']} Gal | 🛣️ {t['Odometro']} km</div>
            </div>
            """, unsafe_allow_html=True)

# --- SECCIÓN 2: VINCULAR PLACA-LLAVE ---
elif opcion == "Vincular nueva placa-llave":
    st.subheader("🔗 Registro de Nueva Maquinaria")
    with st.form("vinculo_form"):
        p_new = st.text_input("Placa Nueva").upper().strip()
        l_new = st.text_input("Asignar Llave", type="password").strip()
        r_new = st.text_input("Responsable")
        if st.form_submit_button("VINCULAR AL SISTEMA"):
            if p_new and l_new:
                db_m = cargar_json(MAQ_FILE)
                db_m[p_new] = {
                    "llave": l_new,
                    "responsable": r_new,
                    "fecha": datetime.now(ZONA_HORARIA).strftime("%Y-%m-%d")
                }
                guardar_json(db_m, MAQ_FILE)
                st.success(f"Placa {p_new} vinculada correctamente.")
            else: st.warning("Placa y Llave son obligatorias.")

# --- SECCIÓN 3: PANEL ADMINISTRATIVO (0303) ---
elif opcion == "Panel Administrativo":
    st.subheader("🛠️ Control Maestro")
    if st.text_input("🔑 Llave Maestra", type="password") == "0303":
        tab1, tab2, tab3 = st.tabs(["📜 Tabla General", "🚜 Máquinas Registradas", "🔍 Buscador/Editor"])
        
        with tab1:
            data_f = cargar_json(FUEL_FILE)
            if data_f:
                df = pd.DataFrame(data_f)
                st.write("### Historial Global de Tanqueos")
                st.dataframe(df.sort_values(by='Fecha', ascending=False), use_container_width=True, hide_index=True)
                st.metric("Total Galones", f"{df['Galones'].sum():,.1f} G")
            else: st.info("Sin registros de tanqueo.")

        with tab2:
            st.write("### Base de Datos Placa-Llave")
            db_admin = cargar_json(MAQ_FILE)
            if db_admin:
                registros = []
                for placa, datos in db_admin.items():
                    fila = {"Placa": placa}
                    fila.update(datos)
                    registros.append(fila)
                df_maq = pd.DataFrame(registros)
                st.dataframe(df_maq, use_container_width=True, hide_index=True)
            else:
                st.info("No hay máquinas vinculadas actualmente.")

        with tab3:
            p_edit = st.text_input("Buscar Placa para editar tanqueos").upper().strip()
            if p_edit:
                tanqueos_all = cargar_json(FUEL_FILE)
                for idx, t in enumerate(tanqueos_all):
                    if t.get("Placa") == p_edit:
                        with st.expander(f"Editar registro: {t['Fecha']}"):
                            with st.form(key=f"ed_{idx}"):
                                n_gal = st.number_input("Galones", value=float(t['Galones']))
                                n_odo = st.number_input("Odómetro", value=float(t['Odometro']))
                                if st.form_submit_button("GUARDAR"):
                                    tanqueos_all[idx].update({"Galones": n_gal, "Odometro": n_odo})
                                    guardar_json(tanqueos_all, FUEL_FILE)
                                    st.success("Dato actualizado.")
                                    st.rerun()