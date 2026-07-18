import streamlit as st
import pandas as pd
import datetime
import urllib.parse
from fpdf import FPDF

# 📄 GERADOR DE PDF ISOLADO


def gerar_pdf_demandas(df_aba):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(
            200, 10,
            txt="Relatorio Demandas",
            ln=1, align="C"
        )
        for _, r in df_aba.iterrows():
            txt_l = f"- {r['O que Falta']} " \
                f"| {r['Local/Referência']}"
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


def renderizar(supabase):
    loja_alvo_prioridade = "Mercadinho Do Bairro"
    termo_busca = st.session_state.get(
        "termo_busca_temp", ""
    )
    p_cli = st.session_state.perfil_cliente

    # NAVEGAÇÃO SUPERIOR NATIVA
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

    # PAINEL MESTRE ADMINISTRADOR
    if p_cli == "admin":
        st.markdown(
            "<h3>🛠️ ERP Cadastros</h3>",
            unsafe_allow_html=True
        )
        with st.form(
            key="form_admin_mestre_cad",
            clear_on_submit=True
        ):
            nome_novo = st.text_input(
                "Nome do Estabelecimento:"
            )
            perfil_novo = st.selectbox(
                "Perfil de Acesso:",
                ["comerciante", "saude",
                 "petshop", "beleza",
                 "investidor", "gestor",
                 "jornalista"]
            )
            regiao_novo = st.text_input(
                "Região/Cidade de Atuação:"
            )
            if st.form_submit_button(
                "💼 Cadastrar Lojista"
            ):
                if nome_novo and regiao_novo:
                    try:
                        supabase.table(
                            "clientes_b2b"
                        ).insert({
                            "nome_estabelecimento":
                                nome_novo.strip()
                                .title(),
                            "perfil_segmento":
                                perfil_novo,
                            "regiao_atuacao":
                                regiao_novo.strip(),
                            "status_pagamento":
                                "Ativo",
                            "recurso_marketplace_"
                            "reverso": True,
                            "recurso_whatsapp":
                                True,
                            "recurso_pdf": True
                        }).execute()
                        st.success("🎉 Pronto!")
                        import time
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as err:
                        st.error(f"Erro: {err}")
        st.markdown(
            "<h3>📊 Central "
            "Financeira</h3>",
            unsafe_allow_html=True
        )
        try:
            r_c = supabase.table(
                "clientes_b2b"
            ).select("*").order(
                "created_at",
                desc=True
            ).execute()
            if r_c.data:
                for cli in r_c.data:
                    c_id = cli["id"]
                    n_e = cli[
                        'nome_estabele'
                        'cimento']
                    with st.expander(
                        f"🏢 {n_e}"
                    ):
                        col_s, col_p = \
                            st.columns(2)
                        with col_s:
                            st_p = \
                                st.selectbox(
                                    "Pagamento:",
                                    ["Ativo",
                                     "Inadimpl"
                                     "ente",
                                     "Cancela"
                                     "do"],
                                    index=[
                                        "Ativo",
                                        "Inadimpl"
                                        "ente",
                                        "Cancela"
                                        "do"
                                    ].index(
                                        cli.get(
                                            "status_pa"
                                            "gamento",
                                            "Ativo"
                                        )
                                    ),
                                    key=f"s_{c_id}"
                                )
                        with col_p:
                            pl_c = \
                                st.selectbox(
                                    "Plano:",
                                    ["Bronze",
                                     "Prata",
                                     "Ouro"],
                                    index=[
                                        "Bronze",
                                        "Prata",
                                        "Ouro"
                                    ].index(
                                        cli.get(
                                            "plano_con"
                                            "tratado",
                                            "Ouro"
                                        )
                                    ),
                                    key=f"p_{c_id}"
                                )
                        c_rev = \
                            st.checkbox(
                                "Marketplace "
                                "Reverso",
                                value=cli.get(
                                    "recurso_m"
                                    "arketplace"
                                    "_reverso",
                                    True
                                ),
                                key=f"r_{c_id}"
                            )
                        c_wa = \
                            st.checkbox(
                                "WhatsApp "
                                "LGPD",
                                value=cli.get(
                                    "recurso_w"
                                    "hatsapp",
                                    True
                                ),
                                key=f"w_{c_id}"
                            )
                        c_pdf = \
                            st.checkbox(
                                "Relatórios "
                                "PDF",
                                value=cli.get(
                                    "recurso_p"
                                    "df",
                                    True
                                ),
                                key=f"d_{c_id}"
                            )
                        if st.button(
                            "💾 Salvar",
                            key=f"f_{c_id}"
                        ):
                            supabase.table(
                                "clientes_"
                                "b2b"
                            ).update({
                                "status_pa"
                                "gamento":
                                    st_p,
                                "plano_con"
                                "tratado":
                                    pl_c,
                                "recurso_m"
                                "arketplace"
                                "_reverso":
                                    c_rev,
                                "recurso_w"
                                "hatsapp":
                                    c_wa,
                                "recurso_p"
                                "df":
                                    c_pdf
                            }).eq(
                                "id", c_id
                            ).execute()
                            st.success(
                                "🔒 Salvo!"
                            )
                            import time
                            time.sleep(0.5)
                            st.rerun()
        except:
            pass
    else:
        try:
            r_b = supabase.table(
                "relatos_escassez"
            ).select(
                "id, item_solicit"
                "ado, tipo_carenc"
                "ia, data_registr"
                "o, status, obser"
                "vacao_detalhe, "
                "sub_segmento, pe"
                "gada_digital, co"
                "ntato_aviso, loc"
                "ais_destino(nome"
                "_exibicao, regia"
                "o_cidade)"
            ).execute()
            c_det = set()
            b_c = {}
            d_l = []
            now = datetime\
                .datetime.now(
                    datetime
                    .timezone.utc
                )

            if r_b.data:
                for reg in \
                        r_b.data:
                    st_r = \
                        reg.get("status")
                    l_d = \
                        reg.get(
                            "locais_"
                            "destino"
                        )
                    is_ok = (
                        st_r
                        !=
                        "Atendido"
                        and l_d
                    )
                    if is_ok:
                        lc = str(
                            l_d[
                                "regiao_"
                                "cidade"]
                        ).strip()
                        if " - " \
                           in lc:
                            cr, \
                                br = \
                                lc.split(
                                    " - ",
                                    1
                                )
                        else:
                            cr = lc
                            br = \
                                "Geral"
                        cr = \
                            cr.strip()
                        br = \
                            br.strip()
                        c_det.add(cr)
                        if cr \
                           not in \
                           b_c:
                            b_c[
                                cr] = \
                                set()
                        b_c[cr]\
                            .add(br)

                        sub = str(
                            reg.get(
                                "sub_seg"
                                "mento",
                                "Geral"
                            )
                        ).strip()
                        cat = str(
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
                        dias = max(
                            0, (
                                now -
                                datetime
                                .datetime
                                .fromisoformat(
                                    dt
                                    .replace(
                                        "Z",
                                        "+00:00"
                                    )
                                )
                            ).days) if \
                            dt else 0
                        is_p = (
                            "Público" in cat or
                            "Publico" in cat or
                            "Infra" in cat or
                            "Zeladoria" in sub
                        )
                        is_l = (
                            "Local" in cat or
                            "Invest" in sub
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
                        n_lc = l_d["nome_exibicao"]
                        is_df = (
                            n_lc !=
                            loja_alvo_prioridade
                        )
                        is_pl = p_cli in [
                            "comerciante", "saude",
                            "petshop", "beleza"
                        ]

                        if is_pl and is_df:
                            if sub == "Supermercado":
                                n_ex = "Mercado " \
                                       "Concorrente"
                            elif sub in ["Saude",
                                         "Saúde"]:
                                n_ex = "Clínica " \
                                       "Concorrente"
                            elif sub == "Petshop":
                                n_ex = "Petshop " \
                                       "Concorrente"
                            elif sub == "Beleza":
                                n_ex = "Salão " \
                                       "Concorrente"
                            else:
                                n_ex = "Parceiro " \
                                       "Comercial"
                        else:
                            n_ex = n_lc

                        d_l.append({
                            "ID": reg["id"],
                            "O que Falta": i_lm,
                            "Categoria": c_lm,
                            "Local/Referência": n_ex,
                            "CidadeRaiz": cr,
                            "Bairro": br,
                            "CidadeCompleta": lc,
                            "Dias": dias,
                            "Observação": reg.get(
                                "observacao_detalhe"
                            ) or "Sem detalhes.",
                            "SubSegmento": sub,
                            "Pegada": reg.get(
                                "pegada_digital"
                            ) or f"an_{reg['id']}",
                            "Contato": reg.get(
                                "contato_aviso"
                            ) or ""
                        })
            l_c = [
                "[ Mostrar Todas "
                "as Cidades ]"
            ] + sorted(
                list(c_det)
            )
            c_sel = \
                st.selectbox(
                    "📍 1. Selecionar "
                    "Cidade (Global):",
                    options=l_c,
                    key="b2b_c_auto"
                )
            if c_sel == (
               "[ Mostrar Todas "
               "as Cidades ]"
               ):
                b_sel = \
                    st.selectbox(
                        "🏘️ 2. Refinar "
                        "por Bairro:",
                        options=[
                            "--- Selecione "
                            "uma Cidade ---"
                        ],
                        disabled=True,
                        key="b2b_b_auto"
                    )
            else:
                b_o = [
                    " Mostrar Todos "
                    "os Bairros "
                ] + sorted(
                    list(
                        b_c.get(
                            c_sel,
                            set()
                        )
                    )
                )
                b_sel = \
                    st.selectbox(
                        "🏘️ 2. Refinar "
                        "por Bairro:",
                        options=b_o,
                        key="b2b_b_auto"
                    )

            df_total = pd.DataFrame(
                d_l
            ) if d_l else \
                pd.DataFrame(
                    columns=[
                        "ID",
                        "O que Falta",
                        "Categoria",
                        "Local/Referên"
                        "cia",
                        "CidadeRaiz",
                        "Bairro",
                        "CidadeComplet"
                        "a",
                        "Dias",
                        "Observação",
                        "SubSegmento",
                        "Pegada",
                        "Contato"
                    ]
            )
            if not df_total.empty and \
               c_sel != (
                   "[ Mostrar Todas "
                   "as Cidades ]"
               ):
                df_total = df_total[
                    df_total[
                        'CidadeRaiz']
                    == c_sel
                ]
                if b_sel != (
                    " Mostrar Todos "
                    "os Bairros "
                ):
                    df_total = \
                        df_total[
                            df_total[
                                'Bairro']
                            == b_sel
                        ]
            st.session_state\
              .dados_grafico = \
                df_total
        except Exception as e:
            st.error(
                f"⚠️ Erro: {str(e)}"
            )
        if st.session_state\
           .dados_grafico \
           is not None:
            df = st.session_state\
                .dados_grafico
            if not df.empty:
                dict_nichos = {
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
                n_abas = dict_nichos\
                    .get(
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
                        dict_liberados = \
                            st\
                            .session_state\
                            .get(
                                "recursos_"
                                "liberados",
                                {}
                            )
                        p_rev = (
                            dict_liberados
                            .get(
                                "reverso",
                                True
                            )
                            if isinstance(
                                dict_liberados,
                                dict
                            )
                            else True
                        )
                        if is_rev and \
                           not p_rev:
                            st.warning(
                                "🔒 Suspensa."
                            )
                            continue
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
                            df_f_aba = df[df['SubSegmento'].str.contains(
                                map_filtros.get(p_cli, "Geral"), case=False, na=False)]

                        if termo_busca:
                            c_item = df_f_aba['O que Falta'].str.contains(
                                termo_busca, case=False)
                            c_local = df_f_aba['Local/Referência'].str.contains(
                                termo_busca, case=False)
                            df_f_aba = df_f_aba[c_item | c_local]
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
                            p_pdf = (
                                dict_liberados
                                .get(
                                    "pdf",
                                    True
                                )
                                if isinstance(
                                    dict_liberados,
                                    dict
                                )
                                else True
                            )

                            # 📄 ATENDIDO: BOTÃO DE PDF REACTIVADO NATIVAMENTE NO TOPO DE CADA ABA
                            if p_pdf:
                                bytes_pdf = \
                                    gerar_pdf_demandas(
                                        df_f_aba
                                    )
                                if bytes_pdf:
                                    st\
                                        .download_button(
                                            label="📄 Baixar "
                                            "Relatório de "
                                            "Demandas "
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
                                            f"final_"
                                            f"{num_aba}"
                                        )

                            t_sua = len(
                                df_f_aba[
                                    df_f_aba[
                                        'Local/'
                                        'Refer\u00ea'
                                        'ncia'] ==
                                    loja_alvo_
                                    prioridade
                                ]
                            ) if not \
                                is_rev else 0
                            st.markdown(
                                f"<div style="
                                f"'text-align"
                                f": right; "
                                f"font-size: "
                                f"15px; font"
                                f"-weight: "
                                f"bold; color"
                                f": #00803B; "
                                f"margin-top:"
                                f" 10px; marg"
                                f"in-bottom: "
                                f"20px;'>Sua "
                                f"Loja: "
                                f"{t_sua} \u2022 "
                                f"Concorr\u00eanci"
                                f"a: {len(df_f_aba) - t_sua} "
                                f"\u2022 Total Ge"
                                f"ral: {len(
                                    df_f_aba)} "
                                f"</div>",
                                unsafe_al
                                low_html=True
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
                                        "\u00c9_Minha"
                                        "_Loja",
                                        "max"
                                    )
                                ).sort_values(
                                    by="V_"
                                       "Total",
                                    ascending=False
                                ).reset_index()
                            for _, \
                                    lin in \
                                    df_agr\
                                    .iterrows():
                                nm = \
                                    lin[
                                        'O que '
                                        'Falta']
                                s_a = \
                                    int(
                                        lin[
                                            'F_Dono']
                                    )
                                if is_rev:
                                    tg = \
                                        "🎯 RE" \
                                        "VERSO"
                                else:
                                    tg = \
                                        "🎯 SEU" \
                                        " MERCA" \
                                        "DO" if \
                                        s_a == \
                                        1 else \
                                        "🌍 CON" \
                                        "CORRÊN" \
                                        "CIA"

                                num_p = \
                                    int(
                                        lin[
                                            "V_Total"]
                                    )
                                txt_cap = \
                                    f"📦 {nm} | " \
                                    f"{tg} ({num_p})"
                                st.caption(
                                    txt_cap
                                )

                                df_f_it = \
                                    df_f_aba[
                                        df_f_aba[
                                            'O que '
                                            'Falta']
                                        == nm
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
                                    s_id = \
                                        s_l['ID']
                                    s_lo = \
                                        s_l[
                                            'Local/'
                                            'Referê'
                                            'ncia']
                                    c_mr = \
                                        s_l[
                                            'Contato']
                                    is_dv = \
                                        (s_lo
                                         ==
                                         loja_alvo_
                                         prioridade
                                         ) and not \
                                        is_rev

                                    p_txt = \
                                        '🔥 **SEU' \
                                        ' ESTABEL' \
                                        'ECIMENTO' \
                                        ':** ' if \
                                        is_dv else \
                                        '📍 **Cap' \
                                        'tado no' \
                                        ' concor' \
                                        'rente:** '
                                    st.markdown(
                                        f"{p_txt}"
                                        f"{s_lo}"
                                    )

                                    c_mr_s = \
                                        str(
                                            c_mr
                                        ).strip()
                                    is_ok_w = \
                                        c_mr_s \
                                        != "" \
                                        and \
                                        c_mr_s \
                                        != "None"

                                    p_wa_v = (
                                        dict_liberados
                                        .get(
                                            "what"
                                            "sapp",
                                            True
                                        )
                                        if isinstance(
                                            dict_liberados,
                                            dict
                                        )
                                        else True
                                    )
                                    if is_ok_w \
                                       and \
                                       p_wa_v:
                                        u_w = (
                                            f"https://"
                                            f"api.wh"
                                            f"atsapp"
                                            f".com/"
                                            f"send?"
                                            f"phone="
                                            f"55"
                                            f"{c_mr_s}"
                                        )
                                        st\
                                            .link_button(
                                                label="📱 WhatsApp",
                                                url=u_w,
                                                use_container_width=True
                                            )
                                    elif is_ok_w \
                                            and \
                                            not \
                                            p_wa_v:
                                        st.warning(
                                            "🔒 Bloq"
                                        )
                                    else:
                                        st.markdown("⚠️ sem número")

                                    if is_dv:
                                        id_cf = \
                                            f"conf_" \
                                            f"baixa" \
                                            f"_{s_id}"
                                        if id_cf \
                                           not in \
                                           st\
                                           .session\
                                           _state:
                                            st\
                                                .session\
                                                _state[
                                                    id_cf] \
                                                = False

                                        if not st\
                                           .session\
                                           _state[
                                               id_cf]:
                                            if st.button(f"Baixa", key=f"btn_pre_{s_id}_{num_aba}"):
                                                st.session_state[id_cf] = True
                                                st.rerun()
                                        else:
                                            if st.button("🚨 Confirmar", key=f"btn_real_{s_id}_{num_aba}"):
                                                supabase.table("relatos_escassez").update(
                                                    {"status": "Atendido"}).eq("id", s_id).execute()
                                                st.success("🎉 Concluído!")
                                                import time
                                                time.sleep(0.5)
                                                st.session_state[id_cf] = False
                                                st.session_state.busca_ativa = False
                                                st.rerun()
                        else:
                            st.info(
                                "ℹ️ Vazio."
                            )
