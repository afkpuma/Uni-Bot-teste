"""
Controller de Webhook — Recebe eventos da Evolution API (WhatsApp).
Fluxo: Ouvir (Evolution) → Pensar (Flowise) → Falar (Evolution)
"""
import logging
from fastapi import APIRouter, Request, BackgroundTasks
from app.services.flowise_service import FlowiseService
from app.services.evolution_service import EvolutionService

logger = logging.getLogger("uvicorn")
router = APIRouter()


async def process_message(remote_jid: str, user_message: str):
    """Função em background para não travar o webhook"""

    # 1. Obter resposta da IA
    ai_response = await FlowiseService.generate_response(user_message)

    # 2. Enviar resposta no WhatsApp
    await EvolutionService.send_message(remote_jid, ai_response)


@router.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
        event_type = payload.get("type") or payload.get("event")

        if event_type == "messages.upsert":
            data = payload.get("data", {})
            key = data.get("key", {})

            # Ignora mensagens enviadas por mim mesmo (para evitar loop infinito)
            if key.get("fromMe", False):
                return {"status": "ignored_from_me"}

            message_data = data.get("message", {})
            remote_jid = key.get("remoteJid")
            push_name = data.get("pushName")

            # Extrai texto
            user_message = message_data.get("conversation") or \
                           message_data.get("extendedTextMessage", {}).get("text")

            if user_message and remote_jid:
                logger.info(f"📩 MENSAGEM DE {push_name}: {user_message}")

                # 🔥 AQUI ESTÁ A MÁGICA:
                # Processamos em background para responder rápido ao webhook (200 OK)
                # enquanto a IA pensa.
                background_tasks.add_task(process_message, remote_jid, user_message)

                return {"status": "processing"}

        return {"status": "ignored"}

    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return {"status": "error"}
