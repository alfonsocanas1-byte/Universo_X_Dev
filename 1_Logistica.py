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

# Configuración de Zona Horaria Colombia
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
    div.stButton > button {
        background-color: #000000 !important; 
        color: #FFFFFF !important;
        border: 1px solid #4B4B4B !important; 
        font-weight: bold;
        width: 100%;
    }
    .tanqueo-card {
        background-color: #111111;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .eficiencia-badge {
        background-color: #1E1E1E;
        color: #00FF00;
        padding: 2px 8px;
        border-radius: 5px;
        font-weight: bold;
        border: 1px solid #00FF00;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE CARGA Y GUARDADO ---
def cargar_json(ruta):
    if os.path.exists(ruta):
        with open(ruta, "r") as f:
            try: return json.load(f)
            except: return {} if "placa" in ruta else []
    return {} if "placa" in ruta else []

def guardar_json(data, ruta):
    with open(ruta, "w") as f:
        json.dump(data, f, indent=4)

# --- INTERFAZ PRINCIPAL ---
st.title("🚜 GESTIÓN DE MÁQUINAS")

opcion = st.selectbox(
    "Selecciona una operación:", 
    ["Validar para tanqueo", "Vincular nueva placa-llave", "Panel Administrativo"]
)

# Resetear sesión si se cambia de pestaña del menú
if 'opcion_previa' not in st.session_state:
    st.session_state.opcion_previa = opcion

if st.session_state.opcion_previa != opcion:
    st.session_state.validado_tanqueo = False
    st.session_state.opcion_previa = opcion

st.divider()

# --- SECCIÓN 1: VALIDAR PARA TANQUEO ---
if opcion == "Validar para tanqueo":
    if 'validado_tanqueo' not in st.session_state:
        st.session_state.validado_tanqueo = False

    if not st.session_state.validado_tanqueo:
        with st.form("validar_acceso"):
            st.subheader("⛽ Acceso a Tanqueo")
            placa_in = st.text_input("Placa").upper().strip()
            llave_in = st.text_input("Llave", type="password").strip()
            if st.form_submit_button("VALIDAR"):
                db_m = cargar_json(MAQ_FILE)
                if placa_in in db_m and str(db_m[placa_in].get("llave")) == llave_in:
                    st.session_state.validado_tanqueo = True
                    st.session_state.placa_activa = placa_in
                    st.rerun()
                else: st.error("Acceso denegado.")
    else:
        # Cabecera indicando placa activa
        st.success(f"✅ Sesión Activa: {st.session_state.placa_activa}")

        tanqueos_all = cargar_json(FUEL_FILE)
        hist_placa = [t for t in tanqueos_all if t.get("Placa") == st.session_state.placa_activa]
        ultimo_odo = hist_placa[-1]["Odometro"] if hist_placa else 0
        
        # FORMULARIO DE TANQUEO
        with st.form("reg_tanqueo"):
            st.write("### Nuevo Registro")
            gal = st.number_input("Galones", min_value=0.1, step=0.1)
            odo = st.number_input(f"Odómetro (Anterior: {ultimo_odo})", min_value=float(ultimo_odo))
            
            # Botones en paralelo: Guardar y Cerrar Sesión
            col_save, col_logout = st.columns(2)
            
            btn_guardar = col_save.form_submit_button("💾 GUARDAR")
            btn_cerrar = col_logout.form_submit_button("🔴 CERRAR SESIÓN")

            if btn_guardar:
                ahora_co = datetime.now(ZONA_HORARIA)
                rend = round((odo - ultimo_odo) / gal, 2) if ultimo_odo > 0 else 0.0
                
                nuevo = {
                    "ID_Tanqueo": f"{st.session_state.placa_activa}-{ahora_co.strftime('%y%m%d%H%M')}",
                    "Placa": st.session_state.placa_activa,
                    "Galones": gal, "Odometro": odo, "Km_Galon": rend,
                    "Fecha": ahora_co.strftime("%Y-%m-%d %H:%M")
                }
                tanqueos_all.append(nuevo)
                guardar_json(tanqueos_all, FUEL_FILE)
                st.success(f"Guardado con éxito: {rend} km/gal")
                st.rerun()
            
            if btn_cerrar:
                st.session_state.validado_tanqueo = False
                st.session_state.placa_activa = None
                st.rerun()

        # Historial abajo
        st.write("### 📊 Historial Reciente")
        for t in reversed(hist_placa):
            st.markdown(f"""
            <div class="tanqueo-card">
                <div style="display: flex; justify-content: space-between;">
                    <b>📅 {t['Fecha']}</b>
                    <span class="eficiencia-badge">{t.get('Km_Galon', 0.0)} km/gal</span>
                </div>
                <div style="font-size: 0.9em; color: #AAA;">⛽ {t['Galones']} Gal | 🛣️ {t['Odometro']} km</div>
            </div>""", unsafe_allow_html=True)

# --- SECCIONES RESTANTES (Vincular y Admin se mantienen igual) ---
elif opcion == "Vincular nueva placa-llave":
    st.subheader("🔗 Vinculación")
    with st.form("vinculo_form"):
        p_new = st.text_input("Placa Nueva").upper().strip()
        l_new = st.text_input("Asignar Llave", type="password").strip()
        r_new = st.text_input("Responsable")
        if st.form_submit_button("VINCULAR"):
            if p_new and l_new:
                db_m = cargar_json(MAQ_FILE)
                db_m[p_new] = {"llave": l_new, "responsable": r_new, "tipo": "maquina", "fecha": datetime.now(ZONA_HORARIA).strftime("%Y-%m-%d")}
                guardar_json(db_m, MAQ_FILE)
                st.success(f"Placa {p_new} vinculada.")
            else: st.warning("Faltan datos.")

elif opcion == "Panel Administrativo":
    st.subheader("🛠️ Control Maestro")
    if st.text_input("🔑 Llave Maestra", type="password") == "0303":
        db_m = cargar_json(MAQ_FILE)
        if db_m:
            df = pd.DataFrame([{"Placa": k, **v} for k, v in db_m.items()])
            st.dataframe(df.fillna("N/A"), use_container_width=True, hide_index=True)