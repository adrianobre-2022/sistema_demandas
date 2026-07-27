import streamlit as st
import pandas as pd
import datetime
import urllib.parse
import time

# 📄 SOLUÇÃO REAL: GERADOR DE RELATÓRIO VIA CSV COMPATÍVEL COM IMPRESSÃO EXCEL/PDF


@st.cache_data
def converter_dados_para_relatorio(df_aba):
    try:
        # Transforma os dados em formato CSV legível por qualquer dispositivo
        return df_aba[["O que Falta", "Categoria", "Local/Referência", "CidadeCompleta", "Dias"]].to_csv(index=False).encode('utf-8')
    except:
        return b""

# 📱 COMPONENTE MORADOR COM WHATSAPP COMPACTO ORIGINAL RESTAURADO


def desenhar_morador(s_l, nm, num_aba, supabase, loja_alvo):
    sub_id = s_l['ID']
    sub_local = s_l['Local/Referência']
    c_morador = s_l['Contato']
    is_rev = st.session_state.get("is_marketplace_reverso", False)
    is_dono_vazio = (sub_local == loja_alvo) and not is_rev

    p_txt = '🔥 **SEU ESTABELECIMENTO:** ' if is_dono_vazio else '📍 **Captado no concorrente:** '
    st.markdown(f"{p_txt}{sub_local} ({s_l['CidadeCompleta']})")
    if s_l['Observação'] and s_l['Observação'] != "Sem detalhes.":
        st.info(f"💬 *Relato:* \"{s_l['Observação']}\"")

    c_morador_s = str(c_morador).strip()
    is_ok_w = c_morador_s != "" and c_morador_s != "None"

    if is_ok_w:
        msg_enc = urllib.parse.quote(
            f"Olá! Temos {nm} disponível no quarteirão!")
        html_wa = f'<a href="https://whatsapp.com{c_morador_s}&text={msg_enc}" target="_blank"><button style="background-color: #25D366 !important; color: white !important; font-weight: bold !important; border: none !important; padding: 0.5rem 1rem !important; border-radius: 8px !important; width: auto !important; margin-bottom: 10px; font-size: 14px; cursor: pointer;">📱 Falar no WhatsApp</button></a>'
        st.markdown(html_wa, unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='botao-contato-vazio-v'>⚠️ sem número de contato</div>", unsafe_allow_html=True)

    if is_dono_vazio:
        id_conf = f"confirma_baixa_{sub_id}"
        if id_conf not in st.session_state:
            st.session_state[id_conf] = False
        if not st.session_state[id_conf]:
            if st.button(f"Dar baixa no {sub_local}", key=f"btn_pre_{sub_id}_{num_aba}"):
                st.session_state[id_conf] = True
                st.rerun()
        else:
            if st.button("🚨 Confirmar Exclusão", key=f"btn_real_{sub_id}_{num_aba}"):
                supabase.table("relatos_escassez").update(
                    {"status": "Atendido"}).eq("id", sub_id).execute()
                st.success("🎉 Concluído!")
                time.sleep(0.5)
                st.session_state[id_conf] = False
                st.session_state.busca_ativa = False
                st.rerun()


def renderizar(supabase):
    # 🎨 INJEÇÃO DE CSS: Força as caixas de seleção (selectbox) a respeitarem o fundo escuro do tema
    st.markdown("""
        <style>
        div[data-baseweb="popover"] ul {
            background-color: #1A1A1A !important;
            color: #FFFFFF !important;
        }
        div[data-baseweb="popover"] li:hover {
            background-color: #00803B !important;
            color: #FFFFFF !important;
        }
        div[data-baseweb="select"] div {
            color: #FFFFFF !important;
        }
        div.stDownloadButton > button {
            background-color: #262626 !important;
            color: #FFFFFF !important;
            border: 1px solid #404040 !important;
            border-radius: 8px !important;
        }
        div.stDownloadButton > button:hover {
            background-color: #404040 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    loja_alvo_prioridade = "Mercadinho Do Bairro"
    p_cli = st.session_state.get("perfil_cliente", "comerciante")

    # ⬅️ BARRA NATIVA DE DESCONEXÃO (LOGOFF)
    col_nav1, _ = st.columns(2)
    with col_nav1:
        if st.button("⬅️ Sair do Painel (Logoff)", key="btn_voltar_com_nativo_v", use_container_width=True):
            st.session_state.tela_atual = "home"
            st.session_state.token_valido = False
            st.session_state.perfil_cliente = None
            st.session_state.busca_ativa = False
            st.session_state.dados_grafico = None
            st.rerun()

    st.markdown("<h1 style='text-align: center; font-weight: 900; margin-bottom: 0px;'>🔍 Sistema de Demandas</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; font-style: italic; color: #aaaaaa; margin-top: 5px; margin-bottom: 25px;'>O termômetro de carências da nossa região.</p>", unsafe_allow_html=True)
    st.write("---")

    # 🔍 CAPTURA CENTRAL DE PALAVRA-CHAVE
    termo_busca = st.text_input(label="Refinar por palavra-chave:",
                                placeholder="Digite para filtrar...", key="input_busca_painel").strip()

    # 🛠️ MÓDULO EXCLUSIVO DO ADMIN MESTRE
    if p_cli == "admin":
        st.markdown(
            "<h3 style='text-align: center;'>🛠️ Cadastro de Assinantes (ERP)</h3>", unsafe_allow_html=True)
        with st.form(key="form_admin_mestre_cad", clear_on_submit=True):
            nome_novo = st.text_input(
                "Nome do Estabelecimento:", placeholder="Ex: Supermercado...")
            perfil_novo = st.selectbox("Perfil de Acesso Corporativo:", [
                                       "comerciante", "saude", "petshop", "beleza", "investidor", "gestor", "jornalista"])
            regiao_novo = st.text_input(
                "Região/Cidade de Atuação:", placeholder="Ex: São Paulo/SP...")
            if st.form_submit_button("💼 Cadastrar Lojista"):
                if nome_novo and regiao_novo:
                    try:
                        n_c = nome_novo.strip().title()
                        r_c = regiao_novo.strip()
                        supabase.table("clientes_b2b").insert({
                            "nome_estabelecimento": n_c, "perfil_segmento": perfil_novo, "regiao_atuacao": r_c,
                            "status_pagamento": "Ativo", "recurso_marketplace_reverso": True, "recurso_whatsapp": True, "recurso_pdf": True
                        }).execute()
                        st.success("🎉 Cadastrado!")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as err:
                        st.error(f"Erro: {str(err)}")

        st.markdown(
            "<h3 style='text-align: center;'>📊 Central Financeira</h3>", unsafe_allow_html=True)
        try:
            resposta_clientes = supabase.table("clientes_b2b").select(
                "*").order("created_at", desc=True).execute()
            if resposta_clientes.data:
                df_clientes = pd.DataFrame(resposta_clientes.data)

                # 🔥 CONEXÃO DO FILTRO DO ADMIN (Filtra a Central Financeira na hora por Hortifruti, etc.)
                if termo_busca:
                    filtro_admin = df_clientes["nome_estabelecimento"].str.contains(termo_busca, case=False, na=False) | \
                        df_clientes["perfil_segmento"].str.contains(
                            termo_busca, case=False, na=False)
                    df_clientes = df_clientes[filtro_admin]

                if not df_clientes.empty:
                    for _, cli in df_clientes.iterrows():
                        c_id = cli["id"]
                        with st.expander(f"🏢 {cli['nome_estabelecimento']} ({str(cli['perfil_segmento']).upper()})"):
                            st.text_input(
                                "🔑 Token Completo:", value=cli['token_acesso'], disabled=True, key=f"tk_full_{c_id}")
                            col_status, col_plan = st.columns(2)
                            with col_status:
                                status_pag = st.selectbox("Status de Pagamento:", ["Ativo", "Inadimplente", "Cancelado"],
                                                          index=["Ativo", "Inadimplente", "Cancelado"].index(cli.get("status_pagamento", "Ativo")), key=f"pay_{c_id}")
                            with col_plan:
                                plano_cont = st.selectbox("Plano Contratado:", ["Bronze", "Prata", "Ouro"],
                                                          index=["Bronze", "Prata", "Ouro"].index(cli.get("plano_contratado", "Ouro")), key=f"plan_{c_id}")
                            if st.button("💾 Salvar Alterações", key=f"save_{c_id}"):
                                supabase.table("clientes_b2b").update(
                                    {"status_pagamento": status_pag, "plano_contratado": plano_cont}).eq("id", c_id).execute()
                                st.success("🔒 Sincronizado!")
                                time.sleep(0.5)
                                st.rerun()
                else:
                    st.write(
                        "ℹ️ Nenhum estabelecimento correspondente encontrado para a palavra-chave.")
        except Exception as e:
            st.error(f"Erro ao renderizar central financeira: {str(e)}")
    # 🏪 PERFIS DE VAREJO / COMERCIANTES GERAIS
    else:
        try:
            resposta_bruta = supabase.table("relatos_escassez").select(
                "id, item_solicitado, tipo_carencia, data_registro, status, observacao_detalhe, sub_segmento, pegada_digital, contato_aviso, locais_destino(nome_exibicao, regiao_cidade)").execute()
            cidades_detectadas = set()
            bairros_por_cidade = {}
            dados_brutos_limpos = []
            agora = datetime.datetime.now(datetime.timezone.utc)

            if resposta_bruta.data:
                for reg in resposta_bruta.data:
                    if reg.get("status") != "Atendido" and reg.get("locais_destino"):
                        loc_c = str(reg["locais_destino"]
                                    ["regiao_cidade"]).strip()
                        c_raiz, b_raiz = loc_c.split(
                            " - ", 1) if " - " in loc_c else (loc_c, "Geral")
                        c_raiz, b_raiz = c_raiz.strip(), b_raiz.strip()
                        cidades_detectadas.add(c_raiz)
                        if c_raiz not in bairros_por_cidade:
                            bairros_por_cidade[c_raiz] = set()
                        bairros_por_cidade[c_raiz].add(b_raiz)

                        sub_seg = str(reg.get("sub_segmento", "Geral")).strip()
                        cat_b = str(reg.get("tipo_carencia",
                                    "Produto / Marca")).strip()
                        idade_dias = max(0, (agora - datetime.datetime.fromisoformat(reg.get(
                            "data_registro").replace("Z", "+00:00"))).days) if reg.get("data_registro") else 0
                        cat_limpa = "Serviço Público / Infraestrutura" if ("Público" in cat_b or "Publico" in cat_b or "Infra" in cat_b or "Zeladoria" in sub_seg) else (
                            "Serviço Local / Novo Estabelecimento" if ("Local" in cat_b or "Invest" in sub_seg) else "Produto / Marca")
                        item_limpo = str(reg["item_solicitado"]).rstrip(
                            " 0123456789").strip().title()
                        n_local_b = reg["locais_destino"]["nome_exibicao"]

                        if p_cli in ["comerciante", "saude", "petshop", "beleza"] and n_local_b != loja_alvo_prioridade:
                            if sub_seg == "Supermercado":
                                n_local_ex = "Mercado Concorrente"
                            elif sub_seg in ["Saude", "Saúde"]:
                                n_local_ex = "Clínica Concorrente"
                            elif sub_seg == "Petshop":
                                n_local_ex = "Petshop Concorrente"
                            elif sub_seg == "Beleza":
                                n_local_ex = "Salão Concorrente"
                            else:
                                n_local_ex = "Parceiro Comercial"
                        else:
                            n_local_ex = n_local_b

                        dados_brutos_limpos.append({
                            "ID": reg["id"], "O que Falta": item_limpo, "Categoria": cat_limpa, "Local/Referência": n_local_ex, "CidadeRaiz": c_raiz, "Bairro": b_raiz, "CidadeCompleta": loc_c, "Dias": idade_dias,
                            "Observação": reg.get("observacao_detalhe") or "Sem detalhes.", "SubSegmento": sub_seg, "Pegada": reg.get("pegada_digital") or f"anon_{reg['id']}", "Contato": reg.get("contato_aviso") or ""
                        })

            l_cidades = ["[ Mostrar Todas as Cidades ]"] + \
                sorted(list(cidades_detectadas))
            cidade_sel = st.selectbox(
                "📍 1. Selecionar Cidade (Global):", options=l_cidades, key="b2b_cidade_auto")
            if city_sel := (cidade_sel == "[ Mostrar Todas as Cidades ]"):
                bairro_sel = st.selectbox("🏘️ 2. Refinar por Bairro:", options=[
                                          "--- Selecione uma Cidade ---"], disabled=True, key="b2b_bairro_auto")
            else:
                b_opts = [" Mostrar Todos os Bairros "] + \
                    sorted(list(bairros_por_cidade.get(cidade_sel, set())))
                bairro_sel = st.selectbox(
                    "🏘️ 2. Refinar por Bairro:", options=b_opts, key="b2b_bairro_auto")

            df_total = pd.DataFrame(dados_brutos_limpos) if dados_brutos_limpos else pd.DataFrame(columns=[
                "ID", "O que Falta", "Categoria", "Local/Referência", "CidadeRaiz", "Bairro", "CidadeCompleta", "Dias", "Observação", "SubSegmento", "Pegada", "Contato"])
            if not df_total.empty and cidade_sel != "[ Mostrar Todas as Cidades ]":
                df_total = df_total[df_total['CidadeRaiz'] == cidade_sel]
                if bairro_sel != " Mostrar Todos os Bairros ":
                    df_total = df_total[df_total['Bairro'] == bairro_sel]
            st.session_state.dados_grafico = df_total
        except Exception as e:
            st.error(f"⚠️ Erro de performance: {str(e)}")

        if st.session_state.dados_grafico is not None and not st.session_state.dados_grafico.empty:
            df = st.session_state.dados_grafico
            dict_nichos = {
                "comerciante": ["📦 Varejo", "🎯 Marketplace Reverso"], "saude": ["📦 Saúde", "🎯 Marketplace Reverso"],
                "petshop": ["📦 Pet", "🎯 Marketplace Reverso"], "beleza": ["📦 Estética", "🎯 Marketplace Reverso"],
                "investidor": ["💼 Novos Negócios"], "jornalista": ["🏛️ Infraestrutura", "💼 Novos Negócios"]
            }
            n_abas = dict_nichos.get(p_cli, ["🏛️ Infraestrutura"])

            abas_st = st.tabs(n_abas)
            for num_aba, n_aba_atv in enumerate(n_abas):
                with abas_st[num_aba]:
                    fr_atv = "Infra" if "Infra" in n_aba_atv else (
                        "Services" if "Negócios" in n_aba_atv else "Varejo")
                    is_rev = "Marketplace Reverso" in n_aba_atv
                    st.session_state["is_marketplace_reverso"] = is_rev

                    df_f_aba = df
                    if fr_atv == "Infra":
                        df_f_aba = df[df['Categoria'] ==
                                      "Serviço Público / Infraestrutura"]
                    elif fr_atv == "Services":
                        df_f_aba = df[df['Categoria'] ==
                                      "Serviço Local / Novo Estabelecimento"]
                    elif fr_atv == "Varejo":
                        map_filtros = {"comerciante": "Supermercado|Geral",
                                       "saude": "Saude|Saúde", "petshop": "Pet", "beleza": "Beleza"}
                        df_f_aba = df[df['SubSegmento'].str.contains(
                            map_filtros.get(p_cli, "Geral"), case=False, na=False)]

                    # 🔥 FILTRO GERAL DE PALAVRA-CHAVE (Ativo para os Lojistas e Comércios refinarem os produtos)
                    if termo_busca:
                        df_f_aba = df_f_aba[df_f_aba['O que Falta'].str.contains(
                            termo_busca, case=False, na=False) | df_f_aba['Local/Referência'].str.contains(termo_busca, case=False, na=False)]

                    if not df_f_aba.empty:
                        df_f_aba['É_Minha_Loja'] = df_f_aba['Local/Referência'].apply(
                            lambda x: 1 if x == loja_alvo_prioridade else 0)

                        dados_relatorio = converter_dados_para_relatorio(
                            df_f_aba)
                        if dados_relatorio:
                            st.download_button(
                                label="📥 Exportar Relatório de Demanda (Excel/PDF)",
                                data=dados_relatorio,
                                file_name=f"relatorio_demandas_{fr_atv}_{datetime.date.today()}.csv",
                                mime="text/csv",
                                key=f"btn_dl_{fr_atv}_{num_aba}"
                            )

                        st.write("")
                        for _, s_l in df_f_aba.iterrows():
                            nm_item = s_l['O que Falta']
                            desenhar_morador(
                                s_l, nm_item, num_aba, supabase, loja_alvo_prioridade)
                    else:
                        st.write(
                            "ℹ️ Nenhuma carência encontrada com os filtros selecionados.")
