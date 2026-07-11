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
                else: st.warning("⚠️ Preencha o nome do estabelecimento para emitir a credencial.")

    # --- PROCESSAMENTO GLOBAL DE DADOS REAL / SIMULADO ---
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
                            elif st.session_state.perfil_cliente == "saude" and "Saude" not in sub_seg and "Saúde" not in sub_seg: continue
                            elif st.session_state.perfil_cliente == "petshop" and "Pet" not in sub_seg:
                                continue
                            elif st.session_state.perfil_cliente == "beleza" and "Beleza" not in sub_seg: continue

                        if st.session_state.perfil_cliente == "investidor" and ("Invest" not in sub_seg or "Local" not in cat_bruta):
                            continue
                        if st.session_state.perfil_cliente == "jornalista" and ("Super" in sub_seg or "Saude" in sub_seg or "Pet" in sub_seg or "Beleza" in sub_seg): continue
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
                dados_limpos = [d for d in dados_limpos if "Super" in str(d["SubSegmento"]) and d["Categoria"] != "Serviço Público / Infraestrutura"]
            elif st.session_state.perfil_cliente == "saude": dados_limpos = [d for d in dados_limpos if ("Saude" in str(d["SubSegmento"]) or "Saúde" in str(d["SubSegmento"])) and d["Categoria"] != "Serviço Público / Infraestrutura"]
            elif st.session_state.perfil_cliente == "petshop":
                dados_limpos = [d for d in dados_limpos if "Pet" in str(d["SubSegmento"]) and d["Categoria"] != "Serviço Público / Infraestrutura"]
            elif st.session_state.perfil_cliente == "beleza": dados_limpos = [d for d in dados_limpos if "Beleza" in str(d["SubSegmento"]) and d["Categoria"] != "Serviço Público / Infraestrutura"]
            elif st.session_state.perfil_cliente == "investidor":
                dados_limpos = [d for d in dados_limpos if "Invest" in str(d["SubSegmento"])]
            elif st.session_state.perfil_cliente == "gestor": dados_limpos = [d for d in dados_limpos if d["Categoria"] == "Serviço Público / Infraestrutura" or "Zeladoria" in str(d["SubSegmento"])]
            elif st.session_state.perfil_cliente == "jornalista":
                dados_limpos = [d for d in dados_limpos if "Zeladoria" in str(d["SubSegmento"]) or "Invest" in str(d["SubSegmento"])]
            st.session_state.dados_grafico = pd.DataFrame(dados_limpos)
        except Exception as e:
            st.error(f"⚠️ Erro técnico: {str(e)}")
    if st.session_state.busca_ativa and st.session_state.dados_grafico is not None:
        df = st.session_state.dados_grafico
        if not df.empty:
            df_filtrado = df
            if filtro_frente == "Infraestrutura Urbana (Setor Público)": df_filtrado = df[df['Categoria'] == "Serviço Público / Infraestrutura"]
            elif filtro_frente == "Oportunidades de Novos Negócios (Serviços)": df_filtrado = df[df['Categoria'] == "Serviço Local / Novo Estabelecimento"]
            elif filtro_frente == "Apenas Produtos/Marcas (Varejo)": df_filtrado = df[df['Categoria'] == "Produto / Marca"]
            if termo_busca: df_filtrado = df_filtrado[df_filtrado['O que Falta'].str.contains(termo_busca, case=False) | df_filtrado['Local/Referência'].str.contains(termo_busca, case=False)]
            
            if not df_filtrado.empty:
                df_filtrado['É_Minha_Loja'] = df_filtrado['Local/Referência'].apply(lambda x: 1 if x == loja_alvo_prioridade else 0)
                
                # --- INTERFACE 1: INTERFACE ANALÍTICA AGRUPADA (INVESTIDOR / GESTOR / JORNALISTA) ---
                if espectador_analitico and st.session_state.perfil_cliente != "admin":
                    st.markdown("#### 📈 Ranking de Oportunidades")
                    st.markdown(f"<div style='text-align: right; font-size: 13px; color: #888888; margin-top:-35px; margin-bottom:15px;'>Total de Oportunidades: {len(df_filtrado)}</div>", unsafe_allow_html=True)
                    st.download_button(label="Baixar Relatório de Vazios (PDF)", data=b"PDF_DUMMY", file_name="expansao.pdf", mime="application/pdf", key=f"btn_pdf_{filtro_frente}")
                    st.write("---")
                    df_agrupado_mestre = df_filtrado.groupby(["O que Falta", "Categoria"]).agg(Clientes_Unicos=("Pegada", "nunique"), Alertas_Totais=("ID", "count"), Maior_Espera=("Dias", "max")).sort_values(by="Clientes_Unicos", ascending=False).reset_index()
                    for indice, mestre_line in df_agrupado_mestre.iterrows():
                        item_nome = mestre_line['O que Falta']; clientes = int(mestre_line['Clientes_Unicos']); alertas = int(mestre_line['Alertas_Totais'])
                        classe_tag = "tag-calor-alta" if clientes >= 5 else ("tag-calor-media" if clientes >= 2 else "tag-calor-baixa")
                        label_tag = f"🔥 CRÍTICO • {clientes} CPFs" if clientes >= 5 else (f"⚠️ OPORTUNIDADE • {clientes} CPFs" if clientes >= 2 else f"🔹 INICIAL • {clientes} CPF")
                        st.markdown(f'<div class="bloco-lista-premium"><span class="{classe_tag}">{label_tag}</span><b style="color: #FFFFFF; font-size: 16px;">🏢 Falta: {item_nome}</b><div style="margin-top: 0.5rem; color: #aaaaaa; font-size: 13px;">⏱️ Demanda de {alertas} relatos • Maior espera: {mestre_line["Maior_Espera"]} dias</div></div>', unsafe_allow_html=True)
                        detalhes_item = df_filtrado[df_filtrado['O que Falta'] == item_nome]
                        st.write("📍 **Localização e Detalhes das Ocorrências Coletadas:**")
                        for _, sub_item in detalhes_item.iterrows():
                            st.markdown(f"  * **{sub_item['Cidade']}** - *Ponto:* {sub_item['Local/Referência']}")
                            if sub_item['Observação']: st.markdown(f"    * 💬 *Relato:* \"{sub_item['Observação']}\"")
                        st.markdown("<hr style='border-top: 1px dashed #333; margin: 1rem 0;'/>", unsafe_allow_html=True)
                        
                # --- INTERFACE 2: INTERFACE OPERACIONAL AGRUPADA (LOJISTAS) ---
                elif st.session_state.perfil_cliente != "admin":
                    st.markdown("#### 📈 Detalhamento das Demandas Ativas")
                    total_sua_loja = len(df_filtrado[df_filtrado['Local/Referência'] == loja_alvo_prioridade])
                    total_concorrencia = len(df_filtrado) - total_sua_loja
                    st.markdown(f"<div style='text-align: right; font-size: 12px; color: #888888; margin-top:-35px; margin-bottom:15px;'>Sua Loja: {total_sua_loja} • Concorrência: {total_concorrencia} • Total Geral: {len(df_filtrado)}</div>", unsafe_allow_html=True)
                    st.download_button(label="Baixar Relatório (PDF)", data=b"PDF", file_name="relatorio.pdf", mime="application/pdf", key="btn_pdf_operacional")
                    st.write("---")
                    df_agrupado_mestre = df_filtrado.groupby(["O que Falta", "Categoria"]).agg(Volume_Total=("ID", "count"), Menor_Idade=("Dias", "min"), Foco_Dono=("É_Minha_Loja", "max")).sort_values(by=["Foco_Dono", "Volume_Total"], ascending=[False, False]).reset_index()
                    for indice, linha in df_agrupado_mestre.iterrows():
                        item_nome = linha['O que Falta']; volume = float(linha['Volume_Total']); sou_alvo = int(linha['Foco_Dono'])
                        classe_tag, label_tag = ("tag-calor-media", f"🎯 REVERSO • {int(volume)} Pedidos") if "Marketplace" in filtro_frente else (("tag-calor-alta", f"🎯 SEU MERCADO • {int(volume)} Pedidos") if sou_alvo == 1 else ("tag-calor-baixa", f"🌍 CONCORRÊNCIA • {int(volume)} Pedidos"))
                        st.markdown(f'<div class="bloco-lista-premium"><span class="{classe_tag}">{label_tag}</span><b style="color: #FFFFFF; font-size: 16px;">📦 {item_nome}</b><div style="margin-top: 0.5rem; color: #aaaaaa; font-size: 13px;">⏱️ Alerta ativo há {linha["Menor_Idade"]} dias</div></div>', unsafe_allow_html=True)
                        detalhes_item = df_filtrado[df_filtrado['O que Falta'] == item_nome]
                        for _, sub_linha in detalhes_item.iterrows():
                            sub_id = sub_linha['ID']; sub_local = sub_linha['Local/Referência']; contato_morador = sub_linha['Contato']
                            is_dono_vazio = (sub_local == loja_alvo_prioridade)
                            st.markdown(f"{'🔥 **SEU ESTABELECIMENTO:** ' if is_dono_vazio else '📍 **Captado no concorrente:** '}{sub_local} ({sub_linha['Cidade']})")
                            if sub_linha['Observação']: st.info(f"💬 *Relato:* \"{sub_linha['Observação']}\"")
                            if contato_morador and ("Marketplace" in filtro_frente or not is_dono_vazio): st.success(f"📱 **Cliente Faminto!** WhatsApp: `{contato_morador}`")
                            if "Marketplace" not in filtro_frente and is_dono_vazio:
                                id_confirmacao = f"confirma_baixa_{sub_id}"
                                if id_confirmacao not in st.session_state: st.session_state[id_confirmacao] = False
                                if not st.session_state[id_confirmacao]:
                                    if st.button(f"Dar baixa no {sub_local}", key=f"btn_pre_{sub_id}"): st.session_state[id_confirmacao] = True; st.rerun()
                                else:
                                    st.warning("Confirmar reposição?"); col_b1, col_b2 = st.columns(2)
                                    with col_b1:
                                        if st.button("🚨 Confirmar", key=f"btn_real_{sub_id}"): supabase.table("relatos_escassez").update({"status": "Atendido"}).eq("id", sub_id).execute(); st.success("🎉 Concluído!"); import time; time.sleep(1); st.session_state[id_confirmacao] = False; st.session_state.busca_ativa = False; st.rerun()
                                    with col_b2:
                                        if st.button("❌ Cancelar", key=f"btn_cancelar_{sub_id}"): st.session_state[id_confirmacao] = False; st.rerun()
                        st.markdown("<hr style='border-top: 1px dashed #333; margin: 1rem 0;'/>", unsafe_allow_html=True)
            else:
                if st.session_state.perfil_cliente != "admin": st.info("ℹ️ Nenhum registro ativo encontrado para este filtro.")
        else:
            if st.session_state.perfil_cliente != "admin": st.info("ℹ️ O banco de dados está limpo!")
