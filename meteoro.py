import streamlit as st
import random

def juego_meteoro():
    st.subheader("🏎️ Simulador de Flujo: Meteoro machines")
    st.write("Tu máquina debe esquivar los 'Tiempos Muertos' (⚠️) para mantener la productividad.")

    # Estado del juego en la sesión
    if 'lane' not in st.session_state: st.session_state.lane = 1
    if 'score' not in st.session_state: st.session_state.score = 0

    # Controles de la Máquina
    c1, c2, c3 = st.columns(3)
    if c1.button("⬅️ Carril Izquierdo"): st.session_state.lane = 0
    if c2.button("↕️ Centro"): st.session_state.lane = 1
    if c3.button("Derecha ➡️"): st.session_state.lane = 2

    # Generar obstáculo (Falla de máquina)
    obstaculo = random.randint(0, 2)
    
    # Representación visual de los 3 carriles
    pista = ["|   |", "|   |", "|   |"]
    pista[obstaculo] = "| ⚠️ |"  # El obstáculo
    
    st.text("CAMINO DE PRODUCCIÓN:")
    for i, linea in enumerate(pista):
        if i == st.session_state.lane:
            # Si el carro está en este carril
            st.text(linea.replace(" ", "🚜")) 
        else:
            st.text(linea)

    if st.button("⚙️ Sincronizar Avance"):
        if obstaculo == st.session_state.lane:
            st.error("💥 ¡CHOQUE! Tiempo muerto detectado. Productividad reseteada.")
            st.session_state.score = 0
        else:
            st.session_state.score += 10
            st.success(f"Eficiencia de Máquina: {st.session_state.score}%")