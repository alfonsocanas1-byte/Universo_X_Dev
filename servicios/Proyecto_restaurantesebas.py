import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Sebas - Gestión Dark Kitchen", layout="wide", page_icon="🍳")

# Archivos de persistencia
ARCHIVO_PEDIDOS = "pedidos_restaurante.json"
ARCHIVO_MENU = "menu_restaurante.json"

# --- FUNCIONES DE CARGA Y GUARDADO (UNIFICADAS) ---
def cargar_datos(archivo):
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def guardar_datos(datos, archivo):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# --- INICIALIZACIÓN ---
if not os.path.exists(ARCHIVO_MENU):
    menu_inicial = [{"nombre": "Almuerzo Ejecutivo", "precio": 15000}]
    guardar_datos(menu_inicial, ARCHIVO_MENU)

if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# --- NAVEGACIÓN ---
st.sidebar.title("🎛 Panel de Control")
app_mode = st.sidebar.radio("Ir a:", ["🍔 Gestión del Menú", "🛒 Tomar Pedido", "🚚 Control de Entregas"])

# --- 1. GESTIÓN DEL MENÚ ---
if app_mode == "🍔 Gestión del Menú":
    st.header("📋 Configuración del Restaurante")
    with st.form("form_nuevo_plato"):
        col1, col2 = st.columns(2)
        n_plato = col1.text_input("Nombre del plato")
        n_precio = col2.number_input("Precio ($)", min_value=0, step=500)
        if st.form_submit_button("Añadir al Menú"):
            if n_plato:
                m = cargar_datos(ARCHIVO_MENU)
                m.append({"nombre": n_plato, "precio": n_precio})
                guardar_datos(m, ARCHIVO_MENU)
                st.success(f"'{n_plato}' agregado.")
                st.rerun()

# --- 2. TOMAR PEDIDO ---
elif app_mode == "🛒 Tomar Pedido":
    st.header("📝 Registro de Venta")
    menu = cargar_datos(ARCHIVO_MENU)
    
    if not menu:
        st.warning("Agrega platos en 'Gestión del Menú'.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Cliente")
            celular = st.text_input("Celular")
            opciones = {i['nombre']: i['precio'] for i in menu}
            sel = st.selectbox("Producto", list(opciones.keys()))
            if st.button("Agregar al Carrito"):
                st.session_state.carrito.append({"plato": sel, "precio": opciones[sel]})

        with c2:
            if st.session_state.carrito:
                st.table(pd.DataFrame(st.session_state.carrito))
                total = sum(i['precio'] for i in st.session_state.carrito)
                st.write(f"## Total: {total} $")
                
                if st.button("Confirmar Pedido"):
                    if nombre and celular:
                        peds = cargar_datos(ARCHIVO_PEDIDOS)
                        nuevo = {
                            "id": len(peds) + 1,
                            "cliente": nombre,
                            "celular": celular,
                            "items": st.session_state.carrito,
                            "total": total,
                            "estado": "Pendiente",
                            "hora": datetime.now().strftime("%H:%M")
                        }
                        peds.append(nuevo)
                        # AQUÍ ESTABA EL ERROR: ahora usamos guardar_datos correctamente
                        guardar_datos(peds, ARCHIVO_PEDIDOS)
                        st.session_state.carrito = []
                        st.success("¡Pedido enviado!")
                        st.rerun()
                    else:
                        st.error("Faltan datos.")

# --- 3. CONTROL DE ENTREGAS ---
elif app_mode == "🚚 Control de Entregas":
    st.header("📦 Monitor de Despacho")
    pedidos = cargar_datos(ARCHIVO_PEDIDOS)
    pendientes = [p for p in pedidos if p['estado'] == "Pendiente"]
    for p in pendientes:
        with st.expander(f"ORDEN #{p['id']} - {p['cliente']}"):
            if st.button(f"Marcar Entregado #{p['id']}"):
                for ped in pedidos:
                    if ped['id'] == p['id']:
                        ped['estado'] = "Entregado"
                guardar_datos(pedidos, ARCHIVO_PEDIDOS)
                st.rerun()