import streamlit as st
import os
import pandas as pd
import datetime
import hashlib
from dotenv import load_dotenv
from supabase import create_client, Client

# --- DECLARAÇÃO DE VARIÁVEIS UNIVERSAIS PRIVADAS (ANTI-NAMEERROR) ---
botao_enviar = False
termo_busca = ""
filtro_frente = ""

# --- CONEXÃO INTELIGENTE (LOCAL E NUVEM) ---
caminho_atual = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(caminho_atual, ".env"))
url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

if not url or not key:
    st.error("⚠️ As credenciais de conexão não foram encontradas.")
    st.stop()
supabase: Client = create_client(url, key)

st.set_page_config(page_title="E o que falta?",
                   page_icon="🔍", layout="centered")

# --- CAPTURADOR INVISÍVEL DE PEGADA DIGITAL ANTI-FRAUDE ---


def obter_pegada_digital():
    try:
        headers = st.context.headers
        ip = headers.get("X-Forwarded-For", "127.0.0.1").split(",").strip()
        agente = headers.get("User-Agent", "Desconhecido")
        return hashlib.sha256(f"{ip}-{agente}".encode('utf-8')).hexdigest()
    except:
        return "pegada_generica_fallback"


# --- CUSTOMIZAÇÃO ESTÉTICA PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #121212 !important; color: #FFFFFF !important; }
    .stWidgetFormLabel, label, p, .stMarkdown, [data-testid="stWidgetLabel"] { color: #FFFFFF !important; }
    .stButton>button, .stFormSubmitButton>button, [data-testid="stDownloadButton"]>button {
        background-color: #00803B !important; color: #FFFFFF !important; font-weight: 800 !important;
        border-radius: 12px !important; border: none !important; padding: 0.8rem 0.2rem !important;
        font-size: 15px !important; transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important; width: 100% !important; display: block !important;
    }
    .stButton>button:hover, .stFormSubmitButton>button:hover, [data-testid="stDownloadButton"]>button:hover { background-color: #005a24 !important; }
    h1 { font-size: 34px !important; font-weight: 900 !important; text-align: center !important; width: 100% !important; white-space: nowrap !important; margin-bottom: 1.5rem !important; }
    [data-testid="stHorizontalBlock"]:has(button[key*="simetrico"]) { gap: 10px !important; flex-direction: row !important; flex-wrap: nowrap !important; }
    .stTextInput input, .stTextArea textarea, div[data-baseweb="textarea"] textarea, div[data-baseweb="input"] input { background-color: #1E1E1E !important; color: #FFFFFF !important; border-radius: 10px !important; border: 1px solid #444444 !important; }
    input::placeholder, textarea::placeholder { color: #888888 !important; font-style: italic !important; }
    .bloco-lista-premium { background-color: #1E1E1E !important; padding: 1.2rem !important; border-radius: 10px !important; margin-bottom: 0.8rem !important; border: 1px solid #333333 !important; box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important; overflow: hidden !important; }
    .tag-calor-alta { background-color: #ff3333 !important; color: white !important; padding: 0.2rem 0.6rem !important; border-radius: 6px !important; font-weight: bold !important; font-size: 12px !important; float: right !important; }
    .tag-calor-media { background-color: #ff9933 !important; color: black !important; padding: 0.2rem 0.6rem !important; border-radius: 6px !important; font-weight: bold !important; font-size: 12px !important; float: right !important; }
    .tag-calor-baixa { background-color: #3399ff !important; color: white !important; padding: 0.2rem 0.6rem !important; border-radius: 6px !important; font-weight: bold !important; font-size: 12px !important; float: right !important; }
    [data-testid="stForm"] { border: none !important; padding: 0px !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
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
if "dados_grafico" not in st.session_state:
    st.session_state.dados_grafico = None
if "aba_consumidor" not in st.session_state:
    st.session_state.aba_consumidor = "menu_triagem"

# --- TELA: HOME ---
if st.session_state.tela_atual == "home":
    st.title("🔍 E o que falta?")
    st.markdown("##### *O termômetro de carências da nossa região.*")
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Sou Consumidor\n(Registrar Falta)", use_container_width=True, key="btn_ir_consumidor"):
            st.session_state.tela_atual = "consumidor"
            st.session_state.aba_consumidor = "menu_triagem"
            st.rerun()
    with col2:
        if st.button("📊 Sou Comerciante / Gestor\n(Acessar Painel)", use_container_width=True, key="btn_ir_comerciante"):
            st.session_state.tela_atual = "autenticacao"
            st.rerun()

# --- TELA: FORMULÁRIO DO CONSUMIDOR ---
elif st.session_state.tela_atual == "consumidor":
    col_nav1, col_nav2 = st.columns(2, gap="small")
    with col_nav1:
        if st.button("🏠 Ir para Home", key="nav_home_simetrico", use_container_width=True):
            st.session_state.tela_atual = "home"
            st.rerun()
    with col_nav2:
        if st.session_state.aba_consumidor != "menu_triagem":
            if st.button("🗂️ Mudar Categoria", key="nav_categoria_simetrico", use_container_width=True):
                st.session_state.aba_consumidor = "menu_triagem"
                st.rerun()
    st.title("🔍 E o que falta?")
    if st.session_state.aba_consumidor == "menu_triagem":
        st.markdown("##### 📍 Onde você está agora?")
        regiao_final = st.text_input(label="Localizacao", placeholder="Ex: São Paulo/SP - Centro",
                                     key="input_regiao_via_unica", label_visibility="collapsed")
        st.write(
            "Escolha o tipo de ausência que você quer registrar no bairro ou comunidade:")
        if st.button("📦 PRODUTO OU MARCA EM FALTA\n(Falta nas gôndolas de mercados, farmácias...)", use_container_width=True, key="triagem_prod"):
            st.session_state.aba_consumidor = "produto"
            st.rerun()
        st.write("")
        if st.button("🏪 NOVO COMÉRCIO OU SERVIÇO LOCAL\n(Falta de lavanderia, sapataria, padaria...)", use_container_width=True, key="triagem_serv"):
            st.session_state.aba_consumidor = "servico"
            st.rerun()
        st.write("")
        if st.button("🏛️ INFRAESTRUTURA OU ZELADORIA PÚBLICA\n(Falha na iluminação, buracos no asfalto...)", use_container_width=True, key="triagem_infra"):
            st.session_state.aba_consumidor = "infra"
            st.rerun()
# --- TELA: FORMULÁRIO DO CONSUMIDOR ---
elif st.session_state.tela_atual == "consumidor":
    col_nav1, col_nav2 = st.columns(2, gap="small")
    with col_nav1:
        if st.button("🏠 Ir para Home", key="nav_home_simetrico", use_container_width=True):
            st.session_state.tela_atual = "home"
            st.rerun()
    with col_nav2:
        if st.session_state.aba_consumidor != "menu_triagem":
            if st.button("🗂️ Mudar Categoria", key="nav_categoria_simetrico", use_container_width=True):
                st.session_state.aba_consumidor = "menu_triagem"
                st.rerun()
    st.title("🔍 E o que falta?")
    if st.session_state.aba_consumidor == "menu_triagem":
        st.markdown("##### 📍 Onde você está agora?")
        regiao_final = st.text_input(label="Localizacao", placeholder="Ex: São Paulo/SP - Centro",
                                     key="input_regiao_via_unica", label_visibility="collapsed")
        st.write(
            "Escolha o tipo de ausência que você quer registrar no bairro ou comunidade:")
        if st.button("📦 PRODUTO OU MARCA EM FALTA\n(Falta nas gôndolas de mercados, farmácias...)", use_container_width=True, key="triagem_prod"):
            st.session_state.aba_consumidor = "produto"
            st.rerun()
        st.write("")
        if st.button("🏪 NOVO COMÉRCIO OU SERVIÇO LOCAL\n(Falta de lavanderia, sapataria, padaria...)", use_container_width=True, key="triagem_serv"):
            st.session_state.aba_consumidor = "servico"
            st.rerun()
        st.write("")
        if st.button("🏛️ INFRAESTRUTURA OU ZELADORIA PÚBLICA\n(Falha na iluminação, buracos no asfalto...)", use_container_width=True, key="triagem_infra"):
            st.session_state.aba_consumidor = "infra"
            st.rerun()
    else:
        if st.session_state.aba_consumidor == "produto":
            st.markdown(
                "### 📦 Produto / Marca\n##### *Mapeando falhas de estoque e gôndolas vazias.*")
            label_item, placeholder_item = "Qual produto ou marca você buscou e não encontrou?", "Ex: Leite condensado marca X..."
            label_local, placeholder_local = "Em qual estabelecimento isso ocorreu?", "Ex: Nome do mercado, farmácia..."
            label_contato, tipo_envio = "Quer ser avisado caso o estoque seja reposto ou outra loja ofereça? (Opcional)", "Produto / Marca"
        elif st.session_state.aba_consumidor == "servico":
            st.markdown(
                "### 🏪 Novo Comércio / Serviço\n##### *Mapeando oportunidades de novos negócios e conveniência.*")
            label_item, placeholder_item = "Qual tipo de comércio ou serviço falta neste bairro/comunidade?", "Ex: Sapataria, lavanderia..."
            label_local, placeholder_local = "Em qual rua, travessa, faculdade ou ponto isso faz falta?", "Ex: Avenida Principal..."
            label_contato, tipo_envio = "Quer ser avisado caso este serviço seja aberto ou oferecido? (Opcional)", "Serviço Local / Novo Estabelecimento"
        else:
            st.markdown(
                "### 🏛️ Infraestrutura / Zeladoria\n##### *Mapeando melhorias urbanas e cobranças públicas.*")
            label_item, placeholder_item = "Qual carência de infraestrutura/manutenção você identificou?", "Ex: Falha na iluminação..."
            label_local, placeholder_local = "Qual o ponto de referência ou localidade exata?", "Ex: Posto de saúde do bairro Y..."
            label_contato, tipo_envio = "Quer ser avisado caso esta manutenção pública seja realizada? (Opcional)", "Serviço Público / Infraestrutura"
        st.write("")
        with st.form(key="formulario_dinamico_consumidor", clear_on_submit=False):
            item_solicitado = st.text_input(
                label=label_item, placeholder=placeholder_item, key="input_item")
            local_ocorrencia = st.text_input(
                label=label_local, placeholder=placeholder_local, key="input_local")
            observacao_usuario = st.text_area(
                label="Mais detalhes (Opcional):", placeholder="Ex: Detalhe o ocorrido...", key="input_obs")
            contato_usuario = st.text_input(
                label=label_contato, placeholder="Ex: Seu e-mail ou WhatsApp...", key="input_contato")
            st.write("")
            botao_enviar = st.form_submit_button(
                "Registrar Ocorrência", use_container_width=True)
elif st.session_state.tela_atual == "autenticacao":
    if st.button("⬅️ Voltar ao Menu Principal", key="btn_voltar_aut"):
        st.session_state.tela_atual = "home"
        st.session_state.token_valido = False
        st.rerun()
    st.markdown("<h1 style='text-align: center; margin-bottom: 0px !important;'>🔍 E o que falta?</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; font-weight: 600; color: #aaaaaa !important; margin-top: 5px; margin-bottom: 25px;'>Área Restrita para Comerciantes e Gestores</p>", unsafe_allow_html=True)
    st.write("---")
    token_inserido = st.text_input(
        label="Token de Acesso:", type="password", placeholder="Digite seu token de acesso...")
    st.write("")
    if st.button("Validar Credenciais e Acessar", use_container_width=True, key="btn_validar_token_hibrido") or (token_inserido and not st.session_state.token_valido):
        if token_inserido in ["COMERCIO10", "SUPER_VILA_77"]:
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "comerciante"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_inserido == "SAUDE20":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "saude"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_inserido == "PET30":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "petshop"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_inserido == "BELEZA40":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "beleza"
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
        elif token_inserido == "MIDIA40":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "jornalista"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_inserido == "ADMIN99":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "admin"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_inserido != "":
            st.error("❌ Token inválido.")
# --- TELA: PAINEL DE DECISÃO ESTRATÉGICA (B2B) ---
elif st.session_state.tela_atual == "comerciante":
    if not st.session_state.token_valido:
        st.session_state.tela_atual = "home"
        st.rerun()
    if st.button("⬅️ Sair do Painel (Logoff)", key="btn_voltar_com"):
        st.session_state.tela_atual = "home"
        st.session_state.token_valido = False
        st.perfil_cliente = None
        st.session_state.busca_ativa = False
        st.session_state.dados_grafico = None
        st.rerun()
    st.markdown("<h1 style='text-align: center; margin-bottom: 0px !important;'>🔍 E o que falta?</h1>",
                unsafe_allow_html=True)
    loja_alvo_prioridade = "Mercadinho Do Bairro" if st.session_state.perfil_cliente == "comerciante" else ""
    espectador_analitico = st.session_state.perfil_cliente in [
        "investidor", "gestor", "jornalista"]

    if st.session_state.perfil_cliente == "comerciante":
        st.markdown(
            "##### 🏪 *Nível de Acesso: Varejo Local (Foco em Gôndolas)*")
    elif st.session_state.perfil_cliente == "saude":
        st.markdown("##### 🩺 *Nível de Acesso: Saúde & Bem-Estar*")
    elif st.session_state.perfil_cliente == "petshop":
        st.markdown("##### 🐶 *Nível de Acesso: Petshop & Veterinária*")
    elif st.session_state.perfil_cliente == "beleza":
        st.markdown("##### 💈 *Nível de Acesso: Beleza & Estética*")
    elif st.session_state.perfil_cliente == "investidor":
        st.markdown(
            "##### 💼 *Nível de Acesso: Investidor e Expansão (Vazios Comerciais)*")
    elif st.session_state.perfil_cliente == "jornalista":
        st.markdown(
            "##### 📰 *Nível de Acesso: Imprensa e Jornalismo Regional (Dados Consolidados)*")
    elif st.session_state.perfil_cliente == "admin":
        st.markdown("<p style='text-align: center; font-size: 24px; font-weight: 600; color: #aaaaaa !important; margin-top: 5px; margin-bottom: 25px;'>Painel de Controle Mestre</p>", unsafe_allow_html=True)
    else:
        st.markdown(
            "##### 🏛️ *Nível de Acesso: Gestão Pública (Foco em Infraestrutura)*")

    st.write("---")
    termo_busca = st.text_input(label="Refinar por palavra-chave ou estabelecimento (Opcional):",
                                placeholder="Digite para filtrar a lista abaixo...", key="input_busca_painel")

    # --- INTERFACE MASTER ISOLADA: EXCLUSIVA DO ADMINISTRADOR MESTRE ---
    if st.session_state.perfil_cliente == "admin":
        st.markdown("### 🛠️ Cadastro de Assinantes")
        st.markdown(
            "##### *Preencha os campos para emissão automática de tokens UUID na nuvem.*")
        id_formulario_admin = f"form_cadastro_admin_{datetime.datetime.now().strftime('%M%S')}"
        with st.form(key=id_formulario_admin, clear_on_submit=True):
            nome_novo_comercio = st.text_input(
                "Nome do Estabelecimento Comercial / Cliente Real:", placeholder="Ex: Supermercado Xavier, Petshop Bairro Alto...")
            perfil_novo_comercio = st.selectbox("Perfil de Acesso Corporativo (Nível de Filtro):", [
                                                "comerciante", "saude", "petshop", "beleza", "investidor", "gestor", "jornalista"])
            st.write("")
            if st.form_submit_button("💼 Cadastrar Cliente e Emitir Token UUID"):
                if nome_novo_comercio:
                    try:
                        novo_registro = supabase.table("clientes_b2b").insert(
                            {"nome_estabelecimento": nome_novo_comercio.strip().title(), "perfil_segmento": perfil_novo_comercio}).execute()
                        if novo_registro.data:
                            st.success(
                                "🎉 Cliente cadastrado com sucesso absoluto na nuvem!")
                            st.info(
                                f"🔑 **TOKEN PRIVADO GERADO:** `{novo_registro.data['token_acesso']}`")
                            st.warning(
                                "Copie o código acima e envie agora mesmo para o WhatsApp do cliente pagante.")
                    except Exception as error_db:
                        st.error(
                            f"⚠️ Falha na conexão com o banco: {str(error_db)}")
                else:
                    st.warning(
                        "⚠️ Preencha o nome do estabelecimento para emitir a credencial.")
    # --- PROCESSAMENTO GLOBAL DE DADOS REAL / SIMULADO ---
    if st.session_state.perfil_cliente != "admin":
        if not st.session_state.busca_ativa or st.session_state.dados_grafico is None:
            st.session_state.busca_ativa = True
            try:
                resposta = supabase.table("relatos_escassez").select(
                    "id, item_solicitado, tipo_carencia, data_registro, status, detalhes_adicionais, observacao_detalhe, sub_segmento, pegada_digital, contato_aviso, locais_destino(nome_exibicao, regiao_cidade)").execute()
                dados_limpos = []
                agora = datetime.datetime.now(datetime.timezone.utc)
                if resposta.data and len(resposta.data) > 0:
                    for registro in resposta.data:
                        if registro.get("locais_destino"):
                            sub_seg = str(registro.get(
                                "sub_segmento", "Geral")).strip()
                            cat_bruta = str(registro.get(
                                "tipo_carencia", "Produto / Marca")).strip()
                            idade_dias = max(0, (agora - datetime.datetime.fromisoformat(registro.get(
                                "data_registro").replace("Z", "+00:00"))).days) if registro.get("data_registro") else 0
                            categoria_limpa = "Serviço Público / Infraestrutura" if ("Público" in cat_bruta or "Publico" in cat_bruta or "Infra" in cat_bruta or "Zeladoria" in sub_seg) else (
                                "Serviço Local / Novo Estabelecimento" if ("Local" in cat_bruta or "Invest" in sub_seg) else "Produto / Marca")
                            dados_limpos.append({"ID": registro["id"], "O que Falta": registro["item_solicitado"].strip().title(), "Categoria": categoria_limpa, "Local/Referência": registro["locais_destino"]["nome_exibicao"], "Cidade": registro["locais_destino"]["regiao_cidade"],
                                                "Dias": idade_dias, "Observação": registro.get("observacao_detalhe") or registro.get("detalhes_adicionais") or "", "SubSegmento": sub_seg, "Pegada": registro.get("pegada_digital") or f"anon_{registro['id']}", "Contato": registro.get("contato_aviso") or ""})

                dados_mock = [
                    {"ID": 991, "O que Falta": "Leite Desnatado Parmalat 1L", "Categoria": "Produto / Marca", "Local/Referência": "Mercadinho Do Bairro",
                        "Cidade": "São Paulo/SP - Centro", "Dias": 4, "Observação": "Falta toda quarta.", "SubSegmento": "Supermercado", "Pegada": "hash1", "Contato": "11999999999"},
                    {"ID": 994, "O que Falta": "Lavanderia Expressa Auto-Serviço", "Categoria": "Serviço Local / Novo Estabelecimento", "Local/Referência": "Avenida Das Palmeiras",
                        "Cidade": "São Paulo/SP - Tatuapé", "Dias": 45, "Observação": "Prédios novos sem serviço.", "SubSegmento": "Investimento", "Pegada": "hash4", "Contato": ""},
                    {"ID": 997, "O que Falta": "Manutenção De Iluminação Pública", "Categoria": "Serviço Público / Infraestrutura", "Local/Referência": "Rua das Flores, 40",
                        "Cidade": "São Paulo/SP - Centro", "Dias": 2, "Observação": "Poste apagado.", "SubSegmento": "Zeladoria", "Pegada": "hash7", "Contato": ""}
                ]
                for m in dados_mock:
                    if not any(d["O que Falta"].lower() == m["O que Falta"].lower() for d in dados_limpos):
                        dados_limpos.append(m)
                st.session_state.dados_grafico = pd.DataFrame(dados_limpos)
            except Exception as e:
                st.error(f"⚠️ Erro técnico: {str(e)}")
        if st.session_state.busca_ativa and st.session_state.dados_grafico is not None:
            df = st.session_state.dados_grafico
            if not df.empty:
                if st.session_state.perfil_cliente == "comerciante":
                    nomes_abas = [
                        "📦 Apenas Produtos/Marcas (Varejo)", "🎯 Marketplace Reverso (Ocorrências Gerais)"]
                elif st.session_state.perfil_cliente == "saude":
                    nomes_abas = ["📦 Apenas Serviços de Saúde",
                                  "🎯 Marketplace Reverso (Ocorrências Gerais)"]
                elif st.session_state.perfil_cliente == "petshop":
                    nomes_abas = ["📦 Apenas Produtos e Serviços Pet",
                                  "🎯 Marketplace Reverso (Ocorrências Gerais)"]
                elif st.session_state.perfil_cliente == "beleza":
                    nomes_abas = ["📦 Apenas Serviços de Estética",
                                  "🎯 Marketplace Reverso (Ocorrências Gerais)"]
                elif st.session_state.perfil_cliente == "investidor":
                    nomes_abas = ["💼 Oportunidades de Novos Negócios"]
                elif st.session_state.perfil_cliente == "jornalista":
                    nomes_abas = ["🏛️ Infraestrutura Urbana",
                                  "💼 Oportunidades de Novos Negócios"]
                else:
                    nomes_abas = ["🏛️ Infraestrutura Urbana (Setor Público)"]

                abas_st = st.tabs(nomes_abas)
                for num_aba, nome_aba_ativa in enumerate(nomes_abas):
                    with abas_st[num_aba]:
                        frente_ativa = "Infra" if "Infraestrutura" in nome_aba_ativa else (
                            "Serviços" if "Novos Negócios" in nome_aba_ativa else "Varejo")
                        is_reverso_ativa = "Marketplace Reverso" in nome_aba_ativa
                        df_filtro_aba = df
                        if frente_ativa == "Infra":
                            df_filtro_aba = df[df['Categoria'] ==
                                               "Serviço Público / Infraestrutura"]
                        elif frente_ativa == "Serviços":
                            df_filtro_aba = df[df['Categoria'] ==
                                               "Serviço Local / Novo Estabelecimento"]
                        elif frente_ativa == "Varejo" and not is_reverso_ativa:
                            if st.session_state.perfil_cliente == "comerciante":
                                df_filtro_aba = df[(df['Categoria'] == "Produto / Marca") & (
                                    df['SubSegmento'].str.contains("Super", case=False))]
                            elif st.session_state.perfil_cliente == "saude":
                                df_filtro_aba = df[(df['Categoria'] == "Produto / Marca") & (
                                    df['SubSegmento'].str.contains("Saude|Saúde", case=False))]
                            elif st.session_state.perfil_cliente == "petshop":
                                df_filtro_aba = df[(df['Categoria'] == "Produto / Marca") & (
                                    df['SubSegmento'].str.contains("Pet", case=False))]
                            elif st.session_state.perfil_cliente == "beleza":
                                df_filtro_aba = df[(df['Categoria'] == "Produto / Marca") & (
                                    df['SubSegmento'].str.contains("Beleza", case=False))]
                        if termo_busca:
                            df_filtro_aba = df_filtro_aba[df_filtro_aba['O que Falta'].str.contains(
                                termo_busca, case=False) | df_filtro_aba['Local/Referência'].str.contains(termo_busca, case=False)]

                        if not df_filtro_aba.empty:
                            df_filtro_aba['É_Minha_Loja'] = df_filtro_aba['Local/Referência'].apply(
                                lambda x: 1 if x == loja_alvo_prioridade else 0)
                            if espectador_analitico:
                                st.download_button(label="Baixar Relatório de Vazios (PDF)", data=b"PDF_DUMMY",
                                                   file_name="expansao.pdf", mime="application/pdf", key=f"btn_pdf_{num_aba}")
                                st.markdown(
                                    f"<div style='text-align: right; font-size: 16px; font-weight: bold; color: #00803B; margin-top: 10px; margin-bottom: 20px;'>Total de Oportunidades: {len(df_filtro_aba)}</div>", unsafe_allow_html=True)
                                st.write("---")
                                df_agrupado_mestre = df_filtro_aba.groupby(["O que Falta", "Categoria"]).agg(Clientes_Unicos=("Pegada", "nunique"), Alertas_Totais=(
                                    "ID", "count"), Maior_Espera=("Dias", "max")).sort_values(by="Clientes_Unicos", ascending=False).reset_index()
                                for _, mestre_line in df_agrupado_mestre.iterrows():
                                    item_nome = mestre_line['O que Falta']
                                    clientes = int(
                                        mestre_line['Clientes_Unicos'])
                                    classe_tag = "tag-calor-alta" if clientes >= 5 else (
                                        "tag-calor-media" if clientes >= 2 else "tag-calor-baixa")
                                    label_tag = f"🔥 CRÍTICO • {clientes} CPFs" if clientes >= 5 else (
                                        f"⚠️ OPORTUNIDADE • {clientes} CPFs" if clientes >= 2 else f"🔹 INICIAL • {clientes} CPF")
                                    st.markdown(
                                        f'<div class="bloco-lista-premium"><span class="{classe_tag}">{label_tag}</span><b style="color: #FFFFFF; font-size: 16px;">🏢 Falta: {item_nome}</b><div style="margin-top: 0.5rem; color: #aaaaaa; font-size: 13px;">⏱️ Demanda de {mestre_line["Alertas_Totais"]} relatos • Maior espera: {mestre_line["Maior_Espera"]} dias</div></div>', unsafe_allow_html=True)
                                    detalhes_item = df_filtro_aba[df_filtro_aba['O que Falta'] == item_nome]
                                    st.write(
                                        "📍 **Localização e Detalhes das Ocorrências Coletadas:**")
                                    for _, sub_item in detalhes_item.iterrows():
                                        st.markdown(
                                            f"  * **{sub_item['Cidade']}** - *Ponto:* {sub_item['Local/Referência']}")
                                        if sub_item['Observação']:
                                            st.markdown(
                                                f"    * 💬 *Relato:* \"{sub_item['Observação']}\"")
                                    st.markdown(
                                        "<hr style='border-top: 1px dashed #333; margin: 1rem 0;'/>", unsafe_allow_html=True)
                            # --- MODELO B: INTERFACE OPERACIONAL COMERCIAL (LOJISTAS) ---
                            else:
                                st.download_button(label="Baixar Relatório (PDF)", data=b"PDF",
                                                   file_name="relatorio.pdf", mime="application/pdf", key=f"btn_pdf_op_{num_aba}")
                                total_sua_loja = len(
                                    df_filtro_aba[df_filtro_aba['Local/Referência'] == loja_alvo_prioridade]) if not is_reverso_ativa else 0
                                total_concorrencia = len(
                                    df_filtro_aba) - total_sua_loja
                                texto_contador = f"Sua Loja: {total_sua_loja} • Concorrência: {total_concorrencia} • Total Geral: {len(df_filtro_aba)}" if not is_reverso_ativa else f"Oportunidades de Captação: {len(df_filtro_aba)}"
                                st.markdown(
                                    f"<div style='text-align: right; font-size: 15px; font-weight: bold; color: #00803B; margin-top: 10px; margin-bottom: 20px;'>{texto_contador}</div>", unsafe_allow_html=True)
                                st.write("---")
                                df_agrupado_mestre = df_filtro_aba.groupby(["O que Falta", "Categoria"]).agg(Volume_Total=("ID", "count"), Menor_Idade=(
                                    "Dias", "min"), Foco_Dono=("É_Minha_Loja", "max")).sort_values(by=["Foco_Dono", "Volume_Total"], ascending=[False, False]).reset_index()
                                for _, linha in df_agrupado_mestre.iterrows():
                                    item_nome = linha['O que Falta']
                                    volume = float(linha['Volume_Total'])
                                    sou_alvo = int(linha['Foco_Dono'])
                                    classe_tag, label_tag = ("tag-calor-media", f"🎯 REVERSO • {int(volume)} Pedidos") if is_reverso_ativa else (
                                        ("tag-calor-alta", f"🎯 SEU MERCADO • {int(volume)} Pedidos") if sou_alvo == 1 else ("tag-calor-baixa", f"🌍 CONCORRÊNCIA • {int(volume)} Pedidos"))
                                    st.markdown(
                                        f'<div class="bloco-lista-premium"><span class="{classe_tag}">{label_tag}</span><b style="color: #FFFFFF; font-size: 16px;">📦 {item_nome}</b><div style="margin-top: 0.5rem; color: #aaaaaa; font-size: 13px;">⏱️ Alerta ativo há {linha["Menor_Idade"]} dias</div></div>', unsafe_allow_html=True)
                                    detalhes_item = df_filtro_aba[df_filtro_aba['O que Falta'] == item_nome]
                                    for _, sub_linha in detalhes_item.iterrows():
                                        sub_id = sub_linha['ID']
                                        sub_local = sub_linha['Local/Referência']
                                        contato_morador = sub_linha['Contato']
                                        is_dono_vazio = (
                                            sub_local == loja_alvo_prioridade) and not is_reverso_ativa
                                        st.markdown(
                                            f"{'🔥 **SEU ESTABELECIMENTO:** ' if is_dono_vazio else ('🎯 **REVERSO (Lead de Venda):** ' if is_reverso_ativa else '📍 **Captado no concorrente:** ')}{sub_local} ({sub_linha['Cidade']})")
                                        if sub_linha['Observação']:
                                            st.info(
                                                f"💬 *Relato:* \"{sub_linha['Observação']}\"")
                                        if contato_morador:
                                            st.success(
                                                f"📱 **Cliente Faminto!** WhatsApp: `{contato_morador}`")
                                        else:
                                            st.info(
                                                "ℹ️ Registro anônimo sem contato direto (Vazio comercial para expandir mix)")
                                        if not is_reverso_ativa and is_dono_vazio:
                                            id_confirmacao = f"confirma_baixa_{sub_id}"
                                            if id_confirmacao not in st.session_state:
                                                st.session_state[id_confirmacao] = False
                                            if not st.session_state[id_confirmacao]:
                                                if st.button(f"Dar baixa no {sub_local}", key=f"btn_pre_{sub_id}_{num_aba}"):
                                                    st.session_state[id_confirmacao] = True
                                                    st.rerun()
                                            else:
                                                st.warning(
                                                    "Confirmar reposição?")
                                                col_b1, col_b2 = st.columns(2)
                                                with col_b1:
                                                    if st.button("🚨 Confirmar", key=f"btn_real_{sub_id}_{num_aba}"):
                                                        supabase.table("relatos_escassez").update(
                                                            {"status": "Atendido"}).eq("id", sub_id).execute()
                                                        st.success(
                                                            "🎉 Concluído!")
                                                        import time
                                                        time.sleep(1)
                                                        st.session_state[id_confirmacao] = False
                                                        st.session_state.busca_ativa = False
                                                        st.rerun()
                                                with col_b2:
                                                    if st.button("❌ Cancelar", key=f"btn_cancelar_{sub_id}_{num_aba}"):
                                                        st.session_state[id_confirmacao] = False
                                                        st.rerun()
                                    st.markdown(
                                        "<hr style='border-top: 1px dashed #333; margin: 1rem 0;'/>", unsafe_allow_html=True)
                        else:
                            st.info(
                                "ℹ️ Nenhum registro ativo encontrado para esta aba.")
