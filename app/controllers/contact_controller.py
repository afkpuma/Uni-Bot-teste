from typing import Optional

from fastapi import APIRouter, Depends
from app.services.kommo_service import KommoService

router: APIRouter = APIRouter()

@router.get("/contacts")
def read_contacts(busca: Optional[str] = None, page: Optional[int] = None, limit: Optional[int] = None, service: KommoService = Depends(KommoService)) -> dict:
    """Lista/busca contatos. Use query params para filtrar."""
    return service.get_contacts(query=busca, page=page, limit=limit)

@router.get("/contacts/{contact_id}")
def read_contact_by_id(contact_id: int, service: KommoService = Depends(KommoService)) -> dict:
    """Busca um contato específico por ID."""
    return service.get_contact_by_id(contact_id=contact_id)
