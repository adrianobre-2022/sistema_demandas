import streamlit as st
import pandas as pd
import datetime
import urllib.parse
from fpdf import FPDF

# 📄 GERADOR DE PDF INDEPENDENTE


def gerar_pdf_demandas(df_aba):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(
            200, 10,
            txt="Relatorio de Demandas",
            ln=1, align="C"
        )
        for _, r in df_aba.iterrows():
            txt_l = f"- Falta: {r['O que Falta']} " \
                f"| Local: {r['Local/Referência']}"
            pdf.cell(
                190, 10,
                txt=txt_l.encode(
                    'latin-1', 'ignore'
                ).decode('latin-1'),
                ln=1
            )
        return bytes(pdf.output(dest='S'))
    except:
        return b""

# 📱 WHATSAPP COMPACTO ORIGINAL RESTAURADO


def desenhar_morador(
    s_l, nm, num_aba, supabase, loja_alvo
):
    sub_id = s_l['ID']
    sub_local = s_l['Local/Referência']
    c_morador = s_l['Contato']
    is_rev = st.session_state.get(
        "is_marketplace_reverso", False
    )
    is_dono_vazio = (sub_local == loja_alvo) \
        and not is_rev

    p_txt = '🔥 **SEU ESTABELECIMENTO:** ' \
        if is_dono_vazio else \
        '📍 **Captado no concorrente:** '
    st.markdown(
        f"{p_txt}{sub_local} "
        f"({s_l['CidadeCompleta']})"
    )
    if s_l['Observação'] and \
       s_l['Observação'] != "Sem detalhes.":
        st.info(f"💬 *Relato:* \"{s_l['Observação']}\"")

    c_morador_s = str(c_morador).strip()
    is_ok_w = c_morador_s != "" \
        and c_morador_s != "None"

    if is_ok_w:
        msg_enc = urllib.parse.quote(
            f"Olá! Temos {nm} disponível "
            f"no quarteirão!"
        )
        # HTML ORIGINAL BLINDADO CONTRA CORTES
        html_wa = (
            f'<a href="https://whatsapp.com'
            f'send?phone=55{c_morador_s}&text='
            f'{msg_enc}" target="_blank">'
            f'<button style="background-color: '
            f'#25D366 !important; color: white '
            f'!important; font-weight: bold '
            f'!important; border: none !important; '
            f'padding: 0.5rem 1rem !important; '
            f'border-radius: 8px !important; '
            f'width: auto !important; margin-bottom: '
            f'10px; font-size: 14px; cursor: '
            f'pointer;">📱 Falar no WhatsApp'
            f'</button></a>'
        )
        st.markdown(html_wa, unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='botao-contato-vazio-v'>"
            "⚠️ sem número de contato</div>",
            unsafe_allow_html=True
        )

    if is_dono_vazio:
        id_conf = f"confirma_baixa_{sub_id}"
        if id_conf not in st.session_state:
            st.session_state[id_conf] = False
        if not st.session_state[id_conf]:
            if st.button(
                f"Dar baixa no {sub_local}",
                key=f"btn_pre_{sub_id}_{num_aba}"
            ):
                st.session_state[id_conf] = True
                st.rerun()
        else:
            if st.button(
                "🚨 Confirmar Exclusão",
                key=f"btn_real_{sub_id}_{num_aba}"
            ):
                supabase.table("relatos_escassez")\
                    .update({"status": "Atendido"})\
                    .eq("id", sub_id).execute()
                st.success("🎉 Concluído!")
                import time
                time.sleep(0.5)
                st.session_state[id_conf] = False
                st.session_state.busca_ativa = False
                st.rerun()


def renderizar(supabase):
    loja_alvo_prioridade = "Mercadinho Do Bairro"
    termo_busca = st.session_state.get(
        "termo_busca_temp", ""
    )
    p_cli = st.session_state.perfil_cliente

    # ⬅️ BARRA DE NAVEGAÇÃO DE DESCONEXÃO
    col_nav1, _ = st.columns(2)
    with col_nav1:
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

    # 🛠️ CONTEXTO DO ADMIN MESTRE
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
            nome_novo = st.text_input(
                "Nome do Estabelecimento:",
                placeholder="Ex: Supermercado..."
            )
            perfil_novo = st.selectbox(
                "Perfil de Acesso Corporativo:",
                ["comerciante", "saude",
                 "petshop", "beleza",
                 "investidor", "gestor",
                 "jornalista"]
            )
            regiao_novo = st.text_input(
                "Região/Cidade de Atuação:",
                placeholder="Ex: São Paulo/SP..."
            )
            if st.form_submit_button(
                "💼 Cadastrar Lojista"
            ):
                if nome_novo and regiao_novo:
                    try:
                        n_c = nome_novo.strip().title()
                        r_c = regiao_novo.strip()
                        supabase.table("clientes_b2b")\
                            .insert({
                                "nome_estabelecimento":
                                    n_c,
                                "perfil_segmento":
                                    perfil_novo,
                                "regiao_atuacao":
                                    r_c,
                                "status_pagamento":
                                    "Ativo",
                                "recurso_marketplace_"
                                "reverso": True,
                                "recurso_whatsapp":
                                    True,
                                "recurso_pdf": True
                            }).execute()
                        st.success("🎉 Cadastrado!")
                        import time
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as err:
                        st.error(f"Erro: {str(err)}")

        st.markdown(
            "<h3 style='text-align: center;'"
            ">📊 Central Financeira</h3>",
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
                    n_est = cli['nome_estabelecimento']
                    with st.expander(f"🏢 {n_est}"):
                        st.text_input(
                            "🔑 Token Completo:",
                            value=cli['token_acesso'],
                            disabled=True,
                            key=f"tk_full_{c_id}"
                        )
                        col_status, col_plan = \
                            st.columns(2)
                        with col_status:
                            status_pag = st.selectbox(
                                "Status de Pagamento:",
                                ["Ativo",
                                 "Inadimplente",
                                 "Cancelado"],
                                index=[
                                    "Ativo",
                                    "Inadimplente",
                                    "Cancelado"
                                ].index(cli.get(
                                    "status_pagamento",
                                    "Ativo"
                                )),
                                key=f"pay_{c_id}"
                            )
                        with col_plan:
                            plano_cont = st.selectbox(
                                "Plano Contratado:",
                                ["Bronze",
                                 "Prata",
                                 "Ouro"],
                                index=[
                                    "Bronze",
                                    "Prata",
                                    "Ouro"
                                ].index(cli.get(
                                    "plano_contratado",
                                    "Ouro"
                                )),
                                key=f"plan_{c_id}"
                            )
                        if st.button(
                            "💾 Salvar Alterações",
                            key=f"save_{c_id}"
                        ):
                            supabase.table(
                                "clientes_b2b"
                            ).update({
                                "status_pagamento":
                                    status_pag,
                                "plano_contratado":
                                    plano_cont
                            }).eq("id", c_id).execute()
                            st.success("🔒 Sincronizado!")
                            import time
                            time.sleep(0.5)
                            st.rerun()
        except:
            pass
    # CONTEXTO DOS LOJISTAS
    else:
        try:
            r_bruta = supabase\
                .table(
                    "relatos_"
                    "escassez"
                ).select(
                    "id, item_"
                    "solicitado, "
                    "tipo_care"
                    "ncia, data_"
                    "registro, "
                    "status, obs"
                    "ervacao_de"
                    "talhe, sub_"
                    "segmento, "
                    "pegada_di"
                    "gital, con"
                    "tato_avis"
                    "o, locais_"
                    "destino(n"
                    "ome_exibi"
                    "cao, regia"
                    "o_cidade)"
                ).execute()
            c_det = set()
            b_c = {}
            d_limpos = []
            agora = datetime\
                .datetime.now(
                    datetime
                    .timezone.utc
                )

            if r_bruta.data:
                for reg in \
                        r_bruta.data:
                    st_r = \
                        reg.get("status")
                    l_dest = \
                        reg.get(
                            "locais_"
                            "destino"
                        )
                    is_pnd = (
                        st_r
                        !=
                        "Atendido"
                    )
                    if is_pnd \
                       and l_dest:
                        loc_c = \
                            str(
                                l_dest[
                                    "regiao_"
                                    "cidade"]
                            ).strip()
                        if " - " \
                           in loc_c:
                            c_rz, \
                                b_rz = \
                                loc_c\
                                .split(
                                    " - ",
                                    1
                                )
                        else:
                            c_rz = \
                                loc_c
                            b_rz = \
                                "Geral"
                        c_rz = \
                            c_rz.strip()
                        b_rz = \
                            b_rz.strip()
                        c_det.add(c_rz)
                        if c_rz \
                           not in \
                           b_c:
                            b_c[
                                c_rz] \
                                = set()
                        b_c[c_rz]\
                            .add(b_rz)

                        sub_seg = \
                            str(
                                reg.get(
                                    "sub_se"
                                    "gmento",
                                    "Geral"
                                )
                            ).strip()
                        cat_b = \
                            str(
                                reg.get(
                                    "tipo_ca"
                                    "rencia",
                                    "Produto"
                                    " / Marca"
                                )
                            ).strip()
                        dt = reg.get(
                            "data_re"
                            "gistro"
                        )
                        if dt:
                            dt_c = \
                                dt\
                                .replace(
                                    "Z",
                                    "+00:00"
                                )
                            idade_d = \
                                max(
                                    0, (
                                        agora
                                        -
                                        datetime
                                        .datetime
                                        .fromisoformat(
                                            dt_c
                                        )
                                    ).days)
                        else:
                            idade_d = 0
                        is_p = (
                            "Público" in cat_b or
                            "Publico" in cat_b or
                            "Infra" in cat_b or
                            "Zeladoria" in sub_seg
                        )
                        is_l = (
                            "Local" in cat_b or
                            "Invest" in sub_seg
                        )
                        c_lm = (
                            "Serviço Público / "
                            "Infraestrutura" if is_p
                            else (
                                "Serviço Local / "
                                "Novo Estabele"
                                "cimento" if is_l
                                else
                                "Produto / Marca"
                            )
                        )
                        i_lm = str(reg[
                            "item_solicitado"
                        ]).rstrip(" 0123456789")\
                          .strip().title()
                        n_local_b = l_dest[
                            "nome_exibicao"
                        ]

                        is_pl = p_cli in [
                            "comerciante", "saude",
                            "petshop", "beleza"
                        ]
                        is_diff = (
                            n_local_b !=
                            loja_alvo_prioridade
                        )
                        if is_pl and is_diff:
                            if sub_seg == \
                               "Supermercado":
                                n_ex = "Mercado " \
                                       "Concorrente"
                            elif sub_seg in \
                                    ["Saude", "Saúde"]:
                                n_ex = "Clínica " \
                                       "Concorrente"
                            elif sub_seg == \
                                    "Petshop":
                                n_ex = "Petshop " \
                                       "Concorrente"
                            elif sub_seg == \
                                    "Beleza":
                                n_ex = "Salão " \
                                       "Concorrente"
                            else:
                                n_ex = "Parceiro " \
                                       "Comercial"
                        else:
                            n_ex = n_local_b

                        dados_brutos_limpos.append({
                            "ID": reg["id"],
                            "O que Falta": i_lm,
                            "Categoria": c_lm,
                            "Local/Referência": n_ex,
                            "CidadeRaiz": c_rz,
                            "Bairro": b_rz,
                            "CidadeCompleta": loc_c,
                            "Dias": idade_d,
                            "Observação": reg.get(
                                "observacao_detalhe"
                            ) or "Sem detalhes.",
                            "SubSegmento": sub_seg,
                            "Pegada": reg.get(
                                "pegada_digital"
                            ) or f"an_{reg['id']}",
                            "Contato": reg.get(
                                "contato_aviso"
                            ) or ""
                        })

            l_c = [
                "[ Mostrar Todas as Cidades ]"
            ] + sorted(list(c_det))
            c_sel = st.selectbox(
                "📍 1. Selecionar Cidade (Global):",
                options=l_c, key="b2b_cidade_auto"
            )
            if c_sel == "[ Mostrar Todas as Cidades ]":
                b_sel = st.selectbox(
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
                ] + sorted(list(b_c.get(
                    c_sel, set()
                )))
                b_sel = st.selectbox(
                    "🏘️ 2. Refinar por Bairro:",
                    options=b_opts,
                    key="b2b_bairro_auto"
                )

            df_total = pd.DataFrame(
                dados_brutos_limpos
            ) if dados_brutos_limpos else pd.DataFrame(
                columns=[
                    "ID", "O que Falta",
                    "Categoria", "Local/Referência",
                    "CidadeRaiz", "Bairro",
                    "CidadeCompleta", "Dias",
                    "Observação", "SubSegmento",
                    "Pegada", "Contato"
                ]
            )
            is_glob = (
                c_sel != "[ Mostrar Todas as Cidades ]"
            )
            if not df_total.empty and is_glob:
                df_total = df_total[
                    df_total['CidadeRaiz'] == c_sel
                ]
                if b_sel != " Mostrar Todos os Bairros ":
                    df_total = df_total[
                        df_total['Bairro'] == b_sel
                    ]
            st.session_state.dados_grafico = df_total
        except Exception as e:
            st.error(f"⚠️ Erro: {str(e)}")
        if st.session_state\
           .dados_grafico \
           is not None:
            df = st.session_state\
                .dados_grafico
            if not df.empty:
                dict_n = {
                    "comerciante": [
                        "📦 Varejo",
                        "🎯 Marketplace "
                        "Reverso"
                    ],
                    "saude": [
                        "📦 Saúde",
                        "🎯 Marketplace "
                        "Reverso"
                    ],
                    "petshop": [
                        "📦 Pet",
                        "🎯 Marketplace "
                        "Reverso"
                    ],
                    "beleza": [
                        "📦 Estética",
                        "🎯 Marketplace "
                        "Reverso"
                    ],
                    "investidor": [
                        "💼 Novos Negócios"
                    ],
                    "jornalista": [
                        "🏛️ Infraestrutura",
                        "💼 Novos Negócios"
                    ]
                }
                n_abas = dict_n.get(
                    p_cli,
                    ["🏛️ Infra"
                     "estrutura"]
                )

                abas_st = st.tabs(
                    n_abas
                )
                for num_aba, \
                        n_aba_atv in \
                        enumerate(n_abas):
                    with abas_st[
                        num_aba
                    ]:
                        is_inf = (
                            "Infra"
                            in
                            n_aba_atv
                        )
                        is_srv = (
                            "Negócios"
                            in
                            n_aba_atv
                        )
                        fr_atv = \
                            "Infra" if \
                            is_inf \
                            else (
                                "Services"
                                if
                                is_srv
                                else
                                "Varejo"
                            )
                        is_rev = \
                            "Marketplace" \
                            in n_aba_atv
                        st.session_state[
                            "is_market"
                            "place_re"
                            "verso"] = \
                            is_rev

                        df_f_aba = df
                        if fr_atv == \
                           "Infra":
                            df_f_aba = \
                                df[
                                    df[
                                        'Categoria']
                                    ==
                                    "Serviço "
                                    "Público / "
                                    "Infra"
                                    "estrutura"
                                ]
                        elif fr_atv == \
                                "Services":
                            df_f_aba = \
                                df[
                                    df[
                                        'Categoria']
                                    ==
                                    "Serviço "
                                    "Local / "
                                    "Novo Est"
                                    "abelec"
                                    "imento"
                                ]
                        elif fr_atv == \
                                "Varejo":
                            map_filtros = {
                                "comerciante":
                                    "Supermercado"
                                    "|Geral",
                                "saude":
                                    "Saude|Saúde",
                                "petshop":
                                    "Pet",
                                "beleza":
                                    "Beleza"
                            }
                            f_rg = \
                                map_filtros\
                                .get(
                                    p_cli,
                                    "Geral"
                                )
                            df_f_aba = df[df['SubSegmento'].str.contains(
                                f_rg, case=False, na=False)]

                        if termo_busca:
                            c_it = df_f_aba[
                                'O que Falta']\
                                .str.contains(
                                termo_busca,
                                case=False
                            )
                            c_lc = df_f_aba[
                                'Local/'
                                'Referência']\
                                .str.contains(
                                termo_busca,
                                case=False
                            )
                            df_f_aba = df_f_aba[
                                c_it | c_lc
                            ]
                        if not \
                           df_f_aba\
                           .empty:
                            df_f_aba[
                                'É_Minha_Loja'] = \
                                df_f_aba[
                                'Local/'
                                'Referên'
                                'cia']\
                                .apply(
                                    lambda
                                    x: 1
                                    if x ==
                                    loja_alvo_
                                    prioridade
                                    else 0
                            )

                            # 📄 ATENDIDO: IMPRESSÃO EM PDF INCONDICIONAL NO TOPO
                            bytes_pdf = \
                                gerar_pdf_demandas(
                                    df_f_aba
                                )
                            if bytes_pdf:
                                st\
                                    .download_button(
                                        label="📄 Baixar "
                                        "Relatório "
                                        "(PDF)",
                                        data=bytes_pdf,
                                        file_name="demandas_"
                                        "quarteirao"
                                        ".pdf",
                                        mime="applicat"
                                        "ion/pdf",
                                        key=f"btn_"
                                        f"pdf_"
                                        f"real_"
                                        f"{num_aba}"
                                    )

                            t_sua = len(
                                df_f_aba[
                                    df_f_aba[
                                        'Local/'
                                        'Referê'
                                        'ncia'] ==
                                    loja_alvo_
                                    prioridade
                                ]
                            ) if not \
                                is_rev else 0
                            t_con = (
                                len(
                                    df_f_aba
                                ) -
                                t_sua
                            )
                            st.markdown(
                                f"Sua Loja"
                                f": {t_sua} "
                                f"| Outros"
                                f": {t_con} "
                                f"| Total"
                                f": {len(
                                    df_f_aba)}"
                            )

                            df_agr = \
                                df_f_aba\
                                .groupby([
                                    "O que "
                                    "Falta",
                                    "Categor"
                                    "ia"
                                ]).agg(
                                    V_Total=(
                                        "ID",
                                        "count"
                                    ),
                                    M_Idade=(
                                        "Dias",
                                        "min"
                                    ),
                                    F_Dono=(
                                        "É_Minha"
                                        "_Loja",
                                        "max"
                                    )
                                ).sort_values(
                                    by="V_"
                                       "Total",
                                    ascending=False
                                ).reset_index()
                            for _, \
                                    linha in \
                                    df_agr\
                                    .iterrows():
                                i_nome = \
                                    linha[
                                        'O que '
                                        'Falta']
                                s_alvo = \
                                    int(
                                        linha[
                                            'F_Dono']
                                    )
                                if is_rev:
                                    tg = "REV"
                                else:
                                    tg = \
                                        "MINHA" \
                                        if \
                                        s_alvo \
                                        == 1 \
                                        else \
                                        "OUTRA"

                                num_p = \
                                    int(
                                        linha[
                                            "V_Total"]
                                    )
                                d_id = \
                                    int(
                                        linha[
                                            "M_Idade"]
                                    )
                                txt_m = \
                                    f"📦 {i_nome} " \
                                    f"({tg}) | " \
                                    f"{num_p} ped" \
                                    f" | {d_id}d"
                                st.markdown(
                                    txt_m
                                )

                                df_f_it = \
                                    df_f_aba[
                                        df_f_aba[
                                            'O que '
                                            'Falta']
                                        == i_nome
                                    ].drop_du\
                                    plicates(
                                        subset=[
                                            "ID"
                                        ]
                                    )
                                for _, \
                                        s_l in \
                                        df_f_it\
                                        .iterrows():
                                    desenhar_morador(
                                        s_l,
                                        i_nome,
                                        num_aba,
                                        supabase,
                                        loja_alvo_prioridade
                                    )
                        else:
                            st.info(
                                "ℹ️ Vazio."
                            )
