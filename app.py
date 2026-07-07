import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

# --- CONEXÃO INTELIGENTE (LOCAL E NUVEM) ---
caminho_atual = os.path.dirname(os.path.abspath(__file__))
caminho_env = os.path.join(caminho_atual, ".env")
load_dotenv(caminho_env)

url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

if not url or not key:
    st.error("⚠️ As credenciais de conexão com o banco de dados não foram encontradas.")
    st.stop()

supabase: Client = create_client(url, key)
# --------------------------------------------

st.set_page_config(page_title="Sistema de Pesquisas", page_icon="🔍", layout="centered")

# --- CUSTOMIZAÇÃO ESTÉTICA PREMIUM (ESTILO APP MODERNO) ---
st.markdown("""
    <style>
    .stButton>button {
        background-color: #00cc66 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background-color: #00994d !important;
        transform: scale(1.01);
    }
    .stTextInput>div>div>input {
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Cria as duas abas nativas no topo - Perfeito para Celular (Atrito Zero)
aba_formulario, aba_painel = st.tabs([
    "📝 Deixe saber o que você deseja", 
    "📊 Tenha o que o seu cliente deseja"
])

# --- ABA 1: FORMULÁRIO DO CONSUMIDOR ---
with aba_formulario:
    st.title("🔍 Central de Demandas Ocultas")
    st.markdown("##### *Deixe saber o que você deseja e sente falta na região.*")
    st.write("---")

    tipo_selecionado = st.radio(
        label="Que tipo de ausência você quer registrar?",
        options=["Produto / Marca", "Serviço Local / Novo Estabelecimento", "Serviço Público / Infraestrutura"],
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

    item_solicitado = st.text_input(label=label_item, placeholder=placeholder_item, key="input_item")
    local_ocorrencia = st.text_input(label=label_local, placeholder=placeholder_local, key="input_local")

    st.write("")

    if st.button("Registrar Ocorrência", use_container_width=True, key="btn_registrar"):
        if item_solicitado and local_ocorrencia:
            try:
                local_formatado = local_ocorrencia.strip().title()
                
                local_data = supabase.table("locais_destino").insert({
                    "nome_exibicao": local_formatado,
                    "regiao_cidade": "São Paulo",
                    "regiao_estado": "SP"
                }).execute()
                
                local_id = None
                if local_data.data and len(local_data.data) > 0:
                    local_id = local_data.data[0]["id"]
                
                if local_id:
                    item_formatado = item_solicitado.strip().title()
                    
                    supabase.table("relatos_escassez").insert({
                        "local_id": local_id,
                        "item_solicitado": item_formatado,
                        "tipo_carencia": tipo_selecionado
                    }).execute()
                    
                    st.success("✅ Registro computado e salvo na nuvem com anonimato garantido!")
                else:
                    st.error("⚠️ Não foi possível extrair o identificador correto do local.")
                    
            except Exception as e:
                st.error(f"⚠️ Erro técnico detalhado: {str(e)}")
        else:
            st.warning("⚠️ Por favor, preencha ambos os campos.")

# --- ABA 2: PAINEL DO COMERCIANTE / GESTOR (CONSULTA ISOLADA) ---
with aba_painel:
    st.title("📊 Painel de Decisão Estratégica")
    st.markdown("##### *Tenha o produto, marca ou serviço que o seu cliente deseja na prateleira ou região.*")
    st.write("---")

    filtro_frente = st.selectbox(
        label="Selecione a Frente de Inteligência que deseja analisar:",
        options=["Todas as Carências", "Apenas Produtos/Marcas (Varejo)", "Oportunidades de Novos Negócios (Serviços)", "Infraestrutura Urbana (Setor Público)"],
        key="selectbox_frente"
    )

    termo_busca = st.text_input(
        label="Filtrar por palavra-chave (Localidade ou Nome):",
        placeholder="Digite para refinar a busca...",
        key="input_busca_painel"
    )

    # Inicializa a memória do clique para evitar a reexecução global fantasma
    if "clicou_buscar" not in st.session_state:
        st.session_state.clicou_buscar = False

    if st.button("Buscar Oportunidades Ocultas", use_container_width=True, key="btn_buscar"):
        st.session_state.clicou_buscar = True

    # O conteúdo da busca só roda protegido dentro desta trava de estado
    if st.session_state.clicou_buscar:
        try:
            resposta = supabase.table("relatos_escassez").select("item_solicitado, tipo_carencia, locais_destino(nome_exibicao, regiao_cidade)").execute()
            
            if resposta.data:
                dados_limpos = []
                for registro in resposta.data:
                    if registro.get("locais_destino"):
                        dados_limpos.append({
                            "O que Falta": registro["item_solicitado"],
                            "Categoria": registro.get("tipo_carencia", "Produto / Marca"),
                            "Local/Referência": registro["locais_destino"]["nome_exibicao"],
                            "Cidade": registro["locais_destino"]["regiao_cidade"]
                        })
                
                if dados_limpos:
                    df = pd.DataFrame(dados_limpos)

                    if filtro_frente == "Apenas Produtos/Marcas (Varejo)":
                        df = df[df['Categoria'] == "Produto / Marca"]
                    elif filtro_frente == "Oportunidades de Novos Negócios (Serviços)":
                        df = df[df['Categoria'] == "Serviço Local / Novo Estabelecimento"]
                    elif filtro_frente == "Infraestrutura Urbana (Setor Público)":
                        df = df[df['Categoria'] == "Serviço Público / Infraestrutura"]

                    if termo_busca:
                        df = df[df['O que Falta'].str.contains(termo_busca, case=False) | df['Local/Referência'].str.contains(termo_busca, case=False)]

                    if not df.empty:
                        st.write(f"📈 Foram encontrados **{len(df)}** registros mapeados:")
                        st.dataframe(df, use_container_width=True)
                        
                        st.markdown("#### Distribuição de Demandas Reprimidas Encontradas:")
                        contagem_itens = df["O que Falta"].value_counts()
                        st.bar_chart(contagem_itens)
                    else:
                        st.info("ℹ️ Nenhum registro encontrado para os filtros selecionados.")
                else:
                    st.info("ℹ️ O banco de dados ainda não possui registros válidos.")
            else:
                st.info("ℹ️ O banco de dados está vazio.")
                
        except Exception as e:
            st.error(f"⚠️ Erro técnico detalhado: {str(e)}")