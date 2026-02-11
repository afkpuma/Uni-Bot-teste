from fastapi import APIRouter
from app.services.kommo_service import KommoService

router = APIRouter()
kommo_service = KommoService()

@router.get("/leads")
def read_leads(busca: str = None):
    # Chama o serviço que conecta na Kommo
    return kommo_service.get_leads(query=busca)