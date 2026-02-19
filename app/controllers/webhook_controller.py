"""
Controller de Webhook — Recebe eventos da Evolution API (WhatsApp).
Responsável APENAS por receber a requisição, extrair dados e delegar ao service.
"""
import logging
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from app.services.evolution_service import EvolutionService

logger: logging.Logger = logging.getLogger("uvicorn")
router: APIRouter = APIRouter()


@router.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks) -> dict:
    try:
        payload: dict = await request.json()
        event_type: str | None = payload.get("type") or payload.get("event")

        if event_type == "messages.upsert":
            data: dict = payload.get("data", {})
            key: dict = data.get("key", {})

            # Ignora mensagens enviadas por mim mesmo (para evitar loop infinito)
            if key.get("fromMe", False):
                return {"status": "ignored_from_me"}

            message_data: dict = data.get("message", {})
            remote_jid: str | None = key.get("remoteJid")
            push_name: str | None = data.get("pushName")

            # Extrai texto
            user_message: str | None = (
                message_data.get("conversation")
                or message_data.get("extendedTextMessage", {}).get("text")
            )

            if user_message and remote_jid:
                logger.info(f"📩 MENSAGEM DE {push_name}: {user_message}")

                # Processa em background para responder rápido ao webhook (200 OK)
                background_tasks.add_task(
                    EvolutionService.process_incoming_message, remote_jid, user_message
                )

                return {"status": "processing"}

        return {"status": "ignored"}

    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return JSONResponse(content={"status": "error"}, status_code=500)
