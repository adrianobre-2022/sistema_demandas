import streamlit as st
import pandas as pd
import time
from core.database import obter_pegada_digital


def renderizar(supabase):
    # CSS AVANÇADO: Força alinhamento à esquerda, remove fundos e bordas
    st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"]:has(button[key*="limpo"]) {
            justify-content: flex-start !important;
            gap: 20px !important;
        }
        div[data-testid="stHorizontalBlock"]:has(button[key*="limpo"]) button {
            background-color: transparent !important;
            color: #aaaaaa !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0px !important;
            font-size: 14px !important;
            font-weight: bold !important;
            text-align: left !important;
            width: auto !important;
            display: inline-block !important;
        }
        div[data-testid="stHorizontalBlock"]:has(button[key*="limpo"]) button:hover {
            color: #ffffff !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # BARRA DE MENU HORIZONTAL ALINHADA À ESQUERDA
    col_nav1, col_nav2 = st.columns([1, 4])
    with col_nav1:
        if st.button("🏠 Página Inicial", key="nav_home_limpo"):
            st.session_state.tela_atual = "home"
            st.rerun()
    with col_nav2:
        if st.session_state.aba_consumidor != "menu_triagem":
            if st.button("🗂️ Mudar Categoria", key="nav_cat_limpo"):
                st.session_state.aba_consumidor = "menu_triagem"
                st.rerun()
    with col_nav2:
        if st.session_state.aba_consumidor != "menu_triagem":
            if st.button("🗂️ Mudar Categoria", key="nav_cat_limpo"):
                st.session_state.aba_consumidor = "menu_triagem"
                st.rerun()
    st.markdown(
        "<h1 style='text-align: center; "
        "font-weight: 900; margin-bottom: 0px;"
        "'>🔍 E o que falta?</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center; "
        "font-size: 16px; font-style: italic; "
        "color: #aaaaaa; margin-top: 5px; "
        "margin-bottom: 25px;'>O termômetro "
        "de carências da nossa região.</p>",
        unsafe_allow_html=True
    )

    if st.session_state.aba_consumidor == \
       "menu_triagem":
        st.markdown(
            "##### 📍 Região/Cidade da falta:"
        )
        regiao_final = st.text_input(
            label="Localizacao",
            placeholder="Ex: São Paulo/SP - Centro",
            key="input_regiao_via_unica",
            label_visibility="collapsed"
        )
        st.write(
            "Escolha o tipo de ausência "
            "que você quer sinalizar:"
        )
        if st.button(
            "📦 PRODUTO OU MARCA EM FALTA",
            use_container_width=True,
            key="triagem_prod"
        ):
            st.session_state.aba_consumidor = \
                "produto"
            st.rerun()
        if st.button(
            "🏪 NOVO COMÉRCIO LOCAL",
            use_container_width=True,
            key="triagem_serv"
        ):
            st.session_state.aba_consumidor = \
                "servico"
            st.rerun()
        if st.button(
            "🏛️ ZELADORIA PÚBLICA",
            use_container_width=True,
            key="triagem_infra"
        ):
            st.session_state.aba_consumidor = \
                "infra"
            st.rerun()

        st.write("")
        st.markdown(
            "### 🏆 Impactos Recentes no Bairro"
        )
        try:
            resolvidos = supabase\
                .table("relatos_escassez")\
                .select(
                    "item_solicitado, sub_segmento, "
                    "locais_destino(nome_exibicao, "
                    "regiao_cidade)"
                ).eq("status", "Atendido")\
                .order("data_registro", desc=True)\
                .limit(20).execute()
            if resolvidos.data:
                lista_impactos = []
                for item in resolvidos.data:
                    if item.get("locais_destino"):
                        item_limpo_vitrine = str(
                            item["item_solicitado"]
                        ).rstrip(" 0123456789")\
                         .strip().title()
                        lista_impactos.append({
                            "item": item_limpo_vitrine,
                            "nicho": item.get(
                                "sub_segmento", "Geral"
                            ).strip(),
                            "local": item[
                                "locais_destino"]
                            ["nome_exibicao"]
                            .strip().title(),
                            "cidade_exibicao": item[
                                "locais_destino"]
                            ["regiao_cidade"]
                            .strip()
                        })
                df_imp = pd.DataFrame(lista_impactos)\
                    .drop_duplicates(subset=["local"])\
                    .drop_duplicates(subset=["nicho"])

                contador_exibidos = 0
                for _, l_imp in df_imp.iterrows():
                    if contador_exibidos >= 3:
                        break
                    n_nicho = l_imp['nicho']
                    if n_nicho == "Supermercado":
                        icone, acao = "🛒 Varejo:", "repos"
                    elif n_nicho in ["Saude", "Saúde"]:
                        icone, acao = "🩺 Saúde:", "trouxe"
                    elif n_nicho == "Petshop":
                        icone, acao = "🐶 Pet:", "disponibilizou"
                    elif n_nicho == "Beleza":
                        icone, acao = "💈 Estética:", "ativou"
                    else:
                        icone, acao = "✨ Conquista:", "liberou"

                    st.markdown(
                        f"<div style='background-color: "
                        f"#1A1A1A; padding: 0.6rem 1rem; "
                        f"border-radius: 8px; border-left: "
                        f"4px solid #00803B; margin-bottom: "
                        f"8px;'><span style='font-size: "
                        f"13px; color: #aaaaaa; "
                        f"font-weight: 500;'>✅ <b>{icone}"
                        f"</b> {l_imp['local']} {acao} "
                        f"<b>{l_imp['item']}</b>!</span>"
                        f"</div>", unsafe_allow_html=True
                    )
                    contador_exibidos += 1
            else:
                st.write("ℹ️ Nenhuma conquista.")
        except:
            pass
    elif st.session_state.aba_consumidor in \
            ["produto", "servico", "infra"]:
        aba = st.session_state.aba_consumidor
        if aba == "produto":
            l_i, p_i = "Qual produto falta?", \
                       "Ex: Leite condensado..."
            l_l, p_l = "Em qual mercado?", \
                       "Ex: Nome do mercado..."
            l_c, t_e = "🔔 Ativar chance de aviso na reposição? (Opcional)", \
                       "Produto / Marca"
        elif aba == "servico":
            l_i, p_i = "Qual comércio falta?", \
                       "Ex: Sapataria, lavanderia..."
            l_l, p_l = "Em qual rua ou ponto?", \
                       "Ex: Avenida Principal..."
            l_c, t_e = "🔔 Ativar chance de aviso na abertura? (Opcional)", \
                       "Serviço Local"
        elif aba == "infra":
            l_i, p_i = "Qual o problema público?", \
                       "Ex: Falha na iluminação..."
            l_l, p_l = "Qual a referência?", \
                       "Ex: Posto de saúde do bairro Y..."
            l_c, t_e = "🔔 Ativar chance de aviso na conclusão? (Opcional)", \
                       "Serviço Público / Infraestrutura"

        st.write("")
        with st.form(
            key="formulario_dinamico_consumidor",
            clear_on_submit=False
        ):
            # REMOVIDO AUTOFOCUS: Evita a quebra por parâmetro inexistente
            item_solicitado = st.text_input(
                label=l_i, placeholder=p_i,
                key="input_item"
            )
            local_ocorrencia = st.text_input(
                label=l_l, placeholder=p_l,
                key="input_local"
            )
            contato_usuario = st.text_input(
                label=l_c,
                placeholder="Insira WhatsApp ou e-mail para tentarmos te avisar, caso o comerciante informe.",
                key="input_contato"
            )
            observacao_usuario = None
            with st.expander(
                "➕ Adicionar mais detalhes (Opcional)"
            ):
                observacao_usuario = st.text_area(
                    label="Detalhes:",
                    placeholder="Ex: Detalhe o ocorrido...",
                    key="input_obs"
                )
            botao_enviar = st.form_submit_button(
                "🔍 SINALIZAR ESTA FALTA",
                use_container_width=True
            )
        if botao_enviar and item_solicitado and \
           local_ocorrencia:
            try:
                hash_disp = obter_pegada_digital()
                reg_s = st.session_state.get(
                    "input_regiao_via_unica",
                    "São Paulo/SP - Centro"
                )
                txt_reg = reg_s.strip() if reg_s else \
                    "São Paulo/SP - Centro"
                loc_fmt = local_ocorrencia.strip().title()

                l_data = supabase.table("locais_destino")\
                    .insert({
                        "nome_exibicao": loc_fmt,
                        "regiao_cidade": txt_reg,
                        "regiao_estado": "SP"
                    }).execute()
                l_id = l_data.data[0]["id"] if (
                    l_data and l_data.data and
                    len(l_data.data) > 0
                ) else None

                if l_id:
                    seg_det = "Geral"
                    txt_u = item_solicitado.strip().lower()
                    if any(p in txt_u for p in [
                        "leite", "arroz", "feijão", "café",
                        "açúcar", "pão", "mercado", "óleo"
                    ]):
                        seg_det = "Supermercado"
                    elif any(p in txt_u for p in [
                        "remédio", "médico", "dentista",
                        "farmácia", "clínica"
                    ]):
                        seg_det = "Saúde"
                    elif any(p in txt_u for p in [
                        "ração", "pet", "cachorro",
                        "gato", "petshop"
                    ]):
                        seg_det = "Petshop"
                    elif any(p in txt_u for p in [
                        "manicure", "salão",
                        "cabeleireiro", "estética"
                    ]):
                        seg_det = "Beleza"

                    txt_o = observacao_usuario.strip() \
                        if observacao_usuario else None
                    c_aviso = contato_usuario.strip() \
                        if contato_usuario else None

                    supabase.table("relatos_escassez")\
                        .insert({
                            "local_id": l_id,
                            "item_solicitado":
                                item_solicitado.strip().title(),
                            "tipo_carencia": t_e,
                            "status": "Pendente",
                            "sub_segmento": seg_det,
                            "pegada_digital": hash_disp,
                            "observacao_detalhe": txt_o,
                            "contato_aviso": c_aviso
                        }).execute()
                    st.success("✅ Sinalizado com sucesso!")
                    time.sleep(1.2)
                    st.session_state.aba_consumidor = \
                        "menu_triagem"
                    st.session_state.tela_atual = "home"
                    st.rerun()
            except Exception as e:
                st.error(f"⚠️ Erro de persistência: {str(e)}")
