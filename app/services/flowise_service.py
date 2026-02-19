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
            cls._client = httpx.AsyncClient(timeout=30.0)
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
                timeout=30.0  # IA pode demorar um pouco para pensar
            )
            response.raise_for_status()

            # Flowise retorna um JSON: {"text": "Resposta da IA", ...}
            result: dict = response.json()
            return result.get("text", "Desculpe, não consegui processar sua resposta.")

        except Exception as e:
            logger.error(f"❌ Erro no Flowise: {e}")
            return "Estou com uma pequena instabilidade no meu cérebro agora. Tente novamente em instantes."
