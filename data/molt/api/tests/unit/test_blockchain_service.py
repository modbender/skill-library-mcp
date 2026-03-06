"""Unit tests for BlockchainService."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.blockchain import BlockchainService, BlockchainAPIError


@pytest.mark.asyncio
class TestBlockchainService:
    """Tests for BlockchainService."""

    @pytest.fixture
    def service(self):
        return BlockchainService()

    async def test_get_usdc_base_transactions_with_alchemy(self, service):
        """Should return normalized transfers when Alchemy API is available."""
        # Alchemy alchemy_getAssetTransfers response format
        alchemy_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "transfers": [
                    {
                        "hash": "0xabc123",
                        "from": "0xfrom123",
                        "to": "0xrecipient456",
                        "blockNum": "0x12345",
                        "category": "erc20",
                        "value": 100.5,  # Human-readable (100.5 USDC)
                        "rawContract": {
                            "value": "0x5f5e100",  # 100000000 in hex = 100 USDC (6 decimals)
                            "decimal": "0x6",
                        },
                    },
                ],
                "pageKey": None,
            },
        }

        mocked_response = MagicMock()
        mocked_response.json.return_value = alchemy_response
        mocked_response.raise_for_status = MagicMock()

        with patch.object(service, "alchemy_key", "test-key"):
            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = MagicMock()
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_instance.post = AsyncMock(return_value=mocked_response)
                mock_client.return_value = mock_instance

                result = await service.get_usdc_base_transactions(
                    "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb", limit=10
                )

        assert len(result) >= 1
        tx = result[0]
        assert tx.get("hash") == "0xabc123"
        assert tx.get("from") or tx.get("from_address")  # normalized
        assert "value" in tx  # Normalized to smallest unit (6 decimals)
        # rawContract.value "0x5f5e100" = 100000000 (100 USDC in 6 decimals)
        assert tx["value"] == 100000000

    async def test_get_usdc_base_transactions_without_alchemy_falls_back_to_eth_getLogs(
        self, service
    ):
        """When alchemy_key is empty, should use eth_getLogs fallback."""
        # eth_getLogs returns Transfer(address,address,uint256) events
        # topic0 = keccak256("Transfer(address,address,uint256)")
        eth_getLogs_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": [
                {
                    "address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                    "topics": [
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                        "0x000000000000000000000000from12345678901234567890123456789012",
                        "0x000000000000000000000000742d35cc6634c0532925a3b844bc9e7595f0beb",
                    ],
                    "data": "0x0000000000000000000000000000000000000000000000000000000005f5e100",
                    "blockNumber": "0x12345",
                    "transactionHash": "0xdef456",
                },
            ],
        }

        mocked_response = MagicMock()
        mocked_response.json.return_value = eth_getLogs_response
        mocked_response.raise_for_status = MagicMock()

        with patch.object(service, "alchemy_key", ""):
            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = MagicMock()
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_instance.post = AsyncMock(return_value=mocked_response)
                mock_client.return_value = mock_instance

                result = await service.get_usdc_base_transactions(
                    "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb", limit=10
                )

        assert len(result) >= 1
        tx = result[0]
        assert tx.get("hash") == "0xdef456"
        # data 0x5f5e100 = 100000000 (100 USDC)
        assert tx["value"] == 100000000

    async def test_get_usdc_base_transactions_handles_api_error(self, service):
        """Should raise BlockchainAPIError on HTTP error."""
        import httpx

        with patch.object(service, "alchemy_key", "test-key"):
            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = MagicMock()
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_instance.post = AsyncMock(side_effect=httpx.HTTPStatusError("500", request=MagicMock(), response=MagicMock()))
                mock_client.return_value = mock_instance

                with pytest.raises(BlockchainAPIError):
                    await service.get_usdc_base_transactions(
                        "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
                    )

    async def test_get_usdc_base_balance(self, service):
        """Should return USDC balance in smallest unit (6 decimals)."""
        rpc_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": "0x152d02c7e14af6800000",  # Large balance in hex
        }

        mocked_response = MagicMock()
        mocked_response.json.return_value = rpc_response
        mocked_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_instance.post = AsyncMock(return_value=mocked_response)
            mock_client.return_value = mock_instance

            result = await service.get_usdc_base_balance(
                "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
            )

        assert isinstance(result, int)
        assert result > 0

    async def test_get_btc_balance(self, service):
        """Should return BTC balance in satoshi."""
        blockcypher_response = {"balance": 50000000}

        mocked_response = MagicMock()
        mocked_response.json.return_value = blockcypher_response
        mocked_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_instance.get = AsyncMock(return_value=mocked_response)
            mock_client.return_value = mock_instance

            result = await service.get_btc_balance("bc1qtest")

        assert result == 50000000

    async def test_get_eth_balance(self, service):
        """Should return ETH balance in wei."""
        blockcypher_response = {"balance": 1000000000000000000}

        mocked_response = MagicMock()
        mocked_response.json.return_value = blockcypher_response
        mocked_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_instance.get = AsyncMock(return_value=mocked_response)
            mock_client.return_value = mock_instance

            result = await service.get_eth_balance("0xtest")

        assert result == 1000000000000000000

    async def test_get_sol_balance(self, service):
        """Should return SOL balance in lamports when Helius key is set."""
        helius_response = {"nativeBalance": 1000000000}

        mocked_response = MagicMock()
        mocked_response.json.return_value = helius_response
        mocked_response.raise_for_status = MagicMock()

        with patch.object(service, "helius_key", "test-key"):
            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = MagicMock()
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_instance.get = AsyncMock(return_value=mocked_response)
                mock_client.return_value = mock_instance

                result = await service.get_sol_balance(
                    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
                )

        assert result == 1000000000
