import streamlit as st
import pandas as pd
import datetime
import urllib.parse
from fpdf import FPDF


def renderizar(supabase):
    loja_alvo_prioridade = "Mercadinho Do Bairro"
    termo_busca = st.session_state.get(
        "termo_busca_temp", ""
    )
    p_cli = st.session_state.perfil_cliente
    espectador_analitico = p_cli in [
        "investidor", "gestor", "jornalista"
    ]

    # BARRA DE NAVEGAÇÃO B2B SIMÉTRICA (VERDE ORIGINAL)
    col_nav_b1, col_nav_b2 = st.columns(2)
    with col_nav_b1:
        if st.button(
            "⬅️ Sair do Painel (Logoff)",
            key="btn_voltar_com_nativo_v",
            use_container_width=True
        ):
            st.session_state.tela_atual = "home"
            st.session_state.token_valido = False
            st.session_state.perfil_cliente = None
            st.session_state.busca_ativa = False
            st.session_state.dados_grafico = None
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
    st.write("---")
    termo_busca = st.text_input(
        label="Refinar por palavra-chave:",
        placeholder="Digite para filtrar...",
        key="input_busca_painel"
    )

    if p_cli == "admin":
        st.markdown(
            "<h3 style='text-align: center;'"
            ">🛠️ Cadastro de Assinantes (ERP)"
            "</h3>",
            unsafe_allow_html=True
        )
        with st.form(
            key="form_admin_mestre_cad",
            clear_on_submit=True
        ):
            nome_novo_comercio = st.text_input(
                "Nome do Estabelecimento:",
                placeholder="Ex: Supermercado..."
            )
            perfil_novo_comercio = st.selectbox(
                "Perfil de Acesso Corporativo:",
                ["comerciante", "saude",
                 "petshop", "beleza",
                 "investidor", "gestor",
                 "jornalista"]
            )
            regiao_novo_comercio = st.text_input(
                "Região/Cidade de Atuação:",
                placeholder="Ex: São Paulo/SP..."
            )
            if st.form_submit_button(
                "💼 Cadastrar Lojista"
            ):
                if nome_novo_comercio and \
                   regiao_novo_comercio:
                    try:
                        novo_registro = supabase\
                            .table("clientes_b2b")\
                            .insert({
                                "nome_estabelecimento":
                                    nome_novo_comercio
                                    .strip().title(),
                                "perfil_segmento":
                                    perfil_novo_comercio,
                                "regiao_atuacao":
                                    regiao_novo_comercio
                                    .strip(),
                                "status_pagamento":
                                    "Ativo",
                                "recurso_marketplace_reverso":
                                    True,
                                "recurso_whatsapp":
                                    True,
                                "recurso_pdf":
                                    True
                            }).execute()
                        if novo_registro.data:
                            st.success("🎉 Cadastrado!")
                            tk_exibe = novo_registro\
                                .data['token_acesso']
                            st.info(
                                f"🔑 Token: `{tk_exibe}`"
                            )
                    except Exception as err:
                        st.error(f"Erro: {str(err)}")

        st.markdown(
            "<h3 style='text-align: center;'"
            ">📊 Central de Recursos e "
            "Controle Financeiro</h3>",
            unsafe_allow_html=True
        )
        try:
            resposta_clientes = supabase\
                .table("clientes_b2b")\
                .select("*")\
                .order("created_at", desc=True)\
                .execute()
            if resposta_clientes.data:
                for cli in resposta_clientes.data:
                    c_id = cli["id"]
                    ex_label = f"🏢 {cli['nome_estabelecimento']}"
                    with st.expander(ex_label):
                        st.text_input(
                            "🔑 Token Completo:",
                            value=cli['token_acesso'],
                            disabled=True,
                            key=f"tk_full_{c_id}"
                        )
                        col_status, col_plan = st.columns(2)
                        with col_status:
                            status_pag = st.selectbox(
                                "Status de Pagamento:",
                                ["Ativo", "Inadimplente",
                                 "Cancelado"],
                                index=[
                                    "Ativo", "Inadimplente",
                                    "Cancelado"
                                ].index(cli.get(
                                    "status_pagamento", "Ativo"
                                )),
                                key=f"pay_{c_id}"
                            )
                        with col_plan:
                            plano_cont = st.selectbox(
                                "Plano Contratado:",
                                ["Bronze", "Prata", "Ouro"],
                                index=[
                                    "Bronze", "Prata", "Ouro"
                                ].index(cli.get(
                                    "plano_contratado", "Ouro"
                                )),
                                key=f"plan_{c_id}"
                            )
                        c_reverso = st.checkbox(
                            "Acesso ao Marketplace Reverso",
                            value=cli.get(
                                "recurso_marketplace_reverso",
                                True
                            ),
                            key=f"rev_{c_id}"
                        )
                        c_whatsapp = st.checkbox(
                            "Botão de Captação WhatsApp LGPD",
                            value=cli.get(
                                "recurso_whatsapp", True
                            ),
                            key=f"wa_{c_id}"
                        )
                        c_pdf = st.checkbox(
                            "Emissão de Relatórios PDF",
                            value=cli.get(
                                "recurso_pdf", True
                            ),
                            key=f"pdf_ch_{c_id}"
                        )
                        if st.button(
                            "💾 Salvar Alterações",
                            key=f"save_{c_id}"
                        ):
                            supabase.table("clientes_b2b")\
                                .update({
                                    "status_pagamento":
                                        status_pag,
                                    "plano_contratado":
                                        plano_cont,
                                    "recurso_marketplace_reverso":
                                        c_reverso,
                                    "recurso_whatsapp":
                                        c_whatsapp,
                                    "recurso_pdf":
                                        c_pdf
                                }).eq("id", c_id).execute()
                            st.success("🔒 Sincronizado!")
                            import time
                            time.sleep(0.5)
                            st.rerun()
        except:
            pass
        st.markdown(
            "<h3 style='text-align: "
            "center;'>📥 Curadoria de "
            "Nichos (Cenário B)</h3>",
            unsafe_allow_html=True
        )
        try:
            s_brutas = supabase\
                .table("relatos_escassez")\
                .select(
                    "id, item_solicitado, "
                    "sub_segmento"
                )\
                .eq("sub_segmento", "Geral")\
                .limit(5).execute()
            if s_brutas.data:
                for sug in s_brutas.data:
                    id_sug = sug["id"]
                    t_col = f"📥 Termo: " \
                        f"\"{sug['item_solicitado']}\""
                    with st.expander(t_col):
                        n_homolog = \
                            st.selectbox(
                                "Segmento:",
                                ["Supermercado",
                                 "Saúde",
                                 "Petshop",
                                 "Beleza"],
                                key=f"sel_{id_sug}"
                            )
                        n_corrigido = \
                            st.text_input(
                                "Termo:",
                                value=sug[
                                    'item_solicitado'],
                                key=f"tx_{id_sug}"
                            )
                        if st.button(
                            "✅ Homologar",
                            key=f"btn_h_{id_sug}"
                        ):
                            supabase.table(
                                "relatos_escassez"
                            ).update({
                                "item_solicitado":
                                    n_corrigido
                                    .strip().title(),
                                "sub_segmento":
                                    n_homolog
                            }).eq(
                                "id", id_sug
                            ).execute()
                            st.success("🎉 Sim!")
                            import time
                            time.sleep(0.5)
                            st.rerun()
        except:
            pass

    else:
        try:
            resposta_bruta = supabase\
                .table("relatos_escassez")\
                .select(
                    "id, item_solicitado, "
                    "tipo_carencia, "
                    "data_registro, status, "
                    "observacao_detalhe, "
                    "sub_segmento, "
                    "pegada_digital, "
                    "contato_aviso, "
                    "locais_destino("
                    "nome_exibicao, "
                    "regiao_cidade)"
                ).execute()
            cidades_detectadas = set()
            bairros_por_cidade = {}
            dados_brutos_limpos = []
            agora = datetime.datetime.now(
                datetime.timezone.utc
            )
            if resposta_bruta.data:
                for reg in resposta_bruta.data:
                    if reg.get("locais_destino"):
                        loc_c = str(
                            reg["locais_destino"]
                            ["regiao_cidade"]
                        ).strip()
                        if " - " in loc_c:
                            c_raiz, b_raiz = \
                                loc_c.split(" - ", 1)
                            c_raiz = c_raiz.strip()
                            b_raiz = b_raiz.strip()
                        else:
                            c_raiz = loc_c
                            b_raiz = "Geral"
                        cidades_detectadas.add(c_raiz)
                        if c_raiz not in \
                           bairros_por_cidade:
                            bairros_por_cidade[
                                c_raiz] = set()
                        bairros_por_cidade[
                            c_raiz].add(b_raiz)
                        sub_seg = str(
                            reg.get(
                                "sub_segmento",
                                "Geral"
                            )
                        ).strip()
                        cat_b = str(
                            reg.get(
                                "tipo_carencia",
                                "Produto / Marca"
                            )
                        ).strip()
                        idade_dias = max(0, (
                            agora - datetime.datetime
                            .fromisoformat(
                                reg.get("data_registro")
                                .replace("Z", "+00:00")
                            )
                        ).days) if reg.get(
                            "data_registro"
                        ) else 0
                        cat_limpa = \
                            "Serviço Público / " \
                            "Infraestrutura" \
                            if ("Público" in cat_b or
                                "Publico" in cat_b or
                                "Infra" in cat_b or
                                "Zeladoria" in sub_seg) \
                            else (
                                "Serviço Local / "
                                "Novo"
                                " Estabelecimento"
                                if ("Local" in cat_b or
                                    "Invest" in sub_seg)
                                else "Produto / Marca"
                            )
                        item_limpo = str(
                            reg["item_solicitado"]
                        ).rstrip(" 0123456789")\
                         .strip().title()
                        n_local_b = \
                            reg["locais_destino"]["nome_exibicao"]
                        if p_cli in [
                            "comerciante", "saude",
                            "petshop", "beleza"
                        ] and n_local_b != \
                                loja_alvo_prioridade:
                            if sub_seg == "Supermercado":
                                n_local_ex = \
                                    "Mercado Concorrente"
                            elif sub_seg in \
                                    ["Saude", "Saúde"]:
                                n_local_ex = \
                                    "Clínica Concorrente"
                            elif sub_seg == "Petshop":
                                n_local_ex = \
                                    "Petshop Concorrente"
                            elif sub_seg == "Beleza":
                                n_local_ex = \
                                    "Salão Concorrente"
                            else:
                                n_local_ex = \
                                    "Parceiro Comercial"
                        else:
                            n_local_ex = \
                                n_local_b
                        dados_brutos_limpos.append({
                            "ID": reg["id"],
                            "O que Falta":
                                item_limpo,
                            "Categoria":
                                cat_limpa,
                            "Local/Referência":
                                n_local_ex,
                            "CidadeRaiz":
                                c_raiz,
                            "Bairro":
                                b_raiz,
                            "CidadeCompleta":
                                loc_c,
                            "Dias":
                                idade_dias,
                            "Observação":
                                reg.get(
                                    "observacao_detalhe"
                            ) or "Sem detalhes.",
                            "SubSegmento":
                                sub_seg,
                            "Pegada":
                                reg.get("pegada_digital") or
                                f"anon_{reg['id']}",
                            "Contato":
                                reg.get("contato_aviso") or ""
                        })

            l_cidades = [
                "[ Mostrar Todas as Cidades ]"
            ] + sorted(list(cidades_detectadas))
            cidade_sel = st.selectbox(
                "📍 1. Selecionar Cidade (Global):",
                options=l_cidades,
                key="b2b_cidade_auto"
            )
            if city_sel := cidade_sel:
                pass
            if cidade_sel == \
               "[ Mostrar Todas as Cidades ]":
                bairro_sel = st.selectbox(
                    "🏘️ 2. Refinar por Bairro:",
                    options=[
                        "--- Selecione uma Cidade ---"
                    ],
                    disabled=True,
                    key="b2b_bairro_auto"
                )
            else:
                b_opts = [
                    " Mostrar Todos os Bairros "
                ] + sorted(list(
                    bairros_por_cidade.get(
                        cidade_sel, set()
                    )
                ))
                bairro_sel = st.selectbox(
                    "🏘️ 2. Refinar por Bairro:",
                    options=b_opts,
                    key="b2b_bairro_auto"
                )

            df_total = pd.DataFrame(
                dados_brutos_limpos
            ) if dados_brutos_limpos else \
                pd.DataFrame(columns=[
                    "ID", "O que Falta", "Categoria",
                    "Local/Referência", "CidadeRaiz",
                    "Bairro", "CidadeCompleta", "Dias",
                    "Observação", "SubSegmento",
                    "Pegada", "Contato"
                ])
            if not df_total.empty:
                df_filtrado = df_total
                if cidade_sel != \
                   "[ Mostrar Todas as Cidades ]":
                    df_filtrado = df_filtrado[
                        df_filtrado['CidadeRaiz'] ==
                        cidade_sel
                    ]
                    if bairro_sel != \
                       " Mostrar Todos os Bairros ":
                        df_filtrado = df_filtrado[
                            df_filtrado['Bairro'] ==
                            bairro_sel
                        ]
                st.session_state.dados_grafico = \
                    df_filtrado
            else:
                st.session_state.dados_grafico = \
                    df_total
        except Exception as e:
            st.error(f"⚠️ Erro de performance: {str(e)}")
        if st.session_state.dados_grafico \
           is not None:
            df = st.session_state\
                .dados_grafico
            if not df.empty:
                if p_cli == "comerciante":
                    n_abas = ["📦 Varejo",
                              "🎯 Marketplace Reverso"]
                elif p_cli == "saude":
                    n_abas = ["📦 Saúde",
                              "🎯 Marketplace Reverso"]
                elif p_cli == "petshop":
                    n_abas = ["📦 Pet",
                              "🎯 Marketplace Reverso"]
                elif p_cli == "beleza":
                    n_abas = ["📦 Estética",
                              "🎯 Marketplace Reverso"]
                elif p_cli == "investidor":
                    n_abas = ["💼 Novos Negócios"]
                elif p_cli == "jornalista":
                    n_abas = ["🏛️ Infraestrutura",
                              "💼 Novos Negócios"]
                else:
                    n_abas = ["🏛️ Infraestrutura"]

                abas_st = st.tabs(n_abas)
                for num_aba, n_aba_atv \
                        in enumerate(n_abas):
                    with abas_st[num_aba]:
                        fr_atv = "Infra" \
                            if "Infra" in n_aba_atv \
                            else ("Services"
                                  if "Negócios" in n_aba_atv
                                  else "Varejo")
                        is_rev = "Marketplace Reverso" \
                            in n_aba_atv
                        if is_rev and not \
                           st.session_state\
                           .get("recursos_liberados", {})\
                           .get("reverso", True):
                            st.warning("🔒 Suspensa.")
                            continue
                        df_f_aba = df
                        if fr_atv == "Infra":
                            df_f_aba = df[
                                df['Categoria'] ==
                                "Serviço Público / "
                                "Infraestrutura"
                            ]
                        elif fr_atv == "Services":
                            df_f_aba = df[
                                df['Categoria'] ==
                                "Serviço Local / "
                                "Novo"
                                " Estabelecimento"
                            ]
                        elif fr_atv == "Varejo":
                            if p_cli == "comerciante":
                                df_f_aba = df[df['SubSegmento'].str.contains(
                                    "Supermercado|Geral", case=False, na=False)]
                            elif p_cli == "saude":
                                df_f_aba = df[df['SubSegmento'].str.contains(
                                    "Saude|Saúde", case=False, na=False)]
                            elif p_cli == "petshop":
                                df_f_aba = df[df['SubSegmento'].str.contains(
                                    "Pet", case=False, na=False)]
                            elif p_cli == "beleza":
                                df_f_aba = df[df['SubSegmento'].str.contains(
                                    "Beleza", case=False, na=False)]
                        if termo_busca:
                            df_f_aba = df_f_aba[df_f_aba['O que Falta'].str.contains(
                                termo_busca, case=False) | df_f_aba['Local/Referência'].str.contains(termo_busca, case=False)]

                        if not df_f_aba.empty:
                            df_f_aba['É_Minha_Loja'] = \
                                df_f_aba['Local/Referência']\
                                .apply(lambda x: 1
                                       if x == loja_alvo_prioridade
                                       else 0)
                            pode_pdf = \
                                st.session_state\
                                .get("recursos_liberados", {})\
                                .get("pdf", True)

                            # 📄 RESTAURAÇÃO DO BOTÃO DO PDF: Reativado nativamente no topo de cada aba
                            if pode_pdf:
                                try:
                                    p_o = FPDF()
                                    p_o.add_page()
                                    p_o.set_font("Arial", size=12)
                                    p_o.cell(
                                        200, 10, txt="Relatorio de Demanda", ln=1, align="C")
                                    for _, r in df_f_aba.iterrows():
                                        p_o.cell(190, 10, txt=f"- Falta: {r['O que Falta']} | Ponto: {r['Local/Referência']}".encode(
                                            'latin-1', 'ignore').decode('latin-1'), ln=1)
                                    st.download_button(
                                        label="📄 Baixar Relatório de Demandas (PDF)",
                                        data=bytes(p_o.output(dest='S')),
                                        file_name="demandas_quarteirao.pdf",
                                        mime="application/pdf",
                                        key=f"btn_pdf_real_final_{num_aba}"
                                    )
                                except:
                                    pass

                            total_sua_loja = len(
                                df_f_aba[df_f_aba['Local/Referência'] == loja_alvo_prioridade]) if not is_rev else 0
                            t_conc = len(df_f_aba) - total_sua_loja
                            st.markdown(
                                f"<div style='text-align: right; font-size: 15px; font-weight: bold; color: #00803B; margin-top: 10px; margin-bottom: 20px;'>Sua Loja: {total_sua_loja} • Concorrência: {t_conc} • Total Geral: {len(df_f_aba)}</div>", unsafe_allow_html=True)
                            df_agr = df_f_aba.groupby(["O que Falta", "Categoria"]).agg(V_Total=("ID", "count"), M_Idade=(
                                "Dias", "min"), F_Dono=("É_Minha_Loja", "max")).sort_values(by="V_Total", ascending=False).reset_index()
                            for _, linha in df_agr.iterrows():
                                i_nome = linha['O que Falta']
                                s_alvo = int(linha['F_Dono'])
                                if is_rev:
                                    c_tag = "tag-calor-media"
                                    l_tag = "🎯 REVERSO"
                                else:
                                    c_tag = "tag-calor-alta" if s_alvo == 1 else "tag-calor-baixa"
                                    l_tag = "🎯 SEU MERCADO" if s_alvo == 1 else "🌍 CONCORRÊNCIA"
                                st.markdown(
                                    f'<div class="bloco-lista-premium"><span class="{c_tag}">{l_tag} • {int(linha["V_Total"])} Pedidos</span><b style="color: #FFFFFF; font-size: 16px;">📦 {i_nome}</b><div style="margin-top: 0.5rem; color: #aaaaaa; font-size: 13px;">⏱️ Alerta ativo há {linha["M_Idade"]} dias</div></div>', unsafe_allow_html=True)
                                for _, s_l in df_f_aba[df_f_aba['O que Falta'] == i_nome].drop_duplicates(subset=["CidadeCompleta", "Local/Referência", "Observação", "Contato"]).iterrows():
                                    sub_id, sub_local, c_morador = s_l['ID'], s_l['Local/Referência'], s_l['Contato']
                                    is_dono_vazio = (
                                        sub_local == loja_alvo_prioridade) and not is_rev
                                    st.markdown(
                                        f"{'🔥 **SEU ESTABELECIMENTO:** ' if is_dono_vazio else '📍 **Captado no concorrente:** '}{sub_local} ({s_l['CidadeCompleta']})")
                                    if s_l['Observação']:
                                        st.info(
                                            f"💬 *Relato:* \"{s_l['Observação']}\"")
                                    pode_wa = st.session_state.get(
                                        "recursos_liberados", {}).get("whatsapp", True)

                                    # 🎯 REPADRONIZAÇÃO DO CONTATO: Transforma o aviso em um botão estruturado simétrico
                                    if c_morador and str(c_morador).strip() != "" and str(c_morador).strip() != "None" and pode_wa:
                                        st.markdown(f'<a href="https://whatsapp.com{c_morador.strip()}&text=Olá! Temos {i_nome} disponível!" target="_blank"><button style="background-color: #25D366 !important; color: white !important; font-weight: bold !important; border: none !important; padding: 0.5rem 1rem !important; border-radius: 8px !important; width: auto !important; margin-bottom: 10px; font-size: 14px; cursor: pointer;">📱 Falar no WhatsApp</button></a>', unsafe_allow_html=True)
                                    elif c_morador and str(c_morador).strip() != "" and not pode_wa:
                                        st.warning("🔒 WhatsApp Bloqueado.")
                                    else:
                                        # Justificativa visual em formato de botão fosco alinhado para evitar o vácuo de tela
                                        st.markdown(
                                            "<div class='botao-contato-vazio-v'>⚠️ sem número de contato</div>", unsafe_allow_html=True)

                                        if not is_rev and is_dono_vazio:
                                            id_conf = f"confirma_baixa_{sub_id}"
                                            if id_conf not in st.session_state:
                                                st.session_state[id_conf] = False

                                            if not st.session_state[id_conf]:
                                                if st.button(f"Dar baixa no {sub_local}", key=f"btn_pre_{sub_id}_{num_aba}"):
                                                    st.session_state[id_conf] = True
                                                    st.rerun()
                                            else:
                                                if st.button("🚨 Confirmar", key=f"btn_real_{sub_id}_{num_aba}"):
                                                    supabase.table("relatos_escassez").update(
                                                        {"status": "Atendido"}).eq("id", sub_id).execute()
                                                    st.success("🎉 Concluído!")
                                                    import time
                                                    time.sleep(0.5)
                                                    st.session_state[id_conf] = False
                                                    st.session_state.busca_ativa = False
                                                    st.rerun()
                        else:
                            st.info(
                                "ℹ️ Nenhum registro ativo encontrado para esta aba.")
