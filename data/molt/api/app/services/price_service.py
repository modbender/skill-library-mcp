"""Price service for fetching live cryptocurrency prices with Binance + CoinGecko fallback."""
import httpx
import time
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class PriceService:
    """Service for fetching cryptocurrency prices (Binance primary, CoinGecko fallback)."""
    
    def __init__(self):
        self.binance_base = "https://api.binance.com/api/v3"
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        # Cache for prices (price, timestamp)
        self._price_cache: Dict[str, tuple[float, float]] = {}
        self._cache_ttl = 60  # Cache for 60 seconds
        # Map Binance symbols to CoinGecko IDs
        self._coingecko_ids = {
            "BTCUSDT": "bitcoin",
            "ETHUSDT": "ethereum",
            "SOLUSDT": "solana",
        }
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """Check if cached price is still valid."""
        if symbol not in self._price_cache:
            return False
        price, timestamp = self._price_cache[symbol]
        return (time.time() - timestamp) < self._cache_ttl
    
    async def _fetch_binance(self, symbol: str) -> float:
        """Fetch price from Binance."""
        url = f"{self.binance_base}/ticker/price"
        params = {"symbol": symbol}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return float(data["price"])
    
    async def _fetch_coingecko(self, symbol: str) -> float:
        """Fetch price from CoinGecko as fallback."""
        coin_id = self._coingecko_ids.get(symbol)
        if not coin_id:
            raise ValueError(f"No CoinGecko mapping for {symbol}")
        
        url = f"{self.coingecko_base}/simple/price"
        params = {"ids": coin_id, "vs_currencies": "usd"}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return float(data[coin_id]["usd"])
    
    async def get_price(self, symbol: str) -> float:
        """
        Get current price for a cryptocurrency symbol.
        Tries Binance first, falls back to CoinGecko, then stale cache.
        
        Args:
            symbol: Binance-style symbol (e.g., 'BTCUSDT', 'ETHUSDT', 'SOLUSDT')
        
        Returns:
            Price in USD as float
        """
        # Check cache first
        if self._is_cache_valid(symbol):
            price, _ = self._price_cache[symbol]
            return price
        
        # Try Binance first
        try:
            price = await self._fetch_binance(symbol)
            self._price_cache[symbol] = (price, time.time())
            return price
        except Exception as e:
            logger.warning(f"Binance failed for {symbol}: {e}")
        
        # Fallback to CoinGecko
        try:
            price = await self._fetch_coingecko(symbol)
            self._price_cache[symbol] = (price, time.time())
            logger.info(f"Used CoinGecko fallback for {symbol}: ${price}")
            return price
        except Exception as e:
            logger.warning(f"CoinGecko fallback failed for {symbol}: {e}")
        
        # Last resort: stale cache
        if symbol in self._price_cache:
            price, _ = self._price_cache[symbol]
            logger.warning(f"All providers failed for {symbol}, using stale cache: ${price}")
            return price
        
        raise Exception(f"Failed to fetch price for {symbol} from all providers")
    
    async def get_prices(self) -> Dict[str, float]:
        """
        Get prices for all supported cryptocurrencies.
        
        Returns:
            Dictionary with keys: 'btc', 'eth', 'sol', 'usdc_base'
            Values are prices in USD
        """
        prices = {}
        
        try:
            prices['btc'] = await self.get_price('BTCUSDT')
            prices['eth'] = await self.get_price('ETHUSDT')
            prices['sol'] = await self.get_price('SOLUSDT')
        except Exception as e:
            logger.error(f"Error fetching prices: {e}")
            raise
        
        # USDC is always $1 (stablecoin)
        prices['usdc_base'] = 1.0
        
        return prices
