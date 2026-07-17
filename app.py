import streamlit as st
import os
import datetime
from core.database import (
    inicializar_supabase,
    obter_pegada_digital
)
from telas import morador, b2b

# --- VARIÁVEIS UNIVERSAIS ---
botao_enviar = False
termo_busca = ""
loja_alvo_prioridade = "Mercadinho Do Bairro"

# --- CONEXÃO BANCO ---
supabase = inicializar_supabase()

st.set_page_config(
    page_title="E o que falta?",
    page_icon="🔍",
    layout="centered"
)

# --- INJEÇÃO CSS EXTERNO ---
try:
    with open("core/styles.css", "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )
except:
    pass

# --- ESTILOS EXCLUSIVOS UTILITÁRIOS ---
st.markdown("""
    <style>
    button[key="nav_home_final_v"], 
    button[key="nav_cat_final_v"],
    button[key="btn_voltar_aut_final_v"],
    button[key="btn_voltar_com_final_v"] {
        background-color: #1A1A1A !important;
        color: #aaaaaa !important;
        border: 1px solid #333333 !important;
        box-shadow: none !important;
        width: 100% !important;
        display: block !important;
    }
    button[key="nav_home_final_v"]:hover, 
    button[key="nav_cat_final_v"]:hover,
    button[key="btn_voltar_aut_final_v"]:hover,
    button[key="btn_voltar_com_final_v"]:hover {
        background-color: #262626 !important;
        color: #ffffff !important;
        border: 1px solid #444444 !important;
    }
    button[key*="btn_ir_"] {
        background-color: #00803B !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        padding: 0.8rem 0.2rem !important;
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE SESSÕES ---
if "seguranca_master" not in st.session_state:
    st.session_state.seguranca_master = False
if "tela_atual" not in st.session_state:
    st.session_state.tela_atual = "home"
if "token_valido" not in st.session_state:
    st.session_state.token_valido = False
if "perfil_cliente" not in st.session_state:
    st.session_state.perfil_cliente = None
if "busca_ativa" not in st.session_state:
    st.session_state.busca_ativa = False
if "dados_grafico" not in st.session_state:
    st.session_state.dados_grafico = None
if "aba_consumidor" not in st.session_state:
    st.session_state.aba_consumidor = "menu_triagem"
if "regiao_cliente" not in st.session_state:
    st.session_state.regiao_cliente = "São Paulo/SP"

# --- 🔐 MANUTENÇÃO ---
if not st.session_state.seguranca_master:
    st.markdown(
        "<h3 style='text-align: center; color: #ff3333; "
        "margin-top: 50px;'>⚠️ Sistema em Manutenção</h3>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center; font-size: 14px; "
        "color: #aaaaaa;'>Ambiente restrito.</p>",
        unsafe_allow_html=True
    )
    st.write("---")

    senha_desenvolvimento = st.text_input(
        label="Chave de Engenharia:",
        type="password",
        placeholder="Insira a credencial aqui...",
        key="campo_senha_manutencao_limpo"
    )

    if st.button("🔓 Acessar Ambiente de Testes", use_container_width=True, key="btn_destravar_nativo"):
        senha_correta = os.environ.get("CHAVE_ENGENHARIA") or \
            st.secrets.get("CHAVE_ENGENHARIA")
        if senha_desenvolvimento.strip() == senha_correta:
            st.session_state.seguranca_master = True
            st.rerun()
        else:
            st.error("❌ Credencial incorreta.")
    st.stop()

# --- ROTEADOR SUPREMO ---
if st.session_state.tela_atual == "home":
    st.markdown(
        "<h1 style='text-align: center; font-weight: 900; "
        "margin-bottom: 0px;'>🔍 E o que falta?</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center; font-size: 16px; "
        "font-style: italic; color: #aaaaaa; margin-top: 5px; "
        "margin-bottom: 25px;'>O termômetro de "
        "carências da nossa região.</p>",
        unsafe_allow_html=True
    )
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "📝 Sou Consumidor\n(Registrar Falta)",
            use_container_width=True,
            key="btn_ir_consumidor"
        ):
            st.session_state.tela_atual = "consumidor"
            st.session_state.aba_consumidor = "menu_triagem"
            st.rerun()
    with col2:
        if st.button(
            "📊 Sou Comerciante / Gestor\n(Acessar Painel)",
            use_container_width=True,
            key="btn_ir_comerciante"
        ):
            st.session_state.tela_atual = "autenticacao"
            st.rerun()

elif st.session_state.tela_atual == "consumidor":
    morador.renderizar(supabase)

elif st.session_state.tela_atual == "autenticacao":
    col_nav_c1, col_nav_c2 = st.columns(2)
    with col_nav_c1:
        if st.button(
            "🏠 Página Inicial",
            key="btn_voltar_aut_final_v",
            use_container_width=True
        ):
            st.session_state.tela_atual = "home"
            st.session_state.token_valido = False
            st.rerun()

    st.markdown(
        "<h1 style='text-align: center; font-weight: 900; "
        "margin-bottom: 0px;'>🔍 E o que falta?</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center; font-size: 16px; "
        "font-style: italic; color: #aaaaaa; margin-top: 5px; "
        "margin-bottom: 25px;'>O termômetro de "
        "carências da nossa região.</p>",
        unsafe_allow_html=True
    )
    st.write("---")

    # REMOVIDO ST.FORM: Libera o campo de Token e o olho contra esmagamento
    token_inserido = st.text_input(
        label="Token de Acesso corporativo:",
        type="password",
        placeholder="Digite seu token de acesso...",
        key="campo_token_autenticacao_limpo"
    )

    if st.button("🔑 Autenticar e Entrar no Painel", use_container_width=True, key="btn_validar_b2b_nativo"):
        if token_inserido:
            token_limpo = token_inserido.strip()
            tokens_fixos = {
                "COMERCIO10": "comerciante", "SAUDE20": "saude",
                "PET30": "petshop", "BELEZA40": "beleza",
                "INVEST20": "investidor", "GESTOR30": "gestor",
                "MIDIA40": "jornalista", "ADMIN99": "admin"
            }
            if token_limpo in tokens_fixos:
                st.session_state.token_valido = True
                st.session_state.perfil_cliente = tokens_fixos[token_limpo]
                st.session_state.regiao_cliente = "São Paulo/SP"
                st.session_state.tela_atual = "comerciante"
                st.rerun()
            else:
                try:
                    busca_db = supabase.table("clientes_b2b")\
                        .select("*").eq("token_acesso", token_limpo)\
                        .execute()
                    if busca_db and busca_db.data and len(busca_db.data) > 0:
                        dados_l = busca_db.data[0]
                        if dados_l.get("status_pagamento") == "Cancelado":
                            st.error("❌ Token suspenso administrativamente.")
                        else:
                            st.session_state.perfil_cliente = dados_l.get(
                                "perfil_segmento", "comerciante")
                            st.session_state.regiao_cliente = dados_l.get(
                                "regiao_atuacao", "São Paulo/SP")
                            st.session_state.recursos_liberados = {
                                "reverso": dados_l.get("recurso_marketplace_reverso", True),
                                "whatsapp": dados_l.get("recurso_whatsapp", True),
                                "pdf": dados_l.get("recurso_pdf", True)
                            }
                            st.session_state.token_valido = True
                            st.session_state.tela_atual = "comerciante"
                            st.rerun()
                    else:
                        st.error("❌ Token inválido.")
                except:
                    st.error("❌ Erro de autenticidade na base.")

elif st.session_state.tela_atual == "comerciante":
    b2b.renderizar(supabase)
