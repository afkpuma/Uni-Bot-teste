import json
import os
import time
from supabase import create_client, Client
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GEMINI_API_KEY,
    task_type="RETRIEVAL_DOCUMENT",
    dimensions=768
)

# --- Rate Limiting ---
RATE_LIMIT = 90  # parar a cada 90 requests (cota free = 100/min)
PAUSE_SECONDS = 65  # esperar 65s para garantir reset da cota
contadores = {"sucesso": 0, "erro": 0, "requests": 0}

def rate_limit_check():
    """Pausa automaticamente ao atingir o limite de requests por minuto."""
    contadores["requests"] += 1
    if contadores["requests"] >= RATE_LIMIT:
        print(f"\n⏳ Limite de {RATE_LIMIT} requests atingido. Pausando {PAUSE_SECONDS}s para reset da cota...")
        time.sleep(PAUSE_SECONDS)
        contadores["requests"] = 0
        print("▶️  Retomando processamento...\n")

def salvar_no_supabase(content, metadata, max_retries=3):
    """Salva no Supabase com retry automático em caso de rate limit."""
    for tentativa in range(max_retries):
        try:
            rate_limit_check()
            vetor = embeddings.embed_query(content)
            vetor = vetor[:768]  # Truncar para 768 dimensões
            registro = {"content": content, "metadata": metadata, "embedding": vetor}
            supabase.table("documentos_unibot").insert(registro).execute()
            label = metadata.get('curso') or metadata.get('item') or metadata.get('fonte')
            print(f"✅ [{contadores['sucesso']+1}] Salvo: {label}")
            contadores["sucesso"] += 1
            return True
        except Exception as e:
            erro_str = str(e)
            if "429" in erro_str or "quota" in erro_str.lower():
                wait_time = 30 * (tentativa + 1)
                print(f"⏳ Rate limit! Tentativa {tentativa+1}/{max_retries}. Aguardando {wait_time}s...")
                time.sleep(wait_time)
                contadores["requests"] = 0  # resetar contador
            else:
                print(f"❌ Erro ao salvar: {e}")
                contadores["erro"] += 1
                return False
    print(f"❌ Falha após {max_retries} tentativas para: {metadata}")
    contadores["erro"] += 1
    return False

# ===== PROCESSADORES =====

def processar_cursos(caminho_arquivo, tipo_curso):
    print(f"\n📂 Processando: {caminho_arquivo}...")
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    for curso in dados.get("cursos", []):
        nome = curso.get("nome")
        duracao = curso.get("duracao")
        modalidade = curso.get("modalidade", "Online")
        valor = curso.get("valor_face")
        
        content = (f"Curso de {tipo_curso.replace('_', ' ').title()} em {nome}. "
                   f"A modalidade é {modalidade} e a duração é de {duracao}. "
                   f"O valor de face (sem aplicação de descontos) é R$ {valor}.")
        
        metadata = {"fonte": tipo_curso, "curso": nome, "tipo_dado": "curso"}
        salvar_no_supabase(content, metadata)

def processar_cursos_pos(caminho_arquivo):
    print(f"\n📂 Processando: {caminho_arquivo}...")
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    for curso in dados.get("cursos", []):
        nome = curso.get("nome")
        area = curso.get("area", "")
        subarea = curso.get("subarea", "")
        duracao = curso.get("duracao")
        valor_parcela = curso.get("valor_parcela")
        valor_total = curso.get("valor_total")
        parcelas = curso.get("parcelas", 18)
        
        content = (f"Pós-Graduação em {nome}, na área de {area} ({subarea}). "
                   f"Duração de {duracao}, parcelado em {parcelas}x de R$ {valor_parcela} "
                   f"(total R$ {valor_total}). Início imediato após pagamento. "
                   f"Especialização lato sensu reconhecida pelo MEC, 100% online.")
        
        metadata = {"fonte": "pos_graduacao", "curso": nome, "area": area, "tipo_dado": "curso"}
        salvar_no_supabase(content, metadata)

def processar_cursos_tecnicos(caminho_arquivo):
    print(f"\n📂 Processando: {caminho_arquivo}...")
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    for curso in dados.get("cursos", []):
        nome = curso.get("nome")
        duracao = curso.get("duracao")
        valor = curso.get("valor_face")
        
        content = (f"Curso Técnico em {nome}. "
                   f"Duração de {duracao}, mensalidade de R$ {valor} (valor de face). "
                   f"Provas presenciais no polo. Segue calendário de módulos.")
        
        metadata = {"fonte": "tecnico", "curso": nome, "tipo_dado": "curso"}
        salvar_no_supabase(content, metadata)

def processar_cursos_profissionalizantes(caminho_arquivo):
    print(f"\n📂 Processando: {caminho_arquivo}...")
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    for curso in dados.get("cursos", []):
        nome = curso.get("nome")
        duracao = curso.get("duracao")
        valor = curso.get("valor_face")
        
        content = (f"Curso Profissionalizante em {nome}. "
                   f"Duração de {duracao}, mensalidade de R$ {valor} (valor de face). "
                   f"Avaliações 100% online. Segue calendário de módulos.")
        
        metadata = {"fonte": "profissionalizante", "curso": nome, "tipo_dado": "curso"}
        salvar_no_supabase(content, metadata)

def processar_faqs(caminho_arquivo):
    print(f"\n📂 Processando: {caminho_arquivo}...")
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
        
    for item in dados.get("perguntas", []):
        pergunta = item.get("pergunta")
        resposta_bruta = {k: v for k, v in item.items() if k not in ["id", "pergunta"]}
        resposta_str = json.dumps(resposta_bruta, ensure_ascii=False)
        
        content = f"Dúvida Frequente: {pergunta}. Informações para resposta: {resposta_str}"
        metadata = {"fonte": "faq", "pergunta_id": item.get("id"), "tipo_dado": "duvida"}
        salvar_no_supabase(content, metadata)

def processar_politica_comercial(caminho_arquivo):
    print(f"\n📂 Processando: {caminho_arquivo}...")
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # 1ª Oferta
    p1 = dados.get("primeira_oferta", {})
    content_oferta1 = (
        f"Política Comercial - 1ª Oferta: Desconto promocional de {p1.get('desconto_promocional')} "
        f"mais {p1.get('desconto_pontualidade')} de pontualidade (pagamento até dia 10). "
        f"Fórmula: {p1.get('formula')}. Multiplicador: {p1.get('multiplicador')}. "
        f"Apresentar como promoção limitada/sazonal. Validade: {p1.get('validade')}."
    )
    salvar_no_supabase(content_oferta1, {"fonte": "politica_comercial", "tipo_dado": "politica", "item": "primeira_oferta"})
    
    # 2ª Oferta
    p2 = dados.get("segunda_oferta", {})
    content_oferta2 = (
        f"Política Comercial - 2ª Oferta (somente após resistência ao preço): "
        f"Desconto especial de {p2.get('desconto_especial')} mais {p2.get('desconto_pontualidade')} de pontualidade. "
        f"Fórmula: {p2.get('formula')}. Multiplicador: {p2.get('multiplicador')}. "
        f"Quando usar: {', '.join(p2.get('quando_usar', []))}. "
        f"Apresentar como condição exclusiva do supervisor."
    )
    salvar_no_supabase(content_oferta2, {"fonte": "politica_comercial", "tipo_dado": "politica", "item": "segunda_oferta"})
    
    # Matrícula
    mat = dados.get("matricula", {})
    content_matricula = (
        f"Informações de Matrícula: {mat.get('taxa')}. "
        f"Primeira mensalidade de R$ {mat.get('primeira_mensalidade')}. "
        f"Chave PIX (CNPJ): {mat.get('pix', {}).get('chave')}. "
        f"Formas de pagamento: {', '.join(dados.get('formas_pagamento', []))}. "
        f"Vencimento dia {dados.get('vencimento', {}).get('dia')}, "
        f"feriado: {dados.get('vencimento', {}).get('feriado')}."
    )
    salvar_no_supabase(content_matricula, {"fonte": "politica_comercial", "tipo_dado": "politica", "item": "matricula"})
    
    # Descontos especiais
    desc = dados.get("descontos_especiais", {})
    content_desc = (
        f"Descontos Especiais: Ex-alunos recebem {desc.get('ex_alunos')} adicional. "
        f"Programa Eu Indico: EAD {desc.get('eu_indico_ead')}, Semipresencial {desc.get('eu_indico_semipresencial')}. "
        f"Financiamentos: {desc.get('financiamentos')}."
    )
    salvar_no_supabase(content_desc, {"fonte": "politica_comercial", "tipo_dado": "politica", "item": "descontos_especiais"})
    
    # Regras
    regras = dados.get("regras", [])
    content_regras = f"Regras da Política Comercial: {'. '.join(regras)}."
    salvar_no_supabase(content_regras, {"fonte": "politica_comercial", "tipo_dado": "politica", "item": "regras"})

def processar_calendario(caminho_arquivo):
    print(f"\n📂 Processando: {caminho_arquivo}...")
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Módulos 2026
    modulos = dados.get("modulos_2026", {})
    partes = []
    for chave, mod in modulos.items():
        if "nome" in mod:
            partes.append(f"{mod['nome']}: {mod.get('periodo', mod.get('descricao', ''))}")
    
    content_modulos = (
        f"Calendário Acadêmico 2026. "
        f"Estrutura modular: {dados.get('estrutura_modular', {}).get('descricao', '')}. "
        f"{'. '.join(partes)}."
    )
    salvar_no_supabase(content_modulos, {"fonte": "calendario", "tipo_dado": "calendario", "item": "modulos_2026"})
    
    # Períodos de matrícula
    periodos = dados.get("periodos_matricula", {})
    partes_mat = []
    for chave, per in periodos.items():
        status = f" ({per.get('status')})" if per.get("status") else ""
        partes_mat.append(f"{chave.replace('_', ' ').title()}: {per.get('periodo')}{status}")
    
    content_periodos = f"Períodos de matrícula 2026: {'. '.join(partes_mat)}."
    salvar_no_supabase(content_periodos, {"fonte": "calendario", "tipo_dado": "calendario", "item": "periodos_matricula"})
    
    # Pós-graduação início imediato
    pos = dados.get("pos_graduacao_inicio_imediato", {})
    content_pos = (
        f"Pós-graduação: {pos.get('descricao')}. "
        f"Processo: {'. '.join(pos.get('processo', []))}. "
        f"Matrículas: {pos.get('matriculas')}."
    )
    salvar_no_supabase(content_pos, {"fonte": "calendario", "tipo_dado": "calendario", "item": "pos_graduacao"})

def processar_estrutura_pedagogica(caminho_arquivo):
    print(f"\n📂 Processando: {caminho_arquivo}...")
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # EAD
    ead = dados.get("ead", {})
    content_ead = (
        f"Estrutura pedagógica EAD: {ead.get('descricao')}. "
        f"Cada disciplina dura {ead.get('disciplina', {}).get('duracao')}, "
        f"{ead.get('por_modulo')} disciplinas por módulo. "
        f"Dedicação: {ead.get('dedicacao')}. "
        f"Material: {', '.join(ead.get('material', []))}. "
        f"Provas: {ead.get('provas', {}).get('tipo')} no {ead.get('provas', {}).get('local')}, "
        f"{ead.get('provas', {}).get('quando')}. {ead.get('provas', {}).get('agendamento')}."
    )
    salvar_no_supabase(content_ead, {"fonte": "estrutura_pedagogica", "tipo_dado": "estrutura", "item": "ead"})
    
    # Semipresencial
    semi = dados.get("semipresencial", {})
    content_semi = (
        f"Estrutura pedagógica Semipresencial: {semi.get('descricao')}. "
        f"Práticas presenciais a partir do {semi.get('praticas_presenciais', {}).get('inicio')}, "
        f"{semi.get('praticas_presenciais', {}).get('frequencia')}, "
        f"período {semi.get('praticas_presenciais', {}).get('periodo')}. "
        f"Cursos semipresenciais: {', '.join(semi.get('cursos', []))}."
    )
    salvar_no_supabase(content_semi, {"fonte": "estrutura_pedagogica", "tipo_dado": "estrutura", "item": "semipresencial"})
    
    # Aprovação
    aprov = dados.get("aprovacao", {})
    content_aprov = (
        f"Sistema de aprovação: nota mínima {aprov.get('nota_minima')} (escala {aprov.get('escala')}). "
        f"Segunda oportunidade: {aprov.get('segunda_oportunidade', {}).get('descricao')}. "
        f"Reprovação: {aprov.get('reprovacao', {}).get('descricao')}, sem custo adicional."
    )
    salvar_no_supabase(content_aprov, {"fonte": "estrutura_pedagogica", "tipo_dado": "estrutura", "item": "aprovacao"})
    
    # TCC e Estágio
    tcc = dados.get("tcc", {})
    estagio = dados.get("estagio", {})
    content_tcc = (
        f"TCC: {tcc.get('obrigatoriedade')}. {tcc.get('orientacao')}. {tcc.get('quando')}. "
        f"Estágio obrigatório: {estagio.get('obrigatorio', {}).get('descricao')}. "
        f"Estágio não obrigatório: {estagio.get('nao_obrigatorio', {}).get('descricao')}."
    )
    salvar_no_supabase(content_tcc, {"fonte": "estrutura_pedagogica", "tipo_dado": "estrutura", "item": "tcc_estagio"})
    
    # Documentação
    docs = dados.get("documentacao_matricula", {})
    content_docs = (
        f"Documentação para matrícula: {', '.join(docs.get('basicos', []))}. "
        f"Envio: {docs.get('envio', {}).get('metodo')}. {docs.get('envio', {}).get('suporte')}."
    )
    salvar_no_supabase(content_docs, {"fonte": "estrutura_pedagogica", "tipo_dado": "estrutura", "item": "documentacao"})

def processar_personalidade(caminho_arquivo):
    print(f"\n📂 Processando: {caminho_arquivo}...")
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    ia = dados.get("ia", {}).get("wizard_data", {})
    
    # Identidade
    ident = ia.get("identidade", {})
    pers = ia.get("personalidade", {})
    content_ident = (
        f"O assistente virtual se chama {ident.get('nome')}, "
        f"atua como {ident.get('funcao')} na {ident.get('instituicao')}, "
        f"unidade {ident.get('unidade')}. "
        f"Tom: {pers.get('tom_principal')}. "
        f"Características: {', '.join(pers.get('caracteristicas', []))}. "
        f"Abordagem: {pers.get('abordagem')}. "
        f"Missão: {pers.get('missao')}."
    )
    salvar_no_supabase(content_ident, {"fonte": "personalidade", "tipo_dado": "personalidade", "item": "identidade"})
    
    # Polo
    polo = ia.get("polo", {})
    end = polo.get("endereco", {})
    cont = polo.get("contatos", {})
    content_polo = (
        f"Polo Unicesumar Araguari: {end.get('logradouro')}, {end.get('bairro')}, "
        f"{end.get('cidade')}-{end.get('estado')} (Referência: {end.get('referencia')}). "
        f"Telefone: {cont.get('telefone_fixo')}. "
        f"WhatsApp Matrículas: {cont.get('whatsapp_matriculas')}. "
        f"WhatsApp Suporte Alunos: {cont.get('whatsapp_suporte_alunos')}. "
        f"WhatsApp Financeiro: {cont.get('whatsapp_financeiro')}. "
        f"Horário: {polo.get('horario_funcionamento', {}).get('dias_uteis')}. "
        f"Fim de semana: {polo.get('horario_funcionamento', {}).get('fim_de_semana')}."
    )
    salvar_no_supabase(content_polo, {"fonte": "personalidade", "tipo_dado": "personalidade", "item": "polo"})


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Iniciando ingestão COMPLETA de dados para o UniBot...")
    print(f"⚙️  Rate limit: {RATE_LIMIT} req/min | Pausa: {PAUSE_SECONDS}s")
    print("=" * 60)
    
    inicio = time.time()
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Cursos de Graduação (106 cursos)
    processar_cursos(os.path.join(SCRIPT_DIR, "edu_cursos_graduacao.json"), "graduacao")
    
    # 2. Cursos de Pós-Graduação (208 cursos)
    processar_cursos_pos(os.path.join(SCRIPT_DIR, "edu_cursos_pos_graduacao.json"))
    
    # 3. Cursos Técnicos (9 cursos)
    processar_cursos_tecnicos(os.path.join(SCRIPT_DIR, "edu_cursos_tecnicos.json"))
    
    # 4. Cursos Profissionalizantes (80 cursos)
    processar_cursos_profissionalizantes(os.path.join(SCRIPT_DIR, "edu_cursos_profissionalizantes.json"))
    
    # 5. FAQs (10 perguntas)
    processar_faqs(os.path.join(SCRIPT_DIR, "edu_faqs.json"))
    
    # 6. Política Comercial (5 documentos)
    processar_politica_comercial(os.path.join(SCRIPT_DIR, "edu_politica_comercial.json"))
    
    # 7. Calendário Acadêmico (3 documentos)
    processar_calendario(os.path.join(SCRIPT_DIR, "edu_calendario_academico.json"))
    
    # 8. Estrutura Pedagógica (5 documentos)
    processar_estrutura_pedagogica(os.path.join(SCRIPT_DIR, "edu_estrutura_pedagogica.json"))
    
    # 9. Personalidade da IA (2 documentos)
    processar_personalidade(os.path.join(SCRIPT_DIR, "edu_personalidade_config.json"))
    
    duracao_total = time.time() - inicio
    minutos = int(duracao_total // 60)
    segundos = int(duracao_total % 60)
    
    print("\n" + "=" * 60)
    print(f"✅ Sucesso: {contadores['sucesso']} registros salvos")
    print(f"❌ Erros: {contadores['erro']}")
    print(f"📊 Total processado: {contadores['sucesso'] + contadores['erro']}")
    print(f"⏱️  Tempo total: {minutos}min {segundos}s")
    print("🚀 Ingestão COMPLETA finalizada!")
    print("=" * 60)
