# 🚀 UNICESUMAR BOT - RPI PROTOCOL

Este projeto segue estritamente a metodologia **RPI (Research -> Plan -> Implement)**.
NENHUMA linha de código é escrita sem antes passar pelas fases 1 e 2.

## 🔁 O Ciclo RPI

### 1. Research (Pesquisa) 🕵️
* **Objetivo:** Entender o problema e o contexto.
* **Saída:** Arquivo em `planning/contexto_feature.md`.
* **Perguntas:** O que já existe? Qual a limitação da API? Existe solução nativa (ex: Automação Monday) antes de codar?

### 2. Plan (Planejamento) 📝
* **Objetivo:** Desenhar a solução passo a passo.
* **Saída:** Atualização do `planning/contexto_feature.md` com Checklist.
* **Regra:** Quebrar a feature em tarefas **Atômicas** (pequenas o suficiente para um único commit).

### 3. Implement (Implementação) 🔨
* **Objetivo:** Executar o plano.
* **Regra:** **Atomic Commits**. Cada checkbox do plano vira UM commit no Git.
    * ✅ `feat: cria estrutura base do monday_service`
    * ✅ `fix: corrige tipo de dado na query graphql`
    * ✅ `test: valida criação de item com mock`

---

## 🛡️ Diretrizes de Código (The Zen)
1.  **Tipagem Forte:** Todo método DEVE ter Type Hints (`def func(a: int) -> dict:`).
2.  **Zero Hardcode:** Tokens e URLs vêm de `app/core/config.py`.
3.  **Tratamento de Erros:** Sair graciosamente. Se o Monday falhar, o bot continua rodando.
4.  **Logs:** Usar `logger.info()` em vez de `print()`.

## 📁 Estrutura de Pastas
/app
  /services  -> Lógica de Integração (Kommo, Monday)
  /core      -> Configs e Constants (IDs das colunas)
  /planning  -> Documentação RPI (Onde a mágica começa)