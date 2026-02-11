from fastapi import FastAPI
from app.controllers import lead_controller

app = FastAPI(title="Unicesumar Bot API")

# Inclui as rotas do controlador
app.include_router(lead_controller.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "API Unicesumar rodando! Vá para /docs"}