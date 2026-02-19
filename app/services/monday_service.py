import logging
import json
from typing import Optional

import httpx
from app.core.config import settings
from app.core.constants import COL_STATUS

logger = logging.getLogger("uvicorn")


class MondayService:
    _client = httpx.AsyncClient(timeout=10.0)
    _api_url = settings.MONDAY_URL
    _headers = {
        "Authorization": settings.MONDAY_TOKEN,
        "Content-Type": "application/json"
    }

    # Usa a constante centralizada de constants.py
    STATUS_COLUMN_ID = COL_STATUS

    # Labels válidos para a coluna de Status
    VALID_STATUS_LABELS = [
        "Não Iniciado",
        "Em Progresso",
        "Concluído",
        "Atrasado",
    ]

    @staticmethod
    async def send_query(query: str) -> dict:
        """Função auxiliar que empacota o GraphQL e manda pro Monday."""
        data = {"query": query}
        response = await MondayService._client.post(
            MondayService._api_url, json=data, headers=MondayService._headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"⚠️ Erro Monday ({response.status_code}): {response.text}")
            raise Exception(f"Erro na API Monday: {response.text}")

    @staticmethod
    async def find_id_columns(board_id: int) -> dict:
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

        return await MondayService.send_query(query)

    @staticmethod
    async def get_items(board_id: int) -> list:
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

        resultado = await MondayService.send_query(query)
        return resultado["data"]["boards"][0]["items_page"]["items"]

    @staticmethod
    async def update_status(item_id: int, status_label: str, board_id: Optional[int] = None) -> dict:
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
        if status_label not in MondayService.VALID_STATUS_LABELS:
            raise ValueError(
                f"Status inválido: '{status_label}'. "
                f"Valores permitidos: {MondayService.VALID_STATUS_LABELS}"
            )

        if board_id is None:
            board_id = settings.MONDAY_BOARD_ID

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
        ''' % (board_id, item_id, MondayService.STATUS_COLUMN_ID, status_label)

        return await MondayService.send_query(query)


# --- BLOCO DE TESTE RÁPIDO ---
if __name__ == "__main__":
    import asyncio

    async def main():
        MONDAY_BOARD_ID = settings.MONDAY_BOARD_ID

        try:
            # 1. Listar itens do board com status atual
            print("=== Itens do board GESTAO BOT ===\n")
            items = await MondayService.get_items(MONDAY_BOARD_ID)

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
                resultado = await MondayService.update_status(int(primeiro["id"]), "Em Progresso")
                print(json.dumps(resultado, indent=4, ensure_ascii=False))

        except Exception as e:
            print(f"Deu erro: {e}")

    asyncio.run(main())