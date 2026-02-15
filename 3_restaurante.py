import streamlit as st

# --- ESTÉTICA DARK TOTAL ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2, h3, p, label { color: #FFFFFF !important; }
    .banner-cocina {
        background-color: #1A1A1A;
        border: 2px solid #FFD700;
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MENSAJE SOLICITADO ---
st.markdown("""
    <div class="banner-cocina">
        <h1 style="color: #FFD700;">👨‍🍳 BIENVENIDO AQUÍ AL RESTAURANTE</h1>
        <p>Cocina Gourmet del Universo X</p>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.write("🟢 Microservicio: Restaurante")