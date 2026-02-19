import httpx
import logging
from app.core.config import settings

logger: logging.Logger = logging.getLogger("uvicorn")


class FlowiseService:
    @staticmethod
    async def generate_response(message: str, remote_jid: str) -> str:
        """Envia a mensagem para o Flowise e retorna a resposta da IA."""
        try:
            payload: dict = {
                "question": message,
                "sessionId": remote_jid
            }

            async with httpx.AsyncClient() as client:
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
