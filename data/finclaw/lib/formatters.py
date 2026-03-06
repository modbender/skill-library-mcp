"""Price and number formatting utilities for FinClaw."""


def fmt_price(value: float, currency: str = "USD") -> str:
    """Format a price with currency symbol."""
    symbols = {"USD": "$", "TRY": "₺", "EUR": "€", "GBP": "£"}
    sym = symbols.get(currency, currency + " ")
    if value == 0:
        return f"{sym}0.00"
    if abs(value) >= 1:
        return f"{sym}{value:,.2f}"
    return f"{sym}{value:.6f}"


def fmt_change(change: float, change_pct: float) -> str:
    arrow = "▲" if change >= 0 else "▼"
    sign = "+" if change >= 0 else ""
    return f"{arrow} {sign}{change:.2f} ({sign}{change_pct:.2f}%)"


def fmt_number(value: float) -> str:
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.2f}K"
    return f"{value:,.2f}"


def fmt_volume(volume: float) -> str:
    return f"Vol: {fmt_number(volume)}"


def detect_asset_type(symbol: str) -> str:
    """Detect asset type from symbol format."""
    s = symbol.upper().strip()
    forex_pairs = [
        "USD/TRY", "EUR/USD", "GBP/USD", "USD/JPY", "EUR/TRY",
        "USDTRY", "EURUSD", "GBPUSD", "USDJPY", "EURTRY",
    ]
    if s in forex_pairs or ("/" in s and len(s) <= 7):
        return "forex"
    if s.endswith(".IS"):
        return "stock_bist"
    crypto_symbols = {
        "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT",
        "AVAX", "MATIC", "LINK", "UNI", "SHIB", "LTC", "ATOM",
    }
    if s in crypto_symbols or s.endswith("USDT") or s.endswith("BUSD"):
        return "crypto"
    return "stock_us"


def symbol_normalize(symbol: str) -> str:
    s = symbol.upper().strip()
    forex_map = {
        "USDTRY": "USD/TRY", "EURUSD": "EUR/USD", "GBPUSD": "GBP/USD",
        "USDJPY": "USD/JPY", "EURTRY": "EUR/TRY",
    }
    return forex_map.get(s, s)
