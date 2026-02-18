import httpx
import logging
from app.core.config import settings

logger = logging.getLogger("uvicorn")


class FlowiseService:
    @staticmethod
    async def generate_response(message: str) -> str:
        """Envia a mensagem para o Flowise e retorna a resposta da IA."""
        try:
            payload = {"question": message}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.FLOWISE_API_URL,
                    json=payload,
                    timeout=30.0  # IA pode demorar um pouco para pensar
                )
                response.raise_for_status()

                # Flowise retorna um JSON: {"text": "Resposta da IA", ...}
                result = response.json()
                return result.get("text", "Desculpe, não consegui processar sua resposta.")

        except Exception as e:
            logger.error(f"❌ Erro no Flowise: {e}")
            return "Estou com uma pequena instabilidade no meu cérebro agora. Tente novamente em instantes."
