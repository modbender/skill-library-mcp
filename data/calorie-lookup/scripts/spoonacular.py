import requests
from typing import Dict, Any, List, Optional
from config import (
    SPOONACULAR_API_KEY,
    SPOONACULAR_BASE,
    HTTP_TIMEOUT_SEC,
    SPOONACULAR_SEARCH_LIMIT,
)


class SpoonacularError(RuntimeError):
    def __init__(self, message: str, status: Optional[int] = None):
        super().__init__(message)
        self.status = status


def _require_key():
    if not SPOONACULAR_API_KEY:
        raise SpoonacularError("Missing SPOONACULAR_API_KEY env var", status=401)


def _handle_response(r: requests.Response):
    if r.status_code == 401:
        raise SpoonacularError("Spoonacular API key 无效或缺失（401）", status=401)
    if r.status_code == 402:
        raise SpoonacularError("Spoonacular API 配额超限（402）", status=402)
    if r.status_code == 403:
        raise SpoonacularError("Spoonacular API 禁止访问（403）", status=403)
    if r.status_code == 429:
        raise SpoonacularError("Spoonacular API 请求频率超限（429）", status=429)
    if r.status_code >= 500:
        raise SpoonacularError(
            f"Spoonacular 服务器错误（{r.status_code}）", status=r.status_code
        )
    r.raise_for_status()


def search_ingredient(name: str) -> List[Dict[str, Any]]:
    _require_key()
    url = f"{SPOONACULAR_BASE}/food/ingredients/search"
    params = {
        "query": name,
        "number": SPOONACULAR_SEARCH_LIMIT,
        "apiKey": SPOONACULAR_API_KEY,
    }
    r = requests.get(url, params=params, timeout=HTTP_TIMEOUT_SEC)
    _handle_response(r)
    data = r.json()

    # Handle defensive response format: list, dict with results, or empty
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "results" in data:
        return data["results"]
    else:
        return []


def pick_best_ingredient(
    candidates: List[Dict[str, Any]], query: str
) -> Optional[Dict[str, Any]]:
    if not candidates:
        return None

    q = query.lower().strip()

    # Exact name match
    for c in candidates:
        name = (c.get("name") or "").lower()
        if name == q:
            return c

    # Substring match
    for c in candidates:
        name = (c.get("name") or "").lower()
        if q in name:
            return c

    # First result fallback
    return candidates[0]


def get_ingredient_info(ingredient_id: int, amount: float, unit: str) -> Dict[str, Any]:
    _require_key()
    url = f"{SPOONACULAR_BASE}/food/ingredients/{ingredient_id}/information"
    params = {
        "amount": amount,
        "unit": unit,
        "apiKey": SPOONACULAR_API_KEY,
    }
    r = requests.get(url, params=params, timeout=HTTP_TIMEOUT_SEC)
    _handle_response(r)
    return r.json()


def extract_nutrients(info: Dict[str, Any]) -> Dict[str, float]:
    out = {
        "kcal": 0.0,
        "protein_g": 0.0,
        "carb_g": 0.0,
        "fat_g": 0.0,
        "fiber_g": 0.0,
    }

    nutrients = info.get("nutrition", {}).get("nutrients", []) or []

    name_map = {
        "Calories": "kcal",
        "Protein": "protein_g",
        "Carbohydrates": "carb_g",
        "Fat": "fat_g",
        "Fiber": "fiber_g",
    }

    for n in nutrients:
        nutrient_name = n.get("name")
        amount = n.get("amount")
        if nutrient_name in name_map and amount is not None:
            out[name_map[nutrient_name]] = float(amount)

    return out
