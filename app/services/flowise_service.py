import httpx
import logging
from app.core.config import settings

logger: logging.Logger = logging.getLogger("uvicorn")


class FlowiseService:

    _client: httpx.AsyncClient = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        """Retorna ou cria uma instância única do cliente HTTP."""
        if cls._client is None or cls._client.is_closed:
            cls._client = httpx.AsyncClient(timeout=120.0)
        return cls._client

    @classmethod
    async def close_client(cls):
        """Fecha a conexão do cliente HTTP."""
        if cls._client and not cls._client.is_closed:
            await cls._client.aclose()
            logger.info("🔒 Conexão com Flowise API encerrada.")

    @staticmethod
    async def generate_response(message: str, remote_jid: str) -> str:
        """Envia a mensagem para o Flowise e retorna a resposta da IA."""
        try:
            payload: dict = {
                "question": message,
                "sessionId": remote_jid
            }

            client = FlowiseService.get_client()
            response: httpx.Response = await client.post(
                settings.FLOWISE_API_URL,
                json=payload,
                timeout=120.0  # IA (Groq free) e banco de dados podem demorar para pensar
            )
            response.raise_for_status()

            # Flowise retorna um JSON: {"text": "Resposta da IA", ...}
            result: dict = response.json()
            return result.get("text", "Desculpe, não consegui processar sua resposta.")

        except httpx.HTTPStatusError as e:
            error_details = e.response.text
            logger.error(f"❌ Erro HTTP {e.response.status_code} no Flowise: {error_details}")
            return "Estou com uma pequena instabilidade no meu cérebro agora. Tente novamente em instantes."
        except Exception as e:
            logger.error(f"❌ Erro inesperado no Flowise: {repr(e)}")
            return "Estou com uma pequena instabilidade no meu cérebro agora. Tente novamente em instantes."
