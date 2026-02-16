import logging

from fastapi import FastAPI
from app.controllers import lead_controller, contact_controller, webhook_controller

# Configura logging para o projeto inteiro
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

tags_metadata = [
    {"name": "Leads", "description": "Operações com leads da Kommo"},
    {"name": "Contacts", "description": "Operações com contatos da Kommo"},
    {"name": "Webhook", "description": "Recebe eventos da Evolution API (WhatsApp)"},
]

app = FastAPI(title="Unicesumar Bot API", openapi_tags=tags_metadata)

# Inclui as rotas dos controladores
app.include_router(lead_controller.router, prefix="/api", tags=["Leads"])
app.include_router(contact_controller.router, prefix="/api", tags=["Contacts"])
app.include_router(webhook_controller.router, prefix="/api", tags=["Webhook"])


@app.get("/")
def root() -> dict:
    return {"message": "API Unicesumar rodando! Vá para /docs"}