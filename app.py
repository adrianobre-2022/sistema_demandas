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
    st.error("⚠️ As credenciais de conexão não foram encontradas.")
    st.stop()

supabase: Client = create_client(url, key)
# --------------------------------------------

st.set_page_config(page_title="E o que falta?",
                   page_icon="🔍", layout="centered")

# --- CUSTOMIZAÇÃO ESTÉTICA PREMIUM (VERDE FECHADO + LISTAS GRAFITE PREMIUM) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #121212 !important;
        color: #FFFFFF !important;
    }
    .stWidgetFormLabel, label, p, .stMarkdown, [data-testid="stWidgetLabel"] {
        color: #FFFFFF !important;
    }
    
    /* ACESSIBILIDADE WCAG: Verde Floresta Fechado Confortável com Letras Brancas Gorda */
    .stButton>button, .stFormSubmitButton>button, [data-testid="stDownloadButton"]>button {
        background-color: #00803B !important; 
        color: #FFFFFF !important; 
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.8rem 0.2rem !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        width: 100% !important;
        display: block !important;
    }
    .stButton>button:hover, .stFormSubmitButton>button:hover, [data-testid="stDownloadButton"]>button:hover {
        background-color: #005a24 !important;
        color: #FFFFFF !important;
    }
    
    /* BRANDING IMPONENTE: Aumenta o tamanho do título para destacar a marca em uma linha */
    h1 {
        font-size: 32px !important; 
        font-weight: 900 !important;
        white-space: nowrap !important;
    }
    
    [data-testid="stHorizontalBlock"]:has(button[key*="simetrico"]) {
        gap: 10px !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
    }
    
    .stTextInput input, .stTextArea textarea, div[data-baseweb="textarea"] textarea, div[data-baseweb="input"] input {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        border: 1px solid #444444 !important;
    }
    input::placeholder, textarea::placeholder {
        color: #888888 !important;
        font-style: italic !important;
        opacity: 1 !important;
    }
    
    /* ESTILIZAÇÃO DO PRIMEIRO MODELO DE LISTA (GRAFITE COM BORDA FINA) */
    .bloco-lista-premium {
        background-color: #1E1E1E !important; 
        padding: 1.2rem !important; 
        border-radius: 10px !important; 
        margin-bottom: 0.8rem !important; 
        border: 1px solid #333333 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
        overflow: hidden !important;
    }
    
    /* TAGS LATERAIS COLORIDAS DE CALOR DO PRIMEIRO MODELO */
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
    st.write("Selecione o seu perfil de acesso para continuar:")
    st.write("")

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
    st.write("---")

    if st.session_state.aba_consumidor == "menu_triagem":
        st.markdown("##### *O termômetro de carências da nossa região.*")
        st.write("")
        st.write("Escolha o tipo de ausência que você quer registrar no bairro:")
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
                "### 📦 Produto / Marca\n##### *Mapeando falhas de estoque e gôndolas vazias na região.*")
            label_item, placeholder_item = "Qual produto ou marca você buscou e não encontrou?", "Ex: Leite condensado marca X, ração de gato..."
            label_local, placeholder_local = "Em qual estabelecimento isso ocorreu?", "Ex: Nome do mercado, farmácia, padaria..."
            label_contato, tipo_envio = "Quer ser avisado caso o estoque seja reposto? (Opcional)", "Produto / Marca"
        elif st.session_state.aba_consumidor == "servico":
            st.markdown(
                "### 🏪 Novo Comércio / Serviço\n##### *Mapeando oportunidades de novos negócios e conveniência.*")
            label_item, placeholder_item = "Qual tipo de comércio ou serviço falta neste bairro?", "Ex: Sapataria, lavanderia, costureira, padaria..."
            label_local, placeholder_local = "Em qual rua, travessa ou pedaço do bairro isso faz falta?", "Ex: Bairro Centro, Avenida X..."
            label_contato, tipo_envio = "Quer ser avisado caso este novo comércio seja aberto? (Opcional)", "Serviço Local / Novo Estabelecimento"
        else:
            st.markdown(
                "### 🏛️ Infraestrutura / Zeladoria\n##### *Mapeando melhorias urbanas e cobranças aos órgãos públicos.*")
            label_item, placeholder_item = "Qual carência de infraestrutura/manutenção você identificou?", "Ex: Falha na iluminação, falta de médicos..."
            label_local, placeholder_local = "Qual o ponto de referência ou localidade exata?", "Ex: Posto de saúde do bairro Y, Rua Z..."
            label_contato, tipo_envio = "Quer ser avisado caso esta manutenção pública seja realizada? (Opcional)", "Serviço Público / Infraestrutura"
        st.write("")
        with st.form(key="formulario_dinamico_consumidor", clear_on_submit=True):
            item_solicitado = st.text_input(
                label=label_item, placeholder=placeholder_item, key="input_item")
            local_ocorrencia = st.text_input(
                label=label_local, placeholder=placeholder_local, key="input_local")
            observacao_usuario = st.text_area(label="Mais detalhes ou observações sobre o problema (Opcional):",
                                              placeholder="Ex: Detalhe o ocorrido de forma construtiva para ajudar a triagem...", key="input_obs")
            contato_usuario = st.text_input(
                label=label_contato, placeholder="Ex: Seu e-mail ou WhatsApp...", key="input_contato")
            st.write("")
            botao_enviar = st.form_submit_button(
                "Registrar Ocorrência", use_container_width=True)

        if botao_enviar:
            if item_solicitado and local_ocorrencia:
                texto_usuario, local_usuario = item_solicitado.strip(
                ).lower(), local_ocorrencia.strip().lower()
                obs_texto = observacao_usuario.strip().lower() if observacao_usuario else ""

                palavras_ofensivas = ["porra", "caralho", "puta", "merda", "bosta",
                                      "vai tomar", "fudeu", "ladrão", "roubo", "safado", "vagabundo"]
                termos_politicos_proibidos = ["pec", "deputado", "senado", "senador", "presidente",
                                              "governador", "partido", "impeachment", "voto", "eleição", "politica", "político"]
                excecoes_contexto = [
                    "saco de lixo", "sacos de lixo", "lixeira", "pá de lixo", "coleta de lixo"]

                contem_bloqueio, mensagem_erro = False, ""
                if any(p in texto_usuario for p in palavras_ofensivas) or any(p in local_usuario for p in palavras_ofensivas) or any(p in obs_texto for p in palavras_ofensivas):
                    contem_bloqueio = True
                    mensagem_erro = "⚠️ O sistema identificou termos impróprios ou linguagem ofensiva. Por favor, reescreva de forma construtiva."
                if any(p in texto_usuario for p in termos_politicos_proibidos) or any(p in local_usuario for p in termos_politicos_proibidos) or any(p in obs_texto for p in termos_politicos_proibidos):
                    contem_bloqueio = True
                    mensagem_erro = "⚠️ O portal é focado estritamente em zeladoria e carências locais. Manifestações político-ideológicas nacionais (como PECs) devem ser direcionadas às ouvidorias do Senado ou Câmara."
                if "lixo" in texto_usuario or "lixo" in local_usuario:
                    if not any(e in texto_usuario for e in excecoes_contexto) and not any(e in local_usuario for e in excecoes_contexto):
                        contem_bloqueio = True
                        mensagem_erro = "⚠️ O sistema identificou termos impróprios ou linguagem ofensiva. Por favor, reescreva de forma construtiva."

                palavras_infra = ["rua", "praça", "iluminação", "poste", "asfalto", "médico",
                                  "ônibus", "hospital", "bueiro", "segurança", "luz", "polícia", "posto de saúde"]
                palavras_produto = ["leite", "fralda", "ração", "refrigerante",
                                    "cerveja", "sabão", "remédio", "arroz", "feijão", "café", "açúcar"]

                erro_detectado = False
                if contem_bloqueio:
                    st.error(mensagem_erro)
                    erro_detectado = True
                elif tipo_envio == "Produto / Marca" and any(p in texto_usuario for p in palavras_infra):
                    st.error(
                        "⚠️ Ops! Parece um problema de Infraestrutura Pública. Modifique no menu principal.")
                    erro_detectado = True
                elif tipo_envio == "Serviço Local / Novo Estabelecimento" and any(p in texto_usuario for p in palavras_produto):
                    st.error(
                        "⚠️ Ops! Parece a falta de um produto de mercado. Modifique no menu principal.")
                    erro_detectado = True

                if not erro_detectado:
                    try:
                        local_formatado = local_ocorrencia.strip().title()
                        local_data = supabase.table("locais_destino").insert(
                            {"nome_exibicao": local_formatado, "regiao_cidade": "São Paulo", "regiao_estado": "SP"}).execute()
                        local_id = local_data.data["id"] if local_data.data and len(
                            local_data.data) > 0 else None

                        if local_id:
                            item_formatado = item_solicitado.strip().title()

                            # CLASSIFICAÇÃO INTELIGENTE MULTI-SETORIAL: Organiza os dados nas caixas B2B corretas
                            segmento_detectado = "Geral"
                            if any(p in texto_usuario for p in ["leite", "arroz", "feijão", "café", "açúcar", "refrigerante", "cerveja", "sabão", "pão", "bolo", "doce", "salgado", "padaria", "mercado", "hortifruti", "açougue"]):
                                segmento_detectado = "Supermercado"
                            elif any(p in texto_usuario for p in ["remédio", "fisioterapeuta", "fisioterapia", "nutricionista", "clínica", "médico", "psicólogo", "dentista", "farmácia", "xarope"]):
                                segmento_detectado = "Saude"
                            elif any(p in texto_usuario for p in ["ração", "pet", "cachorro", "gato", "veterinária", "tosa", "banho", "petshop", "coleira"]):
                                segmento_detectado = "Petshop"
                            elif any(p in texto_usuario for p in ["manicure", "salão", "barbearia", "cabeleireiro", "estética", "barbeiro", "unha"]):
                                segmento_detectado = "Beleza"

                            texto_obs = observacao_usuario.strip() if observacao_usuario else None
                            supabase.table("relatos_escassez").insert({
                                "local_id": local_id,
                                "item_solicitado": item_formatado,
                                "tipo_carencia": tipo_envio,
                                "status": "Pendente",
                                "contato_aviso": contato_usuario.strip() if contato_usuario else None,
                                "detalhes_adicionais": texto_obs,
                                "observacao_detalhe": texto_obs,
                                "sub_segmento": segmento_detectado
                            }).execute()

                            st.success(
                                "✅ Registro computado e salvo na nuvem com anonimato garantido!")
                            import time
                            time.sleep(1.5)
                            st.session_state.aba_consumidor = "menu_triagem"
                            st.rerun()
                    except Exception as e:
                        st.error(f"⚠️ Erro técnico detalhado: {str(e)}")
            else:
                st.warning(
                    "⚠️ Por favor, preencha os campos obrigatórios antes de enviar.")

    st.write("")
    st.markdown("### 🏆 Impactos Recentes no Bairro")
    try:
        resolvidos = supabase.table("relatos_escassez").select(
            "item_solicitado, locais_destino(nome_exibicao)").eq("status", "Atendido").limit(3).execute()
        if resolvidos.data and len(resolvidos.data) > 0:
            for item in resolvidos.data:
                if item.get("locais_destino"):
                    st.info(
                        f"✅ **{item['locais_destino']['nome_exibicao']}** repôs o estoque: **{item['item_solicitado']}**!")
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
        else:
            st.error(
                "❌ Token inválido ou expirado. Entre em contato com o administrador.")
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
        st.session_state.dados_grafico = None
        st.rerun()

    st.title("📊 Painel de Decisão Estratégica")

    if st.session_state.perfil_cliente == "comerciante":
        st.markdown(
            "##### 🏪 *Nível de Acesso: Varejo Local (Foco em Gôndolas e Supermercados)*")
        opcoes_filtro = ["Apenas Produtos/Marcas (Varejo)"]
    elif st.session_state.perfil_cliente == "saude":
        st.markdown(
            "##### 🩺 *Nível de Acesso: Saúde & Bem-Estar (Foco em Clínicas e Especialistas)*")
        opcoes_filtro = ["Apenas Serviços de Saúde e Clínicas"]
    elif st.session_state.perfil_cliente == "petshop":
        st.markdown(
            "##### 🐶 *Nível de Acesso: Petshop & Veterinária (Foco em Produtos e Serviços Pet)*")
        opcoes_filtro = ["Apenas Produtos e Serviços Pet"]
    elif st.session_state.perfil_cliente == "beleza":
        st.markdown(
            "##### 💈 *Nível de Acesso: Beleza & Estética (Foco em Salões e Barbearias)*")
        opcoes_filtro = ["Apenas Serviços de Estética e Beleza"]
    elif st.session_state.perfil_cliente == "investidor":
        st.markdown(
            "##### 💼 *Nível de Acesso: Investidor e Expansão (Foco em Serviços do Bairro)*")
        opcoes_filtro = ["Oportunidades de Novos Negócios (Serviços)"]
    else:
        st.markdown(
            "##### 🏛️ *Nível de Acesso: Gestão Pública e Imprensa (Foco em Infraestrutura Urbana)*")
        opcoes_filtro = ["Infraestrutura Urbana (Setor Público)"]

    st.write("---")
    filtro_frente = st.selectbox(
        label="Selecione a Frente de Inteligência:", options=opcoes_filtro, key="selectbox_frente")
    termo_busca = st.text_input(label="Filtrar por palavra-chave:",
                                placeholder="Digite para refinar...", key="input_busca_painel")

    if st.button("Buscar Oportunidades Ocultas", use_container_width=True, key="btn_buscar"):
        st.session_state.busca_ativa = True
        try:
            resposta = supabase.table("relatos_escassez").select(
                "id, item_solicitado, tipo_carencia, data_registro, status, detalhes_adicionais, observacao_detalhe, sub_segmento, locais_destino(nome_exibicao, regiao_cidade)").execute()
            dados_limpos = []
            agora = datetime.datetime.now(datetime.timezone.utc)

            if resposta.data and len(resposta.data) > 0:
                for registro in resposta.data:
                    if registro.get("locais_destino"):
                        sub_seg = str(registro.get(
                            "sub_segmento", "Geral")).strip()
                        cat_bruta = str(registro.get(
                            "tipo_carencia", "Produto / Marca")).strip()

                        # ISOLAMENTO DE INFRAESTRUTURA: Proíbe problemas urbanos nas telas de comércios especializados
                        if st.session_state.perfil_cliente in ["comerciante", "saude", "petshop", "beleza"]:
                            if "Infraestrutura" in cat_bruta or "Público" in cat_bruta:
                                continue

                        # Filtro de sub-segmento por token de acesso
                        if st.session_state.perfil_cliente == "comerciante" and sub_seg not in ["Supermercado", "Geral"]:
                            continue
                        elif st.session_state.perfil_cliente == "saude" and sub_seg not in ["Saude", "Geral"]:
                            continue
                        elif st.session_state.perfil_cliente == "petshop" and sub_seg not in ["Petshop", "Geral"]:
                            continue
                        elif st.session_state.perfil_cliente == "beleza" and sub_seg not in ["Beleza", "Geral"]:
                            continue

                        idade_dias = 0
                        data_str = registro.get("data_registro")
                        if data_str:
                            try:
                                data_limpa = data_str.replace("Z", "+00:00")
                                data_reg = datetime.datetime.fromisoformat(
                                    data_limpa)
                                if data_reg.tzinfo is None:
                                    data_reg = data_reg.replace(
                                        tzinfo=datetime.timezone.utc)
                                idade_dias = max(0, (agora - data_reg).days)
                            except:
                                idade_dias = 0

                        texto_detalhe = registro.get("observacao_detalhe") or registro.get(
                            "detalhes_adicionais") or ""

                        dados_limpos.append({
                            "ID": registro["id"], "O que Falta": registro["item_solicitado"].strip().title(),
                            "Categoria": "Produto / Marca" if "Produto" in cat_bruta else ("Serviço Local / Novo Estabelecimento" if "Serviço" in cat_bruta else "Serviço Público / Infraestrutura"),
                            "Local/Referência": registro["locais_destino"]["nome_exibicao"], "Cidade": registro["locais_destino"]["regiao_cidade"],
                            "Dias": idade_dias, "Observação": texto_detalhe, "SubSegmento": sub_seg
                        })

            if not dados_limpos:
                dados_limpos = [
                    {"ID": 991, "O que Falta": "Leite Desnatado Integrado", "Categoria": "Produto / Marca", "Local/Referência": "Mercadinho Do Bairro",
                        "Cidade": "São Paulo", "Dias": 4, "Observação": "Falta nas prateleiras toda quarta à tarde.", "SubSegmento": "Supermercado"},
                    {"ID": 992, "O que Falta": "Feijão Preto Tipo 1", "Categoria": "Produto / Marca", "Local/Referência": "Supermercado Central",
                        "Cidade": "São Paulo", "Dias": 1, "Observação": "Falta feijão da marca X nas gôndolas.", "SubSegmento": "Supermercado"},
                    {"ID": 993, "O que Falta": "Fisioterapeuta Pediátrico", "Categoria": "Serviço Local / Novo Estabelecimento", "Local/Referência": "Condomínio Novo - Bloco B",
                        "Cidade": "São Paulo", "Dias": 5, "Observação": "Não há clínicas com essa especialidade perto.", "SubSegmento": "Saude"},
                    {"ID": 994, "O que Falta": "Nutricionista Esportivo", "Categoria": "Serviço Local / Novo Estabelecimento", "Local/Referência": "Academia Corpo Em Forma",
                        "Cidade": "São Paulo", "Dias": 10, "Observação": "Falta um profissional para atender atletas do bairro.", "SubSegmento": "Saude"},
                    {"ID": 995, "O que Falta": "Ração Premium Gatos Castrados", "Categoria": "Produto / Marca", "Local/Referência": "Petshop Bairro Alto",
                        "Cidade": "São Paulo", "Dias": 3, "Observação": "Marca X sumiu do estoque.", "SubSegmento": "Petshop"},
                    {"ID": 996, "O que Falta": "Barbearia Retrô", "Categoria": "Serviço Local / Novo Estabelecimento", "Local/Referência": "Avenida Principal 1200",
                        "Cidade": "São Paulo", "Dias": 14, "Observação": "Homens do bairro precisam viajar ao centro para cortar cabelo.", "SubSegmento": "Beleza"},
                    {"ID": 997, "O que Falta": "Manutenção De Iluminação", "Categoria": "Serviço Público / Infraestrutura", "Local/Referência": "Rua das Flores, 40",
                        "Cidade": "São Paulo", "Dias": 2, "Observação": "Poste apagado gerando escuridão extrema.", "SubSegmento": "Geral"},
                    {"ID": 998, "O que Falta": "Lavanderia Expressa", "Categoria": "Serviço Local / Novo Estabelecimento", "Local/Referência": "Praça Central",
                        "Cidade": "São Paulo", "Dias": 15, "Observação": "Prédios novos sem lavanderia por perto.", "SubSegmento": "Geral"}
                ]
                if st.session_state.perfil_cliente == "comerciante":
                    dados_limpos = [d for d in dados_limpos if d["SubSegmento"] in [
                        "Supermercado", "Geral"] and d["Categoria"] != "Serviço Público / Infraestrutura"]
                elif st.session_state.perfil_cliente == "saude":
                    dados_limpos = [d for d in dados_limpos if d["SubSegmento"] in [
                        "Saude", "Geral"] and d["Categoria"] != "Serviço Público / Infraestrutura"]
                elif st.session_state.perfil_cliente == "petshop":
                    dados_limpos = [d for d in dados_limpos if d["SubSegmento"] in [
                        "Petshop", "Geral"] and d["Categoria"] != "Serviço Público / Infraestrutura"]
                elif st.session_state.perfil_cliente == "beleza":
                    dados_limpos = [d for d in dados_limpos if d["SubSegmento"] in [
                        "Beleza", "Geral"] and d["Categoria"] != "Serviço Público / Infraestrutura"]
                elif st.session_state.perfil_cliente == "gestor":
                    dados_limpos = [
                        d for d in dados_limpos if d["Categoria"] == "Serviço Público / Infraestrutura"]

            st.session_state.dados_grafico = pd.DataFrame(dados_limpos)
        except Exception as e:
            st.error(f"⚠️ Erro técnico detalhado: {str(e)}")
    if st.session_state.busca_ativa and st.session_state.dados_grafico is not None:
        df = st.session_state.dados_grafico
        if not df.empty:
            df_filtrado = df
            if filtro_frente == "Apenas Produtos/Marcas (Varejo)":
                df_filtrado = df[df['Categoria'] == "Produto / Marca"]
            elif filtro_frente == "Oportunidades de Novos Negócios (Serviços)":
                df_filtrado = df[df['Categoria'] ==
                                 "Serviço Local / Novo Estabelecimento"]
            elif filtro_frente == "Infraestrutura Urbana (Setor Público)":
                df_filtrado = df[df['Categoria'] ==
                                 "Serviço Público / Infraestrutura"]

            if termo_busca:
                df_filtrado = df_filtrado[df_filtrado['O que Falta'].str.contains(
                    termo_busca, case=False) | df_filtrado['Local/Referência'].str.contains(termo_busca, case=False)]

            if not df_filtrado.empty:
                # --- AGRUPAMENTO COMERCIAL CONSOLIDADO POR PRODUTO ---
                df_agrupado = df_filtrado.groupby(["O que Falta", "Categoria", "Cidade"]).agg(
                    Volume_Total=("ID", "count"),
                    Menor_Idade=("Dias", "min")
                ).sort_values(by="Volume_Total", ascending=False).reset_index()

                st.write("---")
                st.markdown("#### 📥 Exportar Inteligência de Mercado")
                df_exportar = df_agrupado.copy()
                df_exportar.columns = ["Item Solicitado", "Segmento",
                                       "Cidade", "Volume Total de Pedidos", "Dias Desde o Alerta"]

                import io
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib import colors

                buffer_pdf = io.BytesIO()
                doc = SimpleDocTemplate(
                    buffer_pdf, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
                elementos_pdf = []
                estilos = getSampleStyleSheet()
                estilo_titulo = ParagraphStyle(
                    'TituloPDF', parent=estilos['Heading1'], fontSize=18, textColor=colors.HexColor('#00803B'), spaceAfter=15)
                estilo_texto = ParagraphStyle(
                    'TextoPDF', parent=estilos['Normal'], fontSize=10, spaceAfter=20)

                elementos_pdf.append(Paragraph(
                    f"<b>RELATÓRIO GERENCIAL - INTELIGÊNCIA DE MERCADO</b>", estilo_titulo))

                from zoneinfo import ZoneInfo
                fuso_brasil = ZoneInfo("America/Sao_Paulo")
                data_hora_brasil = datetime.datetime.now(
                    fuso_brasil).strftime('%d/%m/%Y %H:%M')

                elementos_pdf.append(Paragraph(
                    f"Frente de Análise: {st.session_state.perfil_cliente.upper()}<br/>Data de emissão: {data_hora_brasil}", estilo_texto))
                elementos_pdf.append(Spacer(1, 10))

                dados_tabela = [df_exportar.columns.tolist()] + \
                    df_exportar.values.tolist()
                tabela_pdf = Table(dados_tabela)
                tabela_pdf.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00803B')
                     ), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE',
                                                                      (0, 0), (-1, 0), 10), ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('GRID',
                                                          (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                     [colors.white, colors.HexColor('#F9F9F9')])
                ]))
                elementos_pdf.append(tabela_pdf)
                doc.build(elementos_pdf)
                dados_pdf_final = buffer_pdf.getvalue()

                st.download_button(label="📥 Baixar Relatório Gerencial Oficial (Formato PDF)", data=dados_pdf_final,
                                   file_name=f"relatorio_gerencial_{st.session_state.perfil_cliente}.pdf", mime="application/pdf", key="btn_download_pdf_universal")

                st.write("---")
                st.markdown("#### 📈 Detalhamento das Carências Ativas")
                st.write(
                    f"*(Encontrados {len(df_agrupado)} itens consolidados na região)*")
                st.write("")

                # --- LAYOUT UNIFICADO EM BLOCOS GRAFITE PREMIUM ---
                for indice, linha in df_agrupado.iterrows():
                    item_nome = linha['O que Falta']
                    volume = float(linha['Volume_Total'])

                    classe_tag = "tag-calor-alta" if volume >= 7 else (
                        "tag-calor-media" if volume >= 3 else "tag-calor-baixa")
                    label_tag = f"CRÍTICA • {int(volume)} Pedidos" if volume >= 7 else (
                        f"MODERADA • {int(volume)} Pedidos" if volume >= 3 else f"INICIAL • {int(volume)} Pedido")

                    # Renderiza a caixa com o design do primeiro modelo
                    st.markdown(f"""
                        <div class="bloco-lista-premium">
                            <span class="{classe_tag}">{label_tag}</span>
                            <b style="color: #FFFFFF; font-size: 16px;">📦 {item_nome}</b>
                            <div style="margin-top: 0.5rem; color: #aaaaaa; font-size: 13px;">⏱️ Último alerta há {linha['Menor_Idade']} dias</div>
                        </div>
                    """, unsafe_allow_html=True)

                    # Detalha os locais físicos exatos (bairros/lojas) e as observações reais dentro do mesmo bloco
                    detalhes_item = df_filtrado[df_filtrado['O que Falta'] == item_nome]
                    for _, sub_linha in detalhes_item.iterrows():
                        st.markdown(
                            f"📍 **Local Geográfico Exato:** {sub_linha['Local/Referência']}")
                        obs_texto = str(sub_linha['Observação']).strip()
                        if obs_texto:
                            st.info(
                                f"💬 *Relato da Comunidade:* \"{obs_texto}\"")

                    st.write("")
                    chave_confirmacao = f"confirma_baixa_{indice}"
                    if chave_confirmacao not in st.session_state:
                        st.session_state[chave_confirmacao] = False

                    if not st.session_state[chave_confirmacao]:
                        if st.button("✅ Marcar como Estoque Reposto / Resolvido", key=f"btn_pre_{indice}"):
                            st.session_state[chave_confirmacao] = True
                            st.rerun()
                    else:
                        st.warning(
                            f"⚠️ Confirma dar baixa em todas as {int(volume)} solicitações de '{item_nome}' simultaneamente?")
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.button("🚨 Confirmar Exclusão", key=f"btn_real_{indice}"):
                                supabase.table("relatos_escassez").update({"status": "Atendido"}).eq(
                                    "item_solicitado", item_nome).execute()
                                st.success(
                                    "🎉 Demandas atualizadas com sucesso!")
                                import time
                                time.sleep(1)
                                st.session_state[chave_confirmacao] = False
                                st.session_state.busca_ativa = False
                                st.rerun()
                            with col_b2:
                                if st.button("❌ Cancelar", key=f"btn_cancelar_{indice}"):
                                    st.session_state[chave_confirmacao] = False
                                    st.rerun()
                    st.markdown(
                        "<hr style='border-top: 1px dashed #333; margin-top:1rem; margin-bottom:1rem;'/>", unsafe_allow_html=True)
            else:
                st.info(
                    "ℹ️ Nenhum registro ativo encontrado para os filtros selecionados.")
        else:
            st.info("ℹ️ O banco de dados está limpo e sem demandas pendentes!")
