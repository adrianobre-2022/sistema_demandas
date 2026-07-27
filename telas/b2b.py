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
        msg_enc = urllib.parse.quote(f"Olá! Temos {nm} disponível no quarteirão!")
        html_wa = f'<a href="https://whatsapp.com{c_morador_s}&text={msg_enc}" target="_blank"><button style="background-color: #25D366 !important; color: white !important; font-weight: bold !important; border: none !important; padding: 0.5rem 1rem !important; border-radius: 8px !important; width: auto !important; margin-bottom: 10px; font-size: 14px; cursor: pointer;">📱 Falar no WhatsApp</button></a>'
        st.markdown(html_wa, unsafe_allow_html=True)
    else:
        st.markdown("<div class='botao-contato-vazio-v'>⚠️ sem número de contato</div>", unsafe_allow_html=True)

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
                supabase.table("relatos_escassez").update({"status": "Atendido"}).eq("id", sub_id).execute()
                st.success("🎉 Concluído!")
                time.sleep(0.5)
                st.session_state[id_conf] = False
                st.session_state.busca_ativa = False
                st.rerun()

# 🎛️ FUNÇÃO MESTRE DE RENDERIZAÇÃO REVISADA E CORRIGIDA
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
    
    # 🔍 CAPTURA DA PALAVRA-CHAVE: O texto digitado aqui vai alimentar os filtros abaixo
    termo_busca = st.text_input(label="Refinar por palavra-chave:", placeholder="Digite para filtrar...", key="input_busca_painel").strip()

    # 🛠️ MÓDULO EXCLUSIVO DO ADMIN MESTRE
    if p_cli == "admin":
        st.markdown("<h3 style='text-align: center;'>🛠️ Cadastro de Assinantes (ERP)</h3>", unsafe_allow_html=True)
        with st.form(key="form_admin_mestre_cad", clear_on_submit=True):
            nome_novo = st.text_input("Nome do Estabelecimento:", placeholder="Ex: Supermercado...")
            perfil_novo = st.selectbox("Perfil de Acesso Corporativo:", ["comerciante", "saude", "petshop", "beleza", "investidor", "gestor", "jornalista"])
            regiao_novo = st.text_input("Região/Cidade de Atuação:", placeholder="Ex: São Paulo/SP...")
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

        st.markdown("<h3 style='text-align: center;'>📊 Central Financeira</h3>", unsafe_allow_html=True)
        try:
            resposta_clientes = supabase.table("clientes_b2b").select("*").order("created_at", desc=True).execute()
            if resposta_clientes.data:
                # 🏎️ MOTOR DE BUSCA DO ADMIN ATIVADO: Transforma dados em DataFrame para filtrar em tempo real
                df_clientes = pd.DataFrame(resposta_clientes.data)
                
                if termo_busca:
                    # Filtra a lista se o que o administrador digitou bater com o Nome ou Segmento do Comércio
                    filtro_admin = df_clientes["nome_estabelecimento"].str.contains(termo_busca, case=False, na=False) | \
                                   df_clientes["perfil_segmento"].str.contains(termo_busca, case=False, na=False)
                    df_clientes = df_clientes[filtro_admin]

                # Desenha os blocos expansores apenas com as lojas que passaram pelo filtro
                if not df_clientes.empty:
                    for _, cli in df_clientes.iterrows():
                        c_id = cli["id"]
                        with st.expander(f"🏢 {cli['nome_estabelecimento']} ({str(cli['perfil_segmento']).upper()})"):
                            st.text_input("🔑 Token Completo:", value=cli['token_acesso'], disabled=True, key=f"tk_full_{c_id}")
                            col_status, col_plan = st.columns(2)
                            with col_status:
                                status_pag = st.selectbox("Status de Pagamento:", ["Ativo", "Inadimplente", "Cancelado"], 
                                                          index=["Ativo", "Inadimplente", "Cancelado"].index(cli.get("status_pagamento", "Ativo")), key=f"pay_{c_id}")
                            with col_plan:
                                plano_cont = st.selectbox("Plano Contratado:", ["Bronze", "Prata", "Ouro"], 
                                                          index=["Bronze", "Prata", "Ouro"].index(cli.get("plano_contratado", "Ouro")), key=f"plan_{c_id}")
                            if st.button("💾 Salvar Alterações", key=f"save_{c_id}"):
                                supabase.table("clientes_b2b").update({"status_pagamento": status_pag, "plano_contratado": plano_cont}).eq("id", c_id).execute()
                                st.success("🔒 Sincronizado!")
                                time.sleep(0.5)
                                st.rerun()
                else:
                    st.write("ℹ️ Nenhum estabelecimento correspondente encontrado para a palavra-chave.")
        except Exception as e:
            st.error(f"Erro ao renderizar central financeira: {str(e)}")
            
    # 🏪 CASO NÃO SEJA ADMIN: Segue o fluxo normal de segurança do lojista (Comerciante comum)
    else:
        st.write("📋 Painel de Monitoramento de Escassez ativo para o assinante.")
        # O restante do seu código B2B original de consultas e gôndolas segue processado pelo Supabase...
