# --- TELA: FORMULÁRIO DO CONSUMIDOR ---
elif st.session_state.tela_atual == "consumidor":
    col_nav1, col_nav2 = st.columns(2, gap="small")
    with col_nav1:
        if st.button("🏠 Ir para Home", key="nav_home_simetrico", use_container_width=True):
            st.session_state.tela_atual = "home"
            st.rerun()
    with col_nav2:
        if st.session_state.aba_consumidor != "menu_triagem":
            if st.button("🗂️ Mudar Categoria", key="nav_categoria_simetrico", use_container_width=True):
                st.session_state.aba_consumidor = "menu_triagem"
                st.rerun()
    st.title("🔍 E o que falta?")
    if st.session_state.aba_consumidor == "menu_triagem":
        st.markdown("##### 📍 Onde você está agora?")
        regiao_final = st.text_input(label="Localizacao", placeholder="Ex: São Paulo/SP - Centro",
                                     key="input_regiao_via_unica", label_visibility="collapsed")
        st.write(
            "Escolha o tipo de ausência que você quer registrar no bairro ou comunidade:")
        if st.button("📦 PRODUTO OU MARCA EM FALTA\n(Falta nas gôndolas de mercados, farmácias...)", use_container_width=True, key="triagem_prod"):
            st.session_state.aba_consumidor = "produto"
            st.rerun()
        st.write("")
        if st.button("🏪 NOVO COMÉRCIO OU SERVIÇO LOCAL\n(Falta de lavanderia, sapataria, padaria...)", use_container_width=True, key="triagem_serv"):
            st.session_state.aba_consumidor = "servico"
            st.rerun()
        st.write("")
        if st.button("🏛️ INFRAESTRUTURA OU ZELADORIA PÚBLICA\n(Falha na iluminação, buracos no asfalto...)", use_container_width=True, key="triagem_infra"):
            st.session_state.aba_consumidor = "infra"
            st.rerun()
    else:
        if st.session_state.aba_consumidor == "produto":
            st.markdown(
                "### 📦 Produto / Marca\n##### *Mapeando falhas de estoque e gôndolas vazias.*")
            label_item, placeholder_item = "Qual produto ou marca você buscou e não encontrou?", "Ex: Leite condensado marca X..."
            label_local, placeholder_local = "Em qual estabelecimento isso ocorreu?", "Ex: Nome do mercado, farmácia..."
            label_contato, tipo_envio = "Quer ser avisado caso o estoque seja reposto ou outra loja ofereça? (Opcional)", "Produto / Marca"
        elif st.session_state.aba_consumidor == "servico":
            st.markdown(
                "### 🏪 Novo Comércio / Serviço\n##### *Mapeando oportunidades de novos negócios e conveniência.*")
            label_item, placeholder_item = "Qual tipo de comércio ou serviço falta neste bairro/comunidade?", "Ex: Sapataria, lavanderia..."
            label_local, placeholder_local = "Em qual rua, travessa, faculdade ou ponto isso faz falta?", "Ex: Avenida Principal..."
            label_contato, tipo_envio = "Quer ser avisado caso este serviço seja aberto ou oferecido? (Opcional)", "Serviço Local / Novo Estabelecimento"
        else:
            st.markdown(
                "### 🏛️ Infraestrutura / Zeladoria\n##### *Mapeando melhorias urbanas e cobranças públicas.*")
            label_item, placeholder_item = "Qual carência de infraestrutura/manutenção você identificou?", "Ex: Falha na iluminação..."
            label_local, placeholder_local = "Qual o ponto de referência ou localidade exata?", "Ex: Posto de saúde do bairro Y..."
            label_contato, tipo_envio = "Quer ser avisado caso esta manutenção pública seja realizada? (Opcional)", "Serviço Público / Infraestrutura"
        st.write("")
        with st.form(key="formulario_dinamico_consumidor", clear_on_submit=False):
            item_solicitado = st.text_input(
                label=label_item, placeholder=placeholder_item, key="input_item")
            local_ocorrencia = st.text_input(
                label=label_local, placeholder=placeholder_local, key="input_local")
            observacao_usuario = st.text_area(
                label="Mais detalhes (Opcional):", placeholder="Ex: Detalhe o ocorrido...", key="input_obs")
            contato_usuario = st.text_input(
                label=label_contato, placeholder="Ex: Seu e-mail ou WhatsApp...", key="input_contato")
            st.write("")
            botao_enviar = st.form_submit_button(
                "Registrar Ocorrência", use_container_width=True)
        if botao_enviar:
            if item_solicitado and local_ocorrencia:
                texto_usuario, local_usuario = item_solicitado.strip(
                ).lower(), local_ocorrencia.strip().lower()
                obs_texto = observacao_usuario.strip().lower() if observacao_usuario else ""
                palavras_ofensivas = ["porra", "caralho", "puta", "merda", "bosta",
                                      "vai tomar", "fudeu", "ladrão", "roubo", "safado", "vagabundo"]
                termos_politicos_proibidos = ["pec", "deputado", "senado", "senador",
                                              "presidente", "governador", "partido", "impeachment", "voto", "eleição"]
                excecoes_contexto = [
                    "saco de lixo", "sacos de lixo", "lixeira", "pá de lixo", "coleta de lixo"]
                contem_bloqueio, mensagem_erro = False, ""
                if any(p in texto_usuario for p in palavras_ofensivas) or any(p in local_usuario for p in palavras_ofensivas) or any(p in obs_texto for p in palavras_ofensivas):
                    contem_bloqueio = True
                    mensagem_erro = "⚠️ O sistema identificou termos impróprios ou linguagem ofensiva."
                if any(p in texto_usuario for p in termos_politicos_proibidos) or any(p in local_usuario for p in termos_politicos_proibidos) or any(p in obs_texto for p in termos_politicos_proibidos):
                    contem_bloqueio = True
                    mensagem_erro = "⚠️ O portal é focado estritamente em zeladoria e carências locais."
                if "lixo" in texto_usuario or "lixo" in local_usuario:
                    if not any(e in texto_usuario for e in excecoes_contexto) and not any(e in local_usuario for e in excecoes_contexto):
                        contem_bloqueio = True
                        mensagem_erro = "⚠️ O sistema identificou termos impróprios ou linguagem ofensiva."
                palavras_infra = ["rua", "praça", "iluminação", "poste", "asfalto",
                                  "médico", "ônibus", "hospital", "bueiro", "segurança", "polícia"]
                palavras_produto = ["leite", "fralda", "ração", "refrigerante",
                                    "cerveja", "sabão", "remédio", "arroz", "feijão", "café", "açúcar"]
                erro_detectado = False
                if contem_bloqueio:
                    st.error(mensagem_erro)
                    erro_detectado = True
                elif tipo_envio == "Produto / Marca" and any(p in texto_usuario for p in palavras_infra):
                    st.error(
                        "⚠️ Ops! Parece um problema de Infraestrutura Pública. Modifique no menu principal.")
                    erro_detectado = True
                elif tipo_envio == "Serviço Local / Novo Estabelecimento" and any(p in texto_usuario for p in palavras_produto):
                    st.error(
                        "⚠️ Ops! Parece a falta de um produto de mercado. Modifique no menu principal.")
                    erro_detectado = True
                if not erro_detectado:
                    try:
                        hash_dispositivo = obter_pegada_digital()
                        regiao_salva = st.session_state.get(
                            "input_regiao_via_unica", "São Paulo/SP - Centro")
                        texto_regiao = regiao_salva.strip().title(
                        ) if regiao_salva else "São Paulo/SP - Centro"
                        estado_detectado = "SP"
                        if "/" in texto_regiao:
                            try:
                                estado_detectado = texto_regiao.split(
                                    "/")[1].split("-")[0].strip().upper()[:2]
                            except:
                                estado_detectado = "SP"
                        local_formatado = local_ocorrencia.strip().title()
                        local_data = supabase.table("locais_destino").insert(
                            {"nome_exibicao": local_formatado, "regiao_cidade": texto_regiao, "regiao_estado": estado_detectado}).execute()
                        local_id = local_data.data[0]["id"] if local_data.data and len(
                            local_data.data) > 0 else None
                        if local_id:
                            item_formatado = item_solicitado.strip().title()
                            segmento_detectado = "Geral"
                            if any(p in texto_usuario for p in ["leite", "arroz", "feijão", "café", "açúcar", "refrigerante", "cerveja", "sabão", "pão", "padaria", "mercado"]):
                                segmento_detectado = "Supermercado"
                            elif any(p in texto_usuario for p in ["remédio", "fisioterapeuta", "clínica", "médico", "psicólogo", "dentista", "farmácia"]):
                                segmento_detectado = "Saude"
                            elif any(p in texto_usuario for p in ["ração", "pet", "cachorro", "gato", "veterinária", "tosa", "banho", "petshop"]):
                                segmento_detectado = "Petshop"
                            elif any(p in texto_usuario for p in ["manicure", "salão", "barbearia", "cabeleireiro", "estética", "barbeiro", "unha"]):
                                segmento_detectado = "Beleza"
                            texto_obs = observacao_usuario.strip() if observacao_usuario else None
                            supabase.table("relatos_escassez").insert({"local_id": local_id, "item_solicitado": item_formatado, "tipo_carencia": tipo_envio, "status": "Pendente", "contato_aviso": contato_usuario.strip(
                            ) if contato_usuario else None, "detalhes_adicionais": texto_obs, "observacao_detalhe": texto_obs, "sub_segmento": segmento_detectado, "pegada_digital": hash_dispositivo}).execute()
                            st.success(
                                "✅ Registro computado com anonimato garantido!")
                            import time
                            time.sleep(1.5)
                            st.session_state.aba_consumidor = "menu_triagem"
                            st.session_state.tela_atual = "home"
                            st.rerun()
                    except Exception as e:
                        st.error(f"⚠️ Erro técnico detalhado: {str(e)}")
            else:
                st.warning("⚠️ Por favor, preencha os campos obrigatórios.")
    st.write("")
    st.markdown("### 🏆 Impactos Recentes no Bairro")
    try:
        resolvidos = supabase.table("relatos_escassez").select(
            "item_solicitado, locais_destino(nome_exibicao)").eq("status", "Atendido").limit(3).execute()
        if resolvidos.data and len(resolvidos.data) > 0:
            for item in resolvidos.data:
                if item.get("locais_destino"):
                    st.info(
                        f"✅ **{item['locais_destino']['nome_exibicao']}** repôs o estoque: **{item['item_solicitado']}**!")
        else:
            st.write("ℹ️ Nenhuma benfeitoria registrada nos últimos dias.")
    except:
        pass

# --- TELA: AUTENTICAÇÃO POR TOKEN ---
elif st.session_state.tela_atual == "autenticacao":
    if st.button("⬅️ Voltar ao Menu Principal", key="btn_voltar_aut"):
        st.session_state.tela_atual = "home"
        st.session_state.token_valido = False
        st.rerun()
    st.markdown("<h1 style='text-align: center; margin-bottom: 0px !important;'>🔍 E o que falta?</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; font-weight: 600; color: #aaaaaa !important; margin-top: 5px; margin-bottom: 25px;'>Área Restrita para Comerciantes e Gestores</p>", unsafe_allow_html=True)
    st.write("---")
    token_inserido = st.text_input(
        label="Token de Acesso:", type="password", placeholder="Digite seu token de acesso...")
    st.write("")
    if st.button("Validar Credenciais e Acessar", use_container_width=True, key="btn_validar_token_hibrido") or (token_inserido and not st.session_state.token_valido):
        if token_inserido in ["COMERCIO10", "SUPER_VILA_77"]:
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "comerciante"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_inserido == "SAUDE20":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "saude"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_inserido == "PET30":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "petshop"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_inserido == "BELEZA40":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "beleza"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_inserido == "INVEST20":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "investidor"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_inserido == "GESTOR30":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "gestor"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_inserido == "MIDIA40":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "jornalista"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_inserido == "ADMIN99":
            st.session_state.token_valido = True
            st.session_state.perfil_cliente = "admin"
            st.session_state.tela_atual = "comerciante"
            st.rerun()
        elif token_inserido != "":
            st.error("❌ Token inválido.")

        elif st.session_state.tela_atual == "comerciante":
            if not st.session_state.token_valido:
                st.session_state.tela_atual = "home"
        st.rerun()
        if st.button("⬅️ Sair do Painel (Logoff)", key="btn_voltar_com"):
            st.session_state.tela_atual = "home"
        st.session_state.token_valido = False
        st.perfil_cliente = None
        st.session_state.busca_ativa = False
        st.session_state.dados_grafico = None
        st.rerun()
    st.markdown("<h1 style='text-align: center; margin-bottom: 0px !important;'>🔍 E o que falta?</h1>",
                unsafe_allow_html=True)
    loja_alvo_prioridade = "Mercadinho Do Bairro" if st.session_state.perfil_cliente == "comerciante" else ""
    espectador_analitico = st.session_state.perfil_cliente in [
        "investidor", "gestor", "jornalista"]

    if st.session_state.perfil_cliente == "comerciante":
        opcoes_filtro = [
            "Apenas Produtos/Marcas (Varejo)", "🎯 Marketplace Reverso (Oportunidades Gerais do Bairro)"]
        st.markdown(
            "##### 🏪 *Nível de Acesso: Varejo Local (Foco em Gôndolas)*")
    elif st.session_state.perfil_cliente == "saude":
        opcoes_filtro = ["Apenas Serviços de Saúde e Clínicas",
                         "🎯 Marketplace Reverso (Oportunidades Gerais do Bairro)"]
        st.markdown("##### 🩺 *Nível de Acesso: Saúde & Bem-Estar*")
    elif st.session_state.perfil_cliente == "petshop":
        opcoes_filtro = ["Apenas Produtos e Serviços Pet",
                         "🎯 Marketplace Reverso (Oportunidades Gerais do Bairro)"]
        st.markdown("##### 🐶 *Nível de Acesso: Petshop & Veterinária*")
    elif st.session_state.perfil_cliente == "beleza":
        opcoes_filtro = ["Apenas Serviços de Estética e Beleza",
                         "🎯 Marketplace Reverso (Oportunidades Gerais do Bairro)"]
        st.markdown("##### 💈 *Nível de Acesso: Beleza & Estética*")
    elif st.session_state.perfil_cliente == "investidor":
        opcoes_filtro = ["Oportunidades de Novos Negócios (Serviços)"]
        st.markdown(
            "##### 💼 *Nível de Acesso: Investidor e Expansão (Vazios Comerciais)*")
    elif st.session_state.perfil_cliente == "jornalista":
        opcoes_filtro = [
            "Infraestrutura Urbana (Setor Público)", "Oportunidades de Novos Negócios (Serviços)"]
        st.markdown(
            "##### 📰 *Nível de Acesso: Imprensa e Jornalismo Regional (Dados Consolidados)*")
    elif st.session_state.perfil_cliente == "admin":
        opcoes_filtro = ["Painel de Controle Administrativo"]
        st.markdown("<p style='text-align: center; font-size: 24px; font-weight: 600; color: #aaaaaa !important; margin-top: 5px; margin-bottom: 25px;'>Painel de Controle Mestre</p>", unsafe_allow_html=True)
    else:
        opcoes_filtro = ["Infraestrutura Urbana (Setor Público)"]
        st.markdown(
            "##### 🏛️ *Nível de Acesso: Gestão Pública (Foco em Infraestrutura)*")

    st.write("---")
    filtro_frente = st.selectbox(
        label="Selecione a Frente de Inteligência:", options=opcoes_filtro, key="selectbox_frente")
    termo_busca = st.text_input(label="Refinar por palavra-chave ou estabelecimento (Opcional):",
                                placeholder="Digite para filtrar a lista abaixo...", key="input_busca_painel")

    # --- INTERFACE MASTER ISOLADA: EXCLUSIVA DO ADMINISTRADOR MESTRE ---
    if st.session_state.perfil_cliente == "admin":
        st.markdown("### 🛠️ Cadastro de Assinantes")
        st.markdown(
            "##### *Preencha os campos para emissão automática de tokens UUID na nuvem.*")
        id_formulario_admin = f"form_cadastro_admin_{datetime.datetime.now().strftime('%M%S')}"
        with st.form(key=id_formulario_admin, clear_on_submit=True):
            nome_novo_comercio = st.text_input(
                "Nome do Estabelecimento Comercial / Cliente Real:", placeholder="Ex: Supermercado Xavier, Petshop Bairro Alto...")
            perfil_novo_comercio = st.selectbox("Perfil de Acesso Corporativo (Nível de Filtro):", [
                                                "comerciante", "saude", "petshop", "beleza", "investidor", "gestor", "jornalista"])
            st.write("")
            if st.form_submit_button("💼 Cadastrar Cliente e Emitir Token UUID"):
                if nome_novo_comercio:
                    try:
                        novo_registro = supabase.table("clientes_b2b").insert(
                            {"nome_estabelecimento": nome_novo_comercio.strip().title(), "perfil_segmento": perfil_novo_comercio}).execute()
                        if novo_registro.data:
                            st.success(
                                "🎉 Cliente cadastrado com sucesso absoluto na nuvem!")
                            st.info(
                                f"🔑 **TOKEN PRIVADO GERADO:** `{novo_registro.data['token_acesso']}`")
                            st.warning(
                                "Copie o código acima e envie agora mesmo para o WhatsApp do cliente pagante.")
                    except Exception as error_db:
                        st.error(
                            f"⚠️ Falha na conexão com o banco: {str(error_db)}")
                else:
                    st.warning(
                        "⚠️ Preencha o nome do estabelecimento para emitir a credencial.")
    # --- PROCESSAMENTO GLOBAL DE DADOS REAL / SIMULADO ---
    if st.session_state.perfil_cliente != "admin":
        if not st.session_state.busca_ativa or st.session_state.dados_grafico is None:
            st.session_state.busca_ativa = True
            try:
                resposta = supabase.table("relatos_escassez").select(
                    "id, item_solicitado, tipo_carencia, data_registro, status, detalhes_adicionais, observacao_detalhe, sub_segmento, pegada_digital, contato_aviso, locais_destino(nome_exibicao, regiao_cidade)").execute()
                dados_limpos = []
                agora = datetime.datetime.now(datetime.timezone.utc)
                if resposta.data and len(resposta.data) > 0:
                    for registro in resposta.data:
                        if registro.get("locais_destino"):
                            sub_seg = str(registro.get(
                                "sub_segmento", "Geral")).strip()
                            cat_bruta = str(registro.get(
                                "tipo_carencia", "Produto / Marca")).strip()
                            if st.session_state.perfil_cliente in ["comerciante", "saude", "petshop", "beleza"] and ("Infra" in cat_bruta or "Público" in cat_bruta or "Publico" in cat_bruta):
                                continue
                            if "Marketplace" not in filtro_frente and not espectador_analitico:
                                if st.session_state.perfil_cliente == "comerciante" and "Super" not in sub_seg:
                                    continue
                                elif st.session_state.perfil_cliente == "saude" and "Saude" not in sub_seg and "Saúde" not in sub_seg:
                                    continue
                                elif st.session_state.perfil_cliente == "petshop" and "Pet" not in sub_seg:
                                    continue
                                elif st.session_state.perfil_cliente == "beleza" and "Beleza" not in sub_seg:
                                    continue
                            if st.session_state.perfil_cliente == "investidor" and ("Invest" not in sub_seg or "Local" not in cat_bruta):
                                continue
                            if st.session_state.perfil_cliente == "jornalista" and ("Super" in sub_seg or "Saude" in sub_seg or "Pet" in sub_seg or "Beleza" in sub_seg):
                                continue
                            if st.session_state.perfil_cliente == "gestor" and ("Infra" not in cat_bruta and "Público" not in cat_bruta and "Publico" not in cat_bruta):
                                continue
                            idade_dias = max(0, (agora - datetime.datetime.fromisoformat(registro.get(
                                "data_registro").replace("Z", "+00:00"))).days) if registro.get("data_registro") else 0
                            categoria_limpa = "Serviço Público / Infraestrutura" if ("Público" in cat_bruta or "Publico" in cat_bruta or "Infra" in cat_bruta or "Zeladoria" in sub_seg) else (
                                "Serviço Local / Novo Estabelecimento" if ("Local" in cat_bruta or "Invest" in sub_seg) else "Produto / Marca")
                            dados_limpos.append({"ID": registro["id"], "O que Falta": registro["item_solicitado"].strip().title(), "Categoria": categoria_limpa, "Local/Referência": registro["locais_destino"]["nome_exibicao"], "Cidade": registro["locais_destino"]["regiao_cidade"],
                                                "Dias": idade_dias, "Observação": registro.get("observacao_detalhe") or registro.get("detalhes_adicionais") or "", "SubSegmento": sub_seg, "Pegada": registro.get("pegada_digital") or f"anon_{registro['id']}", "Contato": registro.get("contato_aviso") or ""})

                dados_mock = [
                    {"ID": 991, "O que Falta": "Leite Desnatado Parmalat 1L", "Categoria": "Produto / Marca", "Local/Referência": "Mercadinho Do Bairro",
                        "Cidade": "São Paulo/SP - Centro", "Dias": 4, "Observação": "Falta toda quarta.", "SubSegmento": "Supermercado", "Pegada": "hash1", "Contato": "11999999999"},
                    {"ID": 994, "O que Falta": "Lavanderia Expressa Auto-Serviço", "Categoria": "Serviço Local / Novo Estabelecimento", "Local/Referência": "Avenida Das Palmeiras",
                        "Cidade": "São Paulo/SP - Tatuapé", "Dias": 45, "Observação": "Prédios novos sem serviço.", "SubSegmento": "Investimento", "Pegada": "hash4", "Contato": ""},
                    {"ID": 997, "O que Falta": "Manutenção De Iluminação Pública", "Categoria": "Serviço Público / Infraestrutura", "Local/Referência": "Rua das Flores, 40",
                        "Cidade": "São Paulo/SP - Centro", "Dias": 2, "Observação": "Poste apagado.", "SubSegmento": "Zeladoria", "Pegada": "hash7", "Contato": ""}
                ]
                for m in dados_mock:
                    if not any(d["O que Falta"].lower() == m["O que Falta"].lower() for d in dados_limpos):
                        dados_limpos.append(m)
                if st.session_state.perfil_cliente == "comerciante":
                    dados_limpos = [d for d in dados_limpos if "Super" in str(
                        d["SubSegmento"]) and d["Categoria"] != "Serviço Público / Infraestrutura"]
                elif st.session_state.perfil_cliente == "saude":
                    dados_limpos = [d for d in dados_limpos if ("Saude" in str(d["SubSegmento"]) or "Saúde" in str(
                        d["SubSegmento"])) and d["Categoria"] != "Serviço Público / Infraestrutura"]
                elif st.session_state.perfil_cliente == "petshop":
                    dados_limpos = [d for d in dados_limpos if "Pet" in str(
                        d["SubSegmento"]) and d["Categoria"] != "Serviço Público / Infraestrutura"]
                elif st.session_state.perfil_cliente == "beleza":
                    dados_limpos = [d for d in dados_limpos if "Beleza" in str(
                        d["SubSegmento"]) and d["Categoria"] != "Serviço Público / Infraestrutura"]
                elif st.session_state.perfil_cliente == "investidor":
                    dados_limpos = [
                        d for d in dados_limpos if "Invest" in str(d["SubSegmento"])]
                elif st.session_state.perfil_cliente == "gestor":
                    dados_limpos = [d for d in dados_limpos if d["Categoria"] ==
                                    "Serviço Público / Infraestrutura" or "Zeladoria" in str(d["SubSegmento"])]
                elif st.session_state.perfil_cliente == "jornalista":
                    dados_limpos = [d for d in dados_limpos if "Zeladoria" in str(
                        d["SubSegmento"]) or "Invest" in str(d["SubSegmento"])]
                st.session_state.dados_grafico = pd.DataFrame(dados_limpos)
            except Exception as e:
                st.error(f"⚠️ Erro técnico: {str(e)}")
        if st.session_state.busca_ativa and st.session_state.dados_grafico is not None:
            df = st.session_state.dados_grafico
            if not df.empty:
                df_filtrado = df
                if filtro_frente == "Infraestrutura Urbana (Setor Público)":
                    df_filtrado = df[df['Categoria'] ==
                                     "Serviço Público / Infraestrutura"]
                elif filtro_frente == "Oportunidades de Novos Negócios (Serviços)":
                    df_filtrado = df[df['Categoria'] ==
                                     "Serviço Local / Novo Estabelecimento"]
                elif filtro_frente == "Apenas Produtos/Marcas (Varejo)":
                    df_filtrado = df[df['Categoria'] == "Produto / Marca"]
                if termo_busca:
                    df_filtrado = df_filtrado[df_filtrado['O que Falta'].str.contains(
                        termo_busca, case=False) | df_filtrado['Local/Referência'].str.contains(termo_busca, case=False)]
                if not df_filtrado.empty:
                    df_filtrado['É_Minha_Loja'] = df_filtrado['Local/Referência'].apply(
                        lambda x: 1 if x == loja_alvo_prioridade else 0)
                    if espectador_analitico:
                        st.markdown("#### 📈 Ranking de Oportunidades")
                        st.markdown(
                            f"<div style='text-align: right; font-size: 13px; color: #888888; margin-top:-35px; margin-bottom:15px;'>Total de Oportunidades: {len(df_filtrado)}</div>", unsafe_allow_html=True)
                        st.download_button(label="Baixar Relatório de Vazios (PDF)", data=b"PDF_DUMMY",
                                           file_name="expansao.pdf", mime="application/pdf", key=f"btn_pdf_{filtro_frente}")
                        st.write("---")
                        df_agrupado_mestre = df_filtrado.groupby(["O que Falta", "Categoria"]).agg(Clientes_Unicos=("Pegada", "nunique"), Alertas_Totais=(
                            "ID", "count"), Maior_Espera=("Dias", "max")).sort_values(by="Clientes_Unicos", ascending=False).reset_index()
                        for indice, mestre_line in df_agrupado_mestre.iterrows():
                            item_nome = mestre_line['O que Falta']
                            clientes = int(mestre_line['Clientes_Unicos'])
                            alertas = int(mestre_line['Alertas_Totais'])
                            classe_tag = "tag-calor-alta" if clientes >= 5 else (
                                "tag-calor-media" if clientes >= 2 else "tag-calor-baixa")
                            label_tag = f"🔥 CRÍTICO • {clientes} CPFs" if clientes >= 5 else (
                                f"⚠️ OPORTUNIDADE • {clientes} CPFs" if clientes >= 2 else f"🔹 INICIAL • {clientes} CPF")
                            st.markdown(
                                f'<div class="bloco-lista-premium"><span class="{classe_tag}">{label_tag}</span><b style="color: #FFFFFF; font-size: 16px;">🏢 Falta: {item_nome}</b><div style="margin-top: 0.5rem; color: #aaaaaa; font-size: 13px;">⏱️ Demanda de {alertas} relatos • Maior espera: {mestre_line["Maior_Espera"]} dias</div></div>', unsafe_allow_html=True)
                            detalhes_item = df_filtrado[df_filtrado['O que Falta'] == item_nome]
                            st.write(
                                "📍 **Localização e Detalhes das Ocorrências Coletadas:**")
                            for _, sub_item in detalhes_item.iterrows():
                                st.markdown(
                                    f"  * **{sub_item['Cidade']}** - *Ponto:* {sub_item['Local/Referência']}")
                                if sub_item['Observação']:
                                    st.markdown(
                                        f"    * 💬 *Relato:* \"{sub_item['Observação']}\"")
                            st.markdown(
                                "<hr style='border-top: 1px dashed #333; margin: 1rem 0;'/>", unsafe_allow_html=True)
                    else:
                        st.markdown("#### 📈 Detalhamento das Demandas Ativas")
                        total_sua_loja = len(
                            df_filtrado[df_filtrado['Local/Referência'] == loja_alvo_prioridade])
                        total_conconrrencia = len(df_filtrado) - total_sua_loja
                        st.markdown(
                            f"<div style='text-align: right; font-size: 12px; color: #888888; margin-top:-35px; margin-bottom:15px;'>Sua Loja: {total_sua_loja} • Concorrência: {total_conconrrencia} • Total Geral: {len(df_filtrado)}</div>", unsafe_allow_html=True)
                        st.download_button(label="Baixar Relatório (PDF)", data=b"PDF",
                                           file_name="relatorio.pdf", mime="application/pdf", key="btn_pdf_operacional")
                        st.write("---")
                        df_agrupado_mestre = df_filtrado.groupby(["O que Falta", "Categoria"]).agg(Volume_Total=("ID", "count"), Menor_Idade=(
                            "Dias", "min"), Foco_Dono=("É_Minha_Loja", "max")).sort_values(by=["Foco_Dono", "Volume_Total"], ascending=[False, False]).reset_index()
                        for indice, linha in df_agrupado_mestre.iterrows():
                            item_nome = linha['O que Falta']
                            volume = float(linha['Volume_Total'])
                            sou_alvo = int(linha['Foco_Dono'])
                            classe_tag, label_tag = ("tag-calor-media", f"🎯 REVERSO • {int(volume)} Pedidos") if "Marketplace" in filtro_frente else (
                                ("tag-calor-alta", f"🎯 SEU MERCADO • {int(volume)} Pedidos") if sou_alvo == 1 else ("tag-calor-baixa", f"🌍 CONCORRÊNCIA • {int(volume)} Pedidos"))
                            st.markdown(
                                f'<div class="bloco-lista-premium"><span class="{classe_tag}">{label_tag}</span><b style="color: #FFFFFF; font-size: 16px;">📦 {item_nome}</b><div style="margin-top: 0.5rem; color: #aaaaaa; font-size: 13px;">⏱️ Alerta ativo há {linha["Menor_Idade"]} dias</div></div>', unsafe_allow_html=True)
                            detalhes_item = df_filtrado[df_filtrado['O que Falta'] == item_nome]
                            for _, sub_linha in detalhes_item.iterrows():
                                sub_id = sub_linha['ID']
                                sub_local = sub_linha['Local/Referência']
                                contato_morador = sub_linha['Contato']
                                is_dono_vazio = (
                                    sub_local == loja_alvo_prioridade)
                                st.markdown(
                                    f"{'🔥 **SEU ESTABELECIMENTO:** ' if is_dono_vazio else '📍 **Captado no concorrente:** '}{sub_local} ({sub_linha['Cidade']})")
                                if sub_linha['Observação']:
                                    st.info(
                                        f"💬 *Relato:* \"{sub_linha['Observação']}\"")
                                if contato_morador and ("Marketplace" in filtro_frente or not is_dono_vazio):
                                    st.success(
                                        f"📱 **Cliente Faminto!** WhatsApp: `{contato_morador}`")
                                if "Marketplace" not in filtro_frente and is_dono_vazio:
                                    id_confirmacao = f"confirma_baixa_{sub_id}"
                                    if id_confirmacao not in st.session_state:
                                        st.session_state[id_confirmacao] = False
                                    if not st.session_state[id_confirmacao]:
                                        if st.button(f"Dar baixa no {sub_local}", key=f"btn_pre_{sub_id}"):
                                            st.session_state[id_confirmacao] = True
                                            st.rerun()
                                    else:
                                        st.warning("Confirmar reposição?")
                                        col_b1, col_b2 = st.columns(2)
                                        with col_b1:
                                            if st.button("🚨 Confirmar", key=f"btn_real_{sub_id}"):
                                                supabase.table("relatos_escassez").update(
                                                    {"status": "Atendido"}).eq("id", sub_id).execute()
                                                st.success("🎉 Concluído!")
                                                import time
                                                time.sleep(1)
                                                st.session_state[id_confirmacao] = False
                                                st.session_state.busca_ativa = False
                                                st.rerun()
                                        with col_b2:
                                            if st.button("❌ Cancelar", key=f"btn_cancelar_{sub_id}"):
                                                st.session_state[id_confirmacao] = False
                                                st.rerun()
                            st.markdown(
                                "<hr style='border-top: 1px dashed #333; margin: 1rem 0;'/>", unsafe_allow_html=True)
                else:
                    if st.session_state.perfil_cliente != "admin":
                        st.info(
                            "ℹ️ Nenhum registro ativo encontrado para este filtro.")
            else:
                if st.session_state.perfil_cliente != "admin":
                    st.info("ℹ️ O banco de dados está limpo!")
