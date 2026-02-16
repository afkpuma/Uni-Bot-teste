# Planejamento: Integração Completa Monday.com

## 1. Research (Estado Atual)
- Já temos autenticação funcionando.
- Já sabemos listar colunas.
- Falta: Capacidade de ESCREVER (Mutations) no Monday.

## 2. Mapa de Colunas (Necessário mapear via script)
| Funcionalidade | Coluna (Nome) | ID Provável (Monday) | Tipo Dado |
| :--- | :--- | :--- | :--- |
| Status | Status | `status` (exemplo) | Dropdown Label |
| Responsável | Pessoa | `person` | User ID (Int) |
| Prazo | Data | `date4` | YYYY-MM-DD |
| ID Aluno | ID WhatsApp | `text` | String |

## 3. Plano de Implementação (Atomic Commits)

### Fase A: Infraestrutura
- [ ] `chore: criar constantes com IDs das colunas em app/core/constants.py`
- [ ] `feat: implementar logger configurado em app/core/logger.py`

### Fase B: Mutations Básicas (Service)
- [ ] `feat: criar método create_item no MondayService`
- [ ] `feat: criar método update_status (mover tarefas)`
- [ ] `feat: criar método add_comment (updates)`

### Fase C: Gestão de Pessoas e Prazos
- [ ] `feat: criar método de busca de usuário (Email -> ID)`
- [ ] `feat: criar método assign_person (Atribuir)`
- [ ] `feat: criar método set_deadline`

### Fase D: Integração Gmail (Estratégia Híbrida)
- [ ] `research: validar integração nativa "Monday Automation" para ler emails`
- [ ] `doc: documentar fluxo de emails no README`