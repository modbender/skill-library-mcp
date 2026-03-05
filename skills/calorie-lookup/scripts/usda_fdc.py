import requests
from typing import Dict, Any, List, Optional, Tuple
from config import USDA_API_KEY, FDC_BASE, HTTP_TIMEOUT_SEC, SEARCH_PAGE_SIZE, PREFERRED_DATA_TYPES

NUTRIENT_IDS = {
    "kcal": 1008,
    "protein_g": 1003,
    "fat_g": 1004,
    "carb_g": 1005,
    "fiber_g": 1079,
}

class USDAError(RuntimeError):
    def __init__(self, message: str, status: Optional[int] = None):
        super().__init__(message)
        self.status = status

def _require_key():
    if not USDA_API_KEY:
        raise USDAError("Missing USDA_FDC_API_KEY env var", status=401)

def _handle_response(r: requests.Response):
    if r.status_code == 401:
        raise USDAError("USDA API key 无效或缺失（401）", status=401)
    if r.status_code == 403:
        raise USDAError("USDA API 权限不足（403）", status=403)
    if r.status_code == 429:
        raise USDAError("USDA API 触发限速（429），请稍后再试", status=429)
    if r.status_code >= 500:
        raise USDAError(f"USDA API 服务器错误（{r.status_code}）", status=r.status_code)
    r.raise_for_status()

def search_food(query: str) -> List[Dict[str, Any]]:
    _require_key()
    url = f"{FDC_BASE}/foods/search"
    payload = {
        "query": query,
        "pageSize": SEARCH_PAGE_SIZE,
        "dataType": PREFERRED_DATA_TYPES,
    }
    r = requests.post(url, params={"api_key": USDA_API_KEY}, json=payload, timeout=HTTP_TIMEOUT_SEC)
    _handle_response(r)
    data = r.json()
    return data.get("foods", []) or []

def get_food_detail(fdc_id: int) -> Dict[str, Any]:
    _require_key()
    url = f"{FDC_BASE}/food/{fdc_id}"
    r = requests.get(url, params={"api_key": USDA_API_KEY}, timeout=HTTP_TIMEOUT_SEC)
    _handle_response(r)
    return r.json()

def extract_per_100g_nutrients(food_detail: Dict[str, Any]) -> Dict[str, float]:
    out = {k: 0.0 for k in NUTRIENT_IDS.keys()}
    nutrients = food_detail.get("foodNutrients", []) or []
    for n in nutrients:
        nid = n.get("nutrient", {}).get("id") or n.get("nutrientId")
        amount = n.get("amount")
        if nid is None or amount is None:
            continue
        for key, target_id in NUTRIENT_IDS.items():
            if nid == target_id:
                out[key] = float(amount)
    return out

def pick_best_candidate(cands: List[Dict[str, Any]], query: str) -> Tuple[Optional[Dict[str, Any]], float]:
    if not cands:
        return None, 0.0

    def dt_rank(dt: str) -> int:
        try:
            return PREFERRED_DATA_TYPES.index(dt)
        except ValueError:
            return len(PREFERRED_DATA_TYPES)

    q = query.lower().strip()
    scored = []
    for c in cands:
        desc = (c.get("description") or "").lower()
        dt = c.get("dataType") or ""
        score = 0.0
        score += max(0, 10 - 2 * dt_rank(dt))
        if q and q in desc:
            score += 6
        if desc.startswith(q):
            score += 2
        if c.get("fdcId"):
            score += 1
        scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[0][1]
    top = scored[0][0]
    second = scored[1][0] if len(scored) > 1 else top - 4
    gap = max(0.0, top - second)
    conf = min(1.0, 0.4 + 0.05 * top + 0.06 * gap)
    return best, conf
