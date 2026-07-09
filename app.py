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

st.set_page_config(page_title="Sistema de Pesquisas",
                   page_icon="🔍", layout="centered")

# --- CUSTOMIZAÇÃO ESTÉTICA PREMIUM (IDENTIDADE VISUAL E ACESSIBILIDADE WCAG) ---
st.markdown("""
    <style>
    /* Força o fundo escuro de alta absorção de luz */
    .stApp {
        background-color: #121212 !important;
        color: #FFFFFF !important;
    }
    /* Força subtextos e labels a ficarem brancos puros para contraste */
    .stWidgetFormLabel, label, p, .stMarkdown, [data-testid="stWidgetLabel"] {
        color: #FFFFFF !important;
    }
    /* CORREÇÃO DE ACESSIBILIDADE WCAG: Todos os botões (Normais, Enviar e Download) */
    .stButton>button, .stFormSubmitButton>button, [data-testid="stDownloadButton"]>button {
        background-color: #00B359 !important;
        color: #000000 !important;
        font-weight: 900 !important; /* Negrito ultra destacado */
        border-radius: 12px !important;
        border: none !important;
        padding: 0.8rem 1rem !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        width: 100% !important;
    }
    .stButton>button:hover, .stFormSubmitButton>button:hover, [data-testid="stDownloadButton"]>button:hover {
        background-color: #00803b !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.4) !important;
    }
    /* Customização dos campos de digitação */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 10px !important;
        background-color: #1E1E1E !important;
        color: white !important;
        border: 1px solid #444444 !important;
    }
    /* Cards Sanfona integrados ao tema escuro sem quebras */
    .stExpander {
        background-color: #1E1E1E !important;
        border-left: 5px solid #00B359 !important;
        border-radius: 10px !important;
        margin-bottom: 0.8rem !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
    }
    /* Estilo exclusivo das Tags de Calor Dinâmicas para o Celular */
    .tag-calor-alta {
        background-color: #ff3333;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-weight: bold;
        font-size: 13px;
        float: right;
    }
    .tag-calor-media {
        background-color: #ff9933;
        color: black;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-weight: bold;
        font-size: 13px;
        float: right;
    }
    .tag-calor-baixa {
        background-color: #3399ff;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-weight: bold;
        font-size: 13px;
        float: right;
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

# Inicializa as variáveis na memória do navegador
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
        placeholder_item = "Ex: Nome do produto, marca específica, ração do pet..."
        label_local = "Em qual estabelecimento isso ocorreu?"
        placeholder_local = "Ex: Nome do mercadinho, farmácia, petshop..."
    elif tipo_selecionado == "Serviço Local / Novo Estabelecimento":
        label_item = "Qual tipo de comércio ou serviço falta neste bairro?"
        placeholder_item = "Ex: Sapataria, lavanderia, costureira, padaria..."
        label_local = "Em qual rua, travessa ou pedaço do bairro isso faz falta?"
        placeholder_local = "Ex: Bairro Centro, Próximo à praça principal, Avenida X..."
    else:
        label_item = "Qual carência de infraestrutura/manutenção você identificou?"
        placeholder_item = "Ex: Falha na iluminação, falta de médicos, linha de ônibus ruim..."
        label_local = "Qual o ponto de referência ou localidade exata?"
        placeholder_local = "Ex: Posto de saúde do bairro Y, Praça da igreja, Rua Z..."

    with st.form(key="formulario_demandas", clear_on_submit=True):
        item_solicitado = st.text_input(
            label=label_item, placeholder=placeholder_item, key="input_item")
        local_ocorrencia = st.text_input(
            label=label_local, placeholder=placeholder_local, key="input_local")

        observacao_usuario = st.text_area(
            label="Mais detalhes ou observações sobre o problema (Opcional):",
            placeholder="Ex: Detalhe o ocorrido de forma construtiva para ajudar a triagem...",
            key="input_obs"
        )

        contato_usuario = st.text_input(
            label="Quer ser avisado quando o estoque for reposto? (Opcional)",
            placeholder="Ex: Seu e-mail ou WhatsApp...",
            key="input_contato"
        )

        st.write("")
        botao_enviar = st.form_submit_button(
            "Registrar Ocorrência", use_container_width=True)

    if botao_enviar:
        if item_solicitado and local_ocorrencia:
            texto_usuario = item_solicitado.strip().lower()
            local_usuario = local_ocorrencia.strip().lower()
            obs_texto = observacao_usuario.strip().lower() if observacao_usuario else ""

            # --- BLINDAGEM SESSÃO 5: FILTRO DE OFENSAS E PROTESTOS POLÍTICOS ---
            palavras_ofensivas = ["porra", "caralho", "puta", "merda", "lixo",
                                  "bosta", "vai tomar", "fudeu", "ladrão", "safado", "vagabundo"]

            # BARREIRA ANTI-PEC: Identifica ativismo ideológico legislativo nacional
            termos_politicos_proibidos = ["pec", "deputado", "senado", "senador", "presidente",
                                          "governador", "partido", "impeachment", "voto", "eleição", "politica", "político"]

            excecoes_contexto = ["saco de lixo", "sacos de lixo",
                                 "lixeira", "pá de lixo", "coleta de lixo"]

            contem_bloqueio = False
            mensagem_erro = ""

            # Varredura de segurança contra insultos e palavrões
            if any(p in texto_usuario for p in palavras_ofensivas) or any(p in local_usuario for p in palavras_ofensivas) or any(p in obs_texto for p in palavras_ofensivas):
                contem_bloqueio = True
                mensagem_erro = "⚠️ O sistema identificou termos impróprios ou linguagem ofensiva. Escreva seu relato focado no item de forma construtiva."

            # Varredura de segurança contra militância ideológica nacional
            if any(p in texto_usuario for p in termos_politicos_proibidos) or any(p in local_usuario for p in termos_politicos_proibidos) or any(p in obs_texto for p in termos_politicos_proibidos):
                contem_bloqueio = True
                mensagem_erro = "⚠️ O portal é focado estritamente em zeladoria e carências locais. Manifestações político-ideológicas nacionais ou legislativas (como PECs) devem ser direcionadas às ouvidorias do Senado ou Câmara."

            if "lixo" in texto_usuario or "lixo" in local_usuario:
                if not any(e in texto_usuario for e in excecoes_contexto) and not any(e in local_usuario for e in excecoes_contexto):
                    contem_bloqueio = True
                    mensagem_erro = "⚠️ O sistema identificou termos impróprios ou linguagem ofensiva. Escreva seu relato focado no item de forma construtiva."

            palavras_infra = ["rua", "praça", "iluminação", "poste", "asfalto", "médico",
                              "ônibus", "hospital", "bueiro", "segurança", "luz", "polícia", "posto de saúde"]
            palavras_produto = ["leite", "fralda", "ração", "refrigerante",
                                "cerveja", "sabão", "remédio", "arroz", "feijão", "café", "açúcar"]

            erro_detectado = False
            if contem_bloqueio:
                st.error(mensagem_erro)
                erro_detectado = True
            elif tipo_selecionado == "Produto / Marca" and any(p in texto_usuario for p in palavras_infra):
                st.error(
                    "⚠️ Ops! Parece um problema de Infraestrutura Pública. Modifique no topo.")
                erro_detectado = True
            elif tipo_selecionado == "Serviço Local / Novo Estabelecimento" and any(p in texto_usuario for p in palavras_produto):
                st.error(
                    "⚠️ Ops! Parece a falta de um produto de mercado. Modifique no topo.")
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

                        # --- CLASSIFICADOR SUB_SEGMENTO AUTOMÁTICO DO PYTHON ---
                        segmento_detectado = "Geral"
                        if any(p in texto_usuario for p in ["leite", "arroz", "feijão", "café", "açúcar", "refrigerante", "cerveja", "sabão"]):
                            segmento_detectado = "Supermercado"
                        elif any(p in texto_usuario for p in ["remédio", "xarope", "fralda", "pomada", "curativo"]):
                            segmento_detectado = "Farmácia"
                        elif any(p in texto_usuario for p in ["ração", "pet", "cachorro", "gato", "coleira"]):
                            segmento_detectado = "Petshop"
                        elif any(p in texto_usuario for p in ["pão", "bolo", "doce", "salgado", "padaria"]):
                            segmento_detectado = "Padaria"

                        supabase.table("relatos_escassez").insert({
                            "local_id": local_id,
                            "item_solicitado": item_formatado,
                            "tipo_carencia": tipo_selecionado,
                            "status": "Pendente",
                            "contato_aviso": contato_usuario.strip() if contato_usuario else None,
                            "observacao_detalhe": observacao_usuario.strip() if observacao_usuario else None,
                            "sub_segmento": segmento_detectado
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
        try:
            # Puxa a nova coluna observacao_detalhe da nuvem para entregar ao Gestor
            resposta = supabase.table("relatos_escassez").select(
                "id, item_solicitado, tipo_carencia, data_registro, status, observacao_detalhe, locais_destino(nome_exibicao, regiao_cidade)").eq("status", "Pendente").execute()

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

                            calculo_idade = (agora - data_reg).days
                            idade_dias = max(0, calculo_idade)
                            categoria = registro.get(
                                "tipo_carencia", "Produto / Marca")

                            manter_registro = False
                            if categoria == "Produto / Marca" and idade_dias <= 30:
                                manter_registro = True
                            elif categoria == "Serviço Local / Novo Estabelecimento" and idade_dias <= 365:
                                manter_registro = True
                            elif categoria == "Serviço Público / Infraestrutura" and idade_dias <= 180:
                                manter_registro = True

                            if manter_registro:
                                dados_limpos.append({
                                    "ID": registro["id"],
                                    "O que Falta": registro["item_solicitado"],
                                    "Categoria": categoria,
                                    "Local/Referência": registro["locais_destino"]["nome_exibicao"],
                                    "Cidade": registro["locais_destino"]["regiao_cidade"],
                                    "Dias": idade_dias,
                                    "Observação": registro.get("observacao_detalhe", "Sem observações registradas.")
                                })

                if dados_limpos:
                    st.session_state.dados_grafico = pd.DataFrame(dados_limpos)
                else:
                    st.session_state.dados_grafico = pd.DataFrame()
            else:
                st.session_state.dados_grafico = pd.DataFrame()
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
                # --- AGRAUPAMENTO INTELIGENTE POR PERFIL B2B ---
                if st.session_state.perfil_cliente == "comerciante":
                    df_agrupado = df_filtrado.groupby(["O que Falta", "Categoria", "Local/Referência", "Cidade", "Observação"]).agg(
                        Volume_Pedidos=("ID", "count"), Menor_Idade=("Dias", "min")
                    ).sort_values(by="Volume_Pedidos", ascending=False).reset_index()
                else:
                    df_agrupado = df_filtrado.groupby(["O que Falta", "Categoria", "Cidade", "Observação"]).agg(
                        Volume_Pedidos=("ID", "count"), Menor_Idade=("Dias", "min")
                    ).sort_values(by="Volume_Pedidos", ascending=False).reset_index()
                    df_agrupado["Local/Referência"] = "Mapeamento Consolidado da Região"

                # --- EXIBIÇÃO: RANKING DE CALOR NO TOPO ---
                st.markdown(
                    "#### 🔥 Termômetro de Demandas Reprimidas (Ranking)")
                st.write(
                    "##### *Análise em tempo real ordenada por volume de intenção de compra:*")

                for _, linha_rank in df_agrupado.iterrows():
                    volume = linha_rank['Volume_Pedidos']
                    if volume >= 7:
                        classe_tag = "tag-calor-alta"
                        label_tag = f"CRÍTICA • {volume} Pedidos"
                    elif volume >= 3:
                        classe_tag = "tag-calor-media"
                        label_tag = f"MODERADA • {volume} Pedidos"
                    else:
                        classe_tag = "tag-calor-baixa"
                        label_tag = f"INICIAL • {volume} Pedido"

                    st.markdown(f"""
                        <div style="background-color: #1E1E1E; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem; border: 1px solid #333;">
                            <span class="{classe_tag}">{label_tag}</span>
                            <b style="color: #FFFFFF; font-size: 15px;">📦 {linha_rank['O que Falta']}</b>
                        </div>
                    """, unsafe_allow_html=True)

                st.write("---")

                # --- EXPORTADOR EM FORMATO PDF UNIVERSAL TABULADO ---
                st.markdown("#### 📥 Exportar Inteligência de Mercado")
                df_exportar = df_agrupado.copy()
                if st.session_state.perfil_cliente == "comerciante":
                    df_exportar.columns = ["Item Solicitado", "Segmento", "Ponto de Referência",
                                           "Cidade", "Detalhes/Contexto", "Volume de Pedidos", "Dias Desde o Alerta"]
                else:
                    df_exportar.columns = ["Item Solicitado", "Segmento", "Cidade",
                                           "Detalhes/Contexto", "Volume Total de Pedidos", "Dias Desde o Alerta", "Escopo"]

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
                    'TituloPDF', parent=estilos['Heading1'], fontSize=18, textColor=colors.HexColor('#00B359'), spaceAfter=15)
                estilo_texto = ParagraphStyle(
                    'TextoPDF', parent=estilos['Normal'], fontSize=10, spaceAfter=20)

                elementos_pdf.append(Paragraph(
                    f"<b>RELATÓRIO GERENCIAL - INTELIGÊNCIA DE MERCADO</b>", estilo_titulo))
                elementos_pdf.append(Paragraph(
                    f"Frente de Análise: {st.session_state.perfil_cliente.upper()}<br/>Data de emissão: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", estilo_texto))
                elementos_pdf.append(Spacer(1, 10))

                dados_tabela = [df_exportar.columns.tolist()] + \
                    df_exportar.values.tolist()
                tabela_pdf = Table(dados_tabela)
                tabela_pdf.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00B359')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                     [colors.white, colors.HexColor('#F9F9F9')])
                ]))
                elementos_pdf.append(tabela_pdf)
                doc.build(elementos_pdf)
                dados_pdf_final = buffer_pdf.getvalue()

                st.download_button(
                    label="📥 Baixar Relatório Gerencial Oficial (Formato PDF)",
                    data=dados_pdf_final,
                    file_name=f"relatorio_gerencial_{st.session_state.perfil_cliente}.pdf",
                    mime="application/pdf",
                    key="btn_download_pdf_universal"
                )

                st.write("---")
                st.write(
                    f"📈 **Detalhamento das carências ativas ({len(df_agrupado)} itens encontrados):**")
                st.write(
                    "##### *Toque em cima do item correspondente para abrir as opções.*")

                for indice, linha in df_agrupado.iterrows():
                    titulo_card = f"❌ {linha['O que Falta']} ({linha['Volume_Pedidos']} solicitações)"

                    with st.expander(titulo_card):
                        if st.session_state.perfil_cliente == "comerciante":
                            st.write(
                                f"📍 **Local:** {linha['Local/Referência']} ({linha['Cidade']})")
                        else:
                            st.write(
                                f"📍 **Escopo Geográfico:** Consolidação Geral ({linha['Cidade']})")
                        st.write(
                            f"⏱️ **Último alerta há:** {linha['Menor_Idade']} dias")

                        # --- EXIBIÇÃO DO CAMPO DE CONTEXTO EXCLUSIVO PARA O GESTOR PÚBLICO E INVESTIDOR ---
                        if linha['Observação'] and linha['Observação'] != "Sem observações registradas.":
                            st.info(
                                f"📝 **Relato de Contexto da Comunidade:** {linha['Observação']}")

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
                                "⚠️ Atenção: Esta ação dará baixa em todas as solicitações deste item simultaneamente.")
                            col_b1, col_b2 = st.columns(2)
                            with col_b1:
                                if st.button("🚨 Confirmar Exclusão", key=f"btn_real_{indice}"):
                                    supabase.table("relatos_escassez").update({"status": "Atendido"}).eq(
                                        "item_solicitado", linha['O que Falta']).execute()
                                    st.success(
                                        f"🎉 Sucesso! O item foi atualizado.")
                                    st.session_state[chave_confirmacao] = False
                                    st.session_state.busca_ativa = False
                                    st.rerun()
                            with col_b2:
                                if st.button("❌ Cancelar", key=f"btn_cancelar_{indice}"):
                                    st.session_state[chave_confirmacao] = False
                                    st.rerun()
            else:
                st.info(
                    "ℹ️ Nenhum registro ativo encontrado para os filtros selecionados.")
        else:
            st.info("ℹ️ O banco de dados está limpo e sem demandas pendentes!")
