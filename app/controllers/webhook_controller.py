"""
Controller de Webhook — Recebe eventos da Evolution API (WhatsApp).
"""
import logging
from fastapi import APIRouter, Request

# Configura o logger para aparecer nos logs do Docker
logger = logging.getLogger("uvicorn")

router = APIRouter()

@router.post("/webhook")
async def receive_webhook(request: Request) -> dict:
    """
    Endpoint que recebe eventos da Evolution API.
    Filtra apenas eventos do tipo 'messages.upsert' (mensagens recebidas).
    """
    try:
        payload: dict = await request.json()
        
        # CORREÇÃO: Evolution usa 'type' ou 'event' dependendo da versão. 
        event_type = payload.get("type") or payload.get("event") or ""

        # Log para debug (INFO aparece no terminal)
        logger.info(f"🔔 Webhook recebido! Tipo: '{event_type}'")

        if event_type != "messages.upsert":
            return {"status": "ignored", "event": event_type}

        # Extrai dados da mensagem
        data: dict = payload.get("data", {})
        key: dict = data.get("key", {})
        message_data: dict = data.get("message", {})

        remote_jid: str = key.get("remoteJid", "desconhecido")
        push_name: str = data.get("pushName", "Sem Nome")
        
        # Extrai o texto (lógica para Android/iPhone)
        text: str = message_data.get("conversation", "")
        if not text:
            text = message_data.get("extendedTextMessage", {}).get("text", "")

        if not text:
            logger.info(f"⚠️ Mensagem sem texto de {push_name}")
            return {"status": "no_text"}

        logger.info(f"📩 MENSAGEM DE {push_name} ({remote_jid}): {text}")

        return {
            "status": "received",
            "from": remote_jid,
            "name": push_name,
            "text": text,
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar webhook: {e}")
        return {"status": "error"}
