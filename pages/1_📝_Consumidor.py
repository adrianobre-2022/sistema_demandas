import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client

caminho_atual = os.path.dirname(os.path.abspath(__file__))
# Como estamos dentro da pasta 'pages', precisamos subir um nível para achar o .env
caminho_env = os.path.join(os.path.dirname(caminho_atual), ".env")
load_dotenv(caminho_env)

url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

if not url or not key:
    st.error("⚠️ As credenciais de conexão não foram encontradas.")
    st.stop()

supabase: Client = create_client(url, key)

st.title("🔍 Central de Demandas Ocultas")
st.markdown("##### *Deixe saber o que você deseja e sente falta na região.*")
st.write("---")

tipo_selecionado = st.radio(
    label="Que tipo de ausência você quer registrar?",
    options=["Produto / Marca", "Serviço Local / Novo Estabelecimento", "Serviço Público / Infraestrutura"],
    horizontal=True,
    key="page_radio_tipo"
)

if tipo_selecionado == "Produto / Marca":
    label_item = "Qual produto ou marca você buscou e não encontrou?"
    placeholder_item = "Ex: Nome do produto, marca específica..."
    label_local = "Em qual estabelecimento isso ocorreu?"
    placeholder_local = "Ex: Nome do mercadinho, farmácia..."
elif tipo_selecionado == "Serviço Local / Novo Estabelecimento":
    label_item = "Qual tipo de comércio ou serviço falta neste bairro?"
    placeholder_item = "Ex: Sapataria, lavanderia, costureira..."
    label_local = "Em qual rua ou pedaço do bairro isso faz falta?"
    placeholder_local = "Ex: Bairro Centro, Próximo à praça..."
else:
    label_item = "Qual carência de infraestrutura você identificou?"
    placeholder_item = "Ex: Falha na iluminação, falta de médicos..."
    label_local = "Qual o ponto de referência exata?"
    placeholder_local = "Ex: Posto de saúde do bairro Y..."

item_solicitado = st.text_input(label=label_item, placeholder=placeholder_item, key="p1_item")
local_ocorrencia = st.text_input(label=label_local, placeholder=placeholder_local, key="p1_local")

if st.button("Registrar Ocorrência", use_container_width=True, key="p1_btn"):
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
                st.error("⚠️ Erro ao gerar identificador.")
        except Exception as e:
            st.error(f"⚠️ Erro técnico: {str(e)}")
    else:
        st.warning("⚠️ Preencha todos os campos.")