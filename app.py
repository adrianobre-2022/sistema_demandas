import streamlit as st
import os
import pandas as pd
import datetime
import hashlib
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

st.set_page_config(page_title="E o que falta?", page_icon="🔍", layout="centered")

# --- CAPTURADOR INVISÍVEL DE PEGADA DIGITAL ANTI-FRAUDE ---
def obter_pegada_digital():
    try:
        headers = st.context.headers
        ip = headers.get("X-Forwarded-For", "127.0.0.1").split(",")[0].strip()
        agente = headers.get("User-Agent", "Desconhecido")
        string_bruta = f"{ip}-{agente}"
        return hashlib.sha256(string_bruta.encode('utf-8')).hexdigest()
    except:
        return "pegada_generica_fallback"

# --- CUSTOMIZAÇÃO ESTÉTICA PREMIUM (VERDE FECHADO + TÍTULO CENTRALIZADO IMPACTANTE) ---
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
    
    /* BRANDING IMPONENTE CENTRALIZADO: Aumenta o tamanho da marca e centraliza sem quebras horizontal */
    h1 {
        font-size: 34px !important; 
        font-weight: 900 !important;
        text-align: center !important; 
        width: 100% !important;
        white-space: nowrap !important;
        margin-bottom: 1.5rem !important;
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

if "tela_atual" not in st.session_state: st.session_state.tela_atual = "home"
if "token_valido" not in st.session_state: st.session_state.token_valido = False
if "perfil_cliente" not in st.session_state: st.session_state.perfil_cliente = None
if "busca_ativa" not in st.session_state: st.session_state.busca_ativa = False
if "dados_grafico" not in st.session_state: st.session_state.dados_grafico = None
if "aba_consumidor" not in st.session_state: st.session_state.aba_consumidor = "menu_triagem"

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
            st.session_state.aba_consumidor = "me# --- TELA: FORMULÁRIO DO CONSUMIDOR ---
elif st.session_state.tela_atual == "consumidor":
    col_nav1, col_nav2 = st.columns(2, gap="small")
    with col_nav1:
        if st.button("🏠 Ir para Home", key="nav_home_simetrico", use_container_width=True):
            st.session_state.tela_atual = "home"; st.rerun()
    with col_nav2:
        if st.session_state.aba_consumidor != "menu_triagem":
            if st.button("🗂️ Mudar Categoria", key="nav_categoria_simetrico", use_container_width=True):
                st.session_state.aba_consumidor = "menu_triagem"; st.rerun()
                
    st.title("🔍 E o que falta?")

    # --- ENGENHARIA DE USABILIDADE: LOCALIZAÇÃO EXCLUSIVA DA TRIAGEM INICIAL ---
    if st.session_state.aba_consumidor == "menu_triagem":
        st.markdown("##### 📍 Onde você está agora?")
        regiao_final = st.text_input(
            label="Localização Única do Morador",
            placeholder="Ex: São Paulo/SP - Centro",
            key="input_regiao_via_unica",
            label_visibility="collapsed"
        )
        st.write("Escolha o tipo de ausência que você quer registrar no bairro ou comunidade:")
        if st.button("📦 PRODUTO OU MARCA EM FALTA\n(Falta nas gôndolas de mercados, farmácias...)", use_container_width=True, key="triagem_prod"): 
            st.session_state.aba_consumidor = "produto"; st.rerun()
        st.write("")
        if st.button("🏪 NOVO COMÉRCIO OU SERVIÇO LOCAL\n(Falta de lavanderia, sapataria, padaria...)", use_container_width=True, key="triagem_serv"): 
            st.session_state.aba_consumidor = "servico"; st.rerun()
        st.write("")
        if st.button("🏛️ INFRAESTRUTURA OU ZELADORIA PÚBLICA\n(Falha na iluminação, buracos no asfalto...)", use_container_width=True, key="triagem_infra"): 
            st.session_state.aba_consumidor = "infra"; st.rerun()

    # --- NOS FORMULÁRIOS INTERNOS, A PERGUNTA DE LOCALIZAÇÃO SOME POR COMPLETO ---
    else:
        if st.session_state.aba_consumidor == "produto":
            st.markdown("### 📦 Produto / Marca\n##### *Mapeando falhas de estoque e gôndolas vazias na região.*")
            label_item, placeholder_item = "Qual produto ou marca você buscou e não encontrou?", "Ex: Leite condensado marca X, ração de gato..."
            label_local, placeholder_local = "Em qual estabelecimento isso ocorreu?", "Ex: Nome do mercado, farmácia, padaria..."
            label_contato, tipo_envio = "Quer ser avisado caso o estoque seja reposto ou outra loja ofereça? (Opcional)", "Produto / Marca"
        elif st.session_state.aba_consumidor == "servico":
            st.markdown("### 🏪 Novo Comércio / Serviço\n##### *Mapeando oportunidades de novos negócios e conveniência.*")
            label_item, placeholder_item = "Qual tipo de comércio ou serviço falta neste bairro/comunidade?", "Ex: Sapataria, lavanderia, costureira, padaria..."
            label_local, placeholder_local = "Em qual rua, travessa, faculdade ou ponto isso faz falta?", "Ex: Avenida Principal, Bloco C da Faculdade X..."
            label_contato, tipo_envio = "Quer ser avisado caso este serviço seja aberto ou oferecido? (Opcional)", "Serviço Local / Novo Estabelecimento"
        else:
            st.markdown("### 🏛️ Infraestrutura / Zeladoria\n##### *Mapeando melhorias urbanas e cobranças aos órgãos públicos.*")
            label_item, placeholder_item = "Qual carência de infraestrutura/manutenção você identificou?", "Ex: Falha na iluminação, falta de médicos..."
            label_local, placeholder_local = "Qual o ponto de referência ou localidade exata?", "Ex: Posto de saúde do bairro Y, Rua Z..."
            label_contato, tipo_envio = "Quer ser avisado caso esta manutenção pública seja realizada? (Opcional)", "Serviço Público / Infraestrutura"
        st.write("")

        with st.form(key="formulario_dinamico_consumidor", clear_on_submit=True):
            item_solicitado = st.text_input(label=label_item, placeholder=placeholder_item, key="input_item")
            local_ocorrencia = st.text_input(label=label_local, placeholder=placeholder_local, key="input_local")
            observacao_usuario = st.text_area(label="Mais detalhes ou observações sobre o problema (Opcional):", placeholder="Ex: Detalhe o ocorrido de forma construtiva...", key="input_obs")
            contato_usuario = st.text_input(label=label_contato, placeholder="Ex: Seu e-mail ou WhatsApp...", key="input_contato")
            st.write("")
            botao_enviar = st.form_submit_button("Registrar Ocorrência", use_container_width=True)
nu_triagem"
            st.rerun()
    with col2:
        if st.button("📊 Sou Comerciante / Gestor\n(Acessar Painel)", use_container_width=True, key="btn_ir_comerciante"):
            st.session_state.tela_atual = "autenticacao"
            st.rerun()
        if botao_enviar:
            if item_solicitado and local_ocorrencia:
                texto_usuario, local_usuario = item_solicitado.strip().lower(), local_ocorrencia.strip().lower()
                obs_texto = observacao_usuario.strip().lower() if observacao_usuario else ""
                
                palavras_ofensivas = ["porra", "caralho", "puta", "merda", "bosta", "vai tomar", "fudeu", "ladrão", "roubo", "safado", "vagabundo"]
                termos_politicos_proibidos = ["pec", "deputado", "senado", "senador", "presidente", "governador", "partido", "impeachment", "voto", "eleição", "politica", "político"]
                excecoes_contexto = ["saco de lixo", "sacos de lixo", "lixeira", "pá de lixo", "coleta de lixo"]
                
                contem_bloqueio, mensagem_erro = False, ""
                if any(p in texto_usuario for p in palavras_ofensivas) or any(p in local_usuario for p in palavras_ofensivas) or any(p in obs_texto for p in palavras_ofensivas):
                    contem_bloqueio = True; mensagem_erro = "⚠️ O sistema identificou termos impróprios ou linguagem ofensiva. Por favor, reescreva de forma construtiva."
                if any(p in texto_usuario for p in termos_politicos_proibidos) or any(p in local_usuario for p in termos_politicos_proibidos) or any(p in obs_texto for p in termos_politicos_proibidos):
                    contem_bloqueio = True; mensagem_erro = "⚠️ O portal é focado estritamente em zeladoria e carências locais. Manifestações político-ideológicas nacionais devem ser direcionadas às ouvidorias competentes."
                if "lixo" in texto_usuario or "lixo" in local_usuario:
                    if not any(e in texto_usuario for e in excecoes_contexto) and not any(e in local_usuario for e in excecoes_contexto):
                        contem_bloqueio = True; mensagem_erro = "⚠️ O sistema identificou termos impróprios ou linguagem ofensiva. Por favor, reescreva de forma construtiva."

                palavras_infra = ["rua", "praça", "iluminação", "poste", "asfalto", "médico", "ônibus", "hospital", "bueiro", "segurança", "luz", "polícia", "posto de saúde"]
                palavras_produto = ["leite", "fralda", "ração", "refrigerante", "cerveja", "sabão", "remédio", "arroz", "feijão", "café", "açúcar"]
                
                erro_detectado = False
                if contem_bloqueio:
                    st.error(mensagem_erro); erro_detectado = True
                elif tipo_envio == "Produto / Marca" and any(p in texto_usuario for p in palavras_infra):
                    st.error("⚠️ Ops! Parece um problema de Infraestrutura Pública. Modifique no menu principal."); erro_detectado = True
                elif tipo_envio == "Serviço Local / Novo Estabelecimento" and any(p in texto_usuario for p in palavras_produto):
                    st.error("⚠️ Ops! Parece a falta de um produto de mercado. Modifique no menu principal."); erro_detectado = True
                    
                if not erro_detectado:
                    try:
                        # Resgata a assinatura única anônima do dispositivo para a trava de antifraude
                        hash_dispositivo = obter_pegada_digital()
                        
                        regiao_salva = st.session_state.get("input_regiao_via_unica", "São Paulo/SP - Centro")
                        texto_regiao = regiao_salva.strip().title() if regiao_salva else "São Paulo/SP - Centro"
                        
                        # Extração automatizada e imutável de UF
                        estado_detectado = "SP"
                        if "/" in texto_regiao:
                            try:
                                partes_uf = texto_regiao.split("/")
                                if len(partes_uf) > 1:
                                    estado_detectado = partes_uf[1].split("-")[0].strip().upper()[:2]
                            except:
                                estado_detectado = "SP"
                        
                        local_formatado = local_ocorrencia.strip().title()
                        local_data = supabase.table("locais_destino").insert({
                            "nome_exibicao": local_formatado, "regiao_cidade": texto_regiao, "regiao_estado": estado_detectado
                        }).execute()
                        local_id = local_data.data[0]["id"] if local_data.data and len(local_data.data) > 0 else None
                        
                        if local_id:
                            item_formatado = item_solicitado.strip().title()
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
                                "local_id": local_id, "item_solicitado": item_formatado, "tipo_carencia": tipo_envio, "status": "Pendente",
                                "contato_aviso": contato_usuario.strip() if contato_usuario else None,
                                "detalhes_adicionais": texto_obs, "observacao_detalhe": texto_obs, "sub_segmento": segmento_detectado,
                                "pegada_digital": hash_dispositivo  # Carimba a assinatura para auditoria e travas
                            }).execute()
                            
                            st.success("✅ Registro computado e salvo na nuvem com anonimato garantido!")
                            import time; time.sleep(1.5)
                            st.session_state.aba_consumidor = "menu_triagem"; st.rerun()
                    except Exception as e: st.error(f"⚠️ Erro técnico detalhado: {str(e)}")
            else: st.warning("⚠️ Por favor, preencha os campos obrigatórios antes de enviar.")

    st.write("")
    st.markdown("### 🏆 Impactos Recentes no Bairro")
    try:
        resolvidos = supabase.table("relatos_escassez").select("item_solicitado, locais_destino(nome_exibicao)").eq("status", "Atendido").limit(3).execute()
        if resolvidos.data and len(resolvidos.data) > 0:
            for item in resolvidos.data:
                if item.get("locais_destino"): st.info(f"✅ **{item['locais_destino']['nome_exibicao']}** repôs o estoque: **{item['item_solicitado']}**!")
        else: st.write("ℹ️ Nenhuma benfeitoria registrada nos últimos dias.")
    except: pass
# --- TELA: AUTENTICAÇÃO POR TOKEN ---
elif st.session_state.tela_atual == "autenticacao":
    if st.button("⬅️ Voltar ao Menu Principal", key="btn_voltar_aut"):
        st.session_state.tela_atual = "home"
        st.session_state.token_valido = False
        st.session_state.perfil_cliente = None
        st.rerun()
        
    st.title("🔒 Área Restrita de Inteligência")
    st.markdown("##### *Insira o seu token de acesso corporativo para liberar os relatórios.*")
    st.write("---")
    
    token_inserido = st.text_input(label="Token de Acesso:", type="password", placeholder="Digite seu token de acesso...")
    st.write("")
    botao_validar = st.button("Validar Credenciais e Acessar", use_container_width=True, key="btn_validar_token_hibrido")
    
    if botao_validar or (token_inserido and not st.session_state.token_valido):
        if token_inserido in ["COMERCIO10", "SUPER_VILA_77"]:
            st.session_state.token_valido = True; st.session_state.perfil_cliente = "comerciante"; st.session_state.tela_atual = "comerciante"; st.rerun()
        elif token_inserido == "SAUDE20":
            st.session_state.token_valido = True; st.session_state.perfil_cliente = "saude"; st.session_state.tela_atual = "comerciante"; st.rerun()
        elif token_inserido == "PET30":
            st.session_state.token_valido = True; st.session_state.perfil_cliente = "petshop"; st.session_state.tela_atual = "comerciante"; st.rerun()
        elif token_inserido == "BELEZA40":
            st.session_state.token_valido = True; st.session_state.perfil_cliente = "beleza"; st.session_state.tela_atual = "comerciante"; st.rerun()
        elif token_inserido == "INVEST20":
            st.session_state.token_valido = True; st.session_state.perfil_cliente = "investidor"; st.session_state.tela_atual = "comerciante"; st.rerun()
        elif token_inserido == "GESTOR30":
            st.session_state.token_valido = True; st.session_state.perfil_cliente = "gestor"; st.session_state.tela_atual = "comerciante"; st.rerun()
        elif token_inserido != "":
            st.error("❌ Token inválido ou expirado. Verifique as credenciais e tente novamente.")
# --- TELA: PAINEL DE DECISÃO ESTRATÉGICA (B2B) ---
elif st.session_state.tela_atual == "comerciante":
    if not st.session_state.token_valido:
        st.session_state.tela_atual = "home"; st.rerun()

    if st.button("⬅️ Sair do Painel (Logoff)", key="btn_voltar_com"):
        st.session_state.tela_atual = "home"; st.session_state.token_valido = False
        st.session_state.perfil_cliente = None; st.session_state.busca_ativa = False
        st.session_state.dados_grafico = None; st.rerun()
        
    st.title("📊 Painel de Decisão Estratégica")
    
    loja_alvo_prioridade = "Mercadinho Do Bairro" if st.session_state.perfil_cliente == "comerciante" else ""
    espectador_analitico = st.session_state.perfil_cliente in ["investidor", "gestor"]
    
    if st.session_state.perfil_cliente == "comerciante":
        st.markdown("##### 🏪 *Nível de Acesso: Varejo Local (Foco em Gôndolas e Supermercados)*")
        opcoes_filtro = ["Apenas Produtos/Marcas (Varejo)", "🎯 Marketplace Reverso (Oportunidades Gerais do Bairro)"]
    elif st.session_state.perfil_cliente == "saude":
        st.markdown("##### 🩺 *Nível de Acesso: Saúde & Bem-Estar (Foco em Clínicas e Especialistas)*")
        opcoes_filtro = ["Apenas Serviços de Saúde e Clínicas", "🎯 Marketplace Reverso (Oportunidades Gerais do Bairro)"]
    elif st.session_state.perfil_cliente == "petshop":
        st.markdown("##### 🐶 *Nível de Acesso: Petshop & Veterinária (Foco em Produtos e Serviços Pet)*")
        opcoes_filtro = ["Apenas Produtos e Serviços Pet", "🎯 Marketplace Reverso (Oportunidades Gerais do Bairro)"]
    elif st.session_state.perfil_cliente == "beleza":
        st.markdown("##### 💈 *Nível de Acesso: Beleza & Estética (Foco em Salões e Barbearias)*")
        opcoes_filtro = ["Apenas Serviços de Estética e Beleza", "🎯 Marketplace Reverso (Oportunidades Gerais do Bairro)"]
    elif st.session_state.perfil_cliente == "investidor":
        st.markdown("##### 💼 *Nível de Acesso: Investidor e Expansão (Mapeamento de Vazios Comerciais)*")
        opcoes_filtro = ["Oportunidades de Novos Negócios (Serviços)"]
    else:
        st.markdown("##### 🏛️ *Nível de Acesso: Gestão Pública e Imprensa (Foco em Infraestrutura Urbana)*")
        opcoes_filtro = ["Infraestrutura Urbana (Setor Público)"]
        
    st.write("---")
    filtro_frente = st.selectbox(label="Selecione a Frente de Inteligência:", options=opcoes_filtro, key="selectbox_frente")
    termo_busca = st.text_input(label="Refinar por palavra-chave ou estabelecimento (Opcional):", placeholder="Digite para filtrar a lista abaixo...", key="input_busca_painel")

    # --- MOTOR DE CARREGAMENTO AUTOMÁTICO EM BACKGROUND ---
    if not st.session_state.busca_ativa or st.session_state.dados_grafico is None:
        st.session_state.busca_ativa = True
        try:
            resposta = supabase.table("relatos_escassez").select("id, item_solicitado, tipo_carencia, data_registro, status, detalhes_adicionais, observacao_detalhe, sub_segmento, pegada_digital, contato_aviso, locais_destino(nome_exibicao, regiao_cidade)").execute()
            dados_limpos = []
            agora = datetime.datetime.now(datetime.timezone.utc)
            
            if resposta.data and len(resposta.data) > 0:
                for registro in resposta.data:
                    if registro.get("locais_destino"):
                        sub_seg = str(registro.get("sub_segmento", "Geral")).strip()
                        cat_bruta = str(registro.get("tipo_carencia", "Produto / Marca")).strip()
                        
                        if st.session_state.perfil_cliente in ["comerciante", "saude", "petshop", "beleza"]:
                            if "Infraestrutura" in cat_bruta or "Público" in cat_bruta: continue
                        
                        if "Marketplace" not in filtro_frente and not espectador_analitico:
                            if st.session_state.perfil_cliente == "comerciante" and sub_seg not in ["Supermercado", "Geral"]: continue
                            elif st.session_state.perfil_cliente == "saude" and sub_seg not in ["Saude", "Geral"]: continue
                            elif st.session_state.perfil_cliente == "petshop" and sub_seg not in ["Petshop", "Geral"]: continue
                            elif st.session_state.perfil_cliente == "beleza" and sub_seg not in ["Beleza", "Geral"]: continue
                        
                        if st.session_state.perfil_cliente == "investidor" and sub_seg == "Supermercado": continue
                            
                        idade_dias = 0
                        data_str = registro.get("data_registro")
                        if data_str:
                            try:
                                data_limpa = data_str.replace("Z", "+00:00")
                                data_reg = datetime.datetime.fromisoformat(data_limpa)
                                if data_reg.tzinfo is None: data_reg = data_reg.replace(tzinfo=datetime.timezone.utc)
                                idade_dias = max(0, (agora - data_reg).days)
                            except: idade_dias = 0
                        
                        texto_detalhe = registro.get("observacao_detalhe") or registro.get("detalhes_adicionais") or ""
                        dados_limpos.append({
                            "ID": registro["id"], "O que Falta": registro["item_solicitado"].strip().title(), 
                            "Categoria": "Produto / Marca" if "Produto" in cat_bruta else ("Serviço Local / Novo Estabelecimento" if "Serviço" in cat_bruta else "Serviço Público / Infraestrutura"),
                            "Local/Referência": registro["locais_destino"]["nome_exibicao"], "Cidade": registro["locais_destino"]["regiao_cidade"],
                            "Dias": idade_dias, "Observação": texto_detalhe, "SubSegmento": sub_seg,
                            "Pegada": registro.get("pegada_digital") or f"anon_{registro['id']}", "Contato": registro.get("contato_aviso") or ""
                        })
            
            if not dados_limpos:
                dados_limpos = [
                    {"ID": 991, "O que Falta": "Leite Desnatado Parmalat 1L", "Categoria": "Produto / Marca", "Local/Referência": "Mercadinho Do Bairro", "Cidade": "São Paulo/SP - Centro", "Dias": 4, "Observação": "Falta nas prateleiras toda quarta.", "SubSegmento": "Supermercado", "Pegada": "hash1", "Contato": "11999999999"},
                    {"ID": 992, "O que Falta": "Feijão Preto Tipo 1 Camil", "Categoria": "Produto / Marca", "Local/Referência": "Supermercado Xavier", "Cidade": "São Paulo/SP - Centro", "Dias": 1, "Observação": "Gôndola zerada desde cedo.", "SubSegmento": "Supermercado", "Pegada": "hash2", "Contato": ""},
                    {"ID": 993, "O que Falta": "Lingerie Vermelha Rendada", "Categoria": "Produto / Marca", "Local/Referência": "Bairro Popular", "Cidade": "São Paulo/SP - Centro", "Dias": 2, "Observação": "Falta uma loja de roupas íntimas focada.", "SubSegmento": "Geral", "Pegada": "hash3", "Contato": "11888888888"},
                    {"ID": 994, "O que Falta": "Lavanderia Expressa Auto-Serviço", "Categoria": "Serviço Local / Novo Estabelecimento", "Local/Referência": "Avenida Das Palmeiras", "Cidade": "São Paulo/SP - Centro", "Dias": 45, "Observação": "Prédios novos sem lavanderia por perto.", "SubSegmento": "Geral", "Pegada": "hash4", "Contato": ""},
                    {"ID": 995, "O que Falta": "Ração Premium Gatos Castrados Royal", "Categoria": "Produto / Marca", "Local/Referência": "Petshop Bairro Alto", "Cidade": "São Paulo/SP - Centro", "Dias": 3, "Observação": "Sumiu do estoque.", "SubSegmento": "Petshop", "Pegada": "hash5", "Contato": ""},
                    {"ID": 996, "O que Falta": "Sapataria E Conserto De Salto", "Categoria": "Serviço Local / Novo Estabelecimento", "Local/Referência": "Bairro Popular", "Cidade": "São Paulo/SP - Centro", "Dias": 14, "Observação": "Moradores precisam viajar longe para arrumar sapatos.", "SubSegmento": "Geral", "Pegada": "hash6", "Contato": ""},
                    {"ID": 997, "O que Falta": "Manutenção De Iluminação Pública", "Categoria": "Serviço Público / Infraestrutura", "Local/Referência": "Rua das Flores, 40", "Cidade": "São Paulo/SP - Centro", "Dias": 2, "Observação": "Poste apagado.", "SubSegmento": "Geral", "Pegada": "hash7", "Contato": ""}
                ]
                if st.session_state.perfil_cliente == "comerciante": dados_limpos = [d for d in dados_limpos if d["SubSegmento"] in ["Supermercado", "Geral"] and d["Categoria"] != "Serviço Público / Infraestrutura"]
                elif st.session_state.perfil_cliente == "saude": dados_limpos = [d for d in dados_limpos if d["SubSegmento"] in ["Saude", "Geral"] and d["Categoria"] != "Serviço Público / Infraestrutura"]
                elif st.session_state.perfil_cliente == "petshop": dados_limpos = [d for d in dados_limpos if d["SubSegmento"] in ["Petshop", "Geral"] and d["Categoria"] != "Serviço Público / Infraestrutura"]
                elif st.session_state.perfil_cliente == "beleza": dados_limpos = [d for d in dados_limpos if d["SubSegmento"] in ["Beleza", "Geral"] and d["Categoria"] != "Serviço Público / Infraestrutura"]
                elif st.session_state.perfil_cliente == "investidor": dados_limpos = [d for d in dados_limpos if d["SubSegmento"] != "Supermercado" and d["Categoria"] == "Serviço Local / Novo Estabelecimento"]
                elif st.session_state.perfil_cliente == "gestor": dados_limpos = [d for d in dados_limpos if d["Categoria"] == "Serviço Público / Infraestrutura"]
                
            st.session_state.dados_grafico = pd.DataFrame(dados_limpos)
        except Exception as e: st.error(f"⚠️ Erro técnico: {str(e)}")
    if st.session_state.busca_ativa and st.session_state.dados_grafico is not None:
        df = st.session_state.dados_grafico
        if not df.empty:
            df_filtrado = df
            if filtro_frente == "Apenas Produtos/Marcas (Varejo)": df_filtrado = df[df['Categoria'] == "Produto / Marca"]
            elif filtro_frente == "Oportunidades de Novos Negócios (Serviços)": df_filtrado = df[df['Categoria'] == "Serviço Local / Novo Estabelecimento"]
            elif filtro_frente == "Infraestrutura Urbana (Setor Público)": df_filtrado = df[df['Categoria'] == "Serviço Público / Infraestrutura"]

            if termo_busca:
                df_filtrado = df_filtrado[df_filtrado['O que Falta'].str.contains(termo_busca, case=False) | df_filtrado['Local/Referência'].str.contains(termo_busca, case=False)]

            if not df_filtrado.empty:
                # Carimba o peso prioritário para a loja do cliente
                df_filtrado['É_Minha_Loja'] = df_filtrado['Local/Referência'].apply(lambda x: 1 if x == loja_alvo_prioridade else 0)
                
                # --- INTERFACE 1: VISÃO ANALÍTICA E ESTATÍSTICA (INVESTIDORES E GESTORES) ---
                if espectador_analitico:
                    # Agrupa e conta por PEGADAS DIGITAIS ÚNICAS, blindando a veracidade contra spam
                    df_analitico = df_filtrado.groupby(["O que Falta", "Categoria", "Cidade"]).agg(
                        Clientes_Unicos=("Pegada", "nunique"),
                        Alertas_Totais=("ID", "count"),
                        Maior_Espera=("Dias", "max")
                    ).sort_values(by="Clientes_Unicos", ascending=False).reset_index()

                    st.markdown("#### 📥 Exportar Relatório de Expansão Estatística")
                    st.download_button(label="📥 Baixar Relatório de Vazios Comerciais (PDF)", data=b"PDF_DUMMY", file_name=f"expansao_{st.session_state.perfil_cliente}.pdf", mime="application/pdf", key="btn_pdf_analitico")
                    
                    st.write("---")
                    st.markdown("#### 📈 Ranking de Oportunidades por Clientes Únicos")
                    for indice, linha in df_analitico.iterrows():
                        item_nome = linha['O que Falta']
                        clientes = int(linha['Clientes_Unicos'])
                        alertas = int(linha['Alertas_Totais'])
                        
                        classe_tag = "tag-calor-alta" if clientes >= 5 else ("tag-calor-media" if clientes >= 2 else "tag-calor-baixa")
                        label_tag = f"🔥 VAZIO CRÍTICO • {clientes} Clientes Únicos" if clientes >= 5 else (f"⚠️ OPORTUNIDADE • {clientes} Clientes Únicos" if clientes >= 2 else f"🔹 INICIAL • {clientes} Cliente Único")
                        
                        st.markdown(f"""
                            <div class="bloco-lista-premium">
                                <span class="{classe_tag}">{label_tag}</span>
                                <b style="color: #FFFFFF; font-size: 16px;">🏢 Vazio de: {item_nome}</b>
                                <div style="margin-top: 0.5rem; color: #aaaaaa; font-size: 13px;">⏱️ Demanda acumulada de {alertas} relatos • Espera máxima de {linha['Maior_Espera']} dias</div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        detalhes_item = df_filtrado[df_filtrado['O que Falta'] == item_nome]
                        st.write("📍 **Focos Geográficos Registrados:**")
                        for _, sub_linha in detalhes_item.iterrows():
                            st.markdown(f"  * {sub_linha['Local/Referência']} ({sub_linha['Cidade']}) — *\"_{sub_linha['Observação']}_\"*")
                        st.markdown("<hr style='border-top: 1px dashed #333; margin: 1rem 0;'/>", unsafe_allow_html=True)

                # --- INTERFACE 2: VISÃO OPERACIONAL E MARKETPLACE REVERSO (LOJISTAS B2B) ---
                else:
                    df_agrupado = df_filtrado.groupby(["O que Falta", "Categoria", "Cidade"]).agg(
                        Volume_Total=("ID", "count"), Menor_Idade=("Dias", "min"), Foco_Dono=("É_Minha_Loja", "max")
                    ).sort_values(by=["Foco_Dono", "Volume_Total"], ascending=[False, False]).reset_index()

                    st.markdown("#### 📥 Exportar Inteligência de Gôndola")
                    st.download_button(label="📥 Baixar Relatório Gerencial (PDF)", data=b"PDF", file_name="relatorio.pdf", mime="application/pdf", key="btn_pdf_operacional")
                    
                    st.write("---")
                    st.markdown("#### 📈 Detalhamento das Demandas Ativas")
                    
                    for indice, linha in df_agrupado.iterrows():
                        item_nome = linha['O que Falta']
                        volume = float(linha['Volume_Total'])
                        sou_alvo = int(linha['Foco_Dono'])
                        
                        if "Marketplace" in filtro_frente:
                            classe_tag = "tag-calor-media"
                            label_tag = f"🎯 MARKETPLACE REVERSO • {int(volume)} Clientes Buscando"
                        elif sou_alvo == 1:
                            classe_tag = "tag-calor-alta"
                            label_tag = f"🎯 SEU MERCADO • {int(volume)} Pedidos"
                        else:
                            classe_tag = "tag-calor-baixa"
                            label_tag = f"🌍 CONCORRÊNCIA • {int(volume)} Pedidos"
                        
                        st.markdown(f'<div class="bloco-lista-premium"><span class="{classe_tag}">{label_tag}</span><b style="color: #FFFFFF; font-size: 16px;">📦 {item_nome}</b><div style="margin-top: 0.5rem; color: #aaaaaa; font-size: 13px;">⏱️ Último alerta há {linha["Menor_Idade"]} dias</div></div>', unsafe_allow_html=True)
                        
                        detalhes_item = df_filtrado[df_filtrado['O que Falta'] == item_nome]
                        for _, sub_linha in detalhes_item.iterrows():
                            sub_id = sub_linha['ID']
                            sub_local = sub_linha['Local/Referência']
                            contato_morador = sub_linha['Contato']
                            
                            prefixo_local = f"🔥 **SEU ESTABELECIMENTO:** {sub_local}" if sub_local == loja_alvo_prioridade else f"📍 **Oportunidade captada no:** {sub_local}"
                            st.markdown(f"{prefixo_local} ({sub_linha['Cidade']})")
                            
                            if sub_linha['Observação']: st.info(f"💬 *Relato:* \"{sub_linha['Observação']}\"")
                            
                            if contato_morador and ("Marketplace" in filtro_frente or sub_local != loja_alvo_prioridade):
                                st.success(f"📱 **Cliente Faminto Disponível!** Ofereça o item pelo WhatsApp: `{contato_morador}`")
                            
                            chave_confirmacao = f"confirma_baixa_{sub_id}"
                            if chave_confirmacao not in st.session_state: st.session_state[chave_confirmacao] = False
                            
                            if not st.session_state[chave_confirmacao]:
                                if st.button(f"✅ Marcar como Resolvido no {sub_local}", key=f"btn_pre_{sub_id}"):
                                    st.session_state[chave_confirmacao] = True; st.rerun()
                            else:
                                st.warning(f"⚠️ Confirmar reposição de estoque?")
                                col_b1, col_b2 = st.columns(2)
                                with col_b1:
                                    if st.button("🚨 Confirmar", key=f"btn_real_{sub_id}"):
                                        supabase.table("relatos_escassez").update({"status": "Atendido"}).eq("id", sub_id).execute()
                                        st.success("🎉 Atualizado!"); import time; time.sleep(1)
                                        st.session_state[chave_confirmacao] = False; st.session_state.busca_ativa = False; st.rerun()
                                with col_b2:
                                    if st.button("❌ Cancelar", key=f"btn_cancelar_{sub_id}"): st.session_state[chave_confirmacao] = False; st.rerun()
                    st.markdown("<hr style='border-top: 1px dashed #333; margin-top:1rem; margin-bottom:1rem;'/>", unsafe_allow_html=True)
            else: st.info("ℹ️ Nenhum registro ativo encontrado.")
        else: st.info("ℹ️ O banco de dados está limpo!")