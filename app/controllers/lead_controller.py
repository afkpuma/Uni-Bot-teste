from typing import Optional

from fastapi import APIRouter, Depends
from app.services.kommo_service import KommoService
from app.schemas.lead_schema import LeadSchema


router = APIRouter()


@router.post("/leads")
def criar_novo_lead(dados: LeadSchema, service: KommoService = Depends(KommoService)) -> dict:
    # O FastAPI converte o JSON recebido para o objeto 'dados'
    return service.create_lead(dados.nome, dados.price)

@router.get("/leads")
def read_leads(busca: Optional[str] = None, service: KommoService = Depends(KommoService)) -> dict:
    # Chama o serviço que conecta na Kommo
    return service.get_leads(query=busca)
