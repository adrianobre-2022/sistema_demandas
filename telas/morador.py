import streamlit as st
import datetime


def renderizar(supabase):
    # BOTÃO VOLTAR ORIGINAL
    col_v1, _ = st.columns(2)
    with col_v1:
        if st.button(
            "⬅️ Voltar ao Início",
            key="btn_voltar_morador_nat",
            use_container_width=True
        ):
            st.session_state.tela_atual = "home"
            st.session_state.busca_ativa = False
            st.rerun()

    st.markdown(
        "<h1 style='text-align: center; "
        "font-weight: 900; margin-bottom: 0px;"
        "'>🏘️ Painel do Morador</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center; "
        "font-size: 16px; font-style: italic; "
        "color: #aaaaaa; margin-top: 5px; "
        "margin-bottom: 25px;'>Sua voz "
        "constrói o comércio do nosso "
        "quarteirão.</p>",
        unsafe_allow_html=True
    )
    st.write("---")

    # CARGA ORIGINAL DE LOJAS
    locais_disponiveis = []
    try:
        res_loc = supabase\
            .table("locais_destino")\
            .select("id, nome_exibicao, regiao_cidade")\
            .execute()
        if res_loc.data:
            locais_disponiveis = res_loc.data
    except:
        pass

    if not locais_disponiveis:
        st.info("ℹ️ Nenhum local mapeado.")
        return

    st.markdown(
        "### 📢 O que você procurou "
        "e não encontrou?"
    )

    # FORMULÁRIO COMPLETO ORIGINAL RESTAURADO
    with st.form(
        key="form_demanda_mor",
        clear_on_submit=True
    ):
        item_p = st.text_input(
            "Nome do Produto / Marca faltante:",
            placeholder="Ex: Leite Desnatado..."
        )
        opc_l = [
            f"{l['nome_exibicao']} "
            f"({l['regiao_cidade']})"
            for l in locais_disponiveis
        ]
        loja_txt = st.selectbox(
            "Em qual estabelecimento faltou?",
            options=opc_l
        )
        idx = opc_l.index(loja_txt)
        id_local = locais_disponiveis[idx]["id"]

        tipo_c = st.selectbox(
            "Tipo de Carência:",
            ["Produto / Marca",
             "Serviço Público / Infraestrutura",
             "Serviço Local / Novo Estabelecimento"]
        )
        obs_d = st.text_area(
            "Informações Adicionais (Opcional):"
        )
        ct_av = st.text_input(
            "Seu WhatsApp (Opcional):"
        )

        if st.form_submit_button(
            "🚀 Registrar Alerta de Escassez"
        ):
            if not item_p.strip():
                st.error("⚠️ Digite o produto.")
            else:
                try:
                    supabase.table("relatos_escassez")\
                        .insert({
                            "item_solicitado":
                                item_p.strip(),
                            "local_destino_id":
                                id_local,
                            "tipo_carencia":
                                tipo_c,
                            "observacao_detalhe":
                                obs_d.strip() or None,
                            "contato_aviso":
                                ct_av.strip() or None,
                            "status": "Pendente",
                            "sub_segmento": "Geral"
                        }).execute()
                    st.success("🎉 Registrado!")
                    import time
                    time.sleep(0.5)
                    st.rerun()
                except:
                    st.error("Erro ao salvar.")
    st.write("---")
    st.markdown(
        "### 📈 Impactos Recentes no Bairro"
    )

    # RECONEXÃO ESTÁVEL COM O HISTÓRICO ORIGINAL
    try:
        res_rec = supabase\
            .table("relatos_escassez")\
            .select(
                "item_solicitado, "
                "locais_destino("
                "nome_exibicao)"
            ).order(
                "created_at",
                desc=True
            ).limit(3).execute()

        if res_rec.data:
            for relato in res_rec.data:
                item = str(
                    relato.get(
                        "item_solicitado",
                        "Produto"
                    )
                ).title()

                n_loja = "Loja"
                if relato.get("locais_destino"):
                    n_loja = relato[
                        "locais_destino"]\
                        .get(
                        "nome_exibicao",
                        "Loja"
                    )

                # CARDS ESTÁTICOS NATIVOS ORIGINAIS RECUPERADOS
                with st.container():
                    st.success(
                        f"📦 **{item}**\n\n"
                        f"Faltando em: {n_loja}"
                    )
        else:
            st.info(
                "ℹ️ Nenhum impacto "
                "recente registrado."
            )
    except:
        st.info(
            "ℹ️ Carregando atualizações "
            "do quarteirão..."
        )
