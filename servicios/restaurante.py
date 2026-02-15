import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- FUNCIONES DE CARGA Y GUARDADO ---
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

# --- FUNCIÓN PRINCIPAL (LA QUE LLAMA EL HUB) ---
def ejecutar():
    st.header("🍳 Mesa Gourmet - Gestión de Cocina")
    
    # Archivos de persistencia (viven en la carpeta raíz para no perderse)
    ARCHIVO_PEDIDOS = "pedidos_restaurante.json"
    ARCHIVO_MENU = "menu_restaurante.json"

    # Inicialización de estado para el carrito
    if 'carrito' not in st.session_state:
        st.session_state.carrito = []

    # Pestañas internas del microservicio
    tab1, tab2, tab3 = st.tabs(["🛒 Tomar Pedido", "📦 Entregas", "🍔 Configurar Menú"])

    # --- 1. TAB: TOMAR PEDIDO ---
    with tab1:
        menu = cargar_datos(ARCHIVO_MENU)
        if not menu:
            st.warning("⚠️ El menú está vacío. Ve a la pestaña 'Configurar Menú'.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Datos del Cliente")
                nombre = st.text_input("Nombre y Apellido", key="rest_nom")
                celular = st.text_input("Celular", key="rest_cel")
                
                opciones_menu = {item['nombre']: item['precio'] for item in menu}
                seleccion = st.selectbox("Elegir producto", list(opciones_menu.keys()))
                if st.button("Agregar al Carrito"):
                    st.session_state.carrito.append({"plato": seleccion, "precio": opciones_menu[seleccion]})
                    st.success(f"{seleccion} añadido.")

            with col2:
                st.subheader("Resumen")
                if st.session_state.carrito:
                    df_c = pd.DataFrame(st.session_state.carrito)
                    st.table(df_c)
                    total = sum(i['precio'] for i in st.session_state.carrito)
                    st.write(f"### Total: ${total:,}")
                    
                    if st.button("Confirmar Pedido ✅"):
                        if nombre and celular:
                            pedidos = cargar_datos(ARCHIVO_PEDIDOS)
                            nuevo_p = {
                                "id": len(pedidos) + 1,
                                "cliente": nombre,
                                "celular": celular,
                                "items": st.session_state.carrito,
                                "total": total,
                                "estado": "Pendiente",
                                "hora": datetime.now().strftime("%H:%M")
                            }
                            pedidos.append(nuevo_p)
                            guardar_datos(pedidos, ARCHIVO_PEDIDOS)
                            st.session_state.carrito = []
                            st.success(f"¡Pedido #{nuevo_p['id']} registrado!")
                            st.rerun()
                        else:
                            st.error("Por favor llena el nombre y celular.")

    # --- 2. TAB: ENTREGAS ---
    with tab2:
        st.subheader("Pedidos en Cocina")
        pedidos = cargar_datos(ARCHIVO_PEDIDOS)
        pendientes = [p for p in pedidos if p['estado'] == "Pendiente"]
        
        if pendientes:
            for p in pendientes:
                with st.expander(f"Orden #{p['id']} - {p['cliente']}"):
                    st.write(f"⏰ Hora: {p['hora']} | 📞 {p['celular']}")
                    for item in p['items']:
                        st.write(f"• {item['plato']} - ${item['precio']:,}")
                    if st.button(f"Marcar como Entregado", key=f"btn_{p['id']}"):
                        for ped in pedidos:
                            if ped['id'] == p['id']:
                                ped['estado'] = "Entregado"
                        guardar_datos(pedidos, ARCHIVO_PEDIDOS)
                        st.rerun()
        else:
            st.info("No hay pedidos pendientes por ahora.")

    # --- 3. TAB: CONFIGURAR MENÚ ---
    with tab3:
        st.subheader("Administración de Platos")
        with st.form("nuevo_plato_form"):
            n_plato = st.text_input("Nombre del Plato")
            n_precio = st.number_input("Precio", min_value=0, step=500)
            if st.form_submit_button("Guardar en Menú"):
                if n_plato:
                    m = cargar_datos(ARCHIVO_MENU)
                    m.append({"nombre": n_plato, "precio": n_precio})
                    guardar_datos(m, ARCHIVO_MENU)
                    st.success("Plato agregado correctamente.")
                    st.rerun()
        
        st.divider()
        menu_actual = cargar_datos(ARCHIVO_MENU)
        if menu_actual:
            st.write("Menú vigente:")
            st.table(pd.DataFrame(menu_actual))
            if st.button("Vaciar Menú"):
                guardar_datos([], ARCHIVO_MENU)
                st.rerun()

# Fin del microservicio restaurante.py