from typing import Optional

from fastapi import APIRouter
from app.services.kommo_service import KommoService

router = APIRouter()
kommo_service = KommoService()

@router.get("/contacts")
def read_contacts(busca: Optional[str] = None, page: Optional[int] = None, limit: Optional[int] = None) -> dict:
    """Lista/busca contatos. Use query params para filtrar."""
    return kommo_service.get_contacts(query=busca, page=page, limit=limit)

@router.get("/contacts/{contact_id}")
def read_contact_by_id(contact_id: int) -> dict:
    """Busca um contato específico por ID."""
    return kommo_service.get_contact_by_id(contact_id=contact_id)
