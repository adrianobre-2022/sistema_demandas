import streamlit as st
import pandas as pd
import datetime
import urllib.parse
from fpdf import FPDF


def gerar_pdf_demandas(df_a):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font(
            "Arial", size=12
        )
        pdf.cell(
            200, 10,
            txt="Relatorio",
            ln=1, align="C"
        )
        for _, r in df_a.iterrows():
            f = r['O que Falta']
            p = r['Local/Referência']
            txt_l = f"- {f} | {p}"
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
    col1, col2 = st.columns(2)
    with col1:
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
                                    nome_n
                                    .strip()
                                    .title(),
                                "perfil_se"
                                "gmento":
                                    perfil_n,
                                "regiao_at"
                                "uacao":
                                    regiao_n
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
                                .data['token_'
                                      'acesso']
                            st.info(
                                f"🔑 `{tk}`"
                            )
                    except Exception as e:
                        st.error(
                            f"Erro: {e}"
                        )
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
                        st.text_input(
                            "🔑 Token:",
                            value=cli[
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
        except:
            pass

        st.markdown(
            "<h3>📥 Curadoria "
            "Nichos</h3>",
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
                    datetime
                    .timezone
                    .utc
                )
            if r.data:
                for x in r.data:
                    st_x = x.get("status")
                    ld_x = x.get("locais_destino")
                    if st_x != "Atendido" and ld_x:
                        lc = str(ld_x["regiao_cidade"]).strip()
                        if " - " in lc:
                            cr, br = lc.split(" - ", 1)
                            cr = cr.strip()
                            br = br.strip()
                        else:
                            cr = lc
                            br = "Geral"
                        c_det.add(cr)
                        if cr not in b_c:
                            b_c[cr] = set()
                        b_c[cr].add(br)
                        sub = str(x.get("sub_segmento", "Geral")).strip()
                        cat = str(
                            x.get("tipo_carencia", "Produto / Marca")).strip()
                        dt = x.get("data_registro")
                        dias = max(
                            0, (now - datetime.datetime.fromisoformat(dt.replace("Z", "+00:00"))).days) if dt else 0
                        is_p = "Público" in cat or "Publico" in cat or "Infra" in cat or "Zeladoria" in sub
                        is_l = "Local" in cat or "Invest" in sub
                        c_lm = "Serviço Público / Infraestrutura" if is_p else (
                            "Serviço Local / Novo Estabelecimento" if is_l else "Produto / Marca")
                        i_lm = str(x["item_solicitado"]).rstrip(
                            " 0123456789").strip().title()
                        n_lc = ld_x["nome_exibicao"]
                        is_df = n_lc != loja_alvo_prioridade
                        is_pl = p_cli in ["comerciante",
                                          "saude", "petshop", "beleza"]
                        if is_pl and is_df:
                            if sub == "Supermercado":
                                n_ex = "Mercado Concorrente"
                            elif sub in ["Saude", "Saúde"]:
                                n_ex = "Clínica Concorrente"
                            elif sub == "Petshop":
                                n_ex = "Petshop Concorrente"
                            elif sub == "Beleza":
                                n_ex = "Salão Concorrente"
                            else:
                                n_ex = "Parceiro Comercial"
                        else:
                            n_ex = n_lc
                        obs_x = x.get("observacao_detalhe") or "Sem detalhes."
                        peg_x = x.get("pegada_digital") or f"an_{x['id']}"
                        ct_x = x.get("contato_aviso") or ""

                        d_l.append({
                            "ID": x["id"], "O que Falta": i_lm, "Categoria": c_lm, "Local/Referência": n_ex,
                            "CidadeRaiz": cr, "Bairro": br, "CidadeCompleta": lc, "Dias": dias,
                            "Observação": obs_x, "SubSegmento": sub, "Pegada": peg_x, "Contato": ct_x
                        })

            l_c = ["[ Mostrar Todas as Cidades ]"] + sorted(list(c_det))
            c_sel = st.selectbox(
                "📍 1. Selecionar Cidade (Global):", options=l_c, key="b2b_c_auto")
            if c_sel == "[ Mostrar Todas as Cidades ]":
                b_sel = st.selectbox("🏘️ 2. Refinar por Bairro:", options=[
                                     "--- Selecione uma Cidade ---"], disabled=True, key="b2b_b_auto")
            else:
                b_o = [" Mostrar Todos os Bairros "] + \
                    sorted(list(b_c.get(c_sel, set())))
                b_sel = st.selectbox(
                    "🏘️ 2. Refinar por Bairro:", options=b_o, key="b2b_b_auto")
            df_t = pd.DataFrame(d_l) if d_l else pd.DataFrame(columns=[
                "ID", "O que Falta", "Categoria", "Local/Referência",
                "CidadeRaiz", "Bairro", "CidadeCompleta", "Dias",
                "Observação", "SubSegmento", "Pegada", "Contato"
            ])
            if not df_t.empty:
                df_f = df_t
                if c_sel != "[ Mostrar Todas as Cidades ]":
                    df_f = df_f[df_f['CidadeRaiz'] == c_sel]
                    if b_sel != " Mostrar Todos os Bairros ":
                        df_f = df_f[df_f['Bairro'] == b_sel]
                st.session_state.dados_grafico = df_f
            else:
                st.session_state.dados_grafico = df_t
        except Exception as e:
            st.error(f"⚠️ Erro de performance: {str(e)}")

        if st.session_state.dados_grafico is not None:
            df = st.session_state.dados_grafico
            if not df.empty:
                if p_cli == "comerciante":
                    n_abas = ["📦 Varejo", "🎯 Marketplace Reverso"]
                elif p_cli == "saude":
                    n_abas = ["📦 Saúde", "🎯 Marketplace Reverso"]
                elif p_cli == "petshop":
                    n_abas = ["📦 Pet", "🎯 Marketplace Reverso"]
                elif p_cli == "beleza":
                    n_abas = ["📦 Estética", "🎯 Marketplace Reverso"]
                elif p_cli == "investidor":
                    n_abas = ["💼 Novos Negócios"]
                elif p_cli == "jornalista":
                    n_abas = ["🏛️ Infraestrutura", "💼 Novos Negócios"]
                else:
                    n_abas = ["🏛️ Infraestrutura"]

                abas_st = st.tabs(n_abas)
                for num_aba, n_aba_atv in enumerate(n_abas):
                    with abas_st[num_aba]:
                        is_inf = "Infra" in n_aba_atv
                        is_srv = "Negócios" in n_aba_atv
                        fr_atv = "Infra" if is_inf else (
                            "Services" if is_srv else "Varejo")
                        is_rev = "Marketplace Reverso" in n_aba_atv
                        r_lib = st.session_state.get("recursos_liberados", {})
                        if is_rev and not r_lib.get("reverso", True):
                            st.warning("🔒 Suspensa.")
                            continue
                        df_f_aba = df
                        if fr_atv == "Infra":
                            df_f_aba = df[df['Categoria'] ==
                                          "Serviço Público / Infraestrutura"]
                        elif fr_atv == "Services":
                            df_f_aba = df[df['Categoria'] ==
                                          "Serviço Local / Novo Estabelecimento"]
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
                            c_item = df_f_aba['O que Falta'].str.contains(
                                termo_busca, case=False)
                            c_local = df_f_aba['Local/Referência'].str.contains(
                                termo_busca, case=False)
                            df_f_aba = df_f_aba[c_item | c_local]
                        if not df_f_aba.empty:
                            df_f_aba['É_Minha_Loja'] = df_f_aba['Local/Referência'].apply(
                                lambda x: 1 if x == loja_alvo_prioridade else 0)
                            pode_pdf = st.session_state.get(
                                "recursos_liberados", {}).get("pdf", True)

                            # 📄 ATENDIDO: BOTÃO DE PDF REATIVADO NATIVAMENTE NO TOPO DA ABA
                            if pode_pdf:
                                bytes_pdf = gerar_pdf_demandas(df_f_aba)
                                if bytes_pdf != b"":
                                    st.download_button(label="📄 Baixar Relatório de Demandas (PDF)", data=bytes_pdf,
                                                       file_name="demandas_quarteirao.pdf", mime="application/pdf", key=f"btn_pdf_real_final_{num_aba}")

                            t_sua = len(
                                df_f_aba[df_f_aba['Local/Referência'] == loja_alvo_prioridade]) if not is_rev else 0
                            t_con = len(df_f_aba) - t_sua
                            st.markdown(
                                f"<div style='text-align: right; font-size: 15px; font-weight: bold; color: #00803B; margin-top: 10px; margin-bottom: 20px;'>Sua Loja: {t_sua} • Concorrência: {t_con} • Total Geral: {len(df_f_aba)}</div>", unsafe_allow_html=True)

                            df_agr = df_f_aba.groupby(["O que Falta", "Categoria"]).agg(V_Total=("ID", "count"), M_Idade=(
                                "Dias", "min"), F_Dono=("É_Minha_Loja", "max")).sort_values(by="V_Total", ascending=False).reset_index()
                            for _, linha in df_agr.iterrows():
                                i_nm = linha['O que Falta']
                                s_al = int(linha['F_Dono'])
                                if is_rev:
                                    c_tg, l_tg = "tag-calor-media", "🎯 REVERSO"
                                else:
                                    c_tg = "tag-calor-alta" if s_al == 1 else "tag-calor-baixa"
                                    l_tg = "🎯 SEU MERCADO" if s_al == 1 else "🌍 CONCORRÊNCIA"

                                # TAGS ORIGINAIS FLUTUANDO À DIREITA PELO CSS
                                st.markdown(
                                    f'<div class="bloco-lista-premium"><span class="{c_tg}">{l_tg} • {int(linha["V_Total"])} Pedidos</span><b style="color: #FFFFFF; font-size: 16px;">📦 {i_nm}</b><div style="margin-top: 0.5rem; color: #aaaaaa; font-size: 13px;">⏱️ Alerta ativo há {linha["M_Idade"]} dias</div></div>', unsafe_allow_html=True)

                                # FIX DOS BOTÕES POR ID: Exibição individual garantida sem sumir com linhas
                                for _, s_l in df_f_aba[df_f_aba['O que Falta'] == i_nm].drop_duplicates(subset=["ID"]).iterrows():
                                    sub_id, sub_lo, c_mor = s_l['ID'], s_l['Local/Referência'], s_l['Contato']
                                    is_dv = (
                                        sub_lo == loja_alvo_prioridade) and not is_rev
                                    p_txt = '🔥 **SEU ESTABELECIMENTO:** ' if is_dv else '📍 **Captado no concorrente:** '
                                    st.markdown(
                                        f"{p_txt}{sub_lo} ({s_l['CidadeCompleta']})")
                                    if s_l['Observação'] and s_l['Observação'] != "Sem detalhes.":
                                        st.info(
                                            f"💬 *Relato:* \"{s_l['Observação']}\"")
                                    p_wa = st.session_state.get(
                                        "recursos_liberados", {}).get("whatsapp", True)

                                    c_mor_s = str(c_mor).strip()
                                    is_ok_w = c_mor_s != "" and c_mor_s != "None"

                                    if is_ok_w and p_wa:
                                        st.markdown(f'<a href="https://whatsapp.com{c_mor_s}&text=Olá! Temos {i_nm} disponível!" target="_blank"><button style="background-color: #25D366 !important; color: white !important; font-weight: bold !important; border: none !important; padding: 0.5rem 1rem !important; border-radius: 8px !important; width: auto !important; margin-bottom: 10px; font-size: 14px; cursor: pointer;">📱 Falar no WhatsApp</button></a>', unsafe_allow_html=True)
                                    elif is_ok_w and not p_wa:
                                        st.warning("🔒 WhatsApp Bloqueado.")
                                    else:
                                        # ATENDIDO: BOTÃO FOSCO SIMÉTRICO DA JUSTIFICATIVA DE AUSÊNCIA CONTRA VÁCUO VISUAL
                                        st.markdown(
                                            "<div class='botao-contato-vazio-v'>⚠️ sem número de contato</div>", unsafe_allow_html=True)

                                    if is_dv:
                                        id_cf = f"conf_baixa_{sub_id}"
                                        if id_cf not in st.session_state:
                                            st.session_state[id_cf] = False
                                        if not st.session_state[id_cf]:
                                            if st.button(f"Dar baixa no {sub_lo}", key=f"btn_pre_{sub_id}_{num_aba}"):
                                                st.session_state[id_cf] = True
                                                st.rerun()
                                        else:
                                            if st.button("🚨 Confirmar Exclusão", key=f"btn_real_{sub_id}_{num_aba}"):
                                                supabase.table("relatos_escassez").update(
                                                    {"status": "Atendido"}).eq("id", sub_id).execute()
                                                st.success("🎉 Concluído!")
                                                import time
                                                time.sleep(0.5)
                                                st.session_state[id_cf] = False
                                                st.session_state.busca_ativa = False
                                                st.rerun()
                        else:
                            st.info(
                                "ℹ️ Nenhum registro ativo encontrado para esta aba.")
