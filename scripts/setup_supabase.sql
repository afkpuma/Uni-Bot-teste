-- Habilitar a extensão pgvector (caso não esteja habilitada)
create extension if not exists vector;

-- Criar a tabela de documentos (caso ainda não exista ou queira recriar)
create table if not exists documentos_unibot (
  id bigserial primary key,
  content text,
  metadata jsonb,
  embedding vector(768)
);

-- Função para busca por similaridade (usada pelo script test_rag.py e pelo Flowise)
create or replace function match_documents (
  query_embedding vector(768),
  match_threshold float,
  match_count int
)
returns table (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    documentos_unibot.id,
    documentos_unibot.content,
    documentos_unibot.metadata,
    1 - (documentos_unibot.embedding <=> query_embedding) as similarity
  from documentos_unibot
  where 1 - (documentos_unibot.embedding <=> query_embedding) > match_threshold
  order by similarity desc
  limit match_count;
end;
$$;
