---
title: Sistema Demandas Quarteirao
emoji: 🔍
colorFrom: green
colorTo: darkgreen
sdk: streamlit
sdk_version: 1.35.0
app_file: app.py
pinned: false
license: mit
---

# 🔍 E o que falta? — O Termômetro de Carências do Quarteirão

MVP de inteligência geográfica focado em mapear, auditar e sanar escassezas comerciais, falhas de infraestrutura pública e carências de serviços locais diretamente no quarteirão.

---

## 🏗️ 1. Arquitetura Estrutural do Software

O sistema opera de forma unificada através de três pilares de arquivos em Python (Streamlit), totalizando uma engenharia leve, modular e de alto desempenho:

*   **`app.py`**: O maestro central. Controla os estados de sessão (`st.session_state`), autentica tokens de lojistas e direciona o fluxo de navegação entre as telas.
*   **`telas/morador.py`**: Interface do Consumidor (*134 linhas protegidas*). Permite sinalizar faltas através de formulários dinâmicos inteligentes e exibe a vitrine de conquistas do bairro.
*   **`telas/b2b.py`**: Painel Corporativo e ERP Mestre (*270 linhas compactas*). Filtra carências em cascata por região, gera relatórios em PDF e hospeda as rotinas de baixa operacional por ID.

---

## 🗄️ 2. Modelagem de Dados (Supabase)

O ecossistema é alimentado por duas tabelas principais relacionadas de forma relacional via Chave Estrangeira (`Foreign Key`):

### Tabela: `locais_destino`
Guarda a existência física e geográfica dos pontos comerciais.
*   `id` (int8 / UUID): Chave primária única identificadora do local.
*   `nome_exibicao` (text): Nome fantasia do comércio (Ex: *Drogaria Central, 45*).
*   `regiao_cidade` (text): Cidade e bairro indexados (Ex: *Carapicuíba/SP - Centro*).
*   `regiao_estado` (text): Estado de atuação (Padrão: *SP*).

### Tabela: `relatos_escassez`
Registra o histórico de demandas, camuflagem competitiva e ações de venda.
*   `id` (int8 / UUID): Chave primária única identificadora do relato.
*   `local_id` (int8): ID do estabelecimento (Chave estrangeira conectada a `locais_destino`).
*   `item_solicitado` (text): Nome limpo e tratado do produto (Ex: *Inalador Ultrassônico*).
*   `tipo_carencia` (text): Classificação (*Produto/Marca, Serviço Local ou Infraestrutura*).
*   `sub_segmento` (text): Nicho gerado por IA (*Supermercado, Saúde, Petshop, Beleza, Geral*).
*   `status` (text): Estado da demanda (*Pendente* ou *Atendido*).
*   `observacao_detalhe` (text): Relato opcional fornecido pelo consumidor.
*   `contato_aviso` (text): Contato do morador para disparos LGPD via WhatsApp.
*   `pegada_digital` (text): Hash de segurança para auditoria e prevenção de fraudes.

---

## 🚀 3. Funcionalidades de Negócios Homologadas

1.  **Camuflagem Competitiva**: Lojistas comuns visualizam estabelecimentos rivais mascarados por nicho (Ex: *Mercado Concorrente*), protegendo a privacidade de mercado local.
2.  **Impressão Inteligente (PDF)**: Emissão incondicional de relatórios estruturados no topo das abas comerciais para auditoria física das prateleiras.
3.  **Marketplace Reverso**: Canal de conversão onde o lojista assume o papel ativo de venda, abordando o consumidor via WhatsApp compacto em formato de bala.
4.  **Auditoria ERP Admin**: Painel mestre central para controle financeiro de assinantes (Planos Bronze, Prata e Ouro) e homologação de nichos brutos.

---

## 🛠️ 4. Instruções de Deploy e Sincronização

Sempre que realizar ajustes no ecossistema, execute o protocolo padrão no terminal integrado do seu VS Code:

```bash
git add README.md telas/morador.py telas/b2b.py app.py
git commit -m "docs: criacao da certidao de nascimento tecnica do ecossistema"
git push origin main
```