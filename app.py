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

# Desmembra as abas
aba_formulario, aba_painel = st.tabs(["📝 Registrar Ausência", "📊 Painel de Inteligência B2B"])

# --- ABA 1: FORMULÁRIO DO CONSUMIDOR ---
with aba_formulario:
    st.title("🔍 Central de Demandas Ocultas")
    st.markdown("##### *Deixe saber o que você deseja e sente falta na região.*")
    st.write("---")

    item_solicitado = st.text_input(
        label="O que você buscou e não encontrou?",
        placeholder="Ex: Nome do produto, marca, serviço ou manutenção...",
        key="input_item"
    )

    local_ocorrencia = st.text_input(
        label="Em qual estabelecimento, órgão ou localidade isso ocorreu?",
        placeholder="Ex: Nome da loja, bairro, CNPJ ou repartição...",
        key="input_local"
    )

    st.write("")

    if st.button("Registrar Ausência", use_container_width=True, key="btn_registrar"):
        if item_solicitado and local_ocorrencia:
            try:
                local_formatado = local_ocorrencia.strip().title()
                
                # Insere o local no banco
                local_data = supabase.table("locais_destino").insert({
                    "nome_exibicao": local_formatado,
                    "regiao_cidade": "São Paulo",
                    "regiao_estado": "SP"
                }).execute()
                
                local_id = local_data.data["id"] if local_data.data else None
                
                if local_id:
                    item_formatado = item_solicitado.strip().title()
                    
                    # Insere o relato na nuvem
                    supabase.table("relatos_escassez").insert({
                        "local_id": local_id,
                        "item_solicitado": item_formatado
                    }).execute()
                    
                    # Exibe o sucesso na tela de forma limpa
                    st.success("✅ Ocorrência computada e salva na nuvem com anonimato garantido!")
                    
                    # Truque de Mestre: Força o Streamlit a limpar os campos após o envio, 
                    # matando a memória do clique e impedindo o reenvio por F5 do navegador.
                    st.rerun()
            except Exception as e:
                st.error("⚠️ Falha ao conectar ao servidor de dados seguro.")
        else:
            st.warning("⚠️ Por favor, preencha ambos os campos.")

# --- ABA 2: PAINEL DO COMERCIANTE / GESTOR ---
with aba_painel:
    st.title("📊 Painel de Decisão Estratégica")
    st.markdown("##### *Tenha o produto, marca ou serviço que o seu cliente deseja na prateleira.*")
    st.write("---")

    termo_busca = st.text_input(
        label="Filtrar por Localidade ou Marca/Produto:",
        placeholder="Digite o nome da sua empresa, bairro ou um item específico para pesquisar..."
    )

    if st.button("Buscar Oportunidades Perdidas", use_container_width=True, key="btn_buscar"):
        try:
            resposta = supabase.table("relatos_escassez").select("item_solicitado, locais_destino(nome_exibicao, regiao_cidade)").execute()
            
            if resposta.data:
                dados_limpos = []
                for registro in resposta.data:
                    if registro.get("locais_destino"):
                        dados_limpos.append({
                            "Item Ausente": registro["item_solicitado"],
                            "Local Informado": registro["locais_destino"]["nome_exibicao"],
                            "Cidade": registro["locais_destino"]["regiao_cidade"]
                        })
                
                if dados_limpos:
                    df = pd.DataFrame(dados_limpos)

                    if termo_busca:
                        df = df[df['Item Ausente'].str.contains(termo_busca, case=False) | df['Local Informado'].str.contains(termo_busca, case=False)]

                    if not df.empty:
                        st.write(f"📈 Foram encontrados **{len(df)}** registros de carência de mercado:")
                        st.dataframe(df, use_container_width=True)
                        
                        st.markdown("#### Itens com Maior Demanda Reprimida:")
                        contagem_itens = df["Item Ausente"].value_counts()
                        st.bar_chart(contagem_itens)
                    else:
                        st.info("ℹ️ Nenhum registro encontrado para o termo digitado.")
                else:
                    st.info("ℹ️ O banco de dados ainda não possui registros válidos para exibir.")
            else:
                st.info("ℹ️ O banco de dados ainda não possui registros para exibir.")
                
        except Exception as e:
            st.error("⚠️ Erro ao consultar o banco de dados na nuvem.")