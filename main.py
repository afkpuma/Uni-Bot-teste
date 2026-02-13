from fastapi import FastAPI
from app.controllers import lead_controller, contact_controller

tags_metadata = [
    {"name": "Leads", "description": "Operações com leads da Kommo"},
    {"name": "Contacts", "description": "Operações com contatos da Kommo"},
]

app = FastAPI(title="Unicesumar Bot API", openapi_tags=tags_metadata)

# Inclui as rotas dos controladores
app.include_router(lead_controller.router, prefix="/api", tags=["Leads"])
app.include_router(contact_controller.router, prefix="/api", tags=["Contacts"])

@app.get("/")
def root() -> dict:
    return {"message": "API Unicesumar rodando! Vá para /docs"}