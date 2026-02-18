# 🤖 UniBot — Assistente Virtual Unicesumar via WhatsApp

Bot inteligente de atendimento ao aluno da **Unicesumar**, integrado ao WhatsApp via [Evolution API](https://doc.evolution-api.com/) com inteligência artificial via [Flowise](https://flowiseai.com/).

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura](#-arquitetura)
- [Tech Stack](#-tech-stack)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Pré-Requisitos](#-pré-requisitos)
- [Configuração](#-configuração)
- [Deploy em Produção](#-deploy-em-produção)
- [Endpoints da API](#-endpoints-da-api)
- [Fluxo de Mensagens](#-fluxo-de-mensagens)
- [Serviços](#-serviços)
- [Git Workflow](#-git-workflow)

---

## 🎯 Visão Geral

O UniBot é um chatbot para WhatsApp que atende alunos e interessados nos cursos da Unicesumar. Quando um aluno envia uma mensagem, o bot:

1. **Ouve** — Recebe a mensagem via webhook da Evolution API
2. **Pensa** — Envia para o Flowise AI processar com contexto e memória
3. **Fala** — Responde no WhatsApp com a resposta da IA

O bot mantém o **contexto da conversa por usuário** (via `sessionId`), permitindo conversas naturais e contínuas.

---

## 🏗 Arquitetura

```
┌─────────────┐     Webhook      ┌─────────────────┐     API Call     ┌─────────────┐
│  WhatsApp   │ ───────────────► │    UniBot API    │ ──────────────► │   Flowise   │
│  (Usuário)  │                  │  (FastAPI/Python)│ ◄────────────── │  (IA/LLM)   │
│             │ ◄─────────────── │                  │   AI Response   │             │
└─────────────┘   Send Message   └─────────────────┘                  └─────────────┘
                                        │
                                        │ Send Message
                                        ▼
                                 ┌─────────────────┐
                                 │  Evolution API   │
                                 │   (WhatsApp)     │
                                 └─────────────────┘
```

Todos os serviços rodam em **Docker** na mesma rede interna (`rede_interna`), comunicando-se via nomes de containers.

---

## 🛠 Tech Stack

| Tecnologia | Função |
|---|---|
| **Python 3.11** | Linguagem principal |
| **FastAPI** | Framework web (API REST + Webhooks) |
| **Uvicorn** | Servidor ASGI |
| **httpx** | Cliente HTTP assíncrono |
| **Pydantic** | Validação e gerenciamento de configurações |
| **Docker** | Containerização e deploy |
| **Evolution API** | Gateway WhatsApp (envio/recebimento) |
| **Flowise** | Orquestrador de IA (LangChain visual) |
| **Groq (LLaMA 3.3)** | Modelo LLM para geração de respostas |
| **PostgreSQL** | Banco de dados da Evolution API |
| **Redis** | Cache da Evolution API |

---

## 📁 Estrutura do Projeto

```
uni-bot/
├── main.py                          # Ponto de entrada — inicializa FastAPI
├── Dockerfile                       # Imagem Docker do bot
├── docker-compose.prod.yaml         # Orquestração (Bot + Evolution + Flowise + DB)
├── requirements.txt                 # Dependências Python
├── .env                             # Variáveis de ambiente (não versionado)
├── .gitignore
│
├── app/
│   ├── __init__.py
│   │
│   ├── core/
│   │   └── config.py                # Configurações centralizadas (Pydantic Settings)
│   │
│   ├── controllers/
│   │   ├── webhook_controller.py    # Recebe webhooks da Evolution API
│   │   ├── lead_controller.py       # CRUD de leads (Kommo CRM)
│   │   └── contact_controller.py    # CRUD de contatos (Kommo CRM)
│   │
│   ├── services/
│   │   ├── flowise_service.py       # Comunicação com Flowise AI
│   │   ├── evolution_service.py     # Envio de mensagens via WhatsApp
│   │   └── kommo_service.py         # Integração com Kommo CRM
│   │
│   ├── models/                      # Modelos de dados (futuro)
│   └── schemas/                     # Schemas de validação (futuro)
│
└── planning/                        # Documentação de planejamento
    └── 01_integracao_monday.md
```

### Padrão MVC

O projeto segue o padrão **MVC (Model-View-Controller)**:
- **Controllers** — Recebem requisições HTTP e delegam para os services
- **Services** — Contêm a lógica de negócio e integrações externas
- **Core** — Configurações e utilitários compartilhados

---

## ✅ Pré-Requisitos

- **Docker** e **Docker Compose** instalados na VPS
- Conta na **Evolution API** com instância WhatsApp ativa
- **Flowise** configurado com um chatflow funcional
- (Opcional) Conta no **Kommo CRM** para gestão de leads

---

## ⚙️ Configuração

### 1. Clonar o repositório

```bash
git clone https://github.com/afkpuma/Uni-Bot-teste.git
cd Uni-Bot-teste
```

### 2. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Kommo CRM
KOMMO_URL=https://sua-conta.kommo.com
KOMMO_TOKEN=seu_token_kommo

# Monday.com
MONDAY_TOKEN=seu_token_monday

# Flowise AI
FLOWISE_API_URL=http://flowise:3000/api/v1/prediction/SEU_CHATFLOW_ID

# Evolution API
EVOLUTION_API_URL=http://evolution_api:8080
EVOLUTION_API_TOKEN=seu_token_evolution
INSTANCE_NAME=UniBot

# PostgreSQL (usado pela Evolution)
POSTGRES_PASSWORD=sua_senha_segura
```

> ⚠️ **Importante:** O `.env` está no `.gitignore` e **nunca deve ser commitado**.

### 3. Configurar o Flowise

No painel do Flowise (`http://seu-ip:3000`):

1. Crie um chatflow com: **Chat Prompt Template** + **Buffer Memory** + **LLM** + **Conversation Chain**
2. No prompt, use `{chat_history}` para histórico e `{input}` para a pergunta do usuário
3. Copie o ID do chatflow e coloque na variável `FLOWISE_API_URL`

---

## 🚀 Deploy em Produção

### Subir todos os serviços

```bash
docker compose -f docker-compose.prod.yaml up -d --build
```

Isso inicia 5 containers:

| Container | Porta | Descrição |
|---|---|---|
| `uni_bot_app` | 8000 | API FastAPI (seu bot) |
| `evolution_api` | 8081 | Gateway WhatsApp |
| `flowise` | 3000 | Painel IA + API de predição |
| `evolution_postgres` | — | Banco de dados (interno) |
| `evolution_redis` | — | Cache (interno) |

### Comandos úteis

```bash
# Ver logs do bot em tempo real
docker logs -f uni_bot_app

# Ver logs do Flowise
docker logs -f flowise

# Reiniciar apenas o bot após mudanças
docker compose -f docker-compose.prod.yaml up -d --build uni_bot

# Parar tudo
docker compose -f docker-compose.prod.yaml down
```

### Atualizar com novas mudanças

```bash
git pull origin develop
docker compose -f docker-compose.prod.yaml up -d --build
```

---

## 📡 Endpoints da API

A documentação interativa está disponível em `http://seu-ip:8000/docs` (Swagger UI).

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/api/webhook` | Recebe eventos da Evolution API |
| `GET` | `/api/leads` | Lista leads do Kommo |
| `POST` | `/api/leads` | Cria lead no Kommo |
| `GET` | `/api/contacts` | Lista contatos do Kommo |

---

## 🔄 Fluxo de Mensagens

```
1. Usuário envia "Quanto custa ADS?" no WhatsApp
                    │
                    ▼
2. Evolution API envia webhook POST /api/webhook
   payload: { type: "messages.upsert", data: { key: { remoteJid, ... }, message: { ... } } }
                    │
                    ▼
3. webhook_controller.py extrai:
   - remote_jid (número do WhatsApp)
   - user_message (texto da mensagem)
   - Processa em background (não trava o webhook)
                    │
                    ▼
4. FlowiseService.generate_response(message, remote_jid)
   Envia para Flowise: { "question": "Quanto custa ADS?", "sessionId": "5534..." }
   Flowise usa sessionId para manter contexto da conversa
                    │
                    ▼
5. Flowise processa com LLM (Groq/LLaMA 3.3) e retorna resposta
                    │
                    ▼
6. EvolutionService.send_message(remote_jid, ai_response)
   Envia resposta no WhatsApp com delay de 1.2s (simula digitação)
```

---

## 🔧 Serviços

### FlowiseService (`app/services/flowise_service.py`)
Comunica com a API do Flowise para gerar respostas da IA.
- Envia `question` + `sessionId` (para memória de conversa)
- Timeout de 30s (IA pode demorar)
- Retorna mensagem de fallback em caso de erro

### EvolutionService (`app/services/evolution_service.py`)
Envia mensagens de texto via Evolution API (WhatsApp).
- Usa `httpx` (assíncrono) para não bloquear
- Delay de 1.2s para simular digitação humana

### KommoService (`app/services/kommo_service.py`)
Integração com o CRM Kommo para gestão de leads e contatos.
- `get_leads()` — Busca leads com filtro opcional
- `get_contacts()` — Busca contatos com paginação
- `get_contact_by_id()` — Busca contato específico
- `create_lead()` — Cria novo lead

---

## 🌿 Git Workflow

O projeto utiliza duas branches principais:

| Branch | Função |
|---|---|
| `main` | Código estável, pronto para produção |
| `develop` | Desenvolvimento ativo |

### Fluxo de trabalho

```bash
# 1. Desenvolva na branch develop
git checkout develop

# 2. Faça commits atômicos (uma mudança lógica por commit)
git add <arquivos>
git commit -m "feat: descrição clara da mudança"

# 3. Push para develop
git push origin develop

# 4. Quando estiver estável, merge para main
git checkout main
git merge develop
git push origin main
git checkout develop
```

### Padrão de commits

- `feat:` — Nova funcionalidade
- `fix:` — Correção de bug
- `refactor:` — Refatoração de código
- `docs:` — Documentação
- `chore:` — Tarefas de manutenção

---

## 📄 Licença

Projeto privado — Unicesumar © 2026
