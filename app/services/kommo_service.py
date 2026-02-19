import logging
from typing import Optional

import httpx
from app.core.config import settings

logger = logging.getLogger("uvicorn")


class KommoService:
    _client = httpx.AsyncClient(timeout=10.0)
    _base_url = settings.KOMMO_URL
    _headers = {
        "Authorization": f"Bearer {settings.KOMMO_TOKEN}",
        "Content-Type": "application/json"
    }

    @staticmethod
    def _handle_response(response: httpx.Response) -> dict:
        """Trata resposta da API Kommo: retorna JSON ou dict de erro."""
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"⚠️ Erro Kommo ({response.status_code}): {response.text}")
            return {"error": f"Erro {response.status_code}", "details": response.text}

    @staticmethod
    async def get_leads(query: Optional[str] = None) -> dict:
        """Busca leads na Kommo. Se tiver query, filtra."""
        url = f"{KommoService._base_url}/api/v4/leads"
        params = {}

        if query:
            params["query"] = query

        response = await KommoService._client.get(url, headers=KommoService._headers, params=params)
        return KommoService._handle_response(response)

    @staticmethod
    async def get_contacts(query: Optional[str] = None, page: Optional[int] = None, limit: Optional[int] = None) -> dict:
        """Busca contatos na Kommo. Se tiver query, filtra."""
        url = f"{KommoService._base_url}/api/v4/contacts"
        params = {}

        if query:
            params["query"] = query
        if page:
            params["page"] = page
        if limit:
            params["limit"] = limit

        response = await KommoService._client.get(url, headers=KommoService._headers, params=params)
        return KommoService._handle_response(response)

    @staticmethod
    async def get_contact_by_id(contact_id: int) -> dict:
        """Busca um contato específico por ID na Kommo."""
        url = f"{KommoService._base_url}/api/v4/contacts/{contact_id}"

        response = await KommoService._client.get(url, headers=KommoService._headers)
        return KommoService._handle_response(response)

    @staticmethod
    async def create_lead(name_lead: str, price_course: int) -> dict:
        """Cria um lead na Kommo."""
        url = f"{KommoService._base_url}/api/v4/leads"

        # Kommo exige que os dados venham dentro de uma lista,
        # mesmo que seja apenas um lead.
        payload = [{
            "name": name_lead,
            "price": price_course,
        }]

        response = await KommoService._client.post(url, headers=KommoService._headers, json=payload)
        return KommoService._handle_response(response)