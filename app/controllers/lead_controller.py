from fastapi import APIRouter
from app.services.kommo_service import KommoService
from app.schemas.lead_schema import LeadSchema


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
