from fastapi import APIRouter
from app.services.kommo_service import KommoService
from pydantic import BaseModel

# Criamos um "molde" simples para garantir que o dado chegue certo
class LeadSchema(BaseModel):
    nome: str
    price: int




router = APIRouter()
kommo_service = KommoService()



@router.post("/leads")
def criar_novo_lead(dados: LeadSchema):
    # O FastAPI converte o JSON recebido para o objeto 'dados'
    return kommo_service.create_lead(dados.nome, dados.price)

@router.get("/leads")
def read_leads(busca: str = None):
    # Chama o serviço que conecta na Kommo
    return kommo_service.get_leads(query=busca)
