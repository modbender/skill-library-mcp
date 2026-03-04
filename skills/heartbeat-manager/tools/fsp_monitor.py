#!/usr/bin/env python3
"""
Flight Schedule Pro 监控模块

从 FSP API 获取未来飞行预约，返回标准化事件。

API 文档: https://developer.flightschedulepro.com/
认证: x-subscription-key header
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path

import requests

logger = logging.getLogger("heartbeat.fsp")

CONFIG_DIR = Path(__file__).parent.parent / "config"
FSP_API_BASE = "https://api.flightschedulepro.com"


def _load_settings() -> dict:
    import yaml
    p = CONFIG_DIR / "settings.yaml"
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f).get("monitoring", {}).get("fsp", {})


def _load_credentials() -> tuple[str, str]:
    """
    返回 (api_token, operator_id)
    """
    from dotenv import dotenv_values
    env_path = CONFIG_DIR / ".env"
    if not env_path.exists():
        return "", ""
    values = dotenv_values(env_path)
    return (
        values.get("FSP_API_TOKEN", "").strip(),
        values.get("FSP_OPERATOR_ID", "").strip(),
    )


def is_configured() -> bool:
    """检查 FSP 凭证是否已配置"""
    settings = _load_settings()
    if not settings.get("enabled", True):
        return False
    api_token, operator_id = _load_credentials()
    return bool(api_token and operator_id)


def sync() -> list[dict]:
    """
    从 FSP API 获取未来飞行预约。

    返回:
        [{"id": "fsp-{id}", "date": "YYYY-MM-DD", "description": "飞行描述",
          "category": "飞行", "time": "HH:MM-HH:MM", "src": "fsp"}]

    如果凭证未配置或功能禁用，返回空列表。
    """
    settings = _load_settings()
    if not settings.get("enabled", True):
        logger.debug("FSP 监控已禁用")
        return []

    api_token, operator_id = _load_credentials()
    if not api_token or not operator_id:
        logger.warning(
            "FSP_API_TOKEN 或 FSP_OPERATOR_ID 未配置，跳过 FSP 同步。"
            "请在 config/.env 中配置。"
        )
        return []

    lookahead = settings.get("lookahead_days", 7)
    headers = {"x-subscription-key": api_token}
    timeout = 30

    events = []

    try:
        # 获取未来预约 (Scheduling API - Reservations)
        now = datetime.now()
        end = now + timedelta(days=lookahead)

        url = f"{FSP_API_BASE}/operators/{operator_id}/reservations"
        params = {
            "startTime": f"gte:{now.strftime('%Y-%m-%dT00:00:00')}",
            "endTime": f"lte:{end.strftime('%Y-%m-%dT23:59:59')}",
            "sortBy": "startTime",
            "limit": 100,
        }

        resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        resp.raise_for_status()
        reservations = resp.json()

        # FSP API 可能返回 list 或 {"data": list}
        if isinstance(reservations, dict):
            reservations = reservations.get("data", reservations.get("items", []))

        for res in reservations:
            event = _normalize_reservation(res)
            if event:
                events.append(event)

        logger.info("FSP: 获取到 %d 个预约", len(events))

    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 401:
            logger.error("FSP API 认证失败，请检查 FSP_API_TOKEN")
        elif e.response is not None and e.response.status_code == 403:
            logger.error("FSP API 权限不足，请检查 API 订阅和 OperatorId")
        else:
            logger.error("FSP API 请求失败: %s", e)
    except requests.RequestException as e:
        logger.error("FSP API 连接失败: %s", e)

    return events


def _normalize_reservation(res: dict) -> dict | None:
    """将 FSP 预约标准化为事件格式"""
    res_id = res.get("id") or res.get("reservationId")
    if not res_id:
        return None

    # 解析时间
    start_raw = res.get("startTime") or res.get("start")
    end_raw = res.get("endTime") or res.get("end")

    if not start_raw:
        return None

    try:
        start_dt = _parse_fsp_datetime(start_raw)
    except (ValueError, TypeError):
        logger.warning("FSP: 无法解析 startTime: %s", start_raw)
        return None

    end_str = ""
    if end_raw:
        try:
            end_dt = _parse_fsp_datetime(end_raw)
            end_str = f"-{end_dt.strftime('%H:%M')}"
        except (ValueError, TypeError):
            pass

    # 构建描述
    aircraft = res.get("aircraftName") or res.get("aircraft", {}).get("name", "")
    aircraft_tail = res.get("tailNumber") or res.get("aircraft", {}).get("tailNumber", "")
    instructor = res.get("instructorName") or ""
    location = res.get("location") or res.get("airport") or ""
    res_type = res.get("type") or res.get("reservationType") or "飞行训练"

    parts = []
    if aircraft:
        parts.append(aircraft)
    elif aircraft_tail:
        parts.append(aircraft_tail)
    if res_type and res_type not in ("Flight", "飞行训练"):
        parts.append(res_type)
    else:
        parts.append("飞行训练")
    if location:
        parts.append(location)

    description = " ".join(parts) if parts else "FSP 预约"

    return {
        "id": f"fsp-{res_id}",
        "date": start_dt.strftime("%Y-%m-%d"),
        "description": description,
        "category": "飞行",
        "time": f"{start_dt.strftime('%H:%M')}{end_str}",
        "src": "fsp",
    }


def _parse_fsp_datetime(raw: str) -> datetime:
    """解析 FSP 的时间格式（ISO 8601）"""
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    return dt.astimezone().replace(tzinfo=None)  # 转本地时间


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = sync()
    for r in results:
        print(f"  {r['date']} | {r['description']} | [{r['category']}] @time:{r['time']} @src:{r['src']} @id:{r['id']}")
    if not results:
        print("  (无结果 - 请检查 FSP_API_TOKEN 和 FSP_OPERATOR_ID 配置)")
