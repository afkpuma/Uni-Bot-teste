"""
Testes unitários para EvolutionService.
Mocka httpx.AsyncClient para não fazer chamadas HTTP reais.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.evolution_service import EvolutionService


# ---------------------------------------------------------------------------
# send_message
# ---------------------------------------------------------------------------

class TestSendMessage:
    """Testes para EvolutionService.send_message."""

    async def test_send_message_success(self):
        """Quando a Evolution API retorna 201, loga sucesso."""
        mock_response = MagicMock()
        mock_response.status_code = 201

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch("httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_client

            await EvolutionService.send_message("5511999999999@s.whatsapp.net", "Olá!")

            # Verifica que o POST foi feito com os argumentos corretos
            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args
            assert call_kwargs.kwargs["json"]["number"] == "5511999999999@s.whatsapp.net"
            assert call_kwargs.kwargs["json"]["text"] == "Olá!"

    async def test_send_message_api_error(self, caplog):
        """Quando a Evolution API retorna status != 201, loga erro."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch("httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_client

            await EvolutionService.send_message("5511999999999@s.whatsapp.net", "Oi")

            # Não deve levantar exceção, apenas logar
            assert mock_client.post.called

    async def test_send_message_connection_error(self, caplog):
        """Quando httpx levanta exceção, loga erro de conexão."""
        mock_client = AsyncMock()
        mock_client.post.side_effect = Exception("Connection refused")

        with patch("httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_client

            # Não deve propagar a exceção
            await EvolutionService.send_message("5511999999999@s.whatsapp.net", "Teste")


# ---------------------------------------------------------------------------
# process_incoming_message
# ---------------------------------------------------------------------------

class TestProcessIncomingMessage:
    """Testes para EvolutionService.process_incoming_message."""

    async def test_process_incoming_message(self):
        """Orquestra corretamente: Flowise gera resposta → Evolution envia."""
        with patch(
            "app.services.evolution_service.FlowiseService.generate_response",
            new_callable=AsyncMock,
            return_value="Resposta da IA"
        ) as mock_flowise, patch(
            "app.services.evolution_service.EvolutionService.send_message",
            new_callable=AsyncMock
        ) as mock_send:

            await EvolutionService.process_incoming_message(
                "5511999999999@s.whatsapp.net",
                "Qual o valor da mensalidade?"
            )

            # 1. Flowise foi chamado com a mensagem e o remote_jid
            mock_flowise.assert_called_once_with(
                "Qual o valor da mensalidade?",
                "5511999999999@s.whatsapp.net"
            )

            # 2. send_message foi chamado com a resposta da IA
            mock_send.assert_called_once_with(
                "5511999999999@s.whatsapp.net",
                "Resposta da IA"
            )
