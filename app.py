import streamlit as st
import os
import pandas as pd
import datetime
import hashlib
import io
import urllib.parse
from fpdf import FPDF
from dotenv import load_dotenv
from supabase import create_client, Client

# --- VARIÁVEIS UNIVERSAIS PRIVADAS ---
botao_enviar = False
termo_busca = ""
loja_alvo_prioridade = "Mercadinho Do Bairro"

# --- CONEXÃO INTELIGENTE COM O SUPABASE ---
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


def obter_pegada_digital():
    try:
        headers = st.context.headers
        ip = headers.get("X-Forwarded-For", "127.0.0.1").split(",")[0].strip()
        agente = headers.get("User-Agent", "Desconhecido")
        return hashlib.sha256(f"{ip}-{agente}".encode('utf-8')).hexdigest()
    except:
        return "pegada_generica_fallback"


# --- CUSTOMIZAÇÃO ESTÉTICA PREMIUM (CSS COESIVO) ---
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
    h1 { font-size: 34px !important; font-weight: 900 !important; text-align: center !important; margin-bottom: 0px !important; }
    [data-testid="stHorizontalBlock"]:has(button[key*="simetrico"]) { gap: 10px !important; flex-direction: row !important; flex-wrap: nowrap !important; }
    .stTextInput input, .stTextArea textarea, div[data-baseweb="textarea"] textarea, div[data-baseweb="input"] input { background-color: #1E1E1E !important; color: #FFFFFF !important; border-radius: 10px !important; border: 1px solid #444444 !important; }
    input::placeholder, textarea::placeholder { color: #888888 !important; font-style: italic !important; }
    .bloco-lista-premium { background-color: #1E1E1E !important; padding: 1.2rem !important; border-radius: 10px !important; margin-bottom: 0.8rem !important; border: 1px solid #333333 !important; }
    .tag-calor-alta { background-color: #ff3333 !important; color: white !important; padding: 0.2rem 0.6rem !important; border-radius: 6px !important; font-weight: bold !important; font-size: 12px !important; float: right !important; }
    .tag-calor-media { background-color: #ff9933 !important; color: black !important; padding: 0.2rem 0.6rem !important; border-radius: 6px !important; font-weight: bold !important; font-size: 12px !important; float: right !important; }
    .tag-calor-baixa { background-color: #3399ff !important; color: white !important; padding: 0.2rem 0.6rem !important; border-radius: 6px !important; font-weight: bold !important; font-size: 12px !important; float: right !important; }
    [data-testid="stForm"] { border: none !important; padding: 0px !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- SESSÕES INICIAIS ---
if "seguranca_master" not in st.session_state:
    st.session_state.seguranca_master = False
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
if "regiao_cliente" not in st.session_state:
    st.session_state.regiao_cliente = "São Paulo/SP"

# --- 🔐 CORTINA DE FUMAÇA: MANUTENÇÃO ---
if not st.session_state.seguranca_master:
    st.markdown("<h3 style='text-align: center; color: #ff3333; margin-top: 50px;'>⚠️ Sistema em Manutenção</h3>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 14px; color: #aaaaaa;'>Ambiente restrito à equipe de homologação interna.</p>", unsafe_allow_html=True)
    st.write("---")
    with st.form(key="form_protecao_patente", clear_on_submit=False):
        senha_desenvolvimento = st.text_input(
            label="Chave de Engenharia:", type="password", placeholder="Insira a credencial...")
        botao_destravar_lab = st.form_submit_button(
            "Acessar Ambiente de Testes", use_container_width=True)
    if botao_destravar_lab:
        if senha_desenvolvimento.strip() == "carencias2026":
            st.session_state.seguranca_master = True
            st.rerun()
        else:
            st.error("❌ Credencial de engenharia incorreta.")
    st.stop()
# --- TELA: HOME ---
if st.session_state.tela_atual == "home":
    st.markdown("<h1 style='text-align: center; font-weight: 900; margin-bottom: 0px;'>🔍 E o que falta?</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; font-style: italic; color: #aaaaaa; margin-top: 5px; margin-bottom: 25px;'>O termômetro de carências da nossa região.</p>", unsafe_allow_html=True)
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

# --- TELA: CONSUMIDOR ---
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

    st.markdown("<h1 style='text-align: center; font-weight: 900; margin-bottom: 0px;'>🔍 E o que falta?</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; font-style: italic; color: #aaaaaa; margin-top: 5px; margin-bottom: 25px;'>O termômetro de carências da nossa região.</p>", unsafe_allow_html=True)

    if st.session_state.aba_consumidor == "menu_triagem":
        st.markdown("##### 📍 Região/Cidade da falta:")
        regiao_final = st.text_input(label="Localizacao", placeholder="Ex: São Paulo/SP - Centro",
                                     key="input_regiao_via_unica", label_visibility="collapsed")
        st.write("Escolha o tipo de ausência que você quer sinalizar:")
        if st.button("📦 PRODUTO OU MARCA EM FALTA", use_container_width=True, key="triagem_prod"):
            st.session_state.aba_consumidor = "produto"
            st.rerun()
        if st.button("🏪 NOVO COMÉRCIO OU SERVIÇO LOCAL", use_container_width=True, key="triagem_serv"):
            st.session_state.aba_consumidor = "servico"
            st.rerun()
        if st.button("🏛️ INFRAESTRUTURA OU ZELADORIA PÚBLICA", use_container_width=True, key="triagem_infra"):
            st.session_state.aba_consumidor = "infra"
            st.rerun()

        st.write("")
        st.markdown("### 🏆 Impactos Recentes no Bairro")
        try:
            resolvidos = supabase.table("relatos_escassez").select("item_solicitado, sub_segmento, locais_destino(nome_exibicao, regiao_cidade)").eq(
                "status", "Atendido").order("data_registro", desc=True).limit(20).execute()
            if resolvidos.data and len(resolvidos.data) > 0:
                lista_impactos = []
                for item in resolvidos.data:
                    if item.get("locais_destino"):
                        item_limpo_vitrine = str(item["item_solicitado"]).rstrip(
                            " 0123456789").strip().title()
                        lista_impactos.append({"item": item_limpo_vitrine, "nicho": item.get("sub_segmento", "Geral").strip(
                        ), "local": item["locais_destino"]["nome_exibicao"].strip().title(), "cidade_exibicao": item["locais_destino"]["regiao_cidade"].strip()})
                df_impactos = pd.DataFrame(lista_impactos).drop_duplicates(
                    subset=["local"]).drop_duplicates(subset=["nicho"])

                contador_exibidos = 0
                for _, linha_imp in df_impactos.iterrows():
                    if contador_exibidos >= 3:
                        break
                    if linha_imp['nicho'] == "Supermercado":
                        icone, acao = "🛒 Varejo Alimentar:", "repos o estoque de"
                    elif linha_imp['nicho'] in ["Saude", "Saúde"]:
                        icone, acao = "🩺 Saúde e Bem-Estar:", "trouxe o servico de"
                    elif linha_imp['nicho'] == "Petshop":
                        icone, acao = "🐶 Setor Animal/Pet:", "disponibilizou o item"
                    elif linha_imp['nicho'] == "Beleza":
                        icone, acao = "💈 Beleza e Estética:", "ativou o atendimento de"
                    else:
                        icone, acao = "✨ Conquista Local:", "disponibilizou"

                    st.markdown(
                        f"<div style='background-color: #1A1A1A; padding: 0.6rem 1rem; border-radius: 8px; border-left: 4px solid #00803B; margin-bottom: 8px;'><span style='font-size: 13px; color: #aaaaaa; font-weight: 500;'><b>{icone}</b> {linha_imp['local']} {acao} <b>{linha_imp['item']}</b>!</span></div>", unsafe_allow_html=True)
                    contador_exibidos += 1
            else:
                st.write("ℹ️ Nenhuma benfeitoria recente registrada.")
        except:
            pass
    elif st.session_state.aba_consumidor in ["produto", "servico", "infra"]:
        if st.session_state.aba_consumidor == "produto":
            label_item, placeholder_item = "Qual produto ou marca falta?", "Ex: Leite condensado marca X..."
            label_local, placeholder_local = "Em qual estabelecimento?", "Ex: Nome do mercado..."
            label_contato, tipo_envio = "Quer ser avisado na reposição? (Opcional)", "Produto / Marca"
        elif st.session_state.aba_consumidor == "servico":
            label_item, placeholder_item = "Qual comércio falta no bairro?", "Ex: Sapataria, lavanderia..."
            label_local, placeholder_local = "Em qual rua ou ponto?", "Ex: Avenida Principal..."
            label_contato, tipo_envio = "Quer ser avisado na abertura? (Opcional)", "Serviço Local / Novo Estabelecimento"
        elif st.session_state.aba_consumidor == "infra":
            label_item, placeholder_item = "Qual problema de infraestrutura público?", "Ex: Falha na iluminação..."
            label_local, placeholder_local = "Qual o ponto de referência?", "Ex: Posto de saúde do bairro Y..."
            label_contato, tipo_envio = "Quer ser avisado na conclusão? (Opcional)", "Serviço Público / Infraestrutura"

        st.write("")
        with st.form(key="formulario_dinamico_consumidor", clear_on_submit=False):
            item_solicitado = st.text_input(
                label=label_item, placeholder=placeholder_item, key="input_item")
            local_ocorrencia = st.text_input(
                label=label_local, placeholder=placeholder_local, key="input_local")
            contato_usuario = st.text_input(
                label=label_contato, placeholder="Ex: Seu e-mail ou WhatsApp...", key="input_contato")
            observacao_usuario = None
            with st.expander("➕ Adicionar mais detalhes e observações (Opcional)"):
                observacao_usuario = st.text_area(
                    label="Detalhes adicionais:", placeholder="Ex: Detalhe o ocorrido aqui...", key="input_obs")
            botao_enviar = st.form_submit_button(
                "🔍 SINALIZAR ESTA FALTA", use_container_width=True)

        if botao_enviar and item_solicitado and local_ocorrencia:
            try:
                hash_dispositivo = obter_pegada_digital()
                regiao_salva = st.session_state.get(
                    "input_regiao_via_unica", "São Paulo/SP - Centro")
                texto_regiao = regiao_salva.strip() if regiao_salva else "São Paulo/SP - Centro"
                local_formatado = local_ocorrencia.strip().title()
                local_data = supabase.table("locais_destino").insert(
                    {"nome_exibicao": local_formatado, "regiao_cidade": texto_regiao, "regiao_estado": "SP"}).execute()
                local_id = local_data.data[0]["id"] if (
                    local_data and local_data.data and len(local_data.data) > 0) else None

                if local_id:
                    segmento_detectado = "Geral"
                    texto_usuario = item_solicitado.strip().lower()
                    if any(p in texto_usuario for p in ["leite", "arroz", "feijão", "café", "açúcar", "pão", "mercado", "óleo"]):
                        segmento_detectado = "Supermercado"
                    elif any(p in texto_usuario for p in ["remédio", "médico", "dentista", "farmácia", "clínica"]):
                        segmento_detectado = "Saúde"
                    elif any(p in texto_usuario for p in ["ração", "pet", "cachorro", "gato", "petshop"]):
                        segmento_detectado = "Petshop"
                    elif any(p in texto_usuario for p in ["manicure", "salão", "cabeleireiro", "estética"]):
                        segmento_detectado = "Beleza"

                    texto_obs = observacao_usuario.strip() if observacao_usuario else None
                    supabase.table("relatos_escassez").insert({"local_id": local_id, "item_solicitado": item_solicitado.strip().title(), "tipo_carencia": tipo_envio, "status": "Pendente",
                                                               "sub_segmento": segmento_detectado, "pegada_digital": hash_dispositivo, "observacao_detalhe": texto_obs, "contato_aviso": contato_usuario.strip() if contato_usuario else None}).execute()
                    st.success("✅ Falta sinalizada com sucesso!")
                    import time
                    time.sleep(1.2)
                    st.session_state.aba_consumidor = "menu_triagem"
                    st.session_state.tela_atual = "home"
                    st.rerun()
            except Exception as e:
                st.error(f"⚠️ Erro técnico de persistência: {str(e)}")

# --- TELA: AUTENTICAÇÃO CORPORATIVA ---
elif st.session_state.tela_atual == "autenticacao":
    if st.button("⬅️ Voltar ao Menu Principal", key="btn_voltar_aut"):
        st.session_state.tela_atual = "home"
        st.session_state.token_valido = False
        st.rerun()
    st.markdown("<h1 style='text-align: center; font-weight: 900; margin-bottom: 0px;'>🔍 E o que falta?</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; font-style: italic; color: #aaaaaa; margin-top: 5px; margin-bottom: 25px;'>O termômetro de carências da nossa região.</p>", unsafe_allow_html=True)
    st.write("---")
    with st.form(key="form_autenticacao_b2b", clear_on_submit=False):
        token_inserido = st.text_input(
            label="Token de Acesso:", type="password", placeholder="Digite seu token de acesso...")
        botao_validar = st.form_submit_button(
            "Validar Credenciais e Acessar", use_container_width=True)

    if botao_validar and token_inserido:
        token_limpo = token_inserido.strip()
        if token_limpo == "COMERCIO10":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "comerciante"
            st.session_state.regiao_cliente = "São Paulo/SP"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_limpo == "SAUDE20":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "saude"
            st.session_state.regiao_cliente = "São Paulo/SP"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_limpo == "PET30":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "petshop"
            st.session_state.regiao_cliente = "São Paulo/SP"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_limpo == "BELEZA40":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "beleza"
            st.session_state.regiao_cliente = "São Paulo/SP"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_limpo == "INVEST20":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "investidor"
            st.session_state.regiao_cliente = "São Paulo/SP"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_limpo == "GESTOR30":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "gestor"
            st.session_state.regiao_cliente = "São Paulo/SP"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_limpo == "MIDIA40":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "jornalista"
            st.session_state.regiao_cliente = "São Paulo/SP"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_limpo == "ADMIN99":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "admin"
            st.session_state.regiao_cliente = "São Paulo/SP"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_limpo != "":
            try:
                busca_db = supabase.table("clientes_b2b").select(
                    "*").eq("token_acesso", token_limpo).execute()
                if busca_db and busca_db.data and len(busca_db.data) > 0:
                    dados_linha = busca_db.data[0]
                    if dados_linha.get("status_pagamento") == "Cancelado":
                        st.error("❌ Token suspenso administrativamente.")
                    else:
                        st.session_state.perfil_cliente = dados_linha.get(
                            "perfil_segmento", "comerciante")
                        st.session_state.regiao_cliente = dados_linha.get(
                            "regiao_atuacao", "São Paulo/SP")
                        st.session_state.recursos_liberados = {"reverso": dados_linha.get("recurso_marketplace_reverso", True), "whatsapp": dados_linha.get(
                            "recurso_whatsapp", True), "pdf": dados_linha.get("recurso_pdf", True)}
                        st.session_state.token_valido = True
                        st.session_state.tela_atual = "comerciante"
                        st.rerun()
                else:
                    st.error("❌ Token inválido.")
            except:
                st.error("❌ Erro de autenticidade na base.")
# --- TELA: PAINEL ESTRATÉGICO B2B ---
elif st.session_state.tela_atual == "comerciante":
    if not st.session_state.token_valido:
        st.session_state.tela_atual = "home"
        st.rerun()
    if st.button("⬅️ Sair do Painel (Logoff)", key="btn_voltar_com"):
        st.session_state.tela_atual = "home"
        st.session_state.token_valido = False
        st.session_state.perfil_cliente = None
        st.session_state.busca_ativa = False
        st.session_state.dados_grafico = None
        st.rerun()

    st.markdown("<h1 style='text-align: center; font-weight: 900; margin-bottom: 0px;'>🔍 E o que falta?</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; font-style: italic; color: #aaaaaa; margin-top: 5px; margin-bottom: 25px;'>O termômetro de carências da nossa região.</p>", unsafe_allow_html=True)
    espectador_analitico = st.session_state.perfil_cliente in [
        "investidor", "gestor", "jornalista"]
    st.write("---")
    termo_busca = st.text_input(label="Refinar por palavra-chave ou estabelecimento (Opcional):",
                                placeholder="Digite para filtrar a lista abaixo...", key="input_busca_painel")

    if st.session_state.perfil_cliente == "admin":
        st.markdown(
            "<h3 style='text-align: center;'>🛠️ Cadastro de Assinantes (ERP)</h3>", unsafe_allow_html=True)
        with st.form(key="form_admin_mestre_cad", clear_on_submit=True):
            nome_novo_comercio = st.text_input(
                "Nome do Estabelecimento Comercial:", placeholder="Ex: Supermercado Xavier...")
            perfil_novo_comercio = st.selectbox("Perfil de Acesso Corporativo:", [
                                                "comerciante", "saude", "petshop", "beleza", "investidor", "gestor", "jornalista"])
            regiao_novo_comercio = st.text_input(
                "Região/Cidade de Atuação:", placeholder="Ex: São Paulo/SP - Centro...")
            if st.form_submit_button("💼 Cadastrar Lojista e Gerar Credenciais"):
                if nome_novo_comercio and regiao_novo_comercio:
                    try:
                        novo_registro = supabase.table("clientes_b2b").insert({"nome_estabelecimento": nome_novo_comercio.strip().title(), "perfil_segmento": perfil_novo_comercio, "regiao_atuacao": regiao_novo_comercio.strip(
                        ), "status_pagamento": "Ativo", "recurso_marketplace_reverso": True, "recurso_whatsapp": True, "recurso_pdf": True}).execute()
                        if novo_registro.data:
                            st.success("🎉 Cadastrado!")
                            st.info(
                                f"🔑 Token: `{novo_registro.data['token_acesso']}`")
                    except Exception as err:
                        st.error(f"Erro: {str(err)}")

        st.markdown(
            "<h3 style='text-align: center;'>📊 Central de Recursos e Controle Financeiro</h3>", unsafe_allow_html=True)
        try:
            resposta_clientes = supabase.table("clientes_b2b").select(
                "*").order("created_at", desc=True).execute()
            if resposta_clientes.data:
                for cli in resposta_clientes.data:
                    c_id = cli["id"]
                    with st.expander(f"🏢 {cli['nome_estabelecimento']} ({cli['regiao_atuacao']})"):
                        st.text_input("🔑 Token de Acesso Completo (Selecione e Copie):",
                                      value=cli['token_acesso'], disabled=True, key=f"tk_full_{c_id}")
                        col_status, col_plan = st.columns(2)
                        with col_status:
                            status_pag = st.selectbox("Status de Pagamento:", ["Ativo", "Inadimplente", "Cancelado"], index=[
                                                      "Ativo", "Inadimplente", "Cancelado"].index(cli.get("status_pagamento", "Ativo")), key=f"pay_{c_id}")
                        with col_plan:
                            plano_cont = st.selectbox("Plano Contratado:", ["Bronze", "Prata", "Ouro"], index=[
                                                      "Bronze", "Prata", "Ouro"].index(cli.get("plano_contratado", "Ouro")), key=f"plan_{c_id}")
                        c_reverso = st.checkbox("Acesso ao Marketplace Reverso", value=cli.get(
                            "recurso_marketplace_reverso", True), key=f"rev_{c_id}")
                        c_whatsapp = st.checkbox("Botão de Captação WhatsApp LGPD", value=cli.get(
                            "recurso_whatsapp", True), key=f"wa_{c_id}")
                        c_pdf = st.checkbox("Emissão e Download de Relatórios PDF", value=cli.get(
                            "recurso_pdf", True), key=f"pdf_ch_{c_id}")
                        if st.button("💾 Salvar Alterações e Atualizar Travas", key=f"save_{c_id}"):
                            supabase.table("clientes_b2b").update({"status_pagamento": status_pag, "plano_contratado": plano_cont,
                                                                   "recurso_marketplace_reverso": c_reverso, "recurso_whatsapp": c_whatsapp, "recurso_pdf": c_pdf}).eq("id", c_id).execute()
                            st.success("🔒 Sincronizado!")
                            import time
                            time.sleep(0.5)
                            st.rerun()
        except:
            pass

        st.markdown(
            "<h3 style='text-align: center;'>📥 Sugestões de Novos Nichos Coletados (Cenário B)</h3>", unsafe_allow_html=True)
        try:
            sugestoes_brutas = supabase.table("relatos_escassez").select(
                "id, item_solicitado, sub_segmento").eq("sub_segmento", "Geral").limit(5).execute()
            if sugestoes_brutas.data:
                for sug in sugestoes_brutas.data:
                    id_sug = sug["id"]
                    with st.expander(f"📥 Termo Coletado: \"{sug['item_solicitado']}\""):
                        nicho_homologado = st.selectbox("Vincular ao Segmento Oficial:", [
                                                        "Supermercado", "Saúde", "Petshop", "Beleza"], key=f"sel_nicho_{id_sug}")
                        nome_corrigido = st.text_input(
                            "Corrigir nome / Padronizar termo:", value=sug['item_solicitado'], key=f"txt_nome_{id_sug}")
                        if st.button("✅ Homologar e Ativar no Mercado", key=f"btn_homologar_{id_sug}"):
                            supabase.table("relatos_escassez").update({"item_solicitado": nome_corrigido.strip(
                            ).title(), "sub_segmento": nicho_homologado}).eq("id", id_sug).execute()
                            st.success("🎉 Homologado!")
                            import time
                            time.sleep(0.5)
                            st.rerun()
        except:
            pass
    else:
        try:
            resposta_bruta = supabase.table("relatos_escassez").select(
                "id, item_solicitado, tipo_carencia, data_registro, status, "
                "observacao_detalhe, sub_segmento, pegada_digital, contato_aviso, "
                "locais_destino(nome_exibicao, regiao_cidade)"
            ).execute()
            cidades_detectadas, bairros_por_cidade, dados_brutos_limpos = set(), {}, []
            agora = datetime.datetime.now(datetime.timezone.utc)
            if resposta_bruta.data:
                for reg in resposta_bruta.data:
                    if reg.get("locais_destino"):
                        loc_completo = str(
                            reg["locais_destino"]["regiao_cidade"]).strip()
                        if " - " in loc_completo:
                            cidade_raiz, bairro_raiz = loc_completo.split(
                                " - ", 1)
                            cidade_raiz, bairro_raiz = cidade_raiz.strip(), bairro_raiz.strip()
                        else:
                            cidade_raiz, bairro_raiz = loc_completo, "Geral"
                        cidades_detectadas.add(cidade_raiz)
                        if cidade_raiz not in bairros_por_cidade:
                            bairros_por_cidade[cidade_raiz] = set()
                        bairros_por_cidade[cidade_raiz].add(bairro_raiz)
                        sub_seg = str(reg.get("sub_segmento", "Geral")).strip()
                        cat_bruta = str(
                            reg.get("tipo_carencia", "Produto / Marca")).strip()
                        idade_dias = max(0, (agora - datetime.datetime.fromisoformat(reg.get(
                            "data_registro").replace("Z", "+00:00"))).days) if reg.get("data_registro") else 0
                        categoria_limpa = "Serviço Público / Infraestrutura" if ("Público" in cat_bruta or "Publico" in cat_bruta or "Infra" in cat_bruta or "Zeladoria" in sub_seg) else (
                            "Serviço Local / Novo Estabelecimento" if ("Local" in cat_bruta or "Invest" in sub_seg) else "Produto / Marca")
                        item_limpo_sem_num = str(reg["item_solicitado"]).rstrip(
                            " 0123456789").strip().title()
                        nome_local_bruto = reg["locais_destino"]["nome_exibicao"]
                        if st.session_state.perfil_cliente in ["comerciante", "saude", "petshop", "beleza"] and nome_local_bruto != loja_alvo_prioridade:
                            if sub_seg == "Supermercado":
                                nome_local_exibicao = "Mercado Concorrente da Região"
                            elif sub_seg in ["Saude", "Saúde"]:
                                nome_local_exibicao = "Estabelecimento de Saúde Concorrente"
                            elif sub_seg == "Petshop":
                                nome_local_exibicao = "Petshop Concorrente da Região"
                            elif sub_seg == "Beleza":
                                nome_local_exibicao = "Salão / Clínica de Estética Concorrente"
                            else:
                                nome_local_exibicao = "Estabelecimento Comercial Parceiro"
                        else:
                            nome_local_exibicao = nome_local_bruto
                        dados_brutos_limpos.append({"ID": reg["id"], "O que Falta": item_limpo_sem_num, "Categoria": categoria_limpa, "Local/Referência": nome_local_exibicao, "CidadeRaiz": cidade_raiz, "Bairro": bairro_raiz, "CidadeCompleta": loc_completo,
                                                   "Dias": idade_dias, "Observação": reg.get("observacao_detalhe") or "Sem detalhes.", "SubSegmento": sub_seg, "Pegada": reg.get("pegada_digital") or f"anon_{reg['id']}", "Contato": reg.get("contato_aviso") or ""})

            lista_cidades_filtro = [
                "[ Mostrar Todas as Cidades ]"] + sorted(list(cidades_detectadas))
            cidade_selecionada = st.selectbox(
                "📍 1. Selecionar Cidade (Global):", options=lista_cidades_filtro, key="b2b_cidade_auto")
            if cidade_selecionada == "[ Mostrar Todas as Cidades ]":
                bairro_selecionado = st.selectbox("🏘️ 2. Refinar por Bairro Específico:", options=[
                                                  "--- Selecione uma Cidade Primeiro ---"], disabled=True, key="b2b_bairro_auto")
            else:
                bairro_selecionado = st.selectbox("🏘️ 2. Refinar por Bairro Específico:", options=[
                                                  " Mostrar Todos os Bairros "] + sorted(list(bairros_por_cidade.get(cidade_selecionada, set()))), key="b2b_bairro_auto")

            df_total = pd.DataFrame(dados_brutos_limpos) if dados_brutos_limpos else pd.DataFrame(columns=[
                "ID", "O que Falta", "Categoria", "Local/Referência", "CidadeRaiz", "Bairro", "CidadeCompleta", "Dias", "Observação", "SubSegmento", "Pegada", "Contato"])
            if not df_total.empty:
                df_filtrado = df_total
                if cidade_selecionada != "[ Mostrar Todas as Cidades ]":
                    df_filtrado = df_filtrado[df_filtrado['CidadeRaiz']
                                              == cidade_selecionada]
                    if bairro_selecionado != " Mostrar Todos os Bairros ":
                        df_filtrado = df_filtrado[df_filtrado['Bairro']
                                                  == bairro_selecionado]
                st.session_state.dados_grafico = df_filtrado
            else:
                st.session_state.dados_grafico = df_total
        except Exception as e:
            st.error(f"⚠️ Erro de performance: {str(e)}")
        if st.session_state.dados_grafico is not None:
            df = st.session_state.dados_grafico
            if not df.empty:
                p_cli = st.session_state.perfil_cliente
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
                    n_abas = ["🏛️ Infraestrutura (Pública)"]

                abas_st = st.tabs(n_abas)
                for num_aba, n_aba_atv in enumerate(n_abas):
                    with abas_st[num_aba]:
                        fr_atv = "Infra" if "Infra" in n_aba_atv else (
                            "Serviços" if "Negócios" in n_aba_atv else "Varejo")
                        is_rev = "Reverso" in n_aba_atv
                        if is_rev and not st.session_state.get("recursos_liberados", {}).get("reverso", True):
                            st.warning(
                                "🔒 Visualização suspensa administrativamente.")
                            continue
                        df_f_aba = df
                        if fr_atv == "Infra":
                            df_f_aba = df[df['Categoria'] ==
                                          "Serviço Público / Infraestrutura"]
                        elif fr_atv == "Serviços":
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
                            df_f_aba = df_f_aba[df_f_aba['O que Falta'].str.contains(
                                termo_busca, case=False) | df_f_aba['Local/Referência'].str.contains(termo_busca, case=False)]
                        if not df_f_aba.empty:
                            df_f_aba['É_Minha_Loja'] = df_f_aba['Local/Referência'].apply(
                                lambda x: 1 if x == loja_alvo_prioridade else 0)
                            pode_pdf = st.session_state.get(
                                "recursos_liberados", {}).get("pdf", True)

                            if espectador_analitico:
                                try:
                                    p_r = FPDF()
                                    p_r.add_page()
                                    p_r.set_font("Arial", size=12)
                                    p_r.cell(
                                        200, 10, txt="Relatorio de Vazios Comerciais Regional", ln=1, align="C")
                                    for _, r in df_f_aba.iterrows():
                                        p_r.cell(190, 10, txt=f"- Falta: {r['O que Falta']} | Ponto: {r['Local/Referência']}".encode(
                                            'latin-1', 'ignore').decode('latin-1'), ln=1)
                                    st.download_button(label="Baixar Relatório de Vazios (PDF)", data=bytes(p_r.output(
                                        dest='S')), file_name="expansao.pdf", mime="application/pdf", key=f"btn_pdf_{num_aba}")
                                except:
                                    pass
                                st.markdown(
                                    f"<div style='text-align: right; font-size: 16px; font-weight: bold; color: #00803B; margin-top: 10px; margin-bottom: 20px;'>Total de Oportunidades: {len(df_f_aba)}</div>", unsafe_allow_html=True)
                                df_agr = df_f_aba.groupby(["O que Falta", "Categoria"]).agg(C_Unicos=("Pegada", "nunique"), A_Totais=(
                                    "ID", "count"), M_Espera=("Dias", "max")).sort_values(by="C_Unicos", ascending=False).reset_index()
                                for _, m_line in df_agr.iterrows():
                                    i_nome = m_line['O que Falta']
                                    clis = int(m_line['C_Unicos'])
                                    c_tag = "tag-calor-alta" if clis >= 5 else (
                                        "tag-calor-media" if clis >= 2 else "tag-calor-baixa")
                                    st.markdown(
                                        f'<div class="bloco-lista-premium"><span class="{c_tag}">🔥 CRÍTICO • {clis} CPFs</span><b style="color: #FFFFFF; font-size: 16px;">🏢 Falta: {i_nome}</b><div style="margin-top: 0.5rem; color: #aaaaaa; font-size: 13px;">⏱️ {m_line["A_Totais"]} relatos • Espera: {m_line["M_Espera"]} dias</div></div>', unsafe_allow_html=True)
                                    for _, s_it in df_f_aba[df_f_aba['O que Falta'] == i_nome].drop_duplicates(subset=["CidadeCompleta", "Local/Referência", "Observação"]).iterrows():
                                        st.markdown(
                                            f"  * **{s_it['CidadeCompleta']}** - *Ponto:* {s_it['Local/Referência']}")
                                        if s_it['Observação']:
                                            st.markdown(
                                                f"    * 💬 *Relato:* \"{s_it['Observação']}\"")
                            else:
                                if pode_pdf:
                                    try:
                                        p_o = FPDF()
                                        p_op = p_o
                                        p_op.add_page()
                                        p_op.set_font("Arial", size=12)
                                        p_o.cell(
                                            200, 10, txt="Relatorio Operacional de Demandas", ln=1, align="C")
                                        for _, r in df_f_aba.iterrows():
                                            p_o.cell(190, 10, txt=f"- Falta: {r['O que Falta']} | Ponto: {r['Local/Referência']}".encode(
                                                'latin-1', 'ignore').decode('latin-1'), ln=1)
                                        st.download_button(label="Baixar Relatório (PDF)", data=bytes(p_o.output(
                                            dest='S')), file_name="relatorio.pdf", mime="application/pdf", key=f"btn_pdf_op_{num_aba}")
                                    except:
                                        pass
                                total_sua_loja = len(
                                    df_f_aba[df_f_aba['Local/Referência'] == loja_alvo_prioridade]) if not is_rev else 0
                                st.markdown(
                                    f"<div style='text-align: right; font-size: 15px; font-weight: bold; color: #00803B; margin-top: 10px; margin-bottom: 20px;'>Sua Loja: {total_sua_loja} • Concorrência: {len(df_f_aba) - total_sua_loja} • Total Geral: {len(df_f_aba)}</div>", unsafe_allow_html=True)
                                df_agr = df_f_aba.groupby(["O que Falta", "Categoria"]).agg(V_Total=("ID", "count"), M_Idade=("Dias", "min"), F_Dono=(
                                    "É_Minha_Loja", "max")).sort_values(by=["Foco_Dono", "V_Total"], ascending=[False, False]).reset_index()
                                for _, linha in df_agr.iterrows():
                                    i_nome = linha['O que Falta']
                                    s_alvo = int(
                                        linha['Fono' if 'Fono' in linha else 'Foco_Dono'])
                                    c_tag = "tag-calor-alta" if (
                                        s_alvo == 1 and not is_rev) else "tag-calor-baixa"
                                    l_tag = "🎯 SEU MERCADO" if (
                                        s_alvo == 1 and not is_rev) else "🌍 CONCORRÊNCIA"
                                    st.markdown(
                                        f'<div class="bloco-lista-premium"><span class="{c_tag}">{l_tag} • {int(linha["V_Total"])} Pedidos</span><b style="color: #FFFFFF; font-size: 16px;">📦 {i_nome}</b><div style="margin-top: 0.5rem; color: #aaaaaa; font-size: 13px;">⏱️ Alerta ativo há {linha["M_Idade"]} dias</div></div>', unsafe_allow_html=True)
                                    for _, s_l in df_f_aba[df_f_aba['O que Falta'] == i_nome].drop_duplicates(subset=["CidadeCompleta", "Local/Referência", "Observação", "Contato"]).iterrows():
                                        sub_id, sub_local, c_morador = s_l['ID'], s_l[
                                            'Local/Referência'], s_l['Contato']
                                        is_dono_vazio = (
                                            sub_local == loja_alvo_prioridade) and not is_rev
                                        st.markdown(
                                            f"{'🔥 **SEU ESTABELECIMENTO:** ' if is_dono_vazio else '📍 **Captado no concorrente:** '}{sub_local} ({s_l['CidadeCompleta']})")
                                        if s_l['Observação']:
                                            st.info(
                                                f"💬 *Relato:* \"{s_l['Observação']}\"")
                                        pode_wa = st.session_state.get(
                                            "recursos_liberados", {}).get("whatsapp", True)
                                        if c_morador and pode_wa:
                                            st.markdown(f'<a href="https://whatsapp.com{c_morador.strip()}&text=Olá! Temos {i_nome} disponível!" target="_blank"><button style="background-color: #25D366 !important; color: white !important; font-weight: bold !important; border: none !important; padding: 0.5rem 1rem !important; border-radius: 8px !important; width: auto !important; margin-bottom: 10px; font-size: 14px; cursor: pointer;">📱 Falar no WhatsApp</button></a>', unsafe_allow_html=True)
                                        elif c_morador and not pode_wa:
                                            st.warning("🔒 WhatsApp Bloqueado.")
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
