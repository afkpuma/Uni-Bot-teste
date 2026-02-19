import httpx
import logging
from app.core.config import settings

logger = logging.getLogger("uvicorn")


class FlowiseService:
    _client = httpx.AsyncClient(timeout=30.0)
    _api_url = settings.FLOWISE_API_URL

    @staticmethod
    async def generate_response(message: str, remote_jid: str) -> str:
        """Envia a mensagem para o Flowise e retorna a resposta da IA."""
        try:
            payload = {
                "question": message,
                "sessionId": remote_jid
            }

            response = await FlowiseService._client.post(
                FlowiseService._api_url,
                json=payload,
            )
            response.raise_for_status()

            # Flowise retorna um JSON: {"text": "Resposta da IA", ...}
            result = response.json()
            return result.get("text", "Desculpe, não consegui processar sua resposta.")

        except Exception as e:
            logger.error(f"❌ Erro no Flowise: {e}")
            return "Estou com uma pequena instabilidade no meu cérebro agora. Tente novamente em instantes."
