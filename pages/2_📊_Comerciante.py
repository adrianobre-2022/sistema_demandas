import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

caminho_atual = os.path.dirname(os.path.abspath(__file__))
caminho_env = os.path.join(os.path.dirname(caminho_atual), ".env")
load_dotenv(caminho_env)

url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

if not url or not key:
    st.error("⚠️ Credenciais não encontradas.")
    st.stop()

supabase: Client = create_client(url, key)

st.title("📊 Painel de Decisão Estratégica")
st.markdown("##### *Tenha o produto, marca ou serviço que o seu cliente deseja na prateleira.*")
st.write("---")

filtro_frente = st.selectbox(
    label="Selecione a Frente de Inteligência que deseja analisar:",
    options=["Todas as Carências", "Apenas Produtos/Marcas (Varejo)", "Oportunidades de Novos Negócios (Serviços)", "Infraestrutura Urbana (Setor Público)"],
    key="p2_selectbox"
)

termo_busca = st.text_input(
    label="Filtrar por palavra-chave (Localidade ou Nome):",
    placeholder="Digite para refinar a busca...",
    key="p2_busca"
)

if st.button("Buscar Oportunidades Ocultas", use_container_width=True, key="p2_btn"):
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
                st.info("ℹ️ Banco de dados sem registros válidos.")
        else:
            st.info("ℹ️ Banco de dados vazio.")
    except Exception as e:
        st.error(f"⚠️ Erro técnico: {str(e)}")