---
sdk: streamlit
app_file: app.py
---

# 🔍 Sistema de Demandas — O termômetro de carências da nossa região.

Ecossistema tecnológico avançado de inteligência de mercado e logística reversa regional. O sistema atua como um equalizador urbano, capturando intenções de consumo reprimidas de moradores locais e convertendo-as em painéis estatísticos de alta conversão para o setor de varejo, serviços e infraestrutura regional.

## 📁 Arquitetura Estrutural do Projeto

```text
sistema_demandas/
├── .env                  # Chaves privadas locais (SUPABASE_URL e SUPABASE_KEY)
├── app.py                # Arquivo mestre e centralizador de navegação global
├── requirements.txt      # Manifesto de bibliotecas e dependências do servidor Python
├── README.md             # Documentação técnica e cabeçalho de inicialização
├── core/
│   └── database.py       # Engine de conexão com o banco e criptografia de segurança
└── telas/
    ├── home.py           # Portal inicial e triagem de perfis institucionais
    ├── morador.py        # Formulário de captação e roleta dinâmica de impactos
    └── b2b.py            # Matriz financeira ADMIN e painel de gôndolas comerciais
```

## 🛠️ Funcionalidades Implementadas e Homologadas

*   **Marketing Reverso Ativo (Morador):** Formulário humanizado em formato de perguntas diretas para captação imediata de ruptura de estoque.
*   **Vitrine Dinâmica de Impactos:** Roleta randômica automatizada na interface do usuário, exibindo conquistas reais de todas as verticais e logins (Varejo, Saúde, Pet, Zeladoria) sem vícios de ordenação estática.
*   **Painel B2B Multipessoal (Varejo):** Separação estrita de relatórios agregados por nicho de atuação para preservar o segredo industrial e comercial dos lojistas parceiros.
*   **Central Financeira & ERP (ADMIN):** Área restrita para controle de tokens de acesso, status de pagamento corporativo e gerenciamento de planos contratuais (Bronze, Prata e Ouro).
*   **Filtro Inteligente de Palavra-Chave:** Motor de busca integrado em tempo real no ecossistema do administrador, permitindo refinar buscas textuais instantaneamente no meio de milhares de cadastros.
*   **Blindagem contra Plágio:** Aplicação operando em ambiente público por meio do Streamlit Cloud, mas com repositório blindado contra engenharia reversa por meio da injeção de segredos ocultos.

## 🛰️ Requisitos e Dependências Técnicas

A engrenagem do servidor exige as seguintes bibliotecas oficiais instaladas:
*   `streamlit`
*   `supabase`
*   `pandas`

## 🔐 Configuração e Variáveis de Ambiente

Para o funcionamento completo da integração com o banco de dados Supabase, as seguintes variáveis privadas devem ser injetadas localmente no arquivo `.env` ou registradas no painel de segredos avançados do servidor na nuvem:

```toml
SUPABASE_URL = "https://supabase.co"
SUPABASE_KEY = "sua-chave-anon-public-real-do-banco"
```

---
*Documento de Propriedade Intelectual Privada — Homologação de Lançamento Regional.*