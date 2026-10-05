import streamlit as st
import datetime
import random
import urllib.parse
import time


def obter_local_destino_morador(supabase):
    try:
        resposta = supabase.table("locais_destino").select(
            "id, nome_exibicao, regiao_cidade").execute()
        if resposta.data:
            opcoes = {
                f"{reg['nome_exibicao']} ({reg['regiao_cidade']})": reg['id'] for reg in resposta.data}
            escolha = st.selectbox("📍 Onde você não encontrou o produto?", options=list(
                opcoes.keys()), key="select_local_morador")
            return opcoes[escolha]
    except:
        st.error("⚠️ Erro ao carregar estabelecimentos locais.")
    return None


def renderizar(supabase):
    st.markdown("""
        <style>
        .bloco-impacto-dinamico {
            background-color: #152619 !important;
            border-left: 5px solid #00803B !important;
            padding: 1rem !important;
            border-radius: 8px !important;
            margin-bottom: 25px !important;
            color: #FFFFFF !important;
            font-weight: bold !important;
            font-size: 14px !important;
            text-align: center !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col_nav1, _ = st.columns(2)
    with col_nav1:
        if st.button("⬅️ Voltar ao Início", key="btn_voltar_morador_raiz", use_container_width=True):
            st.session_state.tela_atual = "home"
            st.session_state.aba_consumidor = "menu_triagem"
            st.rerun()

    st.markdown("<h1 style='text-align: center; font-weight: 900; margin-bottom: 0px;'>📝 Central do Morador</h1>",
                unsafe_allow_html=True)
    st.write("---")
    st.markdown("<h3 style='text-align: center; color: #00803B; margin-bottom: 15px;'>🏆 Impactos Recentes no Bairro</h3>", unsafe_allow_html=True)

    try:
        resposta_impactos = supabase.table("relatos_escassez").select("item_solicitado, sub_segmento, locais_destino(nome_exibicao, regiao_cidade)").eq(
            "status", "Atendido").order("data_registro", desc=True).limit(10).execute()
        if resposta_impactos.data and len(resposta_impactos.data) > 0:
            lista_impactos_reais = []
            for reg in resposta_impactos.data:
                item = str(reg.get("item_solicitado")).title()
                nicho = str(reg.get("sub_segmento", "Varejo")).title()
                loja = reg["locais_destino"]["nome_exibicao"] if reg.get(
                    "locais_destino") else "Comércio Local"
                regiao = reg["locais_destino"]["regiao_cidade"] if reg.get(
                    "locais_destino") else "Região"
                lista_impactos_reais.append(
                    f"✅ 📦 {nicho}: A loja '{loja}' ({regiao}) disponibilizou o item '{item}' para a vizinhança!")
            impacto_da_vez = random.choice(lista_impactos_reais)
            st.markdown(
                f"<div class='bloco-impacto-dinamico'>{impacto_da_vez}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align: center; color: #aaaaaa; font-style: italic; padding: 1rem; border: 1px dashed #404040; border-radius: 8px; margin-bottom: 25px;'>🔍 Radar ativo: Aguardando reabastecimento...</div>", unsafe_allow_html=True)
    except:
        st.markdown("<div style='text-align: center; color: #888888; font-size: 13px; margin-bottom: 25px;'>🔄 Sincronizando conquistas...</div>", unsafe_allow_html=True)
    st.write("---")
    if st.session_state.aba_consumidor == "menu_triagem":
        st.markdown(
            "<h4 style='text-align: center; margin-bottom: 20px;'>Qual tipo de ausência você quer relatar?</h4>", unsafe_allow_html=True)
        if st.button("🛒 PRODUTO EM FALTA (Supermercado / Mercearia)", use_container_width=True, key="triagem_prod"):
            st.session_state.aba_consumidor = "formulario_dados"
            st.session_state.sub_segmento_escolhido = "Supermercado"
            st.session_state.tipo_carencia_escolhida = "Produto / Marca"
            st.rerun()
        if st.button("🩺 SAÚDE / MEDICAMENTO (Farmácia / Drogaria)", use_container_width=True, key="triagem_saude"):
            st.session_state.aba_consumidor = "formulario_dados"
            st.session_state.sub_segmento_escolhido = "Saude"
            st.session_state.tipo_carencia_escolhida = "Produto / Marca"
            st.rerun()
        if st.button("🐶 PRODUTO ANIMAL (Petshop / Veterinária)", use_container_width=True, key="triagem_pet"):
            st.session_state.aba_consumidor = "formulario_dados"
            st.session_state.sub_segmento_escolhido = "Petshop"
            st.session_state.tipo_carencia_escolhida = "Produto / Marca"
            st.rerun()
        if st.button("💈 ESTÉTICA / BELEZA (Insumo ou Serviço)", use_container_width=True, key="triagem_beleza"):
            st.session_state.aba_consumidor = "formulario_dados"
            st.session_state.sub_segmento_escolhido = "Beleza"
            st.session_state.tipo_carencia_escolhida = "Serviço Local / Novo Estabelecimento"
            st.rerun()
        if st.button("🏛️ INFRAESTRUTURA / ZELADORIA (Problema de Rua)", use_container_width=True, key="triagem_infra"):
            st.session_state.aba_consumidor = "formulario_dados"
            st.session_state.sub_segmento_escolhido = "Zeladoria"
            st.session_state.tipo_carencia_escolhida = "Serviço Público / Infraestrutura"
            st.rerun()
    elif st.session_state.aba_consumidor == "formulario_dados":
        st.markdown(
            f"<p style='color: #00803B; font-weight: bold;'>Sinalizando: {st.session_state.tipo_carencia_escolhida} » {st.session_state.sub_segmento_escolhido}</p>", unsafe_allow_html=True)
        if st.button("⬅️ Mudar Categoria", key="btn_voltar_triagem"):
            st.session_state.aba_consumidor = "menu_triagem"
            st.rerun()

        with st.form(key="form_captacao_morador", clear_on_submit=True):
            id_local = obter_local_destino_morador(supabase)
            item_txt = st.text_input(
                "O que falta no quarteirão?", placeholder="Ex: Ração marca X, Leite Y...", key="input_item_morador").strip()
            obs_txt = st.text_area(
                "Observação? (Opcional)", placeholder="Ex: Não encontro há duas semanas...", key="input_obs_morador").strip()
            contato_txt = st.text_input("WhatsApp para ser avisado (Opcional)",
                                        placeholder="Ex: 11999998888", key="input_contato_morador").strip()
            st.markdown("<p style='font-size: 11px; color: #888888; font-style: italic;'>🔒 LGPD: Seus dados estão protegidos. O contato é opcional e serve para aviso de reposição.</p>", unsafe_allow_html=True)

            if st.form_submit_button("🔥 Enviar Alerta ao Radar"):
                if item_txt and id_local:
                    try:
                        from core.database import obter_pegada_digital
                        payload = {"item_solicitado": item_txt.title(), "tipo_carencia": st.session_state.tipo_carencia_escolhida, "sub_segmento": st.session_state.sub_segmento_escolhido, "observacao_detalhe":
                                   obs_txt if obs_txt else "Sem detalhes.", "contato_aviso": contato_txt if contato_txt else "", "id_local_destino": id_local, "status": "Pendente", "pegada_digital": obter_pegada_digital()}
                        supabase.table("relatos_escassez").insert(
                            payload).execute()
                        st.success("🎉 Alerta registrado com sucesso!")
                        time.sleep(1.0)
                        st.session_state.aba_consumidor = "menu_triagem"
                        st.rerun()
                    except Exception as err:
                        st.error(f"❌ Erro ao enviar: {str(err)}")
