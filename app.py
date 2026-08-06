import streamlit as st
import os
import datetime
from core.database import (
    inicializar_supabase,
    obter_pegada_digital
)
from telas import morador, b2b

# 🎨 BLINDAGEM VISUAL: Remove menus, rodapés e marcas d'água do Streamlit
st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stDecoration"] {display: none;}
        [data-testid="stHeader"] {display: none;}
        </style>
    """, unsafe_allow_html=True)


# --- INICIALIZAÇÃO DE VARIÁVEIS UNIVERSAIS ---
botao_enviar = False
termo_busca = ""
loja_alvo_prioridade = "Mercadinho Do Bairro"

# --- CONEXÃO COM O BANCO DE DADOS ---
supabase = inicializar_supabase()

st.set_page_config(page_title="Sistema de Demandas",
                   page_icon="🔍", layout="centered")

# 🔍 LOGALIZE O INÍCIO DO SEU APP.PY E ADICIONE ESTE BLOCO:

# Verifica se o link atual na internet é o de testes
# 🎨 SINALIZADOR VISUAL DE TESTES SIMPLIFICADO (Risco Zero de AttributeError)
if st.session_state.get("perfil_cliente") == "admin" or "test" in st.session_state:
    st.markdown("""
        <div style='background-color: #7A5200; padding: 0.4rem; text-align: center; border-radius: 5px; margin-bottom: 20px;'>
            <span style='color: white; font-weight: bold; font-size: 13px;'>⚠️ AMBIENTE DE TESTES (HOMOLOGAÇÃO) — PROJETO PROTEGIDO</span>
        </div>
    """, unsafe_allow_html=True)

# --- INJEÇÃO DO DESIGN VISUAL MESTRE VERDE ---
try:
    with open("core/styles.css", "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )
except:
    pass

# --- INICIALIZAÇÃO DE SESSÕES UNIVERSAIS ---
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

# --- 🔐 CORTINA DE FUMAÇA: MANUTENÇÃO COM VALIDAÇÃO DUPLA (ENTER + CLIQUE) ---
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
        placeholder="Insira a credencial e aperte Enter ou clique abaixo...",
        key="campo_senha_manutencao_final_v"
    )
    botao_destravar_lab = st.button(
        "🔓 Acessar Ambiente de Testes", use_container_width=True)

    # VALIDAÇÃO DUPLA: Captura o preenchimento seja por Enter no input ou pelo clique físico do botão
    if (senha_desenvolvimento and senha_desenvolvimento.strip() != "") or botao_destravar_lab:
        if senha_desenvolvimento.strip() == "carencias2026":
            st.session_state.seguranca_master = True
            st.rerun()
        elif botao_destravar_lab:
            st.error("❌ Credencial incorreta.")
    st.stop()

# --- ROTEADOR SUPREMO DE TELAS MODULARES ---
if st.session_state.tela_atual == "home":
    st.markdown(
        "<h1 style='text-align: center; font-weight: 900; "
        "margin-bottom: 0px;'>🔍 Sistema de Demandas</h1>",
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
            key="btn_voltar_aut_v_original",
            use_container_width=True
        ):
            st.session_state.tela_atual = "home"
            st.session_state.token_valido = False
            st.rerun()

    st.markdown(
        "<h1 style='text-align: center; font-weight: 900; "
        "margin-bottom: 0px;'>🔍 Sistema de Demandas</h1>",
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

    token_inserido = st.text_input(
        label="Token de Acesso:",
        type="password",
        placeholder="Digite seu token e aperte Enter ou clique abaixo...",
        key="campo_token_b2b_final_v"
    )
    botao_validar = st.button(
        "🔑 Autenticar e Entrar no Painel", use_container_width=True)

    # VALIDAÇÃO DUPLA B2B: Aceita Enter no teclado ou o clique físico no botão verde
    if (token_inserido and token_inserido.strip() != "") or botao_validar:
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
        elif token_limpo != "":
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
                elif botao_validar:
                    st.error("❌ Token inválido.")
            except:
                st.error("❌ Erro de autenticidade na base.")

elif st.session_state.tela_atual == "comerciante":
    b2b.renderizar(supabase)
