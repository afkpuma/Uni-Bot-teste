import requests
from app.core.config import settings

class KommoService:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.KOMMO_TOKEN}",
            "Content-Type": "application/json"
        }
        self.base_url = settings.KOMMO_URL

    def get_leads(self, query: str):
        """Busca leads na Kommo. Se tiver query, filtra."""
        url = f"{self.base_url}/api/v4/leads"
        params = {}
        
        if query:
            params['query'] = query

        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Erro {response.status_code}", "details": response.text}

    def get_contacts(self, query: str = None, page: int = None, limit: int = None):
        """Busca contatos na Kommo. Se tiver query, filtra."""
        url = f"{self.base_url}/api/v4/contacts"
        params = {}

        if query:
            params['query'] = query
        if page:
            params['page'] = page
        if limit:
            params['limit'] = limit

        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Erro {response.status_code}", "details": response.text}

    def get_contact_by_id(self, contact_id: int):
        """Busca um contato específico por ID na Kommo."""
        url = f"{self.base_url}/api/v4/contacts/{contact_id}"

        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Erro {response.status_code}", "details": response.text}