import streamlit as st
import os
import pandas as pd
import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# --- CONEXÃO INTELIGENTE (LOCAL E NUVEM) ---
caminho_atual = os.path.dirname(os.path.abspath(__file__))
caminho_env = os.path.join(caminho_atual, ".env")
load_dotenv(caminho_env)

url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

if not url or not key:
    st.error(
        "⚠️ As credenciais de conexão com o banco de dados não foram encontradas.")
    st.stop()

supabase: Client = create_client(url, key)
# --------------------------------------------

st.set_page_config(page_title="Sistema de Pesquisas",
                   page_icon="🔍", layout="centered")

# --- CUSTOMIZAÇÃO ESTÉTICA PREMIUM (TRAVA DE DESIGN DARK COM ALTO CONTRASTE) ---
st.markdown("""
    <style>
    /* Força o fundo escuro moderno */
    .stApp {
        background-color: #121212 !important;
        color: #FFFFFF !important;
    }
    /* CORREÇÃO DE CONTRASTE: Força todas as etiquetas, textos e subtextos a ficarem brancos */
    .stWidgetFormLabel, label, p, .stMarkdown, [data-testid="stWidgetLabel"] {
        color: #FFFFFF !important;
    }
    /* Estilização dos botões verdes premium */
    .stButton>button, .stFormSubmitButton>button {
        background-color: #00cc66 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.8rem 1rem !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
        width: 100% !important;
    }
    .stButton>button:hover, .stFormSubmitButton>button:hover {
        background-color: #00994d !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.3) !important;
    }
    /* Customização dos campos de texto escuros com borda de realce */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 10px !important;
        background-color: #1E1E1E !important;
        color: white !important;
        border: 1px solid #444444 !important;
    }
    .stExpander {
        background-color: #1E1E1E !important;
        border-left: 5px solid #00cc66 !important;
        border-radius: 10px !important;
        margin-bottom: 0.8rem !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15) !important;
    }
    [data-testid="stForm"] {
        border: none !important;
        padding: 0px !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

if "tela_atual" not in st.session_state:
    st.session_state.tela_atual = "home"
if "token_valido" not in st.session_state:
    st.session_state.token_valido = False
if "perfil_cliente" not in st.session_state:
    st.session_state.perfil_cliente = None
if "busca_ativa" not in st.session_state:
    st.session_state.busca_ativa = False
# --- TELA: HOME ---
if st.session_state.tela_atual == "home":
    st.title("🔍 Central de Demandas Ocultas")
    st.markdown("##### *O termômetro de carências da nossa região.*")
    st.write("---")
    st.write("Selecione o seu perfil de acesso para continuar:")
    st.write("")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Sou Consumidor\n(Registrar Falta)", use_container_width=True, key="btn_ir_consumidor"):
            st.session_state.tela_atual = "consumidor"
            st.rerun()
    with col2:
        if st.button("📊 Sou Comerciante / Gestor\n(Acessar Painel)", use_container_width=True, key="btn_ir_comerciante"):
            st.session_state.tela_atual = "autenticacao"
            st.rerun()

# --- TELA: FORMULÁRIO DO CONSUMIDOR ---
elif st.session_state.tela_atual == "consumidor":
    if st.button("⬅️ Voltar ao Menu Principal", key="btn_voltar_cons"):
        st.session_state.tela_atual = "home"
        st.rerun()

    st.title("🔍 Central de Demandas Ocultas")
    st.markdown("##### *Deixe saber o que você deseja e sente falta na região.*")
    st.write("---")

    tipo_selecionado = st.radio(
        label="Que tipo de ausência você quer registrar?",
        options=["Produto / Marca", "Serviço Local / Novo Estabelecimento",
                 "Serviço Público / Infraestrutura"],
        horizontal=True,
        key="radio_tipo_carencia"
    )

    if tipo_selecionado == "Produto / Marca":
        label_item = "Qual produto ou marca você buscou e não encontrou?"
        placeholder_item = "Ex: Nome do produto, marca específica..."
        label_local = "Em qual estabelecimento isso ocorreu?"
        placeholder_local = "Ex: Nome do mercadinho, farmácia..."
    elif tipo_selecionado == "Serviço Local / Novo Estabelecimento":
        label_item = "Qual tipo de comércio ou serviço falta neste bairro?"
        placeholder_item = "Ex: Sapataria, lavanderia, costureira..."
        label_local = "Em qual rua, travessa ou pedaço do bairro isso faz falta?"
        placeholder_local = "Ex: Bairro Centro, Avenida X..."
    else:
        label_item = "Qual carência de infraestrutura/manutenção você identificou?"
        placeholder_item = "Ex: Falha na iluminação, falta de médicos..."
        label_local = "Qual o ponto de referência ou localidade exata?"
        placeholder_local = "Ex: Posto de saúde do bairro Y..."

    with st.form(key="formulario_demandas", clear_on_submit=True):
        item_solicitado = st.text_input(
            label=label_item, placeholder=placeholder_item, key="input_item")
        local_ocorrencia = st.text_input(
            label=label_local, placeholder=placeholder_local, key="input_local")
        st.write("")
        botao_enviar = st.form_submit_button(
            "Registrar Ocorrência", use_container_width=True)

    if botao_enviar:
        if item_solicitado and local_ocorrencia:
            texto_usuario = item_solicitado.strip().lower()
            palavras_infra = ["rua", "praça", "iluminação", "poste", "asfalto",
                              "médico", "ônibus", "hospital", "bueiro", "segurança", "luz", "polícia"]
            palavras_produto = ["leite", "fralda", "ração", "refrigerante",
                                "cerveja", "sabão", "remédio", "arroz", "feijão"]

            erro_detectado = False
            if tipo_selecionado == "Produto / Marca" and any(p in texto_usuario for p in palavras_infra):
                st.error(
                    "⚠️ Ops! Parece que você está relatando um problema de Infraestrutura Pública. Altere a opção no topo.")
                erro_detectado = True
            elif tipo_selecionado == "Serviço Local / Novo Estabelecimento" and any(p in texto_usuario for p in palavras_produto):
                st.error(
                    "⚠️ Ops! Parece que você está relatando a falta de um produto. Altere a opção no topo.")
                erro_detectado = True

            if not erro_detectado:
                try:
                    local_formatado = local_ocorrencia.strip().title()
                    local_data = supabase.table("locais_destino").insert({
                        "nome_exibicao": local_formatado,
                        "regiao_cidade": "São Paulo",
                        "regiao_estado": "SP"
                    }).execute()

                    local_id = None
                    if local_data.data and len(local_data.data) > 0:
                        local_id = local_data.data["id"]

                    if local_id:
                        item_formatado = item_solicitado.strip().title()
                        supabase.table("relatos_escassez").insert({
                            "local_id": local_id,
                            "item_solicitado": item_formatado,
                            "tipo_carencia": tipo_selecionado,
                            "status": "Pendente"
                        }).execute()
                        st.success(
                            "✅ Registro computado e salvo na nuvem com anonimato garantido!")
                except Exception as e:
                    st.error(f"⚠️ Erro técnico detalhado: {str(e)}")
        else:
            st.warning(
                "⚠️ Por favor, preencha ambos os campos antes de enviar.")

    st.write("")
    st.markdown("### 🏆 Impactos Recentes no Bairro")
    try:
        resolvidos = supabase.table("relatos_escassez").select(
            "item_solicitado, locais_destino(nome_exibicao)").eq("status", "Atendido").limit(3).execute()
        if resolvidos.data and len(resolvidos.data) > 0:
            for item in resolvidos.data:
                if item.get("locais_destino"):
                    st.info(
                        f"✅ **{item['locais_destino']['nome_exibicao']}** repôs o estoque ou atendeu: **{item['item_solicitado']}**!")
        else:
            st.write("ℹ️ Nenhuma benfeitoria registrada nos últimos dias.")
    except:
        pass
# --- TELA: AUTENTICAÇÃO POR TOKEN ---
elif st.session_state.tela_atual == "autenticacao":
    if st.button("⬅️ Voltar ao Menu Principal", key="btn_voltar_aut"):
        st.session_state.tela_atual = "home"
        st.session_state.token_valido = False
        st.session_state.perfil_cliente = None
        st.rerun()

    st.title("🔒 Área Restrita de Inteligência")
    st.markdown(
        "##### *Insira a sua chave de acesso corporativa para liberar os relatórios.*")
    st.write("---")

    token_inserido = st.text_input(
        label="Token de Acesso:", type="password", placeholder="Digite seu token de acesso...")

    if st.button("Validar Credenciais", use_container_width=True):
        if token_inserido == "COMERCIO10":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "comerciante"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_inserido == "INVEST20":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "investidor"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_inserido == "GESTOR30":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "gestor"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        else:
            st.error("❌ Token inválido ou expirado.")

# --- TELA: PAINEL DO COMERCIANTE / GESTOR ---
elif st.session_state.tela_atual == "comerciante":
    if not st.session_state.token_valido:
        st.session_state.tela_atual = "home"
        st.rerun()

    if st.button("⬅️ Sair do Painel (Logoff)", key="btn_voltar_com"):
        st.session_state.tela_atual = "home"
        st.session_state.token_valido = False
        st.session_state.perfil_cliente = None
        st.session_state.busca_ativa = False
        st.rerun()

    st.title("📊 Painel de Decisão Estratégica")

    if st.session_state.perfil_cliente == "comerciante":
        st.markdown(
            "##### 🏪 *Nível de Acesso: Varejo Local (Foco em Gôndolas e Marcas)*")
        opcoes_filtro = ["Apenas Produtos/Marcas (Varejo)"]
    elif st.session_state.perfil_cliente == "investidor":
        st.markdown(
            "##### 💼 *Nível de Acesso: Investidor e Expansão (Foco em Serviços do Bairro)*")
        opcoes_filtro = ["Oportunidades de Novos Negócios (Serviços)"]
    else:
        st.markdown(
            "##### 🏛️ *Nível de Acesso: Gestão Pública (Foco em Infraestrutura Urbana)*")
        opcoes_filtro = ["Infraestrutura Urbana (Setor Público)"]

    st.write("---")

    filtro_frente = st.selectbox(
        label="Selecione a Frente de Inteligência:", options=opcoes_filtro, key="selectbox_frente")
    termo_busca = st.text_input(label="Filtrar por palavra-chave:",
                                placeholder="Digite para refinar...", key="input_busca_painel")

    if st.button("Buscar Oportunidades Ocultas", use_container_width=True, key="btn_buscar"):
        st.session_state.busca_ativa = True

    if st.session_state.busca_ativa:
        try:
            resposta = supabase.table("relatos_escassez").select(
                "id, item_solicitado, tipo_carencia, data_registro, status, locais_destino(nome_exibicao, regiao_cidade)").eq("status", "Pendente").execute()

            if resposta.data:
                dados_limpos = []
                agora = datetime.datetime.now(datetime.timezone.utc)

                for registro in resposta.data:
                    if registro.get("locais_destino"):
                        data_str = registro.get("data_registro")
                        if data_str:
                            data_limpa = data_str.replace("Z", "+00:00")
                            data_reg = datetime.datetime.fromisoformat(
                                data_limpa)
                            if data_reg.tzinfo is None:
                                data_reg = data_reg.replace(
                                    tzinfo=datetime.timezone.utc)

                            idade_dias = (agora - data_reg).days
                            categoria = registro.get(
                                "tipo_carencia", "Produto / Marca")

                            manter_registro = False
                            if category == "Produto / Marca" and idade_dias <= 30:
                                manter_registro = True
                            elif category == "Serviço Local / Novo Estabelecimento" and idade_dias <= 365:
                                manter_registro = True
                            elif category == "Serviço Público / Infraestrutura" and idade_dias <= 180:
                                manter_registro = True

                            if manter_registro:
                                dados_limpos.append({
                                    "ID": registro["id"],
                                    "O que Falta": registro["item_solicitado"],
                                    "Categoria": categoria,
                                    "Local/Referência": registro["locais_destino"]["nome_exibicao"],
                                    "Cidade": registro["locais_destino"]["regiao_cidade"],
                                    "Dias": idade_dias
                                })

                if dados_limpos:
                    df = pd.DataFrame(dados_limpos)

                    if filtro_frente == "Apenas Produtos/Marcas (Varejo)":
                        df = df[df['Categoria'] == "Produto / Marca"]
                    elif filtro_frente == "Oportunidades de Novos Negócios (Serviços)":
                        df = df[df['Categoria'] ==
                                "Serviço Local / Novo Estabelecimento"]
                    elif filtro_frente == "Infraestrutura Urbana (Setor Público)":
                        df = df[df['Categoria'] ==
                                "Serviço Público / Infraestrutura"]

                    if termo_busca:
                        df = df[df['O que Falta'].str.contains(
                            termo_busca, case=False) | df['Local/Referência'].str.contains(termo_busca, case=False)]

                    if not df.empty:
                        df_agrupado = df.groupby(["O que Falta", "Categoria", "Local/Referência", "Cidade"]).agg(
                            Volume_Pedidos=("ID", "count"),
                            Menor_Idade=("Dias", "min")
                        ).reset_index()

                        st.markdown(
                            "#### 📊 Distribuição de Demandas na Região (Visão Geral)")
                        contagem_itens = df["O que Falta"].value_counts()
                        st.bar_chart(contagem_itens)

                        st.write("---")
                        st.write(
                            f"📈 **Detalhamento das carências ativas ({len(df_agrupado)} itens encontrados):**")

                        for indice, linha in df_agrupado.iterrows():
                            titulo_card = f"❌ {linha['O que Falta']} ({linha['Volume_Pedidos']} solicitações)"

                            with st.expander(titulo_card):
                                st.write(
                                    f"📍 **Local:** {linha['Local/Referência']} ({linha['Cidade']})")
                                st.write(
                                    f"⏱️ **Último alerta há:** {linha['Menor_Idade']} dias")
                                st.write("")

                                chave_botao = f"btn_baixa_direta_{indice}"
                                if st.button("✅ Marcar como Estoque Reposto / Resolvido", key=chave_botao):
                                    supabase.table("relatos_escassez").update({"status": "Atendido"}).eq(
                                        "item_solicitado", linha['O que Falta']).execute()
                                    st.success(
                                        f"🎉 Sucesso! O item '{linha['O que Falta']}' foi dado baixa coletiva.")
                                    st.session_state.busca_ativa = False
                                    st.rerun()
                    else:
                        st.info("ℹ️ Nenhum registro ativo encontrado.")
                else:
                    st.info(
                        "ℹ️ Os registros existentes já expiraram por tempo de mercado.")
            else:
                st.info("ℹ️ O banco de dados está limpo!")
        except Exception as e:
            st.error(f"⚠️ Erro técnico detalhado: {str(e)}")
