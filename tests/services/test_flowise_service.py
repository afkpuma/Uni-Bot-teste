"""
Testes unitários para FlowiseService.
Mocka httpx.AsyncClient para não fazer chamadas HTTP reais.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.flowise_service import FlowiseService


class TestGenerateResponse:
    """Testes para FlowiseService.generate_response."""

    async def test_generate_response_success(self):
        """Quando Flowise retorna JSON com 'text', extrai a resposta."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"text": "A mensalidade custa R$999,00"}
        mock_response.raise_for_status = MagicMock()  # Não levanta nada

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch("httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_client

            result = await FlowiseService.generate_response(
                "Quanto custa?",
                "5511999999999@s.whatsapp.net"
            )

            assert result == "A mensalidade custa R$999,00"

            # Verifica payload enviado ao Flowise
            call_kwargs = mock_client.post.call_args
            assert call_kwargs.kwargs["json"]["question"] == "Quanto custa?"
            assert call_kwargs.kwargs["json"]["sessionId"] == "5511999999999@s.whatsapp.net"

    async def test_generate_response_missing_text(self):
        """Quando o JSON do Flowise não tem campo 'text', retorna fallback."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"answer": "Algo inesperado"}  # sem 'text'
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch("httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_client

            result = await FlowiseService.generate_response(
                "Oi",
                "5511888888888@s.whatsapp.net"
            )

            assert result == "Desculpe, não consegui processar sua resposta."

    async def test_generate_response_api_error(self):
        """Quando Flowise lança exceção, retorna mensagem de instabilidade."""
        mock_client = AsyncMock()
        mock_client.post.side_effect = Exception("Flowise está fora do ar")

        with patch("httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__.return_value = mock_client

            result = await FlowiseService.generate_response(
                "Oi",
                "5511777777777@s.whatsapp.net"
            )

            assert result == "Estou com uma pequena instabilidade no meu cérebro agora. Tente novamente em instantes."
