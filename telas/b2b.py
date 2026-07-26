import streamlit as st
import pandas as pd

def renderizar(supabase):
    # 🎨 INJEÇÃO DE CSS: Força o tema escuro na lista suspensa (selectbox) e corrige a quebra visual
    st.markdown("""
        <style>
        /* Define fundo escuro e texto branco para a lista suspensa */
        div[data-baseweb="popover"] ul {
            background-color: #1A1A1A !important;
            color: #FFFFFF !important;
        }
        /* Define cor verde institucional quando o mouse passa sobre a cidade */
        div[data-baseweb="popover"] li:hover {
            background-color: #00803B !important;
            color: #FFFFFF !important;
        }
        /* Garante que o texto da cidade selecionada na caixa fique branco */
        div[data-baseweb="select"] div {
            color: #FFFFFF !important;
        }
        /* Alinhamento geral de inputs para manter a simetria */
        .stSelectbox label {
            color: #FFFFFF !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # 🚏 BARRA DE NAVEGAÇÃO: Alinhamento padrão do painel corporativo
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("🏠 Página Inicial", key="nav_home_b2b_v", use_container_width=True):
            st.session_state.tela_atual = "home"
            st.rerun()
    with col_nav2:
        if st.session_state.get("perfil_b2b_atual") is not None:
            if st.button("🚪 Sair do Painel", key="nav_logout_b2b_v", use_container_width=True):
                st.session_state.perfil_b2b_atual = None
                st.rerun()

    # 🛡️ CORTINA DE FUMAÇA: Cabeçalho camuflado sob o codinome de segurança institucional
    st.markdown("<h1 style='text-align: center; font-weight: 900; margin-bottom: 0px;'>🔍 Sistema de Demandas</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; font-style: italic; color: #aaaaaa; margin-top: 5px; margin-bottom: 25px;'>Painel de Inteligência e Monitoramento de Mercado.</p>", unsafe_allow_html=True)

    # 🔐 CONTROLE DE ACESSO: Triagem de perfis B2B (Comércio, Mídia, etc.)
    if st.session_state.get("perfil_b2b_atual") is None:
        st.write("Selecione o seu perfil de acesso corporativo:")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("🏪 COMÉRCIO / VAREJO", use_container_width=True, key="btn_perf_com_v"):
                st.session_state.perfil_b2b_atual = "Comercio"
                st.rerun()
            if st.button("📢 MÍDIA / PUBLICIDADE", use_container_width=True, key="btn_perf_mid_v"):
                st.session_state.perfil_b2b_atual = "Midia"
                st.rerun()
        with col_p2:
            if st.button("🏛️ SETOR PÚBLICO / PREFEITURA", use_container_width=True, key="btn_perf_pub_v"):
                st.session_state.perfil_b2b_atual = "Publico"
                st.rerun()
            if st.button("📊 INVESTIDORES / EXPANSÃO", use_container_width=True, key="btn_perf_inv_v"):
                st.session_state.perfil_b2b_atual = "Investidor"
                st.rerun()

    # 🏙️ RENDERIZAÇÃO DO PAINEL LOGADO: Filtros globais e cruzamento de carências
    else:
        perfil = st.session_state.perfil_b2b_atual
        st.info(f"🔑 Logado com sucesso no Perfil: **{perfil}**")
        
        # 🔍 FILTRO DA CIDADE (Mecanismo Global que estava apresentando fundo branco no navegador)
        try:
            cidades_query = supabase.table("locais_destino").select("regiao_cidade").execute()
            if cidades_query.data:
                df_cid = pd.DataFrame(cidades_query.data)
                lista_cidades = sorted(df_cid["regiao_cidade"].unique().tolist())
        except:
            lista_cidades = []
            
        lista_cidades_opcoes = ["Todos (Global)"] + lista_cidades
        
        # O seletor abaixo agora obedecerá obrigatoriamente as regras de CSS escuras inseridas no topo
        cidade_selecionada = st.selectbox(
            "📍 Selecionar Região/Cidade para Análise:",
            options=lista_cidades_opcoes,
            key="b2b_filtro_cidade_global"
        )
        
        st.write("")
        st.markdown("### 📊 Demandas Ocultas Identificadas na Região")
        
        try:
            # Puxa os dados brutos de relatos para estruturar as tabelas do lojista
            query_relatos = supabase.table("relatos_escassez").select("item_solicitado, status, data_registro, locais_destino(nome_exibicao, regiao_cidade)").eq("status", "Pendente")
            
            if cidade_selecionada != "Todos (Global)":
                # Se não for global, aplica a filtragem estrita da cidade selecionada
                relatos_dados = query_relatos.execute()
                dados_filtrados = [r for r in relatos_dados.data if r.get("locais_destino") and r["locais_destino"]["regiao_cidade"] == cidade_selecionada]
            else:
                relatos_dados = query_relatos.execute()
                dados_filtrados = relatos_dados.data

            if dados_filtrados:
                lista_tabela = []
                for r in dados_filtrados:
                    lista_tabela.append({
                        "Item Ausente": str(r["item_solicitado"]).strip().title(),
                        "Localidade Relatada": str(r["locais_destino"]["nome_exibicao"]).strip().title(),
                        "Cidade/Região": str(r["locais_destino"]["regiao_cidade"]).strip()
                    })
                
                df_relatorio = pd.DataFrame(lista_tabela)
                st.dataframe(df_relatorio, use_container_width=True, hide_index=True)
            else:
                st.write("ℹ️ Nenhuma demanda pendente registrada para a região selecionada.")
        except:
            st.error("⚠️ Falha ao carregar a matriz de dados do banco. Verifique a conexão.")
