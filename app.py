import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

# --- CONEXÃO INTELIGENTE (LOCAL E NUVEM) ---
# 1. Tenta carregar do arquivo local .env (para quando rodar no seu PC)
caminho_atual = os.path.dirname(os.path.abspath(__file__))
caminho_env = os.path.join(caminho_atual, ".env")
load_dotenv(caminho_env)

# 2. Busca as chaves tanto do arquivo local quanto dos Secrets do Streamlit Cloud
url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

# Verifica se os dados foram encontrados em algum dos dois lugares
if not url or not key:
    st.error(
        "⚠️ As credenciais de conexão com o banco de dados não foram encontradas.")
    st.stop()

# Inicializa o conector seguro com a nuvem do Supabase
supabase: Client = create_client(url, key)
# --------------------------------------------

# 2. Configurações visuais modernas e limpas
st.set_page_config(page_title="Sistema de Pesquisas",
                   page_icon="🔍", layout="centered")

# Menu de navegação superior (Abstrato e elegante)
aba_selecionada = st.tabs(
    ["📝 Registrar Ausência", "📊 Painel de Inteligência B2B"])

# --- ABA 1: FORMULÁRIO DO CONSUMIDOR (O QUE JÁ ESTAVA FUNCIONANDO) ---
with aba_selecionada[0]:
    st.title("🔍 Central de Demandas Ocultas")
    st.markdown(
        "### Informe o item ausente e o local para gerar o registro de mercado.")
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
                local_data = supabase.table("locais_destino").insert({
                    "nome_exibicao": local_formatado,
                    "regiao_cidade": "São Paulo",
                    "regiao_estado": "SP"
                }).execute()

                local_id = local_data.data[0]["id"]

                item_formatado = item_solicitado.strip().title()
                supabase.table("relatos_escassez").insert({
                    "local_id": local_id,
                    "item_solicitado": item_formatado
                }).execute()

                st.success(
                    "✅ Ocorrência computada e salva na nuvem com anonimato garantido!")
            except Exception as e:
                st.error("⚠️ Falha ao conectar ao servidor de dados seguro.")
        else:
            st.warning("⚠️ Por favor, preencha ambos os campos.")

# --- ABA 2: PAINEL DO COMERCIANTE / ENTIDADE (NOVA ÁREA) ---
with aba_selecionada[1]:
    st.title("📊 Painel de Decisão Estratégica")
    st.markdown(
        "### Pesquise por termos, marcas ou localidades para extrair as carências registradas.")
    st.write("---")

    # Barra de busca para o comerciante consultar o banco
    termo_busca = st.text_input(
        label="Filtrar por Localidade ou Marca/Produto:",
        placeholder="Digite o nome da sua empresa, bairro ou um item específico para pesquisar..."
    )

    if st.button("Buscar Oportunidades Perdidas", use_container_width=True, key="btn_buscar"):
        try:
            # Puxa os dados da nuvem combinando as duas tabelas (Junção Relacional Básica)
            resposta = supabase.table("relatos_escassez").select(
                "item_solicitado, data_registro, locais_destino(nome_exibicao, regiao_cidade)").execute()

            if resposta.data:
                # Transforma a resposta em uma tabela organizada (Pandas DataFrame)
                dados_limpos = []
                for registro in resposta.data:
                    dados_limpos.append({
                        "Item Ausente": registro["item_solicitado"],
                        "Local Informado": registro["locais_destino"]["nome_exibicao"],
                        "Cidade": registro["locais_destino"]["regiao_cidade"]
                    })

                df = pd.DataFrame(dados_limpos)

                # Se o usuário digitou algo na busca, filtra os resultados
                if termo_busca:
                    df = df[df['Item Ausente'].str.contains(
                        termo_busca, case=False) | df['Local Informado'].str.contains(termo_busca, case=False)]

                if not df.empty:
                    st.write(
                        f"📈 Foram encontrados **{len(df)}** registros de carência de mercado:")
                    st.dataframe(df, use_container_width=True)

                    # Exibe um gráfico simples de contagem dos itens mais procurados
                    st.markdown("#### Itens com Maior Demanda Reprimida:")
                    contagem_itens = df["Item Ausente"].value_counts()
                    st.bar_chart(contagem_itens)
                else:
                    st.info("ℹ️ Nenhum registro encontrado para o termo digitado.")
            else:
                st.info(
                    "ℹ️ O banco de dados ainda não possui registros para exibir.")

        except Exception as e:
            st.error("⚠️ Erro ao consultar o banco de dados na nuvem.")
