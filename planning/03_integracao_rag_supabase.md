# Planejamento 03: Integração Supabase e Arquitetura RAG

## Objetivo
Migrar a base de conhecimento estática (JSONs de Cursos, FAQs, Calendário) para o Supabase usando a extensão `pgvector`. O objetivo é permitir que o Flowise faça buscas semânticas em tempo real, fornecendo contexto preciso para a IA formular as respostas.

## Arquitetura em Duas Fases
1. **Fase Offline (Ingestão):** Um script Python lê os arquivos JSON, formata os objetos em frases semanticamente ricas, gera os embeddings (via Google Gemini `text-embedding-004`) e salva no Supabase.
2. **Fase Runtime (WhatsApp):** O FastAPI recebe a mensagem, envia para o Flowise. O Flowise converte a pergunta em embedding, busca os trechos mais relevantes no Supabase e usa o Llama 3.3 (Groq) para responder ao usuário.

## Tarefas (Checklist)
- [ ] Criar a tabela `documentos_unibot` e a função de busca no SQL Editor do Supabase.
- [ ] Criar pasta `scripts/` para isolar lógicas de ingestão de dados do FastAPI.
- [ ] Implementar `scripts/ingestao_dados.py` para processar os JSONs.
- [ ] Configurar variáveis de ambiente (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `GEMINI_API_KEY`).
- [ ] Atualizar `requirements.txt`.
- [ ] Configurar novo Chatflow no Flowise (Conversational Retrieval QA Chain + nó Supabase).
