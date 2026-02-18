from typing import Optional

import requests
from app.core.config import settings

class KommoService:
    def __init__(self) -> None:
        self.headers: dict = {
            "Authorization": f"Bearer {settings.KOMMO_TOKEN}",
            "Content-Type": "application/json"
        }
        self.base_url: str = settings.KOMMO_URL

    def get_leads(self, query: Optional[str] = None) -> dict:
        """Busca leads na Kommo. Se tiver query, filtra."""
        url: str = f"{self.base_url}/api/v4/leads"
        params: dict = {}
        
        if query:
            params['query'] = query

        response: requests.Response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Erro {response.status_code}", "details": response.text}

    def get_contacts(self, query: Optional[str] = None, page: Optional[int] = None, limit: Optional[int] = None) -> dict:
        """Busca contatos na Kommo. Se tiver query, filtra."""
        url: str = f"{self.base_url}/api/v4/contacts"
        params: dict = {}

        if query:
            params['query'] = query
        if page:
            params['page'] = page
        if limit:
            params['limit'] = limit

        response: requests.Response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Erro {response.status_code}", "details": response.text}

    def get_contact_by_id(self, contact_id: int) -> dict:
        """Busca um contato específico por ID na Kommo."""
        url: str = f"{self.base_url}/api/v4/contacts/{contact_id}"

        response: requests.Response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Erro {response.status_code}", "details": response.text}

    def create_lead(self, name_lead: str, price_course: int) -> dict:
        url: str = f"{self.base_url}/api/v4/leads"

        #kommo exige que os dados venham dentro de uma lista,
        # mesmo que seja apenas um lead.

        payload: list[dict] = [{
            "name": name_lead,
            "price": price_course,
        }]        

        response: requests.Response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Erro {response.status_code}", "details": response.text}