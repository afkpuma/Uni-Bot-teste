# 🧪 Testes Unitários — Camada de Services

## 1. Research (Pesquisa) 🕵️

### Contexto
O projeto **Uni-Bot** possui 4 serviços na camada `app/services/` que integram com APIs externas:

| Service | Tipo | HTTP Client | APIs Externas |
|---------|------|-------------|---------------|
| `EvolutionService` | `async` (`@staticmethod`) | `httpx.AsyncClient` | Evolution API (WhatsApp) |
| `FlowiseService` | `async` (`@staticmethod`) | `httpx.AsyncClient` | Flowise AI |
| `KommoService` | `sync` (instância) | `requests` | Kommo CRM |
| `MondayService` | `sync` (instância) | `requests` | Monday.com GraphQL |

### Problema
- **Zero testes** existem no projeto atualmente
- Todos os services fazem chamadas HTTP reais — impossível testar sem mocks
- Services async (`Evolution`, `Flowise`) precisam de runner `pytest-asyncio`
- Services sync (`Kommo`, `Monday`) usam `requests` — mockáveis com `unittest.mock.patch`

### Decisões Técnicas
- **Framework:** `pytest` + `pytest-asyncio` (padrão da comunidade Python)
- **Mocking:** `unittest.mock` (nativo do Python, sem deps extras)
  - `httpx.AsyncClient` → mockar via `AsyncMock`
  - `requests.get/post` → mockar via `patch`
- **Configuração:** Criar `conftest.py` com fixtures que sobrescrevem as `settings` para não depender do `.env`
- **Estrutura:** Espelhar `app/services/` em `tests/services/`

---

## 2. Plan (Planejamento) 📝

### Estrutura de arquivos a criar

```
tests/
  __init__.py
  conftest.py                      ← fixtures globais (mock settings)
  services/
    __init__.py
    test_evolution_service.py      ← 4 testes
    test_flowise_service.py        ← 3 testes
    test_kommo_service.py          ← 5 testes
    test_monday_service.py         ← 6 testes
```

### Dependências a instalar
```
pytest
pytest-asyncio
```

---

### 📋 Checklist de Implementação

#### Setup
- [x] Adicionar `pytest` e `pytest-asyncio` ao `requirements.txt`
- [x] Criar `tests/__init__.py`
- [x] Criar `tests/conftest.py` com mock das `settings`
- [x] Criar `tests/services/__init__.py`
- [x] Criar `pytest.ini`

#### `test_evolution_service.py`
- [x] ✅ `test_send_message_success` — status 201, verifica log de sucesso
- [x] ⚠️ `test_send_message_api_error` — status != 201, verifica log de erro
- [x] ❌ `test_send_message_connection_error` — httpx levanta exceção
- [x] 🔁 `test_process_incoming_message` — orquestra flowise + send_message

#### `test_flowise_service.py`
- [x] ✅ `test_generate_response_success` — retorna `text` do JSON
- [x] ⚠️ `test_generate_response_missing_text` — JSON sem campo `text`, retorna fallback
- [x] ❌ `test_generate_response_api_error` — exceção retorna mensagem de instabilidade


---

## 3. Estratégia de Mock

### Services Async (Evolution, Flowise)
```python
# Padrão: mockar httpx.AsyncClient como context manager
with patch("httpx.AsyncClient") as MockClient:
    mock_client = AsyncMock()
    MockClient.return_value.__aenter__.return_value = mock_client
    mock_client.post.return_value = mock_response
```

### Services Sync (Kommo, Monday)
```python
# Padrão: mockar requests.get / requests.post
with patch("requests.get") as mock_get:
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"data": ...}
```

### Settings (conftest.py)
```python
# Mockar settings para não depender do .env
@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    monkeypatch.setattr("app.core.config.settings", FakeSettings())
```

---

## 4. Como Rodar

```bash
# Rodar todos os testes
pytest tests/ -v

# Rodar só um arquivo
pytest tests/services/test_monday_service.py -v

# Rodar com coverage
pytest tests/ -v --cov=app/services
```
