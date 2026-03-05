"""A+H share price comparison using Tencent Finance API."""

import re
import urllib.parse
import httpx

from opencc import OpenCC

_t2s = OpenCC("t2s").convert

CNY_HKD_RATE = 1.12

_a_share_cache: dict[str, str | None] = {}


def search_a_share_code(company_name: str) -> str | None:
    """Search for A-share code by company name using Sina suggest API.
    
    Tries both traditional (original) and simplified Chinese names.
    """
    if not company_name:
        return None
    if company_name in _a_share_cache:
        return _a_share_cache[company_name]

    # Try both traditional and simplified
    names_to_try = [company_name]
    simplified = _t2s(company_name)
    if simplified != company_name:
        names_to_try.append(simplified)

    for name in names_to_try:
        try:
            encoded = urllib.parse.quote(name)
            url = f"https://suggest3.sinajs.cn/suggest/type=11,12&key={encoded}"
            resp = httpx.get(url, timeout=10)
            m = re.search(r",(sz|sh)(\d{6}),", resp.text)
            if m:
                code = f"{m.group(1)}{m.group(2)}"
                _a_share_cache[company_name] = code
                return code
        except (httpx.HTTPError, ValueError, AttributeError):
            pass

    _a_share_cache[company_name] = None
    return None


def fetch_a_share_price(a_code: str) -> float:
    """Fetch A-share price from Tencent Finance API."""
    try:
        resp = httpx.get(f"https://qt.gtimg.cn/q={a_code}", timeout=10)
        parts = resp.text.split("~")
        if len(parts) > 3:
            return float(parts[3])
    except (httpx.HTTPError, ValueError, IndexError):
        pass
    return 0


def fetch_ah_comparison(h_code: str, h_price_hkd: float, company_name: str) -> dict | None:
    """Compare A-share and H-share prices.

    Returns dict with: a_share.code, a_share.price_cny, h_share.price_hkd,
    h_share.price_cny, discount_pct.  Returns None if no A-share found.
    """
    a_code = search_a_share_code(company_name)
    if not a_code:
        return None

    a_price = fetch_a_share_price(a_code)
    if a_price <= 0:
        return None

    h_price_cny = h_price_hkd / CNY_HKD_RATE
    discount = round((a_price - h_price_cny) / a_price * 100, 1)

    return {
        "code": h_code,
        "name": company_name,
        "a_share": {"code": a_code, "price_cny": round(a_price, 2)},
        "h_share": {"price_hkd": h_price_hkd, "price_cny": round(h_price_cny, 2)},
        "discount_pct": discount,
    }
