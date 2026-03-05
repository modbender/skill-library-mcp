from typing import Dict, Any, List, Optional, Tuple
from parser import parse_meal_text  # pyright: ignore[reportImplicitRelativeImport]
from units import to_grams  # pyright: ignore[reportImplicitRelativeImport]
from cache import get as cache_get, set as cache_set  # pyright: ignore[reportImplicitRelativeImport]
from usda_fdc import (  # pyright: ignore[reportImplicitRelativeImport]
    search_food,
    pick_best_candidate,
    get_food_detail,
    extract_per_100g_nutrients,
    USDAError,
)
from spoonacular import (  # pyright: ignore[reportImplicitRelativeImport]
    search_ingredient,
    get_ingredient_info,
    extract_nutrients,
    SpoonacularError,
    pick_best_ingredient,
)
from translate import translate_food_name, is_chinese  # pyright: ignore[reportImplicitRelativeImport]
from config import SPOONACULAR_API_KEY  # pyright: ignore[reportImplicitRelativeImport]

try:
    from cooking import apply_cooking_modifier  # pyright: ignore[reportImplicitRelativeImport]
except ImportError:
    apply_cooking_modifier = None

QUERY_TTL = 24 * 3600
ITEM_TTL = 7 * 24 * 3600
SPOONACULAR_ITEM_TTL = 3600  # 1 hour (Spoonacular ToS)
USDA_ITEM_TTL = 7 * 24 * 3600  # 7 days

CROSS_VALIDATE_THRESHOLD = 0.30  # Flag when nutrients differ by >30%


def _round(x: float) -> float:
    return round(float(x), 1)


def _as_float(v: Any) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _cross_validate(
    spoon_nutrients: Dict[str, float], usda_nutrients: Dict[str, float], name: str
) -> List[str]:
    """Compare Spoonacular and USDA nutrients, return warnings if difference >30%."""
    warnings = []
    nutrient_labels = {
        "kcal": "热量",
        "protein_g": "蛋白质",
        "carb_g": "碳水化合物",
        "fat_g": "脂肪",
    }

    for key in ["kcal", "protein_g", "carb_g", "fat_g"]:
        spoon_val = spoon_nutrients.get(key, 0)
        usda_val = usda_nutrients.get(key, 0)
        if spoon_val == 0 or usda_val == 0:
            continue

        diff_ratio = abs(spoon_val - usda_val) / max(spoon_val, usda_val)
        if diff_ratio > CROSS_VALIDATE_THRESHOLD:
            label = nutrient_labels.get(key, key)
            unit = "kcal" if key == "kcal" else "g"
            warnings.append(
                f"Spoonacular 和 USDA 的{label}差异较大："
                f"Spoonacular {spoon_val}{unit} vs USDA {usda_val}{unit}，"
                f"建议确认食物是否一致"
            )

    return warnings






def _error(message: str, status: int = 500) -> Dict[str, Any]:
    return {"ok": False, "error": message, "status": status}


def _search_with_fallback(
    search_name: str, grams: float, search_hint: Optional[str] = None
) -> Tuple[Optional[Tuple[str, Dict[str, Any], str]], List[str]]:
    spoon_errors: List[str] = []
    search_terms = [search_name]
    if search_hint and search_hint.strip():
        hint = search_hint.strip()
        if hint.lower() != search_name.lower():
            search_terms.append(hint)

    if SPOONACULAR_API_KEY.strip():
        for term in search_terms:
            try:
                spoon_cands = search_ingredient(term)
                if not spoon_cands:
                    continue
                spoon_best = pick_best_ingredient(spoon_cands, term)
                if not spoon_best:
                    continue
                ingredient_id = int(spoon_best["id"])
                spoon_detail = get_ingredient_info(ingredient_id, grams, "g")
                spoon_nutrients = extract_nutrients(spoon_detail)
                return (
                    "spoonacular",
                    {
                        "best": spoon_best,
                        "ingredient_id": ingredient_id,
                        "nutrients": spoon_nutrients,
                    },
                    term,
                ), spoon_errors
            except SpoonacularError as e:
                spoon_errors.append(f"Spoonacular 查询失败（{term}）：{e}")
            except Exception as e:
                spoon_errors.append(f"Spoonacular 查询异常（{term}）：{e}")

    for term in search_terms:
        cands = search_food(term)
        best, conf = pick_best_candidate(cands, term)
        if not best:
            continue
        fdc_id = int(best["fdcId"])
        detail = get_food_detail(fdc_id)
        per100 = extract_per_100g_nutrients(detail)
        return (
            "usda_fdc",
            {"best": best, "fdc_id": fdc_id, "per100": per100, "confidence": conf},
            term,
        ), spoon_errors

    return None, spoon_errors


def lookup_food(
    name: str,
    qty: float,
    unit: str,
    search_hint: Optional[str] = None,
    cooking_method: Optional[str] = None,
    cross_validate: bool = False,
) -> Dict[str, Any]:
    grams, note = to_grams(name, qty, unit)
    if grams is None:
        return {
            "ok": False,
            "reason": note,
            "question": {
                "field": "amount_in_grams",
                "ask": f"「{name}」的份量我没法换算：你大概吃了多少克(g)或毫升(ml)？（例如 150g）",
            },
        }

    # Dictionary-based translation (acceleration cache for known Chinese names).
    # For unknown names, the main agent should use the Decomposer sub-agent (LLM).
    search_name = name
    translate_note = None
    if is_chinese(name):
        search_name, translate_note = translate_food_name(name)

    normalized_search_name = search_name.lower().strip()
    normalized_hint = search_hint.lower().strip() if search_hint else None
    rounded_grams = int(round(grams))
    cache_terms = [normalized_search_name]
    if normalized_hint and normalized_hint != normalized_search_name:
        cache_terms.append(normalized_hint)

    cache_keys = [
        f"item::{provider}::{term}::{rounded_grams}g"
        for provider in ["spoonacular", "usda"]
        for term in cache_terms
    ]
    for cache_key in cache_keys:
        cached = cache_get(cache_key)
        if cached:
            response_item = dict(cached)
            if cooking_method and apply_cooking_modifier:
                nutrient_base = {
                    "kcal": _as_float(response_item["kcal"]),
                    "protein_g": _as_float(response_item["protein_g"]),
                    "carb_g": _as_float(response_item["carb_g"]),
                    "fat_g": _as_float(response_item["fat_g"]),
                    "fiber_g": _as_float(response_item["fiber_g"]),
                }
                modified = apply_cooking_modifier(nutrient_base, cooking_method)
                response_item.update({k: _round(v) for k, v in modified.items()})
            return {"ok": True, **response_item}

    try:
        search_result, spoon_errors = _search_with_fallback(
            search_name, grams, search_hint
        )
        if not search_result:
            return {
                "ok": False,
                "reason": "not_found",
                "question": {
                    "field": "food_clarify",
                    "ask": f"我在USDA里没搜到「{name}」。你能换个更像“食材”的说法吗？（例如：鸡胸肉/熟米饭/全脂牛奶）",
                },
            }

        provider, data, actual_term_used = search_result
        notes = [n for n in [note, translate_note] if n]
        notes.extend(spoon_errors)

        if actual_term_used.lower().strip() != search_name.lower().strip():
            notes.append(
                f"原始搜索词 '{search_name}' 未找到，使用 '{actual_term_used}' 查询成功"
            )

        if provider == "spoonacular":
            spoon_best = data["best"]
            spoon_nutrients = data["nutrients"]
            ingredient_id = data["ingredient_id"]

            spoon_name = (spoon_best.get("name") or actual_term_used).strip()
            query_name = actual_term_used.lower().strip()
            spoon_name_lc = spoon_name.lower()
            if spoon_name_lc == query_name:
                spoon_conf = 0.95
            elif query_name and query_name in spoon_name_lc:
                spoon_conf = 0.80
            else:
                spoon_conf = 0.65

            if spoon_name_lc != query_name and len(notes) < 2:
                notes.append(
                    f"搜索到的食物是 '{spoon_name}'，和输入的 '{actual_term_used}' 不完全匹配，确认是否正确？"
                )

            item = {
                "name_raw": f"{name} {qty}{unit}",
                "name_std": spoon_name or name,
                "qty": qty,
                "unit": unit,
                "grams": _round(grams),
                "kcal": _round(spoon_nutrients["kcal"]),
                "protein_g": _round(spoon_nutrients["protein_g"]),
                "carb_g": _round(spoon_nutrients["carb_g"]),
                "fat_g": _round(spoon_nutrients["fat_g"]),
                "fiber_g": _round(spoon_nutrients["fiber_g"]),
                "source": "spoonacular",
                "fdcId": None,
                "spoonacularId": ingredient_id,
                "confidence": _round(spoon_conf),
                "notes": notes,
            }
            cache_key = f"item::spoonacular::{actual_term_used.lower().strip()}::{rounded_grams}g"
            cache_set(cache_key, item, SPOONACULAR_ITEM_TTL)
        else:
            best = data["best"]
            fdc_id = data["fdc_id"]
            per100 = data["per100"]
            conf = data["confidence"]
            factor = grams / 100.0
            item = {
                "name_raw": f"{name} {qty}{unit}",
                "name_std": best.get("description") or name,
                "qty": qty,
                "unit": unit,
                "grams": _round(grams),
                "kcal": _round(per100["kcal"] * factor),
                "protein_g": _round(per100["protein_g"] * factor),
                "carb_g": _round(per100["carb_g"] * factor),
                "fat_g": _round(per100["fat_g"] * factor),
                "fiber_g": _round(per100["fiber_g"] * factor),
                "source": "usda_fdc",
                "fdcId": fdc_id,
                "confidence": _round(conf),
                "notes": notes,
            }
            cache_key = (
                f"item::usda::{actual_term_used.lower().strip()}::{rounded_grams}g"
            )
            cache_set(cache_key, item, USDA_ITEM_TTL)

        # Cross-validation: query OTHER source for comparison if enabled
        if cross_validate and SPOONACULAR_API_KEY.strip():
            try:
                if provider == "spoonacular":
                    # Primary was Spoonacular, query USDA for comparison
                    from usda_fdc import search_food, pick_best_candidate, get_food_detail, extract_per_100g_nutrients  # pyright: ignore
                    usda_cands = search_food(actual_term_used)
                    usda_best, _ = pick_best_candidate(usda_cands, actual_term_used)
                    if usda_best:
                        usda_fdc_id = int(usda_best["fdcId"])
                        usda_detail = get_food_detail(usda_fdc_id)
                        usda_per100 = extract_per_100g_nutrients(usda_detail)
                        usda_factor = grams / 100.0
                        usda_nutrients = {
                            "kcal": usda_per100["kcal"] * usda_factor,
                            "protein_g": usda_per100["protein_g"] * usda_factor,
                            "carb_g": usda_per100["carb_g"] * usda_factor,
                            "fat_g": usda_per100["fat_g"] * usda_factor,
                        }
                        spoon_nutrients_cv = {
                            "kcal": _as_float(item["kcal"]),
                            "protein_g": _as_float(item["protein_g"]),
                            "carb_g": _as_float(item["carb_g"]),
                            "fat_g": _as_float(item["fat_g"]),
                        }
                        cross_warnings = _cross_validate(spoon_nutrients_cv, usda_nutrients, name)
                        if isinstance(item["notes"], list):
                            item["notes"].extend(cross_warnings)
                else:
                    # Primary was USDA, query Spoonacular for comparison
                    from spoonacular import search_ingredient, pick_best_ingredient, get_ingredient_info, extract_nutrients  # pyright: ignore
                    spoon_cands = search_ingredient(actual_term_used)
                    if spoon_cands:
                        spoon_best = pick_best_ingredient(spoon_cands, actual_term_used)
                        if spoon_best:
                            spoon_id = int(spoon_best["id"])
                            spoon_detail = get_ingredient_info(spoon_id, grams, "g")
                            spoon_nutrients_full = extract_nutrients(spoon_detail)
                            spoon_nutrients_cv = {
                                "kcal": spoon_nutrients_full["kcal"],
                                "protein_g": spoon_nutrients_full["protein_g"],
                                "carb_g": spoon_nutrients_full["carb_g"],
                                "fat_g": spoon_nutrients_full["fat_g"],
                            }
                            usda_nutrients = {
                                "kcal": _as_float(item["kcal"]),
                                "protein_g": _as_float(item["protein_g"]),
                                "carb_g": _as_float(item["carb_g"]),
                                "fat_g": _as_float(item["fat_g"]),
                            }
                            cross_warnings = _cross_validate(spoon_nutrients_cv, usda_nutrients, name)
                            if isinstance(item["notes"], list):
                                item["notes"].extend(cross_warnings)
            except Exception:
                pass  # Cross-validation is optional, don't fail if it errors

        response_item = dict(item)
        if cooking_method and apply_cooking_modifier:
            nutrient_base = {
                "kcal": _as_float(response_item["kcal"]),
                "protein_g": _as_float(response_item["protein_g"]),
                "carb_g": _as_float(response_item["carb_g"]),
                "fat_g": _as_float(response_item["fat_g"]),
                "fiber_g": _as_float(response_item["fiber_g"]),
            }
            modified = apply_cooking_modifier(nutrient_base, cooking_method)
            response_item.update({k: _round(v) for k, v in modified.items()})

        return {"ok": True, **response_item}
    except USDAError as e:
        return _error(str(e), status=e.status or 500)
    except Exception as e:
        return _error(f"USDA 查询失败：{e}")


def lookup_meal(text: str, meal_type: str = "unknown") -> Dict[str, Any]:
    qkey = f"meal::{meal_type}::{text.strip().lower()}"
    cached = cache_get(qkey)
    if cached:
        return cached

    parsed = parse_meal_text(text)
    items: List[Dict[str, Any]] = []
    questions: List[Dict[str, Any]] = []

    for p in parsed:
        if len(p.name) <= 1:
            continue

        if p.qty is None or p.unit is None:
            if len(questions) < 2:
                questions.append(
                    {
                        "field": "missing_amount",
                        "ask": f"「{p.name}」你吃了多少？给我一个数字+单位（如 200g / 250ml / 1碗 / 2个）",
                    }
                )
            continue

        r = lookup_food(p.name, p.qty, p.unit)
        if not r.get("ok"):
            if "question" in r and len(questions) < 2:
                questions.append(r["question"])
            elif "error" in r and len(questions) < 2:
                questions.append({"field": "api_error", "ask": r["error"]})
            continue

        items.append(r)

    totals = {
        "kcal": _round(sum(i["kcal"] for i in items)),
        "protein_g": _round(sum(i["protein_g"] for i in items)),
        "carb_g": _round(sum(i["carb_g"] for i in items)),
        "fat_g": _round(sum(i["fat_g"] for i in items)),
        "fiber_g": _round(sum(i["fiber_g"] for i in items)),
    }

    out = {
        "type": "meal_nutrition",
        "meal_type": meal_type,
        "items": items,
        "totals": totals,
        "questions": questions,
    }

    if items:
        cache_set(qkey, out, QUERY_TTL)
    return out
