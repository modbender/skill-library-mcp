"""Unit tests for PriceService."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.price_service import PriceService


@pytest.mark.asyncio
class TestPriceService:
    """Tests for PriceService."""

    @pytest.fixture
    def service(self):
        return PriceService()

    async def test_get_price_fetches_from_binance(self, service):
        """Should fetch price from Binance and return float."""
        with patch.object(service, "_fetch_binance", new_callable=AsyncMock) as mock_binance:
            mock_binance.return_value = 95000.50

            result = await service.get_price("BTCUSDT")

        assert result == 95000.50
        mock_binance.assert_called_once_with("BTCUSDT")

    async def test_get_price_uses_cache(self, service):
        """Should use cached price on second call without making HTTP request."""
        with patch.object(service, "_fetch_binance", new_callable=AsyncMock) as mock_binance:
            mock_binance.return_value = 2700.25

            result1 = await service.get_price("ETHUSDT")
            result2 = await service.get_price("ETHUSDT")

        assert result1 == 2700.25
        assert result2 == 2700.25
        assert mock_binance.call_count == 1

    async def test_get_price_falls_back_to_coingecko(self, service):
        """Should fall back to CoinGecko when Binance fails."""
        with (
            patch.object(
                service, "_fetch_binance", new_callable=AsyncMock,
                side_effect=Exception("Binance blocked"),
            ),
            patch.object(
                service, "_fetch_coingecko", new_callable=AsyncMock,
                return_value=95500.00,
            ) as mock_cg,
        ):
            result = await service.get_price("BTCUSDT")

        assert result == 95500.00
        mock_cg.assert_called_once_with("BTCUSDT")

    async def test_get_price_returns_stale_cache_when_all_fail(self, service):
        """Should return stale cached price when both providers fail."""
        # Populate cache then make it stale
        service._price_cache["SOLUSDT"] = (200.50, 0)

        with (
            patch.object(
                service, "_fetch_binance", new_callable=AsyncMock,
                side_effect=Exception("Binance down"),
            ),
            patch.object(
                service, "_fetch_coingecko", new_callable=AsyncMock,
                side_effect=Exception("CoinGecko down"),
            ),
        ):
            result = await service.get_price("SOLUSDT")

        assert result == 200.50

    async def test_get_price_raises_when_no_cache_and_all_fail(self, service):
        """Should raise when all providers fail and no cache exists."""
        with (
            patch.object(
                service, "_fetch_binance", new_callable=AsyncMock,
                side_effect=Exception("Binance down"),
            ),
            patch.object(
                service, "_fetch_coingecko", new_callable=AsyncMock,
                side_effect=Exception("CoinGecko down"),
            ),
        ):
            with pytest.raises(Exception, match="all providers"):
                await service.get_price("BTCUSDT")

    async def test_get_prices_returns_all_chains(self, service):
        """Should return dict with btc, eth, sol, usdc_base keys."""
        prices = {"BTCUSDT": 95000.0, "ETHUSDT": 2700.0, "SOLUSDT": 200.0}

        with patch.object(service, "_fetch_binance", new_callable=AsyncMock) as mock_binance:
            mock_binance.side_effect = lambda s: prices[s]

            result = await service.get_prices()

        assert result["btc"] == 95000
        assert result["eth"] == 2700
        assert result["sol"] == 200
        assert result["usdc_base"] == 1.0

    async def test_get_prices_usdc_always_1(self, service):
        """Should always return 1.0 for usdc_base regardless of API."""
        with patch.object(service, "get_price", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = 999.99

            result = await service.get_prices()

        assert result["usdc_base"] == 1.0

    async def test_coingecko_fetch_maps_symbols_correctly(self, service):
        """Should map Binance symbols to CoinGecko IDs."""
        coingecko_response = {"bitcoin": {"usd": 96000.0}}

        mocked_response = MagicMock()
        mocked_response.json.return_value = coingecko_response
        mocked_response.raise_for_status = MagicMock()

        with patch("app.services.price_service.httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_instance.get = AsyncMock(return_value=mocked_response)
            mock_client.return_value = mock_instance

            result = await service._fetch_coingecko("BTCUSDT")

        assert result == 96000.0
        call_kwargs = mock_instance.get.call_args
        assert call_kwargs.kwargs["params"]["ids"] == "bitcoin"
