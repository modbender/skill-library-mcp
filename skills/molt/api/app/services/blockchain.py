"""Blockchain API service for querying balances and transactions."""
import httpx
import json
from typing import Optional, List, Dict, Any
from app.core.config import settings

# USDC on Base contract address
USDC_BASE_CONTRACT = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"


class BlockchainAPIError(Exception):
    """Raised when blockchain API calls fail."""
    pass


class BlockchainService:
    """Service for interacting with blockchain APIs (BlockCypher, Helius)."""
    
    def __init__(self):
        self.blockcypher_base = "https://api.blockcypher.com/v1"
        self.helius_base = "https://api.helius.xyz/v0"
        self.blockcypher_token = settings.blockcypher_api_token
        self.helius_key = settings.helius_api_key
        self.base_rpc_url = settings.base_rpc_url
        self.alchemy_key = settings.alchemy_api_key
    
    def _get_blockcypher_url(self, chain: str, endpoint: str) -> str:
        """Build BlockCypher API URL."""
        url = f"{self.blockcypher_base}/{chain}/main/{endpoint}"
        if self.blockcypher_token:
            url += f"?token={self.blockcypher_token}"
        return url
    
    async def get_btc_balance(self, address: str) -> int:
        """Get BTC balance in satoshi."""
        try:
            url = self._get_blockcypher_url("btc", f"addrs/{address}/balance")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                return data.get("balance", 0)
        except httpx.HTTPError as e:
            raise BlockchainAPIError(f"Failed to fetch BTC balance: {e}")
    
    async def get_eth_balance(self, address: str) -> int:
        """Get ETH balance in wei."""
        try:
            url = self._get_blockcypher_url("eth", f"addrs/{address}/balance")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                return data.get("balance", 0)
        except httpx.HTTPError as e:
            raise BlockchainAPIError(f"Failed to fetch ETH balance: {e}")
    
    async def get_sol_balance(self, address: str) -> int:
        """Get SOL balance in lamports."""
        if not self.helius_key:
            raise BlockchainAPIError("Helius API key not configured")
        
        try:
            url = f"{self.helius_base}/addresses/{address}/balances"
            params = {"api-key": self.helius_key}
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                # Helius returns nativeBalance in lamports
                native_balance = data.get("nativeBalance", 0)
                return int(native_balance)
        except httpx.HTTPError as e:
            raise BlockchainAPIError(f"Failed to fetch SOL balance: {e}")
    
    async def get_btc_transactions(self, address: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get BTC transactions for an address."""
        try:
            url = self._get_blockcypher_url("btc", f"addrs/{address}/txs")
            params = {"limit": limit}
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                return data.get("txs", [])
        except httpx.HTTPError as e:
            raise BlockchainAPIError(f"Failed to fetch BTC transactions: {e}")
    
    async def get_eth_transactions(self, address: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get ETH transactions for an address."""
        try:
            url = self._get_blockcypher_url("eth", f"addrs/{address}/txs")
            params = {"limit": limit}
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                return data.get("txs", [])
        except httpx.HTTPError as e:
            raise BlockchainAPIError(f"Failed to fetch ETH transactions: {e}")
    
    async def get_sol_transactions(self, address: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get SOL transactions for an address."""
        if not self.helius_key:
            raise BlockchainAPIError("Helius API key not configured")
        
        try:
            url = f"{self.helius_base}/addresses/{address}/transactions"
            params = {
                "api-key": self.helius_key,
                "limit": limit,
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                return data if isinstance(data, list) else []
        except httpx.HTTPError as e:
            raise BlockchainAPIError(f"Failed to fetch SOL transactions: {e}")
    
    def _encode_balance_of(self, address: str) -> str:
        """Encode balanceOf(address) function call for ERC-20."""
        # balanceOf(address) function signature hash (first 4 bytes)
        # keccak256("balanceOf(address)") = 0x70a08231
        function_selector = "0x70a08231"
        # Pad address to 32 bytes (64 hex chars)
        padded_address = address.lower().replace("0x", "").zfill(64)
        return function_selector + padded_address
    
    async def get_usdc_base_balance(self, address: str) -> int:
        """Get USDC balance on Base in smallest unit (6 decimals)."""
        try:
            # Use Alchemy if available, otherwise public Base RPC
            rpc_url = self.base_rpc_url
            if self.alchemy_key:
                rpc_url = f"https://base-mainnet.g.alchemy.com/v2/{self.alchemy_key}"
            
            # Encode balanceOf(address) call
            data = self._encode_balance_of(address)
            
            # Make eth_call RPC request
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [
                    {
                        "to": USDC_BASE_CONTRACT,
                        "data": data,
                    },
                    "latest",
                ],
                "id": 1,
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(rpc_url, json=payload)
                response.raise_for_status()
                result = response.json()
                
                if "error" in result:
                    raise BlockchainAPIError(f"RPC error: {result['error']}")
                
                # Parse hex result to int
                balance_hex = result.get("result", "0x0")
                balance = int(balance_hex, 16)
                return balance
        except httpx.HTTPError as e:
            raise BlockchainAPIError(f"Failed to fetch USDC Base balance: {e}")
        except (ValueError, KeyError) as e:
            raise BlockchainAPIError(f"Failed to parse USDC Base balance: {e}")
    
    async def get_usdc_base_transactions(self, address: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get USDC on Base transactions for an address. Returns normalized list of {hash, from, value, block_num}."""
        address = address.lower().replace("0x", "")
        address = "0x" + address if address else "0x0"

        if self.alchemy_key:
            try:
                return await self._get_usdc_transactions_alchemy(address, limit)
            except (BlockchainAPIError, httpx.HTTPError):
                raise  # Re-raise our own errors
            except Exception:
                pass  # Fall through to eth_getLogs for other errors

        try:
            return await self._get_usdc_transactions_eth_getlogs(address, limit)
        except httpx.HTTPError as e:
            raise BlockchainAPIError(f"Failed to fetch USDC Base transactions: {e}")

    async def _get_usdc_transactions_alchemy(self, address: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch USDC transfers via Alchemy alchemy_getAssetTransfers."""
        try:
            return await self._get_usdc_transactions_alchemy_impl(address, limit)
        except httpx.HTTPError as e:
            raise BlockchainAPIError(f"Failed to fetch USDC Base transactions: {e}")

    async def _get_usdc_transactions_alchemy_impl(self, address: str, limit: int) -> List[Dict[str, Any]]:
        """Implementation of Alchemy fetch."""
        url = f"https://base-mainnet.g.alchemy.com/v2/{self.alchemy_key}"
        payload = {
            "jsonrpc": "2.0",
            "method": "alchemy_getAssetTransfers",
            "params": [
                {
                    "toAddress": address if address.startswith("0x") else "0x" + address,
                    "contractAddresses": [USDC_BASE_CONTRACT],
                    "category": ["erc20"],
                    "order": "desc",
                    "maxCount": hex(limit),
                    "withMetadata": True,
                }
            ],
            "id": 1,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

        if "error" in result:
            raise BlockchainAPIError(f"Alchemy error: {result['error']}")

        transfers = result.get("result", {}).get("transfers", [])
        normalized = []
        for t in transfers:
            raw_value = t.get("rawContract", {}).get("value")
            if raw_value:
                value = int(raw_value, 16)
            else:
                decimals = 6
                human_value = t.get("value", 0) or 0
                value = int(float(human_value) * (10**decimals))

            normalized.append({
                "hash": t.get("hash", ""),
                "from": t.get("from", ""),
                "value": value,
                "block_num": t.get("blockNum", "0x0"),
                "block_height": int(t.get("blockNum", "0x0"), 16) if isinstance(t.get("blockNum"), str) else t.get("blockNum"),
            })
        return normalized

    async def _get_usdc_transactions_eth_getlogs(self, address: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback: fetch USDC Transfer events via eth_getLogs."""
        # Transfer(address,address,uint256) topic0
        transfer_topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
        to_address_padded = "0x" + address.replace("0x", "").zfill(64)

        rpc_url = self.base_rpc_url
        if self.alchemy_key:
            rpc_url = f"https://base-mainnet.g.alchemy.com/v2/{self.alchemy_key}"

        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getLogs",
            "params": [
                {
                    "address": USDC_BASE_CONTRACT,
                    "topics": [transfer_topic, None, to_address_padded],
                    "fromBlock": "0x0",
                    "toBlock": "latest",
                }
            ],
            "id": 1,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(rpc_url, json=payload)
            response.raise_for_status()
            result = response.json()

        if "error" in result:
            raise BlockchainAPIError(f"RPC error: {result['error']}")

        logs = result.get("result", [])
        if not logs:
            return []

        # Need to fetch tx hashes - eth_getLogs returns logs, each has transactionHash
        # But we need to dedupe by tx hash (one tx can have multiple logs) and get from address
        seen = set()
        normalized = []
        for log in sorted(logs, key=lambda x: int(x.get("blockNumber", "0x0"), 16), reverse=True)[:limit]:
            tx_hash = log.get("transactionHash", "")
            if tx_hash in seen:
                continue
            seen.add(tx_hash)

            data_hex = log.get("data", "0x0")
            value = int(data_hex, 16) if data_hex else 0

            from_topic = log.get("topics", ["", ""])[1] if len(log.get("topics", [])) > 1 else "0x0"
            from_address = "0x" + from_topic[-40:] if from_topic else ""

            normalized.append({
                "hash": tx_hash,
                "from": from_address,
                "value": value,
                "block_num": log.get("blockNumber", "0x0"),
                "block_height": int(log.get("blockNumber", "0x0"), 16) if isinstance(log.get("blockNumber"), str) else 0,
            })

        return normalized