import streamlit as st
import datetime

def renderizar(supabase):
    # 🎨 ESTILOS EXCLUSIVOS BLINDADOS DA VITRINE DE ROLAGEM VERTICAL
    st.markdown("""
        <style>
        .vitrine-rolagem-bairro {
            max-height: 290px;
            overflow-y: auto;
            padding-right: 8px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.02);
            margin-bottom: 20px;
        }
        .vitrine-rolagem-bairro::-webkit-scrollbar {
            width: 6px;
        }
        .vitrine-rolagem-bairro::-webkit-scrollbar-thumb {
            background-color: #00803B;
            border-radius: 10px;
        }
        .card-impacto-recente {
            background-color: #1a1a1a;
            border-left: 4px solid #00803B;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 4px 8px 8px 4px;
        }
        </style>
    """, unsafe_allow_html=True)

    # ⬅️ BOTÃO RETRO_VOLTAR PADRONIZADO E FIXO
    col_v1, _ = st.columns(2)
    with col_v1:
        if st.button("⬅️ Voltar ao Início", key="btn_voltar_morador_nat", use_container_width=True):
            st.session_state.tela_atual = "home"
            st.session_state.busca_ativa = False
            st.rerun()

    st.markdown("<h1 style='text-align: center; font-weight: 900; margin-bottom: 0px;'>🏘️ Painel do Morador</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; font-style: italic; color: #aaaaaa; margin-top: 5px; margin-bottom: 25px;'>Sua voz constrói o comércio do nosso quarteirão.</p>", unsafe_allow_html=True)
    st.write("---")

    # 🏪 BUSCA DE ESTABELECIMENTOS ATIVOS
    locais_disponiveis = []
    try:
        res_locais = supabase.table("locais_destino").select("id, nome_exibicao, regiao_cidade").execute()
        if res_locais.data:
            locais_disponiveis = res_locais.data
    except Exception as e:
        st.error(f"Erro ao conectar com a região: {str(e)}")

    if not locais_disponiveis:
        st.info("ℹ️ Nenhum estabelecimento mapeado na nossa região no momento.")
        return

    # 📝 FORMULÁRIO DE REGISTRO DE DEMANDA DE PRODUTO
    st.markdown("### 📢 O que você procurou e não encontrou?")
    with st.form(key="form_registro_demanda_morador", clear_on_submit=True):
        item_procurado = st.text_input("Nome do Produto / Marca faltante:", placeholder="Ex: Leite Desnatado Marca X...")
        
        opcoes_lojas = [f"{l['nome_exibicao']} ({l['regiao_cidade']})" for l in locais_disponiveis]
        loja_selecionada_txt = st.selectbox("Em qual estabelecimento faltou?", options=opcoes_lojas)
        idx_loja = opcoes_lojas.index(loja_selecionada_txt)
        id_local_escolhido = locais_disponiveis[idx_loja]["id"]
        
        tipo_carencia = st.selectbox("Tipo de Carência:", ["Produto / Marca", "Serviço Público / Infraestrutura", "Serviço Local / Novo Estabelecimento"])
        obs_detalhe = st.text_area("Informações Adicionais (Opcional):", placeholder="Ex: Prateleira estava vazia, disseram que não vem mais...")
        contato_aviso = st.text_input("Seu WhatsApp (Opcional - para o lojista te avisar quando chegar):", placeholder="DDD + Número...")

        if st.form_submit_button("🚀 Registrar Alerta de Escassez"):
            if not item_procurado.strip():
                st.error("⚠️ Por favor, digite o nome do produto ou marca que faltou.")
            else:
                try:
                    payload = {
                        "item_solicitado": item_procurado.strip(),
                        "local_destino_id": id_local_escolhido,
                        "tipo_carencia": tipo_carencia,
                        "observacao_detalhe": obs_detalhe.strip() if obs_detalhe.strip() else None,
                        "contato_aviso": contato_aviso.strip() if contato_aviso.strip() else None,
                        "status": "Pendente",
                        "sub_segmento": "Geral"
                    }
                    supabase.table("relatos_escassez").insert(payload).execute()
                    st.success("🎉 Alerta registrado com sucesso! Os lojistas da região já foram notificados.")
                    import time; time.sleep(0.8); st.rerun()
                except Exception as ex:
                    st.error(f"Erro ao salvar alerta: {str(ex)}")

    st.write("---")
    st.markdown("### 📈 Impactos Recentes no Bairro")

    # 🌪️ CAPTAÇÃO E MONTAGEM DA VITRINE DE ROLAGEM DINÂMICA
    try:
        res_recentes = supabase.table("relatos_escassez").select("item_solicitado, created_at, locais_destino(nome_exibicao, regiao_cidade)").order("created_at", desc=True).limit(20).execute()
        
        if res_recentes.data and len(res_recentes.data) > 0:
            html_vitrine = "<div class='vitrine-rolagem-bairro'>"
            
            for relato in res_recentes.data:
                item = relato.get("item_solicitado", "Produto Indisponível").title()
                nome_loja = "Estabelecimento Local"
                if relato.get("locais_destino"):
                    nome_loja = relato["locais_destino"].get("nome_exibicao", "Loja")
                
                # Injeta cada item dinamicamente mantendo as bordas compactas e o estilo verde
                html_vitrine += f"""
                    <div class='card-impacto-recente'>
                        <span style='color: #00803B; font-weight: bold; font-size: 13px;'>📦 FALTA DETECTADA</span>
                        <div style='color: #FFFFFF; font-size: 15px; font-weight: bold; margin-top: 2px;'>{item}</div>
                        <div style='color: #aaaaaa; font-size: 12px; margin-top: 4px;'>Bairro notificou: {nome_loja}</div>
                    </div>
                """
            
            html_vitrine += "</div>"
            st.markdown(html_vitrine, unsafe_allow_html=True)
        else:
            st.info("ℹ️ O quarteirão está totalmente abastecido! Nenhum impacto recente registrado.")
    except Exception as e:
        # Fallback de segurança silencioso para não quebrar a experiência do morador
        st.info("ℹ️ Carregando atualizações em tempo real do quarteirão...")
