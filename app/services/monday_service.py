import requests
import json
from app.core.config import settings

class MondayService:
    def __init__(self) -> None:
        self.headers = {
            "Authorization": settings.MONDAY_TOKEN,
            "Content-Type": "application/json"
        }
        self.api_url = settings.MONDAY_URL

    def send_query(self, query: str) -> dict:
        """
        Função auxiliar que empacota o GraphQL e manda pro Monday.
        """
        data = {'query': query}
        response = requests.post(self.api_url, json=data, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro na API Monday: {response.text}")

    def find_id_columns(self, board_id: int) -> dict:
        """
        Esta função serve APENAS para descobrirmos os nomes
        internos das colunas do seu quadro.
        """
        query = """
        query {
            boards (ids: %s) {
                name
                columns {
                    title
                    id
                    type
                }
            }
        }
        """ % board_id
        
        return self.send_query(query)

# --- BLOCO DE TESTE RÁPIDO ---
if __name__ == "__main__":
    MONDAY_BOARD_ID = settings.MONDAY_BOARD_ID
    service = MondayService()
    try:
        resultado = service.find_id_columns(MONDAY_BOARD_ID)
        print(json.dumps(resultado, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"Deu erro: {e}")