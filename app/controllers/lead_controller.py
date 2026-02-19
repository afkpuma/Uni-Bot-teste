from typing import Optional

from fastapi import APIRouter
from app.services.kommo_service import KommoService
from app.schemas.lead_schema import LeadSchema


router: APIRouter = APIRouter()


@router.post("/leads")
async def create_lead(dados: LeadSchema) -> dict:
    """Cria um novo lead na Kommo."""
    return await KommoService.create_lead(dados.nome, dados.price)

@router.get("/leads")
async def read_leads(busca: Optional[str] = None) -> dict:
    """Lista/busca leads na Kommo."""
    return await KommoService.get_leads(query=busca)
