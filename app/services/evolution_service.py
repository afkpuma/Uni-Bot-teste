import httpx
import logging
from app.core.config import settings
from app.services.flowise_service import FlowiseService

logger: logging.Logger = logging.getLogger("uvicorn")


class EvolutionService:
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
            logger.info("🔒 Conexão com Evolution API encerrada.")

    @staticmethod
    async def send_message(remote_jid: str, text: str) -> None:
        """Envia uma mensagem de texto via Evolution API."""
        url: str = f"{settings.EVOLUTION_API_URL}/message/sendText/{settings.INSTANCE_NAME}"

        headers: dict = {
            "apikey": settings.EVOLUTION_API_TOKEN,
            "Content-Type": "application/json"
        }

        payload: dict = {
            "number": remote_jid,
            "text": text,
            "delay": 1200  # Delay de 1.2s para parecer humano
        }

        try:
            client = EvolutionService.get_client()
            response: httpx.Response = await client.post(url, json=payload, headers=headers)
            
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
        ai_response: str = await FlowiseService.generate_response(user_message, remote_jid)

        # 2. Enviar resposta no WhatsApp
        await EvolutionService.send_message(remote_jid, ai_response)
