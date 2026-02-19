import httpx
import logging
from app.core.config import settings
from app.services.flowise_service import FlowiseService

logger = logging.getLogger("uvicorn")


class EvolutionService:
    _client = httpx.AsyncClient(timeout=10.0)
    _send_url = f"{settings.EVOLUTION_API_URL}/message/sendText/{settings.INSTANCE_NAME}"
    _headers = {
        "apikey": settings.EVOLUTION_API_TOKEN,
        "Content-Type": "application/json"
    }

    @staticmethod
    async def send_message(remote_jid: str, text: str):
        """Envia uma mensagem de texto via Evolution API."""

        payload = {
            "number": remote_jid,
            "text": text,
            "delay": 1200  # Delay de 1.2s para parecer humano
        }

        try:
            response = await EvolutionService._client.post(EvolutionService._send_url, json=payload, headers=EvolutionService._headers)
            if response.status_code != 201:
                logger.error(f"⚠️ Falha ao enviar mensagem: {response.text}")
            else:
                logger.info(f"📤 Resposta enviada para {remote_jid}")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar na Evolution API: {e}")

    @staticmethod
    async def process_incoming_message(remote_jid: str, user_message: str) -> None:
        """Orquestra o fluxo: recebe mensagem → pensa (Flowise) → responde (WhatsApp)."""

        # 1. Obter resposta da IA
        ai_response = await FlowiseService.generate_response(user_message, remote_jid)

        # 2. Enviar resposta no WhatsApp
        await EvolutionService.send_message(remote_jid, ai_response)
