import streamlit as st

# Configuração global do aplicativo móvel
st.set_page_config(page_title="Sistema de Pesquisas", page_icon="🔍", layout="centered")

st.markdown("""
    <style>
    .stButton>button {
        background-color: #00cc66 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 1rem !important;
    }
    .stTextInput>div>div>input {
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 Central de Demandas Ocultas")
st.markdown("### Bem-vindo ao ecossistema de inteligência de mercado.")
st.info("💡 Use o menu superior ou lateral para navegar entre a área do Consumidor e o Painel do Comerciante.")