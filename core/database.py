import streamlit as st
import os
import hashlib
from dotenv import load_dotenv
from supabase import create_client, Client


def inicializar_supabase():
    caminho_atual = os.path.dirname(
        os.path.abspath(__file__)
    )
    # Sobe um nível para achar o .env na raiz
    raiz = os.path.join(
        caminho_atual, ".."
    )
    load_dotenv(os.path.join(raiz, ".env"))

    url = os.environ.get("SUPABASE_URL") or \
        st.secrets.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY") or \
        st.secrets.get("SUPABASE_KEY")

    if not url or not key:
        st.error("⚠️ Credenciais ausentes.")
        st.stop()

    return create_client(url, key)


def obter_pegada_digital():
    try:
        headers = st.context.headers
        ip = headers.get(
            "X-Forwarded-For", "127.0.0.1"
        ).split(",")[0].strip()
        agente = headers.get(
            "User-Agent", "Desconhecido"
        )
        return hashlib.sha256(
            f"{ip}-{agente}".encode('utf-8')
        ).hexdigest()
    except:
        return "pegada_fallback"
