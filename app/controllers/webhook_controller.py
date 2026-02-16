"""
Controller de Webhook — Recebe eventos da Evolution API (WhatsApp).
"""

import logging
from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhook")
async def receive_webhook(request: Request) -> dict:
    """
    Endpoint que recebe eventos da Evolution API.
    Filtra apenas eventos do tipo 'messages.upsert' (mensagens recebidas).
    """
    payload: dict = await request.json()
    event: str = payload.get("event", "")

    if event != "messages.upsert":
        logger.debug("Evento ignorado: %s", event)
        return {"status": "ignored", "event": event}

    # Extrai dados da mensagem
    data: dict = payload.get("data", {})
    key: dict = data.get("key", {})
    message_data: dict = data.get("message", {})

    remote_jid: str = key.get("remoteJid", "desconhecido")
    push_name: str = data.get("pushName", "Sem Nome")
    text: str = message_data.get("conversation", "")

    # Se não veio texto simples, tenta extendedTextMessage
    if not text:
        text = message_data.get("extendedTextMessage", {}).get("text", "")

    logger.info(
        "📩 Mensagem recebida | De: %s (%s) | Texto: %s",
        push_name,
        remote_jid,
        text,
    )

    return {
        "status": "received",
        "from": remote_jid,
        "name": push_name,
        "text": text,
    }
