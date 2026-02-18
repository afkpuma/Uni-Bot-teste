"""
Fixtures globais para os testes.

Estratégia: Popular os.environ COM TODAS as variáveis obrigatórias
ANTES de qualquer import do app, e impedir que pydantic_settings
leia o .env real (que pode conter variáveis extras como POSTGRES_PASSWORD).
"""
import os

# ─── Impede pydantic_settings de ler o .env real ─────────────────────────────
# Fazemos isso ANTES de importar qualquer módulo do app.
os.environ["KOMMO_URL"] = "https://fake-kommo.com"
os.environ["KOMMO_TOKEN"] = "fake-kommo-token"
os.environ["MONDAY_TOKEN"] = "fake-monday-token"
os.environ["MONDAY_URL"] = "https://fake-monday.com/v2"
os.environ["MONDAY_BOARD_ID"] = "99999"
os.environ["FLOWISE_API_URL"] = "https://fake-flowise.com/api/v1/prediction/abc123"
os.environ["EVOLUTION_API_URL"] = "https://fake-evolution.com"
os.environ["EVOLUTION_API_TOKEN"] = "fake-evolution-token"
os.environ["INSTANCE_NAME"] = "fake-instance"
