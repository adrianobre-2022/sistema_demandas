import streamlit as st
import pandas as pd
import time
from core.database import obter_pegada_digital


def renderizar(supabase):
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("🏠 Página Inicial", key="nav_home_v_original_v", use_container_width=True):
            st.session_state.tela_atual = "home"
            st.rerun()
    with col_nav2:
        if st.session_state.aba_consumidor != "menu_triagem":
            if st.button("🗂️ Mudar Categoria", key="nav_cat_v_original_v", use_container_width=True):
                st.session_state.aba_consumidor = "menu_triagem"
                st.rerun()

    st.markdown("<h1 style='text-align: center; font-weight: 900; margin-bottom: 0px;'>🔍 E o que falta?</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; font-style: italic; color: #aaaaaa; margin-top: 5px; margin-bottom: 25px;'>O termômetro de carências da nossa região.</p>", unsafe_allow_html=True)

    if st.session_state.aba_consumidor == "menu_triagem":
        # ATENDIDO: Texto curto sem quebra de linha
        st.write("Escolha tipo de falta:")
        if st.button("📦 PRODUTO OU MARCA EM FALTA", use_container_width=True, key="tri_prod_v"):
            st.session_state.aba_consumidor = "produto"
            st.rerun()
        if st.button("🏪 NOVO COMÉRCIO OU SERVIÇO LOCAL", use_container_width=True, key="tri_serv_v"):
            st.session_state.aba_consumidor = "servico"
            st.rerun()
        if st.button("🏛️ INFRAESTRUTURA OU ZELADORIA PÚBLICA", use_container_width=True, key="tri_infra_v"):
            st.session_state.aba_consumidor = "infra"
            st.rerun()

        st.write("")
        st.markdown("### 🏆 Impactos Recentes no Bairro")
        try:
            resolvidos = supabase.table("relatos_escassez").select("item_solicitado, sub_segmento, locais_destino(nome_exibicao, regiao_cidade)").eq(
                "status", "Atendido").order("data_registro", desc=True).limit(20).execute()

            if resolvidos.data:
                lista_impactos = []
                for item in resolvidos.data:
                    if item.get("locais_destino"):
                        item_limpo_vitrine = str(item["item_solicitado"]).rstrip(
                            " 0123456789").strip().title()
                        lista_impactos.append({
                            "item": item_limpo_vitrine,
                            "nicho": item.get("sub_segmento", "Geral").strip(),
                            "local": item["locais_destino"]["nome_exibicao"].strip().title(),
                            "cidade_exibicao": item["locais_destino"]["regiao_cidade"].strip()
                        })

                df_imp = pd.DataFrame(lista_impactos)

                st.markdown("""
                    <style>
                    [data-testid="stVerticalBlock"] > div:has(div.box-rolagem-computador) {
                        max-height: 240px !important;
                        overflow-y: scroll !important;
                    }
                    </style>
                """, unsafe_allow_html=True)

                with st.container(height=240, border=False):
                    st.markdown(
                        "<div class='box-rolagem-computador'></div>", unsafe_allow_html=True)

                    for _, l_imp in df_imp.iterrows():
                        n_nicho = l_imp['nicho']

                        # 🎯 CALIBRAÇÃO SEMÂNTICA: Mapeamento de ações realistas por nicho
                        if n_nicho == "Supermercado":
                            icone, acao = "🛒 Varejo Alimentar:", "repôs o estoque de"
                        elif n_nicho in ["Saude", "Saúde"]:
                            icone, acao = "🩺 Saúde e Bem-Estar:", "trouxe o serviço de"
                        elif n_nicho == "Petshop":
                            icone, acao = "🐶 Setor Animal/Pet:", "disponibilizou o item"
                        elif n_nicho == "Beleza":
                            icone, acao = "💈 Beleza e Estética:", "ativou o atendimento de"
                        elif n_nicho == "Serviços":
                            icone, acao = "🏪 Serviços Locais:", "trouxe o serviço de"
                        elif n_nicho == "Infraestrutura":
                            icone, acao = "🏛️ Zeladoria Pública:", "zelou e resolveu o problema de"
                        else:
                            icone, acao = "✨ Conquista Local:", "disponibilizou"

                        st.markdown(
                            f"<div style='background-color: #1A1A1A; padding: 0.6rem 1rem; border-radius: 8px; border-left: 4px solid #00803B; margin-bottom: 8px;'><span style='font-size: 13px; color: #aaaaaa; font-weight: 500;'>✅ <b>{icone}</b> {l_imp['local']} ({l_imp['cidade_exibicao']}) {acao} <b>{l_imp['item']}</b>!</span></div>", unsafe_allow_html=True)
            else:
                st.write("ℹ️ Nenhuma benfeitoria recente registrada.")
        except:
            pass

    elif st.session_state.aba_consumidor in ["produto", "servico", "infra"]:
        aba = st.session_state.aba_consumidor
        if aba == "produto":
            l_i, p_i = "Qual produto ou marca falta? *", "Ex: Leite condensado marca X..."
            l_l, p_l = "Em qual estabelecimento? *", "Ex: Nome do mercado..."
            # ATENDIDO: Texto curto e responsivo para o formulário
            l_c, t_e = "Deixar contato, caso reponham? (Opcional)", "Produto / Marca"
        elif aba == "servico":
            l_i, p_i = "Qual comércio falta no bairro? *", "Ex: Sapataria, lavanderia..."
            l_l, p_l = "Em qual rua ou ponto? *", "Ex: Avenida Principal..."
            l_c, t_e = "Deixar contato, caso reponham? (Opcional)", "Serviço Local / Novo Extabelecimento"
        elif aba == "infra":
            l_i, p_i = "Qual problema de infraestrutura pública? *", "Ex: Falha na iluminação..."
            l_l, p_l = "Qual o ponto de referência? *", "Ex: Posto de saúde do bairro Y..."
            l_c, t_e = "Deixar contato, caso reponham? (Opcional)", "Serviço Público / Infraestrutura"

        st.write("")
        with st.form(key="formulario_dinamico_consumidor", clear_on_submit=False):
            regiao_final = st.text_input(
                label="📍 Região/Cidade da falta: *", placeholder="Ex: São Paulo/SP - Centro")
            item_solicitado = st.text_input(
                label=l_i, placeholder=p_i, key="input_item")
            local_ocorrencia = st.text_input(
                label=l_l, placeholder=p_l, key="input_local")
            contato_usuario = st.text_input(
                label=l_c, placeholder="Insira seu WhatsApp ou e-mail, caso informem reposição.", key="input_contato")
            observacao_usuario = None
            with st.expander("➕ Adicionar mais detalhes e observações (Opcional)"):
                observacao_usuario = st.text_area(
                    label="Detalhes adicionais:", placeholder="Ex: Detalhe o ocorrido aqui...", key="input_obs")
            botao_enviar = st.form_submit_button(
                "🔍 SINALIZAR ESTA FALTA", use_container_width=True)

        if botao_enviar:
            if not regiao_final or regiao_final.strip() == "":
                st.error(
                    "⚠️ O campo '📍 Região/Cidade da falta:' é obrigatório para registrar a carência.")
            elif not item_solicitado or not local_ocorrencia:
                st.error(
                    "⚠️ Por favor, preencha o item que falta e o local da ocorrência.")
            else:
                try:
                    hash_disp = obter_pegada_digital()
                    texto_regiao = regiao_final.strip()
                    local_fmt = local_ocorrencia.strip().title()

                    l_data = supabase.table("locais_destino").insert(
                        {"nome_exibicao": local_fmt, "regiao_cidade": texto_regiao, "regiao_estado": "SP"}).execute()
                    l_id = l_data.data[0]["id"] if (
                        l_data and l_data.data and len(l_data.data) > 0) else None

                    if l_id:
                        seg_det = "Geral"
                        txt_u = item_solicitado.strip().lower()
                        if any(p in txt_u for p in ["leite", "arroz", "feijão", "café", "açúcar", "pão", "mercado", "óleo"]):
                            seg_det = "Supermercado"
                        elif any(p in txt_u for p in ["remédio", "médico", "dentista", "farmácia", "clínica"]):
                            seg_det = "Saúde"
                        elif any(p in txt_u for p in ["ração", "pet", "cachorro", "gato", "petshop"]):
                            seg_det = "Petshop"
                        elif any(p in txt_u for p in ["manicure", "salão", "cabeleireiro", "estética"]):
                            seg_det = "Beleza"

                        txt_o = observacao_usuario.strip() if observacao_usuario else None
                        c_aviso = contato_usuario.strip() if contato_usuario else None

                        supabase.table("relatos_escassez").insert({"local_id": l_id, "item_solicitado": item_solicitado.strip().title(
                        ), "tipo_carencia": t_e, "status": "Pendente", "sub_segmento": seg_det, "pegada_digital": hash_disp, "observacao_detalhe": txt_o, "contato_aviso": c_aviso}).execute()
                        st.success("✅ Falta sinalizada com sucesso!")
                        time.sleep(1.2)
                        st.session_state.aba_consumidor = "menu_triagem"
                        st.session_state.tela_atual = "home"
                        st.rerun()
                except Exception as e:
                    st.error(f"⚠️ Erro técnico de persistência: {str(e)}")
