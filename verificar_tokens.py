import os
import httpx


def carregar_e_consultar():
    print("📂 Procurando credenciais do Supabase no projeto...")
    url = None
    key = None

    # Tentativa 1: Ler do arquivo .env local
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for linha in f:
                if "SUPABASE_URL" in linha:
                    url = linha.split("=")[1].strip().strip('"').strip("'")
                if "SUPABASE_KEY" in list(linha.split("=")[0].strip()) or "SUPABASE_KEY" in linha:
                    if "=" in linha:
                        key = linha.split("=")[1].strip().strip('"').strip("'")

    # Tentativa 2: Ler da pasta oculta do Streamlit (.streamlit/secrets.toml)
    if not url and os.path.exists(".streamlit/secrets.toml"):
        with open(".streamlit/secrets.toml", "r", encoding="utf-8") as f:
            for linha in f:
                if "SUPABASE_URL" in linha:
                    url = linha.split("=")[1].strip().strip('"').strip("'")
                if "SUPABASE_KEY" in linha:
                    key = linha.split("=")[1].strip().strip('"').strip("'")

    if not url or not key:
        print("❌ Não encontrei os arquivos .env ou secrets.toml na raiz.")
        return

    # Corrige a URL tirando barras extras no final
    url = url.rstrip("/")
    print(f"🔗 Conectando na URL: {url}")

    url_final = f"{url}/rest/v1/clientes_b2b?select=nome_estabelecimento,token_acesso"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}"
    }

    try:
        response = httpx.get(url_final, headers=headers)
        if response.status_code == 200:
            dados = response.json()
            if dados:
                print("\n🔑 TOKENS REAIS DISPONÍVEIS NO SEU BANCO:")
                print("-" * 50)
                for cli in dados:
                    print(f"🏢 Empresa: {cli.get('nome_estabelecimento')}")
                    print(f"🔑 Token: {cli.get('token_acesso')}")
                    print("-" * 50)
            else:
                print("\n⚠️ Conectado! Mas a tabela 'clientes_b2b' está vazia.")
        else:
            print(f"❌ Erro na API do Supabase: Código {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")


if __name__ == "__main__":
    carregar_e_consultar()
