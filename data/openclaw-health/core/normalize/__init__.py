from typing import Any, Dict, Optional


def _pick_best(*values):
    for v in values:
        if v is not None:
            return v
    return None


def normalize(date_str: str, sources: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Combine source payloads into a simplified normalized schema.

    Precedence order (first wins): whoop, oura, withings
    """
    order = ["whoop", "oura", "withings"]

    def s(name: str) -> Dict[str, Any]:
        return sources.get(name, {}) or {}

    sleep_total = _pick_best(
        s("whoop").get("sleep", {}).get("total_seconds"),
        s("oura").get("sleep", {}).get("total_seconds"),
        s("withings").get("sleep", {}).get("total_seconds"),
    )
    sleep_score = _pick_best(
        s("whoop").get("sleep", {}).get("score"),
        s("oura").get("sleep", {}).get("score"),
        s("withings").get("sleep", {}).get("score"),
    )

    steps = _pick_best(
        s("whoop").get("activity", {}).get("steps"),
        s("oura").get("activity", {}).get("steps"),
        s("withings").get("activity", {}).get("steps"),
    )
    calories = _pick_best(
        s("whoop").get("activity", {}).get("calories"),
        s("oura").get("activity", {}).get("calories"),
        s("withings").get("activity", {}).get("calories"),
    )
    minutes = _pick_best(
        s("whoop").get("activity", {}).get("minutes"),
        s("oura").get("activity", {}).get("minutes"),
        s("withings").get("activity", {}).get("minutes"),
    )

    resting_hr = _pick_best(
        s("whoop").get("resting_hr"),
        s("oura").get("resting_hr"),
        s("withings").get("resting_hr"),
    )
    hrv = _pick_best(
        s("whoop").get("hrv_rmssd"),
        s("oura").get("hrv_rmssd"),
        s("withings").get("hrv_rmssd"),
    )
    rr = _pick_best(
        s("whoop").get("respiratory_rate"),
        s("oura").get("respiratory_rate"),
    )
    spo2 = _pick_best(
        s("whoop").get("spo2"),
        s("oura").get("spo2"),
        s("withings").get("spo2"),
    )
    readiness = _pick_best(
        s("whoop").get("readiness", {}).get("score"),
        s("oura").get("readiness", {}).get("score"),
        s("withings").get("readiness", {}).get("score"),
    )
    weight = _pick_best(
        s("withings").get("weight_kg"),
    )
    body_fat = _pick_best(
        s("withings").get("body_fat_percent"),
    )

    norm = {
        "date": date_str,
        "sources": {k: v for k, v in sources.items() if v},
        "metrics": {
            "sleep": {"total_seconds": sleep_total, "score": sleep_score},
            "readiness": {"score": readiness},
            "activity": {"steps": steps, "calories": calories, "minutes": minutes},
            "resting_hr": resting_hr,
            "hrv_rmssd": hrv,
            "respiratory_rate": rr,
            "spo2": spo2,
            "weight_kg": weight,
            "body_fat_percent": body_fat,
        },
    }
    return norm

