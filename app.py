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

botao_enviar = False
termo_busca = ""
loja_alvo_prioridade = "Mercadinho Do Bairro"

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
        ip = headers.get("X-Forwarded-For", "127.0.0.1").split(",").strip()
        agente = headers.get("User-Agent", "Desconhecido")
        return hashlib.sha256(f"{ip}-{agente}".encode('utf-8')).hexdigest()
    except:
        return "pegada_generica_fallback"


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
    .stTextInput input, .stTextArea textarea, div[data-baseweb="input"] input { background-color: #1E1E1E !important; color: #FFFFFF !important; border-radius: 10px !important; border: 1px solid #444444 !important; }
    .bloco-lista-premium { background-color: #1E1E1E !important; padding: 1.2rem !important; border-radius: 10px !important; margin-bottom: 0.8rem !important; border: 1px solid #333333 !important; }
    .tag-calor-alta { background-color: #ff3333 !important; color: white !important; padding: 0.2rem 0.6rem !important; border-radius: 6px !important; font-weight: bold !important; font-size: 12px !important; float: right !important; }
    .tag-calor-media { background-color: #ff9933 !important; color: black !important; padding: 0.2rem 0.6rem !important; border-radius: 6px !important; font-weight: bold !important; font-size: 12px !important; float: right !important; }
    .tag-calor-baixa { background-color: #3399ff !important; color: white !important; padding: 0.2rem 0.6rem !important; border-radius: 6px !important; font-weight: bold !important; font-size: 12px !important; float: right !important; }
    [data-testid="stForm"] { border: none !important; padding: 0px !important; }
    </style>
""", unsafe_allow_html=True)

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

if not st.session_state.seguranca_master:
    st.markdown("<h3 style='text-align: center; color: #aaaaaa;'>🔍 Sistema em Manutenção</h3>",
                unsafe_allow_html=True)
    with st.form(key="form_protecao", clear_on_submit=False):
        senha_desenvolvimento = st.text_input(
            label="Chave de Homologação:", type="password")
        if st.form_submit_button("Acessar Ambiente de Testes", use_container_width=True):
            if senha_desenvolvimento.strip() == "carencias2026":
                st.session_state.seguranca_master = True
                st.rerun()
    st.stop()
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
        st.markdown("##### 📍 Região/Cidade da falta:")
        regiao_final = st.text_input(label="Localizacao", placeholder="Ex: São Paulo/SP ou Osasco/SP",
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
    else:
        if st.session_state.aba_consumidor == "produto":
            st.markdown("### 📦 Produto / Marca")
            label_item, placeholder_item = "Qual produto ou marca falta?", "Ex: Leite condensado marca X..."
            label_local, placeholder_local = "Em qual estabelecimento?", "Ex: Nome do mercado..."
            label_contato, tipo_envio = "Quer ser avisado na reposição? (Opcional)", "Produto / Marca"
        elif st.session_state.aba_consumidor == "servico":
            st.markdown("### 🏪 Novo Comércio / Serviço")
            label_item, placeholder_item = "Qual comércio falta no bairro?", "Ex: Sapataria, lavanderia..."
            label_local, placeholder_local = "Em qual rua ou ponto?", "Ex: Avenida Principal..."
            label_contato, tipo_envio = "Quer ser avisado na abertura? (Opcional)", "Serviço Local / Novo Estabelecimento"
        else:
            st.markdown("### 🏛️ Infraestrutura / Zeladoria")
            label_item, placeholder_item = "Qual problema de infraestrutura público?", "Ex: Falha na iluminação..."
            label_local, placeholder_local = "Qual o ponto de referência?", "Ex: Posto de saúde do bairro Y..."
            label_contato, tipo_envio = "Quer ser avisado na conclusão? (Opcional)", "Serviço Público / Infraestrutura"

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
            botao_enviar = st.form_submit_button(
                "🔍 SINALIZAR ESTA FALTA", use_container_width=True)

        if botao_enviar and item_solicitado and local_ocorrencia:
            try:
                hash_dispositivo = obter_pegada_digital()
                regiao_salva = st.session_state.get(
                    "input_regiao_via_unica", "São Paulo/SP")
                texto_regiao = regiao_salva.strip().title() if regiao_salva else "São Paulo/SP"
                local_formatado = local_ocorrencia.strip().title()

                local_data = supabase.table("locais_destino").insert(
                    {"nome_exibicao": local_formatado, "regiao_cidade": texto_regiao, "regiao_estado": "SP"}).execute()
                local_id = local_data.data[0]["id"] if local_data.data and len(
                    local_data.data) > 0 else None

                if local_id:
                    segmento_detectado = "Geral"
                    texto_usuario = item_solicitado.strip().lower()
                    if any(p in texto_usuario for p in ["leite", "arroz", "feijão", "café", "açúcar", "pão", "mercado"]):
                        segmento_detectado = "Supermercado"
                    elif any(p in texto_usuario for p in ["remédio", "médico", "dentista", "farmácia"]):
                        segmento_detectado = "Saude"
                    elif any(p in texto_usuario for p in ["ração", "pet", "cachorro", "gato", "petshop"]):
                        segmento_detectado = "Petshop"
                    elif any(p in texto_usuario for p in ["manicure", "salão", "cabeleireiro", "estética"]):
                        segmento_detectado = "Beleza"

                    texto_obs = observacao_usuario.strip() if observacao_usuario else None
                    supabase.table("relatos_escassez").insert({"local_id": local_id, "item_solicitado": item_solicitado.strip().title(), "tipo_carencia": tipo_envio, "status": "Pendente", "contato_aviso": contato_usuario.strip(
                    ) if contato_usuario else None, "observacao_detalhe": texto_obs, "sub_segmento": segmento_detectado, "pegada_digital": hash_dispositivo}).execute()
                    st.success("✅ Falta sinalizada com sucesso!")
                    import time
                    time.sleep(1.2)
                    st.session_state.aba_consumidor = "menu_triagem"
                    st.session_state.tela_atual = "home"
                    st.rerun()
            except Exception as e:
                st.error(f"⚠️ Erro técnico de persistência: {str(e)}")

    # --- 🏆 SEÇÃO ÚNICA E FIXA: IMPACTOS RECENTES NO BAIRRO ---
    st.write("")
    st.markdown("### 🏆 Impactos Recentes no Bairro")
    try:
        resolvidos = supabase.table("relatos_escassez").select("item_solicitado, sub_segmento, locais_destino(nome_exibicao, regiao_cidade)").eq(
            "status", "Atendido").order("data_registro", desc=True).limit(20).execute()
        if resolvidos.data and len(resolvidos.data) > 0:
            lista_impactos = []
            for item in resolvidos.data:
                if item.get("locais_destino"):
                    lista_impactos.append({"item": item["item_solicitado"].strip().title(), "nicho": item.get("sub_segmento", "Geral").strip(
                    ), "local": item["locais_destino"]["nome_exibicao"].strip().title(), "cidade_exibicao": item["locais_destino"]["regiao_cidade"].strip()})
            df_impactos = pd.DataFrame(lista_impactos)

            df_impactos_locais_unicos = df_impactos.drop_duplicates(subset=[
                                                                    "local"])
            df_impactos_final = df_impactos_locais_unicos.drop_duplicates(subset=[
                                                                          "nicho"])

            contador_exibidos = 0
            for _, linha_imp in df_impactos_final.iterrows():
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

                st.markdown(f"""
                    <div style='background-color: #1A1A1A; padding: 0.6rem 1rem; border-radius: 8px; border-left: 4px solid #00803B; margin-bottom: 8px;'>
                        <span style='font-size: 13px; color: #aaaaaa; font-weight: 500;'>
                            ✅ <b>{icone}</b> O estabelecimento {linha_imp['local']} ({linha_imp['cidade_exibicao']}) {acao} <b>{linha_imp['item']}</b>!
                        </span>
                    </div>
                """, unsafe_allow_html=True)
                contador_exibidos += 1
        else:
            st.write("ℹ️ Nenhuma benfeitoria recente registrada.")
    except:
        pass
# --- TELA: AUTENTICAÇÃO POR TOKEN (REATIVAÇÃO DO ENTER) ---
elif st.session_state.tela_atual == "autenticacao":
    if st.button("⬅️ Voltar ao Menu Principal", key="btn_voltar_aut"):
        st.session_state.tela_atual = "home"
        st.session_state.token_valido = False
        st.rerun()
    st.markdown("<h1 style='text-align: center; margin-bottom: 0px !important;'>🔍 E o que falta?</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; font-weight: 600; color: #aaaaaa !important; margin-top: 5px; margin-bottom: 25px;'>Área Restrita para Comerciantes e Gestores</p>", unsafe_allow_html=True)
    st.write("---")

    with st.form(key="form_autenticacao_b2b", clear_on_submit=False):
        token_inserido = st.text_input(
            label="Token de Acesso:", type="password", placeholder="Digite seu token de acesso...")
        st.write("")
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
                        st.error(
                            "❌ Token suspenso. Entre em contato com a administração.")
                    else:
                        st.session_state.perfil_cliente = dados_linha.get(
                            "perfil_segmento", "comerciante")
                        st.session_state.regiao_cliente = dados_linha.get(
                            "regiao_atuacao", "São Paulo/SP")
                        st.session_state.recursos_liberados = {
                            "reverso": dados_linha.get("recurso_marketplace_reverso", True),
                            "whatsapp": dados_linha.get("recurso_whatsapp", True),
                            "pdf": dados_linha.get("recurso_pdf", True)
                        }
                        st.session_state.token_valido = True
                        st.session_state.tela_atual = "comerciante"
                        st.rerun()
                else:
                    st.error("❌ Token inválido.")
            except Exception as e:
                st.error("❌ Erro de conexão ou token mal formatado.")
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
    espectador_analitico = st.session_state.perfil_cliente in [
        "investidor", "gestor", "jornalista"]

    if st.session_state.perfil_cliente == "comerciante":
        st.markdown("##### 🏪 *Varejo Local (Foco em Gôndolas)*")
    elif st.session_state.perfil_cliente == "saude":
        st.markdown("##### 🩺 *Saúde & Bem-Estar*")
    elif st.session_state.perfil_cliente == "petshop":
        st.markdown("##### 🐶 *Petshop & Veterinária*")
    elif st.session_state.perfil_cliente == "beleza":
        st.markdown("##### 💈 *Beleza & Estética*")
    elif st.session_state.perfil_cliente == "investidor":
        st.markdown("##### 💼 *Investidor e Expansão (Vazios Comerciais)*")
    elif st.session_state.perfil_cliente == "jornalista":
        st.markdown("##### 📰 *Imprensa Regional (Dados Consolidados)*")
    elif st.session_state.perfil_cliente == "admin":
        st.markdown("<p style='text-align: center; font-size: 24px; font-weight: 600; color: #aaaaaa !important; margin-top: 5px; margin-bottom: 25px;'>Painel de Controle Mestre</p>", unsafe_allow_html=True)
    else:
        st.markdown("##### 🏛️ *Gestão Pública (Foco em Infraestrutura)*")

    st.write("---")

    if st.session_state.perfil_cliente != "admin":
        regioes_disponiveis_teste = ["São Paulo/SP",
                                     "Carapicuíba/SP", "Osasco/SP", "Barueri/SP"]
        regiao_padrao_index = regioes_disponiveis_teste.index(
            st.session_state.regiao_cliente) if st.session_state.regiao_cliente in regioes_disponiveis_teste else 0
        regiao_selecionada_painel = st.selectbox("📍 Analisar Região / Cidade (Filtro Dinâmico):",
                                                 options=regioes_disponiveis_teste, index=regiao_padrao_index, key="select_filtro_geografico_b2b")
        if regiao_selecionada_painel != st.session_state.regiao_cliente:
            st.session_state.regiao_cliente = regiao_selecionada_painel
            st.session_state.busca_ativa = False
            st.rerun()

    termo_busca = st.text_input(label="Refinar por palavra-chave ou estabelecimento (Opcional):",
                                placeholder="Digite para filtrar a lista abaixo...", key="input_busca_painel")

    if st.session_state.perfil_cliente == "admin":
        st.markdown("### 🛠️ Cadastro de Assinantes (ERP)")
        id_formulario_admin = f"form_cadastro_admin_{datetime.datetime.now().strftime('%M%S')}"
        with st.form(key=id_formulario_admin, clear_on_submit=True):
            nome_novo_comercio = st.text_input(
                "Nome do Estabelecimento Comercial:", placeholder="Ex: Supermercado Xavier...")
            perfil_novo_comercio = st.selectbox("Perfil de Acesso Corporativo:", [
                                                "comerciante", "saude", "petshop", "beleza", "investidor", "gestor", "jornalista"])
            regiao_novo_comercio = st.text_input(
                "Região/Cidade de Atuação:", placeholder="Ex: São Paulo/SP...")
            st.write("")
            if st.form_submit_button("💼 Cadastrar Lojista e Gerar Credenciais"):
                if nome_novo_comercio and regiao_novo_comercio:
                    try:
                        novo_registro = supabase.table("clientes_b2b").insert({
                            "nome_estabelecimento": nome_novo_comercio.strip().title(),
                            "perfil_segmento": perfil_novo_comercio,
                            "regiao_atuacao": regiao_novo_comercio.strip(),
                            "status_pagamento": "Ativo",
                            "recurso_marketplace_reverso": True,
                            "recurso_whatsapp": True,
                            "recurso_pdf": True
                        }).execute()
                        if novo_registro.data:
                            st.success(
                                "🎉 Cliente cadastrado com sucesso na nuvem!")
                            st.info(
                                f"🔑 **TOKEN UUID EMITIDO:** `{novo_registro.data['token_acesso']}`")
                    except Exception as error_db:
                        st.error(
                            f"⚠️ Falha na conexão com o banco: {str(error_db)}")
                else:
                    st.warning("⚠️ Preencha os campos obrigatórios.")
        st.write("")
        st.markdown("### 📊 Central de Recursos e Controle Financeiro")
        try:
            resposta_clientes = supabase.table("clientes_b2b").select(
                "*").order("created_at", desc=True).execute()
            if resposta_clientes.data and len(resposta_clientes.data) > 0:
                for cli in resposta_clientes.data:
                    c_id = cli["id"]
                    with st.expander(f"🏢 {cli['nome_estabelecimento']} ({cli['regiao_atuacao']}) - Token: {cli['token_acesso'][:8]}..."):
                        col_status, col_plan = st.columns(2)
                        with col_status:
                            status_pag = st.selectbox("Status de Pagamento:", ["Ativo", "Inadimplente", "Cancelado"], index=[
                                                      "Ativo", "Inadimplente", "Cancelado"].index(cli.get("status_pagamento", "Ativo")), key=f"pay_{c_id}")
                        with col_plan:
                            plano_cont = st.selectbox("Plano Contratado:", ["Bronze", "Prata", "Ouro"], index=[
                                                      "Bronze", "Prata", "Ouro"].index(cli.get("plano_contratado", "Ouro")), key=f"plan_{c_id}")

                        st.write(
                            "**⚙️ Habilitar/Desabilitar Serviços do Sistema:**")
                        c_reverso = st.checkbox("Acesso ao Marketplace Reverso", value=cli.get(
                            "recurso_marketplace_reverso", True), key=f"rev_{c_id}")
                        c_whatsapp = st.checkbox("Botão de Captação WhatsApp LGPD", value=cli.get(
                            "recurso_whatsapp", True), key=f"wa_{c_id}")
                        c_pdf = st.checkbox("Emissão e Download de Relatórios PDF", value=cli.get(
                            "recurso_pdf", True), key=f"pdf_ch_{c_id}")

                        if st.button("💾 Salvar Alterações e Atualizar Travas", key=f"save_{c_id}"):
                            supabase.table("clientes_b2b").update({
                                "status_pagamento": status_pag,
                                "plano_contratado": plano_cont,
                                "recurso_marketplace_reverso": c_reverso,
                                "recurso_whatsapp": c_whatsapp,
                                "recurso_pdf": c_pdf
                            }).eq("id", c_id).execute()
                            st.success(
                                "🔒 Configurações de acesso sincronizadas no servidor!")
                            import time
                            time.sleep(0.8)
                            st.rerun()
            else:
                st.info("ℹ️ Nenhum assinante corporativo cadastrado na base.")
        except Exception as err_grid:
            st.error(f"⚠️ Erro ao renderizar a central ERP: {str(err_grid)}")

        st.write("")
        st.markdown("### 📥 Sugestões de Novos Nichos Coletados (Cenário B)")
        try:
            sugestoes_brutas = supabase.table("relatos_escassez").select(
                "id, item_solicitado, sub_segmento").eq("sub_segmento", "Geral").limit(5).execute()
            if sugestoes_brutas.data and len(sugestoes_brutas.data) > 0:
                for sug in sugestoes_brutas.data:
                    id_sug, item_sug = sug["id"], sug["item_solicitado"]
                    with st.expander(f"📥 Termo Coletado: \"{item_sug}\""):
                        nicho_homologado = st.selectbox("Vincular ao Segmento Oficial:", [
                                                        "Supermercado", "Saude", "Petshop", "Beleza"], key=f"sel_nicho_{id_sug}")
                        nome_corrigido = st.text_input(
                            "Corrigir nome / Padronizar termo:", value=item_sug, key=f"txt_nome_{id_sug}")
                        if st.button("✅ Homologar e Ativar no Mercado", key=f"btn_homologar_{id_sug}"):
                            supabase.table("relatos_escassez").update({"item_solicitado": nome_corrigido.strip(
                            ).title(), "sub_segmento": nicho_homologado}).eq("id", id_sug).execute()
                            st.success("🎉 Item homologado com sucesso!")
                            import time
                            time.sleep(1)
                            st.rerun()
            else:
                st.write("ℹ️ Nenhuma sugestão pendente de curadoria.")
        except Exception as err_nicho:
            pass
    # --- PROCESSAMENTO GLOBAL DE DADOS REAL / SIMULADO COM TRAVA POR CIDADES ---
    if st.session_state.perfil_cliente != "admin":
        if not st.session_state.busca_ativa or st.session_state.dados_grafico is None:
            st.session_state.busca_ativa = True
            try:
                regiao_alvo = st.session_state.get(
                    "regiao_cliente", "São Paulo/SP")
                cidade_filtro = regiao_alvo.split(
                    "-")[1].strip() if "-" in regiao_alvo else regiao_alvo.strip()
                resposta = supabase.table("relatos_escassez").select(
                    "id, item_solicitado, tipo_carencia, data_registro, status, observacao_detalhe, sub_segmento, pegada_digital, contato_aviso, locais_destino(nome_exibicao, regiao_cidade)").execute()

                dados_limpos = []
                agora = datetime.datetime.now(datetime.timezone.utc)
                if resposta.data and len(resposta.data) > 0:
                    for registro in resposta.data:
                        if registro.get("locais_destino"):
                            loc_cidade = registro["locais_destino"]["regiao_cidade"]
                            if cidade_filtro.lower() not in loc_cidade.lower():
                                continue
                            sub_seg = str(registro.get(
                                "sub_segmento", "Geral")).strip()
                            cat_bruta = str(registro.get(
                                "tipo_carencia", "Produto / Marca")).strip()
                            idade_dias = max(0, (agora - datetime.datetime.fromisoformat(registro.get(
                                "data_registro").replace("Z", "+00:00"))).days) if registro.get("data_registro") else 0
                            categoria_limpa = "Serviço Público / Infraestrutura" if ("Público" in cat_bruta or "Publico" in cat_bruta or "Infra" in cat_bruta or "Zeladoria" in sub_seg) else (
                                "Serviço Local / Novo Estabelecimento" if ("Local" in cat_bruta or "Invest" in sub_seg) else "Produto / Marca")

                            nome_local_bruto = registro["locais_destino"]["nome_exibicao"]
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

                            dados_limpos.append({"ID": registro["id"], "O que Falta": registro["item_solicitado"].strip().title(), "Categoria": categoria_limpa, "Local/Referência": nome_local_exibicao, "Cidade": loc_cidade, "Dias": idade_dias, "Observação": registro.get(
                                "observacao_detalhe") or "Sem detalhes.", "SubSegmento": sub_seg, "Pegada": registro.get("pegada_digital") or f"anon_{registro['id']}", "Contato": registro.get("contato_aviso") or ""})

                dados_mock = [
                    {"ID": 991, "O que Falta": "Leite Desnatado Parmalat 1L", "Categoria": "Produto / Marca", "Local/Referência": "Mercadinho Do Bairro",
                        "Cidade": "São Paulo/SP - Centro", "Dias": 4, "Observação": "Falta toda quarta.", "SubSegmento": "Supermercado", "Pegada": "hash1", "Contato": "11999999999"},
                    {"ID": 994, "O que Falta": "Lavanderia Expressa Auto-Servico", "Categoria": "Serviço Local / Novo Estabelecimento", "Local/Referência": "Avenida Das Palmeiras",
                        "Cidade": "São Paulo/SP - Tatuapé", "Dias": 45, "Observação": "Prédios novos sem serviço.", "SubSegmento": "Investimento", "Pegada": "hash4", "Contato": ""},
                    {"ID": 997, "O que Falta": "Manutenção De Iluminação Pública", "Categoria": "Serviço Público / Infraestrutura", "Local/Referência": "Rua das Flores, 40",
                        "Cidade": "São Paulo/SP - Centro", "Dias": 2, "Observação": "Poste apagado.", "SubSegmento": "Zeladoria", "Pegada": "hash7", "Contato": ""}
                ]
                for m in dados_mock:
                    if cidade_filtro.lower() in m["Cidade"].lower():
                        if not any(d["O que Falta"].lower() == m["O que Falta"].lower() for d in dados_limpos):
                            if st.session_state.perfil_cliente in ["comerciante", "saude", "petshop", "beleza"] and m["Local/Referência"] != loja_alvo_prioridade:
                                m_copy = m.copy()
                                m_copy["Local/Referência"] = "Estabelecimento Concorrente"
                                dados_limpos.append(m_copy)
                            else:
                                dados_limpos.append(m)
                st.session_state.dados_grafico = pd.DataFrame(dados_limpos)
            except Exception as e:
                st.error(f"⚠️ Erro técnico de performance: {str(e)}")
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

                        # --- TRAVA 1: PLANO E RECURSO ADMIN PARA MARKETPLACE REVERSO ---
                        if is_reverso_ativa and not st.session_state.get("recursos_liberados", {}).get("reverso", True):
                            st.warning(
                                "🔒 Visualização suspensa administrativamente por ausência de pagamento ou inadimplência de mensalidade. Regularize seu plano B2B no Admin para reativar o Marketplace Reverso.")
                            continue

                        df_filtro_aba = df
                        if frente_ativa == "Infra":
                            df_filtro_aba = df[df['Categoria'] ==
                                               "Serviço Público / Infraestrutura"]
                        elif frente_ativa == "Serviços":
                            df_filtro_aba = df[df['Categoria'] ==
                                               "Serviço Local / Novo Estabelecimento"]
                        elif frente_ativa == "Varejo":
                            if st.session_state.perfil_cliente == "comerciante":
                                df_filtro_aba = df[df['SubSegmento'].str.contains(
                                    "Supermercado|Geral", case=False, na=False)]
                            elif st.session_state.perfil_cliente == "saude":
                                df_filtro_aba = df[df['SubSegmento'].str.contains(
                                    "Saude|Saúde", case=False, na=False)]
                            elif st.session_state.perfil_cliente == "petshop":
                                df_filtro_aba = df[df['SubSegmento'].str.contains(
                                    "Pet", case=False, na=False)]
                            elif st.session_state.perfil_cliente == "beleza":
                                df_filtro_aba = df[df['SubSegmento'].str.contains(
                                    "Beleza", case=False, na=False)]
                        if termo_busca:
                            df_filtro_aba = df_filtro_aba[df_filtro_aba['O que Falta'].str.contains(
                                termo_busca, case=False) | df_filtro_aba['Local/Referência'].str.contains(termo_busca, case=False)]

                        if not df_filtro_aba.empty:
                            df_filtro_aba['É_Minha_Loja'] = df_filtro_aba['Local/Referência'].apply(
                                lambda x: 1 if x == loja_alvo_prioridade else 0)

                            # --- TRAVA 2: PLANO E RECURSO ADMIN PARA EXPORTAÇÃO DE RELATÓRIOS PDF ---
                            pode_baixar_pdf = st.session_state.get(
                                "recursos_liberados", {}).get("pdf", True)
                            if espectador_analitico or pode_baixar_pdf:
                                try:
                                    pdf_real = FPDF()
                                    pdf_real.add_page()
                                    pdf_real.set_font("Arial", size=12)
                                    pdf_real.cell(
                                        200, 10, txt="Relatorio de Vazios Comerciais Regional", ln=1, align="C")
                                    pdf_real.cell(
                                        200, 10, txt="--------------------------------------------------", ln=2, align="C")
                                    for _, r in df_filtro_aba.iterrows():
                                        txt_linha = f"- Falta: {r['O que Falta']} | Localizacao: {r['Local/Referência']} ({r['Cidade']})"
                                        pdf_real.cell(190, 10, txt=txt_linha.encode(
                                            'latin-1', 'ignore').decode('latin-1'), ln=1)
                                    pdf_output = pdf_real.output(dest='S')
                                    pdf_bytes = bytes(pdf_output) if isinstance(
                                        pdf_output, bytes) else pdf_output.encode('latin-1')
                                    st.download_button(label="Baixar Relatório de Vazios (PDF)", data=pdf_bytes,
                                                       file_name="expansao.pdf", mime="application/pdf", key=f"btn_pdf_{num_aba}")
                                except Exception as e_pdf:
                                    pass
                            elif not pode_baixar_pdf and not espectador_analitico:
                                st.info(
                                    "🔒 Download de PDFs indisponível no seu plano atual. Faça o upgrade para ativar.")

                            st.markdown(
                                f"<div style='text-align: right; font-size: 16px; font-weight: bold; color: #00803B; margin-top: 10px; margin-bottom: 20px;'>Total de Oportunidades: {len(df_filtro_aba)}</div>", unsafe_allow_html=True)
                            st.write("---")
                            df_agrupado_mestre = df_filtro_aba.groupby(["O que Falta", "Categoria"]).agg(Clientes_Unicos=("Pegada", "nunique"), Alertas_Totais=(
                                "ID", "count"), Maior_Espera=("Dias", "max")).sort_values(by="Clientes_Unicos", ascending=False).reset_index()
                            for _, mestre_line in df_agrupado_mestre.iterrows():
                                item_nome = mestre_line['O que Falta']
                                clientes = int(mestre_line['Clientes_Unicos'])
                                classe_tag = "tag-calor-alta" if clientes >= 5 else (
                                    "tag-calor-media" if clientes >= 2 else "tag-calor-baixa")
                                label_tag = f"🔥 CRÍTICO • {clientes} CPFs" if clientes >= 5 else (
                                    f"⚠️ OPORTUNIDADE • {clientes} CPFs" if clientes >= 2 else f"🔹 INICIAL • {clientes} CPF")
                                st.markdown(
                                    f'<div class="bloco-lista-premium"><span class="{classe_tag}">{label_tag}</span><b style="color: #FFFFFF; font-size: 16px;">🏢 Falta: {item_nome}</b><div style="margin-top: 0.5rem; color: #aaaaaa; font-size: 13px;">⏱️ Demanda de {mestre_line["Alertas_Totais"]} relatos • Maior espera: {mestre_line["Maior_Espera"]} dias</div></div>', unsafe_allow_html=True)

                                detalhes_item = df_filtro_aba[df_filtro_aba['O que Falta'] == item_nome]
                                detalhes_item_limpo = detalhes_item.drop_duplicates(
                                    subset=["Cidade", "Local/Referência", "Observação"])
                                st.write(
                                    "📍 **Localização e Detalhes das Ocorrências Coletadas:**")
                                for _, sub_item in detalhes_item_limpo.iterrows():
                                    st.markdown(
                                        f"  * **{sub_item['Cidade']}** - *Ponto:* {sub_item['Local/Referência']}")
                                    if sub_item['Observação']:
                                        st.markdown(
                                            f"    * 💬 *Relato:* \"{sub_item['Observação']}\"")
                                st.markdown(
                                    "<hr style='border-top: 1px dashed #333; margin: 1rem 0;'/>", unsafe_allow_html=True)
