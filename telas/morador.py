import streamlit as st
import pandas as pd
import time
from core.database import (
    obter_pegada_digital
)


def renderizar(supabase):
    # NAVEGAÇÃO SUPERIOR VERDE NATIVA
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button(
            "🏠 Página Inicial",
            key="nav_home_v_original_v",
            use_container_width=True
        ):
            st.session_state\
              .tela_atual = "home"
            st.rerun()
    with col_nav2:
        if st.session_state\
           .aba_consumidor != \
           "menu_triagem":
            if st.button(
                "🗂️ Mudar Categoria",
                key="nav_cat_v_original_v",
                use_container_width=True
            ):
                st.session_state\
                  .aba_consumidor = \
                    "menu_triagem"
                st.rerun()

    st.markdown(
        "<h1 style='text-align: center; "
        "font-weight: 900; margin-bottom: 0px;"
        "'>🔍 E o que falta?</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center; "
        "font-size: 16px; font-style: italic; "
        "color: #aaaaaa; margin-top: 5px; "
        "margin-bottom: 25px;'>O termômetro "
        "de carências da nossa região.</p>",
        unsafe_allow_html=True
    )

    if st.session_state\
       .aba_consumidor == \
       "menu_triagem":
        # FRASE CURTA ATENDIDA
        st.write("Escolha o tipo de falta:")
        if st.button(
            "📦 PRODUTO OU MARCA EM FALTA",
            use_container_width=True,
            key="tri_prod_v"
        ):
            st.session_state\
              .aba_consumidor = \
                "produto"
            st.rerun()
        if st.button(
            "🏪 NOVO COMÉRCIO OU SERVIÇO LOCAL",
            use_container_width=True,
            key="tri_serv_v"
        ):
            st.session_state\
              .aba_consumidor = \
                "servico"
            st.rerun()
        if st.button(
            "🏛️ INFRAESTRUTURA OU ZELADORIA PÚBLICA",
            use_container_width=True,
            key="tri_infra_v"
        ):
            st.session_state\
              .aba_consumidor = \
                "infra"
            st.rerun()
        st.write("")
        st.markdown(
            "### 🏆 Impactos Recentes "
            "no Bairro"
        )
        try:
            resolvidos = supabase\
                .table(
                    "relatos_escassez"
                )\
                .select(
                    "item_solicitado, "
                    "sub_segmento, "
                    "locais_destino("
                    "nome_exibicao, "
                    "regiao_cidade)"
                )\
                .eq(
                    "status",
                    "Atendido"
                )\
                .order(
                    "data_registro",
                    desc=True
                )\
                .limit(20).execute()
            if resolvidos.data:
                lista_impactos = []
                for item in \
                        resolvidos.data:
                    if item.get(
                        "locais_destino"
                    ):
                        i_vitrine = \
                            str(
                                item[
                                    "item_soli"
                                    "citado"]
                            ).rstrip(
                                " 0123"
                                "456789"
                            ).strip()\
                             .title()
                        lista_impactos\
                            .append({
                                "item":
                                i_vitrine,
                                "nicho":
                                item.get(
                                    "sub_seg"
                                    "mento",
                                    "Geral"
                                ).strip(),
                                "local":
                                item[
                                    "locais_de"
                                    "stino"][
                                    "nome_exi"
                                    "bicao"]
                                .strip()
                                .title(),
                                "cidade_ex":
                                item[
                                    "locais_de"
                                    "stino"][
                                    "regiao_ci"
                                    "dade"]
                                .strip()
                            })
                df_imp = pd.DataFrame(
                    lista_impactos
                ).drop_duplicates(
                    subset=["local"]
                ).drop_duplicates(
                    subset=["nicho"]
                )

                cont_exibidos = 0
                for _, l_imp in \
                        df_imp.iterrows():
                    if cont_exibidos \
                       >= 3:
                        break
                    n_nicho = \
                        l_imp['nicho']
                    if n_nicho == \
                       "Supermercado":
                        icone, acao = \
                            "🛒 Varejo " \
                            "Alimentar:", \
                            "repôs o " \
                            "estoque de"
                    elif n_nicho in \
                        ["Saude",
                         "Saúde"]:
                        icone, acao = \
                            "🩺 Saúde e " \
                            "Bem-Estar:", \
                            "trouxe o " \
                            "serviço de"
                    elif n_nicho == \
                            "Petshop":
                        icone, acao = \
                            "🐶 Setor " \
                            "Animal/Pet:", \
                            "disponibi" \
                            "lizou o item"
                    elif n_nicho == \
                            "Beleza":
                        icone, acao = \
                            "💈 Beleza e " \
                            "Estética:", \
                            "ativou o " \
                            "atendimen" \
                            "to de"
                    else:
                        icone, acao = \
                            "✨ Conquista " \
                            "Local:", \
                            "disponibi" \
                            "lizou"

                    # SEM A REDUNDÂNCIA: "O estabelecimento" removido com sucesso
                    st.markdown(
                        f"<div style='"
                        f"background-"
                        f"color: "
                        f"#1A1A1A; "
                        f"padding: "
                        f"0.6rem "
                        f"1rem; "
                        f"border-"
                        f"radius: "
                        f"8px; "
                        f"border-"
                        f"left: 4px "
                        f"solid "
                        f"#00803B; "
                        f"margin-"
                        f"bottom: "
                        f"8px;'>"
                        f"<span "
                        f"style='"
                        f"font-size: "
                        f"13px; "
                        f"color: "
                        f"#aaaaaa; "
                        f"font-"
                        f"weight: "
                        f"500;'>"
                        f"✅ "
                        f"<b>"
                        f"{icone}"
                        f"</b> "
                        f"{l_imp['local']} "
                        f"("
                        f"{l_imp['cidade_ex']}"
                        f") "
                        f"{acao} "
                        f"<b>"
                        f"{l_imp['item']}"
                        f"</b>!"
                        f"</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    cont_exibidos += 1
            else:
                st.write(
                    "ℹ️ Nenhuma "
                    "benfeitoria "
                    "recente."
                )
        except:
            pass
    elif st.session_state\
        .aba_consumidor in \
        ["produto", "servico",
         "infra"]:
        aba = st.session_state\
                .aba_consumidor
        if aba == "produto":
            l_i, p_i = \
                "Qual produto ou " \
                "marca falta? *", \
                "Ex: Leite condens" \
                "ado marca X..."
            l_l, p_l = \
                "Em qual estabele" \
                "cimento? *", \
                "Ex: Nome do " \
                "mercado..."
            # MUDANÇA SOLICITADA
            l_c, t_e = \
                "Deixar contato, " \
                "caso reponha? " \
                "(Opcional)", \
                "Produto / Marca"
        elif aba == "servico":
            l_i, p_i = \
                "Qual comércio " \
                "falta no bairro? *", \
                "Ex: Sapataria, " \
                "lavanderia..."
            l_l, p_l = \
                "Em qual rua ou " \
                "ponto? *", \
                "Ex: Avenida " \
                "Principal..."
            l_c, t_e = \
                "Deixar contato, " \
                "caso reponha? " \
                "(Opcional)", \
                "Serviço Local / " \
                "Novo Estabeleci" \
                "mento"
        elif aba == "infra":
            l_i, p_i = \
                "Qual problema de " \
                "infraestrutura " \
                "pública? *", \
                "Ex: Falha na " \
                "iluminação..."
            l_l, p_l = \
                "Qual o ponto de " \
                "referência? *", \
                "Ex: Posto de " \
                "saúde do bairro Y..."
            l_c, t_e = \
                "Deixar contato, " \
                "caso reponha? " \
                "(Opcional)", \
                "Serviço Público / " \
                "Infraestrutura"

        st.write("")
        with st.form(
            key="formulario_dinam"
                "ico_consumidor",
            clear_on_submit=False
        ):
            regiao_final = \
                st.text_input(
                    label="📍 Região/"
                          "Cidade da "
                          "falta: *",
                    placeholder="Ex: São "
                                "Paulo/SP - "
                                "Centro"
                )
            item_solicitado = \
                st.text_input(
                    label=l_i,
                    placeholder=p_i,
                    key="input_item"
                )
            local_ocorrencia = \
                st.text_input(
                    label=l_l,
                    placeholder=p_l,
                    key="input_local"
                )
            contato_usuario = \
                st.text_input(
                    label=l_c,
                    placeholder="Insira "
                                "seu Whats"
                                "App ou "
                                "e-mail, "
                                "caso in"
                                "formem re"
                                "posição.",
                    key="input_contato"
                )
            observacao_usuario = None
            with st.expander(
                "➕ Adicionar mais "
                "detalhes e obser"
                "vações (Opcional)"
            ):
                observacao_usuario = \
                    st.text_area(
                        label="Detalhes "
                              "adicionais:",
                        placeholder="Ex: Det"
                                    "alhe o "
                                    "ocorrido "
                                    "aqui...",
                        key="input_obs"
                    )
            botao_enviar = \
                st.form_submit_button(
                    "🔍 SINALIZAR "
                    "ESTA FALTA",
                    use_container_width=True
                )

        if botao_enviar:
            if not regiao_final or \
               regiao_final.strip() \
               == "":
                st.error(
                    "⚠️ O campo '📍 "
                    "Região/Cidade da "
                    "falta:' é obrigató"
                    "rio para registrar "
                    "a carência."
                )
            elif not item_solicitado \
                    or not \
                    local_ocorrencia:
                st.error(
                    "⚠️ Por favor, "
                    "preencha o item "
                    "que falta e o "
                    "local da ocorrên"
                    "cia."
                )
            else:
                try:
                    hash_disp = \
                        obter_pegada_digital()
                    texto_regiao = \
                        regiao_final\
                        .strip()
                    local_fmt = \
                        local_ocorrencia\
                        .strip().title()

                    l_data = supabase\
                        .table(
                            "locais_destino"
                        ).insert({
                            "nome_exibicao":
                                local_fmt,
                            "regiao_cidade":
                                texto_regiao,
                            "regiao_estado":
                                "SP"
                        }).execute()

                    l_id = \
                        l_data.data[0]["id"] \
                        if (l_data and
                            l_data.data and
                            len(l_data.data)
                            > 0) else None

                    if l_id:
                        seg_det = "Geral"
                        txt_u = \
                            item_solicitado\
                            .strip().lower()
                        if any(
                            p in txt_u
                            for p in [
                                "leite",
                                "arroz",
                                "feijão",
                                "café",
                                "açúcar",
                                "pão",
                                "mercado",
                                "óleo"
                            ]
                        ):
                            seg_det = \
                                "Supermercado"
                        elif any(
                            p in txt_u
                            for p in [
                                "remédio",
                                "médico",
                                "dentista",
                                "farmácia",
                                "clínica"
                            ]
                        ):
                            seg_det = \
                                "Saúde"
                        elif any(
                            p in txt_u
                            for p in [
                                "ração",
                                "pet",
                                "cachorro",
                                "gato",
                                "petshop"
                            ]
                        ):
                            seg_det = \
                                "Petshop"
                        elif any(
                            p in txt_u
                            for p in [
                                "manicure",
                                "salão",
                                "cabeleireiro",
                                "estética"
                            ]
                        ):
                            seg_det = \
                                "Beleza"

                        txt_o = \
                            observacao_usuario\
                            .strip() if \
                            observacao_usuario \
                            else None
                        c_aviso = \
                            contato_usuario\
                            .strip() if \
                            contato_usuario \
                            else None

                        supabase.table(
                            "relatos_escassez"
                        ).insert({
                            "local_id":
                                l_id,
                            "item_solicitado":
                                item_solicitado
                                .strip().title(),
                            "tipo_carencia":
                                t_e,
                            "status":
                                "Pendente",
                            "sub_segmento":
                                seg_det,
                            "pegada_digital":
                                hash_disp,
                            "observacao_detalhe":
                                txt_o,
                            "contato_aviso":
                                c_aviso
                        }).execute()

                        st.success(
                            "✅ Falta "
                            "sinalizada "
                            "com sucesso!"
                        )
                        time.sleep(1.2)
                        st.session_state\
                          .aba_consumidor = \
                            "menu_triagem"
                        st.session_state\
                          .tela_atual = \
                            "home"
                        st.rerun()
                except Exception as e:
                    st.error(
                        "⚠️ Erro técnico "
                        "de persistência: "
                        f"{str(e)}"
                    )
