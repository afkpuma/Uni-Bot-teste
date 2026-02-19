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

def testar_retrieval(pergunta):
    print(f"\n❓ Pergunta: {pergunta}")
    
    # 1. Gerar embedding da pergunta
    vetor_pergunta = embeddings.embed_query(pergunta)
    vetor_pergunta = vetor_pergunta[:768] # Truncar para 768 dimensões
    
    # 2. Buscar no Supabase
    response = supabase.rpc(
        "match_documents",
        {
            "query_embedding": vetor_pergunta,
            "match_threshold": 0.5, # Habilita retorno de resultados com similaridade > 0.5
            "match_count": 3
        }
    ).execute()
    
    # 3. Mostrar resultados
    if response.data:
        print(f"✅ Encontrados {len(response.data)} documentos relevantes:\n")
        for i, doc in enumerate(response.data):
            print(f"--- Documento {i+1} (Similaridade: {doc['similarity']:.4f}) ---")
            print(f"Fonte: {doc['metadata'].get('fonte')}")
            print(f"Conteúdo: {doc['content'][:200]}...") # Mostrar apenas os primeiros 200 caracteres
            print("-" * 50)
    else:
        print("❌ Nenhum documento encontrado com similaridade > 0.5")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Testando Retrieval RAG (Supabase + Gemini)...")
    print("=" * 60)
    
    # Teste 1: Curso específico
    testar_retrieval("Quanto custa o curso de Agronomia?")
    
    # Teste 2: Política comercial (desconto)
    testar_retrieval("Tem desconto para ex-aluno?")
    
    # Teste 3: Info institucional
    testar_retrieval("Qual o endereço do polo?")
    
    print("\n" + "=" * 60)
    print("✅ Teste finalizado!")
