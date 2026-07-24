import time
import random
import datetime
import core.database as db

print("🚀 Conectando com a API do Supabase...")
try:
    # Inicializa a conexão usando a estrutura nativa do seu projeto
    supabase = db.inicializar_supabase()
except Exception as e:
    print(f"❌ Erro banco: {e}")
    exit()


def rodar_limpeza_e_carga():
    # 🧹 PASSO 1: LIMPAR REGISTROS ANTIGOS MISTRURADOS
    print("🧹 Limpando registros antigos de teste (QA) do Supabase...")
    try:
        supabase.table("relatos_escassez").delete().like(
            "observacao_detalhe", "QA:%").execute()
        print("✨ Histórico surreal limpo com sucesso!")
    except Exception as e:
        print(f"⚠️ Aviso na limpeza: {e}")

    # 📍 PASSO 2: MAPEAMENTO COERENTE DE PONTOS COMERCIAIS E PÚBLICOS
    print("Iniciando povoamento realista...")
    lojas = [
        {"nome": "Mercadinho Do Bairro", "regiao": "Carapicuíba/SP - Centro"},
        {"nome": "Supermercado Ideal", "regiao": "Carapicuíba/SP - Vila Nova"},
        {"nome": "Drogaria Central, 45", "regiao": "Carapicuíba/SP - Centro"},
        {"nome": "Petshop Cão Alerta", "regiao": "Carapicuíba/SP - Centro"},
        {"nome": "Salão Estética Real", "regiao": "Carapicuíba/SP - Cohab"},
        {"nome": "Galeria Comercial Centro", "regiao": "Carapicuíba/SP - Centro"},
        {"nome": "Prefeitura Comunitária", "regiao": "Carapicuíba/SP - Centro"}
    ]

    locais_ids = {}
    for lj in lojas:
        try:
            res = supabase.table("locais_destino").insert({
                "nome_exibicao": lj["nome"], "regiao_cidade": lj["regiao"], "regiao_estado": "SP"
            }).execute()
            if res.data:
                locais_ids[lj["nome"]] = res.data[0]["id"] if isinstance(
                    res.data, list) else res.data["id"]
        except:
            pass

    if not locais_ids:
        try:
            res = supabase.table("locais_destino").select(
                "id, nome_exibicao").execute()
            for item in res.data:
                locais_ids[item["nome_exibicao"]] = item["id"]
        except:
            pass

    id_padrao = list(locais_ids.values()) if locais_ids else 1

    demandas_teste = {
        "Supermercado": [
            "Leite Condensado Zero Lactose", "Arroz Integral Tipo 1",
            "Feijão Preto Premium", "Café Gourmet Moído",
            "Açúcar Mascavo Orgânico", "Óleo de Coco Extra Virgem",
            "Pão de Forma Artesanal", "Azeite de Oliva Extrafino",
            "Farinha de Aveia Fina", "Macarrão Sem Glúten",
            "Manteiga Ghee Clari", "Sal Rosa do Himalaia",
            "Suco de Uva Integral", "Biscoito de Polvilho Integral",
            "Cereal Matinal Sem Açúcar"
        ],
        "Saúde": [
            "Inalador Ultrassônico Portátil", "Termômetro Digital de Testa",
            "Aparelho de Pressão Pulso", "Suplemento de Vitamina D3",
            "Glicosímetro de Alta Precisão", "Protetor Solar Facial FPS 60",
            "Curativo Hidrocoloide", "Máscara Descartável PFF2",
            "Soro Fisiológico 500ml", "Suplemento de Ômega 3 Premium",
            "Gel Antisséptico 70%", "Sabonete Líquido Neutro",
            "Colírio Lubrificante", "Algodão em Disco Hidrófilo",
            "Fita Micropore Cirúrgica"
        ],
        "Petshop": [
            "Ração Premium Gatos Castrados", "Ração de Cão Filhote Porte Pequeno",
            "Areia Higiênica de Sílica", "Petisco Dental Pro Cães",
            "Brinquedo Mordedor Interativo", "Shampoo Neutro para Filhotes",
            "Arranhador de Gato com Torre", "Coleira Peitoral Antipuxão",
            "Tapete Higiênico Absorvente", "Escova de Pelagem Dupla Face",
            "Snack Saudável de Frutas Pet", "Eliminador de Odores Enzimático",
            "Guia Retrátil 5 Metros", "Cama Sanitária de Gatos",
            "Suplemento Articular Canino"
        ],
        "Beleza": [
            "Esmalte Hipoalergênico Nude", "Creme de Hidratação Profunda",
            "Óleo Capilar de Argan", "Protetor Térmico Spray",
            "Base Fluida Efeito Matte", "Água Micelar Demaquilante",
            "Sérum Facial Ácido Hialurônico", "Cera Depilatória Roll-On",
            "Creme Esfoliante Corporal", "Shampoo Anticaspa Purificante",
            "Tônico Capilar Fortalecedor", "Máscara de Cílios À Prova D'Água",
            "Pó Translucido Antibrilho", "Fixador de Maquiagem Spray",
            "Creme de Mãos Hidratante"
        ],
        "Serviços": [
            "Sapataria e Conserto de Botas", "Lavanderia de Tapetes e Edredons",
            "Chaveiro Residencial 24h", "Costureira para Ajustes de Ternos",
            "Afiação de Facas e Alicates", "Encadernação e Cópias Coloridas",
            "Manutenção de Fogões a Gás", "Conserto de Cadeiras de Escritório",
            "Limpeza de Estofados a Seco", "Reparo de Joias e Relógios",
            "Instalação de Varal de Teto", "Marido de Aluguel Reparos",
            "Eletricista Predial Padrão Enel", "Pintor para Pequenos Reparos",
            "Desentupidora Residencial"
        ],
        "Infraestrutura": [
            "Falha na Iluminação Pública", "Buraco na Camada Asfáltica",
            "Calçada Quebrada com Risco", "Poda de Árvore Tocando Fiação",
            "Falta de Sinalização de Pare", "Boca de Lobo Obstruída",
            "Faixa de Pedestres Apagada", "Vazamento de Água Limpa na Rua",
            "Acúmulo de Lixo no Terreno", "Falta de Abrigo no Ponto de Ônibus",
            "Sinal de Trânsito Intermitente", "Placa de Rua Arrancada",
            "Poste de Energia Inclinado", "Falta de Lixeira Comunitária",
            "Mato Alto Ocupando Acostamento"
        ]
    }

    total_inserido = 0
    for nicho, itens in demandas_teste.items():
        for idx, item in enumerate(itens):
            status_atual = "Atendido" if idx % 2 == 0 else "Pendente"

            if nicho == "Supermercado":
                loc_id = locais_ids.get("Mercadinho Do Bairro", id_padrao)
                tipo_c = "Produto / Marca"
            elif nicho == "Saúde":
                loc_id = locais_ids.get("Drogaria Central, 45", id_padrao)
                tipo_c = "Produto / Marca"
            elif nicho == "Petshop":
                loc_id = locais_ids.get("Petshop Cão Alerta", id_padrao)
                tipo_c = "Produto / Marca"
            elif nicho == "Beleza":
                loc_id = locais_ids.get("Salão Estética Real", id_padrao)
                tipo_c = "Produto / Marca"
            elif nicho == "Serviços":
                # 🏪 Serviços agora vão para a Galeria Comercial
                loc_id = locais_ids.get("Galeria Comercial Centro", id_padrao)
                tipo_c = "Serviço Local / Novo Estabelecimento"
            else:
                # 🏛️ Infraestrutura agora vai para a Prefeitura Comunitária
                loc_id = locais_ids.get("Prefeitura Comunitária", id_padrao)
                tipo_c = "Serviço Público / Infraestrutura"

            tem_telefone = random.choice([True, False])
            contato = f"1198888{random.randint(1000, 9999)}" if tem_telefone else None

            try:
                supabase.table("relatos_escassez").insert({
                    "local_id": loc_id, "item_solicitado": item, "tipo_carencia": tipo_c,
                    "status": status_atual, "sub_segmento": nicho, "observacao_detalhe": f"QA: {item}.",
                    "contato_aviso": contato, "pegada_digital": f"qa_{random.randint(100, 999)}"
                }).execute()
                total_inserido += 1
            except:
                pass

    print(
        f"🎉 Processo concluído! {total_inserido} registros 100% coerentes injetados.")


if __name__ == "__main__":
    rodar_limpeza_e_carga()
