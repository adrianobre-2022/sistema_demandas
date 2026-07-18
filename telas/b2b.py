import streamlit as st
import pandas as pd
import datetime
import urllib.parse
from fpdf import FPDF

# FUNÇÃO EXTERNA QUE GERA O PDF


def gerar_pdf_demandas(df_aba):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font(
            "Arial", size=12
        )
        pdf.cell(
            200, 10,
            txt="Relatorio Demandas",
            ln=1, align="C"
        )
        for _, r in df_aba.iterrows():
            txt_l = f"- " \
                    f"{r['O que Falta']}" \
                    f" | Point: " \
                    f"{r['Local/'" \
                    f"Referência']}"
            pdf.cell(
                190, 10, 
                txt=txt_l.encode(
                    'latin-1', 
                    'ignore'
                ).decode('latin-1'), 
                ln=1
            )
        return bytes(
            pdf.output(dest='S')
        )
    except:
        return b""

def renderizar(supabase):
    loja_alvo_prioridade = (
        "Mercadinho Do Bairro"
    )
    termo_busca = st.session_state\
        .get("termo_busca_temp", "")
    p_cli = st.session_state\
        .perfil_cliente
    espectador_analitico = \
        p_cli in [
            "investidor", 
            "gestor", 
            "jornalista"
        ]

    # BARRA NATIVA RESPONSIVA
    col_nav_b1, col_nav_b2 = \
        st.columns(2)
    with col_nav_b1:
        if st.button(
            "⬅️ Sair do Painel",
            key="btn_voltar_com",
            use_container_width=True
        ):
            st.session_state\
                .tela_atual = "home"
            st.session_state\
                .token_valido = False
            st.session_state\
                .perfil_cliente = None
            st.session_state\
                .busca_ativa = False
            st.session_state\
                .dados_grafico = None
            st.rerun()
    
    st.markdown(
        "<h1 style='text-align: "
        "center; font-weight: 900; "
        "margin-bottom: 0px;'"
        ">🔍 E o que falta?</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: "
        "center; font-size: 16px; "
        "font-style: italic; "
        "color: #aaaaaa; margin-top: "
        "5px; margin-bottom: 25px;'"
        ">O termômetro de carências "
        "da nossa região.</p>",
        unsafe_allow_html=True
    )
    st.write("---")
    termo_busca = st.text_input(
        label="Refinar palavra-chave:",
        placeholder="Filtrar...",
        key="input_busca_painel"
    )

    if p_cli == "admin":
        st.markdown(
            "<h3>🛠️ ERP Cadastros</h3>",
            unsafe_allow_html=True
        )
        with st.form(
            key="form_admin_mestre",
            clear_on_submit=True
        ):
            nome_n = st.text_input(
                "Estabelecimento:",
                placeholder="Nome..."
            )
            perfil_n = st.selectbox(
                "Perfil Corporativo:",
                ["comerciante", 
                 "saude", 
                 "petshop", 
                 "beleza", 
                 "investidor", 
                 "gestor", 
                 "jornalista"]
            )
            regiao_n = st.text_input(
                "Região/Atuação:",
                placeholder="Cidade..."
            )
            if st.form_submit_button(
                "💼 Cadastrar Lojista"
            ):
                if nome_n and regiao_n:
                    try:
                        novo = supabase\
                            .table(
                                "clientes_"
                                "b2b"
                            ).insert({
                                "nome_estab"
                                "elecimento": 
                                    nome_n\
                                    .strip()\
                                    .title(), 
                                "perfil_se"
                                "gmento": 
                                    perfil_n, 
                                "regiao_at"
                                "uacao": 
                                    regiao_n\
                                    .strip(), 
                                "status_pa"
                                "gamento": 
                                    "Ativo", 
                                "recurso_m"
                                "arketplace"
                                "_reverso": 
                                    True, 
                                "recurso_w"
                                "hatsapp": 
                                    True, 
                                "recurso_p"
                                "df": 
                                    True
                            }).execute()
                        if novo.data:
                            st.success(
                                "🎉 Pronto!"
                            )
                            tk = novo\
                                .data\
                                ['token_'
                                 'acesso']
                            st.info(
                                f"🔑 `{tk}`"
                            )
                    except Exception as e:
                        st.error(
                            f"Erro: {e}"
                        )
        st.markdown(
            "<h3>📊 Central Financeira"
            "</h3>",
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
                    n_e = cli[\
                    'nome_estabele'
                    'cimento']
                    with st.expander(
                        f"🏢 {n_e}"
                    ):
                        st.text_input(
                            "🔑 Token:",
                            value=cli[\
                            'token_ace'
                            'sso'],
                            disabled=True,
                            key=f"t_{c_id}"
                        )
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
        except: pass

        st.markdown(
            "<h3>📥 Curadoria Nichos</h3>",
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
                                value=sug[\
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
                                    n_corrigido\
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
        except: pass
    else:
        try:
            q = (
                "id,item_"
                "solicitado"
                ",tipo_care"
                "ncia,data_"
                "registro,"
                "status,obs"
                "ervacao_de"
                "talhe,sub_"
                "segmento,"
                "pegada_di"
                "gital,con"
                "tato_avis"
                "o,locais_"
                "destino(n"
                "ome_exibi"
                "cao,regia"
                "o_cidade)"
            )
            r = supabase\
                .table(
                    "relatos"
                    "_escas"
                    "sez"
                ).select(
                    q
                ).execute()
            c_det = set()
            b_c = {}
            d_l = []
            now = datetime\
                .datetime\
                .now(
                    datetime\
                    .timezone\
                    .utc
                )
            if r.data:
                for x in \
                    r.data:
                    st_x = \
                    x.get(
                        "status"
                    )
                    ld_x = \
                    x.get(
                        "locai"
                        "s_des"
                        "tino"
                    )
                    if (
                        st_x \
                        !=
                        "Atend"
                        "ido"
                    ) and \
                       ld_x:
                        lc = \
                        str(
                            ld_x\
                            ["reg"
                             "iao_"
                             "cida"
                             "de"]
                        ).strip()
                        if " - " \
                           in \
                           lc:
                            cr, \
                            br = \
                            lc\
                            .split(
                                " - ",
                                1
                            )
                            cr = \
                            cr\
                            .strip()
                            br = \
                            br\
                            .strip()
                        else:
                            cr = \
                            lc
                            br = \
                            "Gera" \
                            "l"
                        c_det\
                            .add(
                                cr
                            )
                        if cr \
                           not in \
                           b_c:
                            b_c[\
                            cr] \
                            = \
                            set()
                        b_c[\
                        cr]\
                          .add(
                              br
                          )
                        sub = str(
                            x.get(
                                "sub_se"
                                "gmento",
                                "Geral"
                            )
                        ).strip()
                        cat = str(
                            x.get(
                                "tipo_ca"
                                "rencia",
                                "Produto"
                                " / Marca"
                            )
                        ).strip()
                        dt = x.get(
                            "data_re"
                            "gistro"
                        )
                        dias = max(
                            0, (
                            now - \
                            datetime\
                            .datetime\
                            .fromisoformat(
                                dt\
                                .replace(
                                "Z",
                                "+00:00"
                                )
                            )
                        ).days) if \
                        dt else 0
                        is_p = (
                            "Público"
                            in cat
                            or
                            "Publico"
                            in cat
                            or
                            "Infra"
                            in cat
                            or
                            "Zelado"
                            "ria"
                            in sub
                        )
                        is_l = (
                            "Local"
                            in cat
                            or
                            "Invest"
                            in sub
                        )
                        c_lm = (
                            "Serviço "
                            "Público / "
                            "Infrae"
                            "strutura"
                            if is_p
                            else (
                                "Serviço "
                                "Local / "
                                "Novo Est"
                                "abeleci"
                                "mento"
                                if is_l
                                else
                                "Produto / "
                                "Marca"
                            )
                        )
                        i_lm = str(
                            x["item_"
                              "soli"
                              "cita"
                              "do"]
                        ).rstrip(
                            " 0123"
                            "456789"
                        ).strip()\
                         .title()
                        n_lc = \
                            ld_x["no"
                                 "me_"
                                 "exib"
                                 "icao"]
                        is_df = (
                            n_lc \
                            != \
                            loja_alvo_prioridade
                        )
                        is_pl = (
                            p_cli in [
                                "comer"
                                "ciante",
                                "saude",
                                "petsh"
                                "op",
                                "beleza"
                            ]
                        )
                        if is_pl \
                           and \
                           is_df:
                            if sub \
                               == \
                               "Super" \
                               "mercado":
                                n_ex = \
                                    "Mercado " \
                                    "Concor" \
                                    "rente"
                            elif sub \
                                 in [
                                 "Saude",
                                 "Saúde"
                                 ]:
                                n_ex = \
                                    "Clínica " \
                                    "Concor" \
                                    "rente"
                            elif sub \
                                 == \
                                 "Petshop":
                                n_ex = \
                                    "Petshop " \
                                    "Concor" \
                                    "rente"
                            elif sub \
                                 == \
                                 "Beleza":
                                n_ex = \
                                    "Salão " \
                                    "Concor" \
                                    "rente"
                            else:
                                n_ex = \
                                    "Parce" \
                                    "iro Co" \
                                    "merci" \
                                    "al"
                        else:
                            n_ex = \
                                n_lc
                        obs_x = \
                        x.get(
                            "obser"
                            "vacao"
                            "_deta"
                            "lhe"
                        ) or (
                            "Sem "
                            "detal"
                            "hes."
                        )
                        peg_x = \
                        x.get(
                            "pegad"
                            "a_dig"
                            "ital"
                        ) or (
                            f"an_"
                            f"{x['id']}"
                        )
                        ct_x = \
                        x.get(
                            "conta"
                            "to_av"
                            "iso"
                        ) or ""
                        
                        d_l\
                        .append({
                            "ID":
                                x["id"],
                            "O que Falta":
                                i_lm,
                            "Categoria":
                                c_lm,
                            "Local/Referên"
                            "cia":
                                n_ex,
                            "CidadeRaiz":
                                cr,
                            "Bairro":
                                br,
                            "CidadeComplet"
                            "a":
                                lc,
                            "Dias":
                                dias,
                            "Observação":
                                obs_x,
                            "SubSegmento":
                                sub,
                            "Pegada":
                                peg_x,
                            "Contato":
                                ct_x
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
            df_t = pd.DataFrame(
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
            if not df_t.empty:
                df_f = df_t
                if c_sel != (
                   "[ Mostrar Todas "
                   "as Cidades ]"
                ):
                    df_f = df_f[
                        df_f[\
                        'CidadeRaiz'] \
                        == c_sel
                    ]
                    if b_sel != (
                       " Mostrar Todos "
                       "os Bairros "
                    ):
                        df_f = df_f[
                            df_f[\
                            'Bairro'] \
                            == b_sel
                        ]
                st.session_state\
                  .dados_grafico = \
                  df_f
            else:
                st.session_state\
                  .dados_grafico = \
                  df_t
        except Exception as e:
            st.error(
                f"⚠️ Erro de perfo"
                f"rmance: {str(e)}"
            )
        if st.session_state\
           .dados_grafico \
           is not None:
            df = st.session_state\
                .dados_grafico
            if not df.empty:
                if p_cli == \
                   "comerciante":
                    n_abas = [
                        "📦 Varejo", 
                        "🎯 Marketplace "
                        "Reverso"
                    ]
                elif p_cli == \
                     "saude":
                    n_abas = [
                        "📦 Saúde", 
                        "🎯 Marketplace "
                        "Reverso"
                    ]
                elif p_cli == \
                     "petshop":
                    n_abas = [
                        "📦 Pet", 
                        "🎯 Marketplace "
                        "Reverso"
                    ]
                elif p_cli == \
                     "beleza":
                    n_abas = [
                        "📦 Estética", 
                        "🎯 Marketplace "
                        "Reverso"
                    ]
                elif p_cli == \
                     "investidor":
                    n_abas = [
                        "💼 Novos Negócios"
                    ]
                elif p_cli == \
                     "jornalista":
                    n_abas = [
                        "🏛️ Infraestrutura", 
                        "💼 Novos Negócios"
                    ]
                else:
                    n_abas = [
                        "🏛️ Infraestrutura"
                    ]
                
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
                            "Infra" \
                            in \
                            n_aba_atv
                        )
                        is_srv = (
                            "Negócios" \
                            in \
                            n_aba_atv
                        )
                        fr_atv = \
                            "Infra" if \
                            is_inf \
                            else (
                                "Services" \
                                if \
                                is_srv \
                                else \
                                "Varejo"
                            )
                        is_rev = \
                            "Marketplace" \
                            in n_aba_atv
                        r_lib = \
                            st\
                            .session_state\
                            .get(
                                "recursos_"
                                "liberados", 
                                {}
                            )
                        if is_rev and \
                           not r_lib\
                           .get(
                               "reverso", 
                               True
                           ):
                            st.warning(
                                "🔒 Suspensa."
                            )
                            continue
                        df_f_aba = df
                        if fr_atv == \
                           "Infra":
                            df_f_aba = \
                                df[
                                    df[\
                                    'Categoria']\
                                    == \
                                    "Serviço "
                                    "Público / "
                                    "Infra"
                                    "estrutura"
                                ]
                        elif fr_atv == \
                             "Services":
                            df_f_aba = \
                                df[
                                    df[\
                                    'Categoria']\
                                    == \
                                    "Serviço "
                                    "Local / "
                                    "Novo Est"
                                    "abelec"
                                    "imento"
                                ]
                        elif fr_atv == \
                             "Varejo":
                            if p_cli == \
                               "comerci" \
                               "ante":
                                df_f_aba = df[df['SubSegmento'].str.contains("Supermercado|Geral", case=False, na=False)]
                            elif p_cli == \
                                 "saude":
                                df_f_aba = df[df['SubSegmento'].str.contains("Saude|Saúde", case=False, na=False)]
                            elif p_cli == \
                                 "petshop":
                                df_f_aba = df[df['SubSegmento'].str.contains("Pet", case=False, na=False)]
                            elif p_cli == \
                                 "beleza":
                                df_f_aba = df[df['SubSegmento'].str.contains("Beleza", case=False, na=False)]
                        
                        if termo_busca:
                            c_item = df_f_aba['O que Falta'].str.contains(termo_busca, case=False)
                            c_local = df_f_aba['Local/Referência'].str.contains(termo_busca, case=False)
                            df_f_aba = df_f_aba[c_item | c_local]
                        if not \
                           df_f_aba\
                           .empty:
                            df_f_aba[\
                            'É_Minha_Loja'] = \
                                df_f_aba[\
                                'Local/'
                                'Referência']\
                                .apply(
                                    lambda \
                                    x: 1 \
                                    if x == \
                                    loja_alvo_prioridade \
                                    else 0
                                )
                            pode_pdf = \
                                st\
                                .session_state\
                                .get(
                                    "recursos_"
                                    "liberados", 
                                    {}
                                ).get(
                                    "pdf", 
                                    True
                                )
                            
                            # 📄 ATENDIDO: BOTÃO DE PDF RECUPERADO NATIVAMENTE NO TOPO DE CADA ABA
                            if pode_pdf:
                                bytes_pdf = \
                                    gerar_pdf_demandas(
                                        df_f_aba
                                    )
                                if bytes_pdf \
                                   != b"":
                                    st\
                                    .download_button(
                                        label="📄 Baixar "
                                              "Relatório de "
                                              "Demandas "
                                              "(PDF)", 
                                        data=
                                        bytes_pdf, 
                                        file_name=
                                        "demandas_"
                                        "quarteirao"
                                        ".pdf", 
                                        mime=
                                        "applicat"
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
                                    'Referê'
                                    'ncia'] == 
                                    loja_alvo_
                                    prioridade
                                ]
                            ) if not \
                            is_rev else 0
                            t_con = len(
                                df_f_aba
                            ) - t_sua
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
                                f"{t_sua} • "
                                f"Concorrênci"
                                f"a: {t_con} "
                                f"• Total Ge"
                                f"ral: {len(
                                df_f_aba)} "
                                f"</div>", 
                                unsafe_al\
                                low_html=
                                True
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
                                    ascending=
                                    False
                                ).reset_index()
                            for _, \
                                linha in \
                                df_agr\
                                .iterrows():
                                i_nm = \
                                linha[\
                                'O que '
                                'Falta']
                                s_al = \
                                int(
                                linha[\
                                'F_Dono']
                                )
                                if is_rev:
                                    c_tg = \
                                    "tag-ca" \
                                    "lor-me" \
                                    "dia"
                                    l_tg = \
                                    "🎯 RE" \
                                    "VERSO"
                                else:
                                    c_tg = \
                                    "tag-ca" \
                                    "lor-al" \
                                    "ta" if \
                                    s_al == \
                                    1 else \
                                    "tag-ca" \
                                    "lor-ba" \
                                    "ixa"
                                    l_tg = \
                                    "🎯 SEU" \
                                    " MERCA" \
                                    "DO" if \
                                    s_al == \
                                    1 else \
                                    "🌍 CON" \
                                    "CORRÊN" \
                                    "CIA"
                                
                                st.markdown(
                                    f'<div cl'
                                    f'ass="bl'
                                    f'oco-lis'
                                    f'ta-prem'
                                    f'ium"><s'
                                    f'pan cla'
                                    f'ss="{c_'\
                                    f'tg}">'  \
                                    f'{l_tg} '\
                                    f'• {int( '\
                                    f'linha["'\
                                    f'V_Total'\
                                    f'"])} Pe'\
                                    f'didos</'\
                                    f'span><b'\
                                    f' style="'\
                                    f'color: '\
                                    f'#FFFFFF'\
                                    f'; font-'\
                                    f'size: 1'\
                                    f'6px;">📦'\
                                    f' {i_nm}'\
                                    f'</b><di'\
                                    f'v style'\
                                    f'="margi'\
                                    f'n-top: '\
                                    f'0.5rem;'\
                                    f' color: '\
                                    f'#aaaaaa'\
                                    f'; font-'\
                                    f'size: 1'\
                                    f'3px;">⏱'\
                                    f'️ Alert'\
                                    f'a ativo'\
                                    f' há {li'\
                                    f'nha["M_'\
                                    f'Idade"]'\
                                    f'} dias<'\
                                    f'/div></'\
                                    f'div>', 
                                    unsafe_al\
                                    low_html=
                                    True
                                )
                                df_f_it = \
                                df_f_aba[
                                    df_f_aba[
                                    'O que '
                                    'Falta'] 
                                    == i_nm
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
                                    sub_id = \
                                    s_l['ID']
                                    sub_lo = \
                                    s_l[\
                                    'Local/'
                                    'Referê'
                                    'ncia']
                                    c_mor = \
                                    s_l[\
                                    'Contato']
                                    is_dv = \
                                    (sub_lo \
                                    == \
                                    loja_alvo_
                                    prioridade\
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
                                        f"{sub_lo}"
                                        f" ("
                                        f"{s_l['C"
                                        f"idadeCo"
                                        f"mpleta"
                                        f"']})"
                                    )
                                    if s_l[\
                                    'Observa'
                                    'ção'] \
                                    and s_l[\
                                    'Observa'
                                    'ção'] \
                                    != "Sem " \
                                       "detal" \
                                       "hes.":
                                        st.info(
                                            f"💬 *"
                                            f"Relat"
                                            f"o:* "
                                            f"\"{s_l"
                                            f"['Obse"
                                            f"rvaçã"
                                            f"o']}\""
                                        )
                                    p_wa = \
                                    st\
                                    .session_\
                                    state\
                                    .get(
                                        "recurso"
                                        "s_liber"
                                        "ados", 
                                        {}
                                    ).get(
                                        "whatsap"
                                        "p", 
                                        True
                                    )
                                    
                                    c_mor_s = \
                                    str(
                                    c_mor
                                    ).strip()
                                    is_ok_w = \
                                    c_mor_s \
                                    != "" \
                                    and \
                                    c_mor_s \
                                    != "None"
                                    
                                    if is_ok_w \
                                       and \
                                       p_wa:
                                        st.markdown(f'<a href="https://whatsapp.com{c_mor_s}&text=Olá! Temos {i_nm} disponível!" target="_blank"><button style="background-color: #25D366 !important; color: white !important; font-weight: bold !important; border: none !important; padding: 0.5rem 1rem !important; border-radius: 8px !important; width: auto !important; margin-bottom: 10px; font-size: 14px; cursor: pointer;">📱 Falar no WhatsApp</button></a>', unsafe_allow_html=True)
                                    elif is_ok_w \
                                         and \
                                         not \
                                         p_wa:
                                        st.warning(
                                            "🔒 Wh"
                                            "atsAp"
                                            "p Blo"
                                            "quead"
                                            "o."
                                        )
                                    else:
                                        st.markdown("<div class='botao-contato-vazio-v'>⚠️ sem número de contato</div>", unsafe_allow_html=True)
                                        
                                    if is_dv:
                                        id_cf = \
                                        f"conf_" \
                                        f"baixa" \
                                        f"_{sub_id}"
                                        if id_cf \
                                           not in \
                                           st\
                                           .session\
                                           _state:
                                            st\
                                            .session\
                                            _state[\
                                            id_cf] \
                                            = False
                                            
                                        if not st\
                                           .session\
                                           _state[\
                                           id_cf]:
                                            if st.button(f"Dar baixa no {sub_lo}", key=f"btn_pre_{sub_id}_{num_aba}"):
                                                st.session_state[id_cf] = True
                                                st.rerun()
                                        else:
                                            if st.button("🚨 Confirmar Exclusão", key=f"btn_real_{sub_id}_{num_aba}"):
                                                supabase.table("relatos_escassez").update({"status": "Atendido"}).eq("id", sub_id).execute()
                                                st.success("🎉 Concluído!")
                                                import time
                                                time.sleep(0.5)
                                                st.session_state[id_cf] = False
                                                st.session_state.busca_ativa = False
                                                st.rerun()
                        else:
                            st.info(
                                "ℹ️ Nenhum "
                                "registro "
                                "ativo para "
                                "esta aba."
                            )