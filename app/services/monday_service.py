import requests
import json
from app.core.config import settings

class MondayService:
    # ID da coluna de Status no board GESTAO BOT
    STATUS_COLUMN_ID = "color_mm0hepv9"

    # Labels válidos para a coluna de Status
    VALID_STATUS_LABELS = [
        "Não Iniciado",
        "Em Progresso",
        "Concluído",
        "Atrasado",
    ]

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

    def get_items(self, board_id: int) -> list:
        """
        Retorna todos os itens de um quadro com seus IDs,
        nomes e valores das colunas.
        """
        query = """
        query {
            boards (ids: %s) {
                items_page (limit: 50) {
                    items {
                        id
                        name
                        column_values {
                            id
                            text
                        }
                    }
                }
            }
        }
        """ % board_id

        resultado = self.send_query(query)
        return resultado["data"]["boards"][0]["items_page"]["items"]

    def update_status(self, item_id: int, status_label: str, board_id: int = None) -> dict:
        """
        Atualiza o status de um item no quadro.

        Args:
            item_id: ID do item no Monday.
            status_label: Um dos valores: "Não Iniciado", "Em Progresso",
                          "Concluído", "Atrasado".
            board_id: ID do quadro (padrão: MONDAY_BOARD_ID do config).

        Returns:
            dict com a resposta da API.

        Raises:
            ValueError: Se o status_label não for válido.
            Exception: Se a API retornar erro.
        """
        if status_label not in self.VALID_STATUS_LABELS:
            raise ValueError(
                f"Status inválido: '{status_label}'. "
                f"Valores permitidos: {self.VALID_STATUS_LABELS}"
            )

        if board_id is None:
            board_id = settings.MONDAY_BOARD_ID

        column_value = json.dumps({"label": status_label})

        query = '''
        mutation {
            change_simple_column_value (
                board_id: %s,
                item_id: %s,
                column_id: "%s",
                value: "%s"
            ) {
                id
                name
            }
        }
        ''' % (board_id, item_id, self.STATUS_COLUMN_ID, status_label)

        return self.send_query(query)


# --- BLOCO DE TESTE RÁPIDO ---
if __name__ == "__main__":
    MONDAY_BOARD_ID = settings.MONDAY_BOARD_ID
    service = MondayService()

    try:
        # 1. Listar itens do board com status atual
        print("=== Itens do board GESTAO BOT ===\n")
        items = service.get_items(MONDAY_BOARD_ID)

        if not items:
            print("Nenhum item encontrado no board.")
            print("Crie um item no Monday.com para testar.")
        else:
            for item in items:
                status = next(
                    (c["text"] for c in item["column_values"]
                     if c["id"] == MondayService.STATUS_COLUMN_ID),
                    "Sem status"
                )
                print(f"  ID: {item['id']} | Nome: {item['name']} | Status: {status}")

            # 2. Demonstrar alteração de status no primeiro item
            primeiro = items[0]
            print(f"\n=== Alterando status do item '{primeiro['name']}' para 'Em Progresso' ===\n")
            resultado = service.update_status(int(primeiro["id"]), "Em Progresso")
            print(json.dumps(resultado, indent=4, ensure_ascii=False))

    except Exception as e:
        print(f"Deu erro: {e}")