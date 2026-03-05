from __future__ import annotations

import argparse
import ipaddress
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib import error, request

DEFAULT_BASE_URL = "http://localhost:8000"
MODE_CHOICES = ("download_only", "bidirectional", "upload_only")
UNIT_CHOICES = ("seconds", "hours", "days")


@dataclass(frozen=True)
class ApiResult:
    ok: bool
    status_code: int
    data: Any


def _normalize_base_url(base_url: str) -> str:
    value = base_url.strip().rstrip("/")
    return value or DEFAULT_BASE_URL


def _build_url(base_url: str, path: str) -> str:
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{_normalize_base_url(base_url)}{path}"


def _is_loopback_host(host: str) -> bool:
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def validate_base_url(base_url: str, allow_remote: bool = False) -> str:
    normalized = _normalize_base_url(base_url)
    parsed = urlparse(normalized)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("base_url 仅支持 http 或 https")

    host = parsed.hostname or ""
    if not host:
        raise ValueError("base_url 缺少有效主机名")

    if not allow_remote and not _is_loopback_host(host):
        raise ValueError(
            "默认仅允许 localhost/127.0.0.1/::1。"
            "如需连接远程地址，请显式传入 --allow-remote-base-url 并确认目标可信。"
        )

    return normalized


def _validate_hhmm(value: str) -> bool:
    parts = value.split(":")
    if len(parts) != 2:
        return False
    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError:
        return False
    return 0 <= hour <= 23 and 0 <= minute <= 59


def infer_md_sync_mode(sync_mode: str) -> str:
    if sync_mode == "download_only":
        return "download_only"
    return "enhanced"


def build_download_config_payload(value: float, unit: str, daily_time: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "download_interval_value": float(value),
        "download_interval_unit": unit,
    }
    if unit == "days":
        if not _validate_hhmm(daily_time):
            raise ValueError("daily_time 格式无效，必须为 HH:MM")
        payload["download_daily_time"] = daily_time
    return payload


def build_task_payload(
    *,
    name: str,
    local_path: str,
    cloud_folder_token: str,
    sync_mode: str,
    enabled: bool = True,
) -> dict[str, Any]:
    if sync_mode not in MODE_CHOICES:
        raise ValueError(f"sync_mode 不支持: {sync_mode}")
    if not local_path.strip():
        raise ValueError("local_path 不能为空")
    if not cloud_folder_token.strip():
        raise ValueError("cloud_folder_token 不能为空")
    return {
        "name": name.strip() or "OpenClaw-LarkSync 任务",
        "local_path": str(Path(local_path).expanduser()),
        "cloud_folder_token": cloud_folder_token.strip(),
        "sync_mode": sync_mode,
        "update_mode": "auto",
        "md_sync_mode": infer_md_sync_mode(sync_mode),
        "enabled": bool(enabled),
        "is_test": False,
    }


def _request_json(
    *,
    base_url: str,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    timeout: float = 15.0,
) -> ApiResult:
    data_bytes: bytes | None = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = request.Request(
        _build_url(base_url, path),
        data=data_bytes,
        headers=headers,
        method=method.upper(),
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            parsed = json.loads(raw) if raw else {}
            return ApiResult(ok=True, status_code=resp.getcode(), data=parsed)
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload_data = json.loads(body) if body else {"detail": body}
        except json.JSONDecodeError:
            payload_data = {"detail": body}
        return ApiResult(ok=False, status_code=exc.code, data=payload_data)
    except Exception as exc:  # noqa: BLE001
        return ApiResult(
            ok=False,
            status_code=0,
            data={"detail": f"{type(exc).__name__}: {exc}"},
        )


def _must_ok(result: ApiResult, action: str) -> Any:
    if result.ok:
        return result.data
    detail = result.data.get("detail") if isinstance(result.data, dict) else result.data
    raise RuntimeError(f"{action} 失败: HTTP {result.status_code} - {detail}")


def _find_existing_task(
    *, base_url: str, local_path: str, cloud_folder_token: str
) -> dict[str, Any] | None:
    result = _request_json(base_url=base_url, method="GET", path="/sync/tasks")
    if not result.ok or not isinstance(result.data, list):
        return None
    normalized_path = str(Path(local_path).expanduser())
    for item in result.data:
        if (
            isinstance(item, dict)
            and item.get("local_path") == normalized_path
            and item.get("cloud_folder_token") == cloud_folder_token
        ):
            return item
    return None


def do_check(base_url: str) -> dict[str, Any]:
    health = _request_json(base_url=base_url, method="GET", path="/health")
    auth = _request_json(base_url=base_url, method="GET", path="/auth/status")
    config = _request_json(base_url=base_url, method="GET", path="/config")
    tasks = _request_json(base_url=base_url, method="GET", path="/sync/tasks")
    task_count = len(tasks.data) if tasks.ok and isinstance(tasks.data, list) else 0
    connected = bool(auth.data.get("connected")) if auth.ok and isinstance(auth.data, dict) else False
    return {
        "base_url": _normalize_base_url(base_url),
        "health": {"ok": health.ok, "status_code": health.status_code, "data": health.data},
        "auth": {"ok": auth.ok, "status_code": auth.status_code, "data": auth.data},
        "config": {"ok": config.ok, "status_code": config.status_code, "data": config.data},
        "tasks": {"ok": tasks.ok, "status_code": tasks.status_code, "count": task_count, "data": tasks.data},
        "ready_for_sync": bool(health.ok and connected),
    }


def do_configure_download(base_url: str, value: float, unit: str, daily_time: str) -> dict[str, Any]:
    if unit not in UNIT_CHOICES:
        raise ValueError(f"download_unit 不支持: {unit}")
    payload = build_download_config_payload(value, unit, daily_time)
    updated = _must_ok(
        _request_json(base_url=base_url, method="PUT", path="/config", payload=payload),
        "更新下载策略",
    )
    return {"action": "configure-download", "payload": payload, "result": updated}


def do_create_task(
    *,
    base_url: str,
    name: str,
    local_path: str,
    cloud_folder_token: str,
    sync_mode: str,
) -> dict[str, Any]:
    payload = build_task_payload(
        name=name,
        local_path=local_path,
        cloud_folder_token=cloud_folder_token,
        sync_mode=sync_mode,
        enabled=True,
    )
    created = _request_json(base_url=base_url, method="POST", path="/sync/tasks", payload=payload)
    if created.ok:
        return {"action": "create-task", "created": True, "task": created.data}
    if created.status_code == 409:
        existing = _find_existing_task(
            base_url=base_url,
            local_path=local_path,
            cloud_folder_token=cloud_folder_token,
        )
        if existing:
            return {
                "action": "create-task",
                "created": False,
                "reason": "task_conflict_reused_existing",
                "task": existing,
                "detail": created.data,
            }
    detail = created.data.get("detail") if isinstance(created.data, dict) else created.data
    raise RuntimeError(f"创建任务失败: HTTP {created.status_code} - {detail}")


def do_run_task(base_url: str, task_id: str) -> dict[str, Any]:
    if not task_id.strip():
        raise ValueError("task_id 不能为空")
    status = _must_ok(
        _request_json(base_url=base_url, method="POST", path=f"/sync/tasks/{task_id}/run"),
        "执行任务",
    )
    return {"action": "run-task", "task_id": task_id, "status": status}


def do_bootstrap_daily(
    *,
    base_url: str,
    name: str,
    local_path: str,
    cloud_folder_token: str,
    sync_mode: str,
    download_value: float,
    download_unit: str,
    download_time: str,
    run_now: bool,
) -> dict[str, Any]:
    check_result = do_check(base_url)
    config_result = do_configure_download(
        base_url=base_url,
        value=download_value,
        unit=download_unit,
        daily_time=download_time,
    )
    task_result = do_create_task(
        base_url=base_url,
        name=name,
        local_path=local_path,
        cloud_folder_token=cloud_folder_token,
        sync_mode=sync_mode,
    )
    run_result: dict[str, Any] | None = None
    if run_now:
        task = task_result.get("task") or {}
        task_id = str(task.get("id", "")).strip()
        if task_id:
            run_result = do_run_task(base_url, task_id)
    return {
        "action": "bootstrap-daily",
        "check": check_result,
        "configure_download": config_result,
        "task": task_result,
        "run_now": run_result,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="OpenClaw x LarkSync skill helper: 低频同步与任务自动化"
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="LarkSync API 地址（默认仅允许 localhost）",
    )
    parser.add_argument(
        "--allow-remote-base-url",
        action="store_true",
        help="显式允许非 localhost 地址（存在令牌泄露风险，仅在可信网络使用）",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="检查 LarkSync 健康、授权与任务状态")

    cfg = sub.add_parser("configure-download", help="配置低频下载策略")
    cfg.add_argument("--download-value", type=float, default=1.0)
    cfg.add_argument("--download-unit", choices=UNIT_CHOICES, default="days")
    cfg.add_argument("--download-time", default="01:00", help="当 unit=days 时生效，格式 HH:MM")

    create = sub.add_parser("create-task", help="创建同步任务")
    create.add_argument("--name", default="OpenClaw-LarkSync 任务")
    create.add_argument("--local-path", required=True)
    create.add_argument("--cloud-folder-token", required=True)
    create.add_argument("--sync-mode", choices=MODE_CHOICES, default="download_only")

    run = sub.add_parser("run-task", help="立即执行任务")
    run.add_argument("--task-id", required=True)

    bootstrap = sub.add_parser("bootstrap-daily", help="一键配置每日低频同步并创建任务")
    bootstrap.add_argument("--name", default="OpenClaw-LarkSync 每日同步")
    bootstrap.add_argument("--local-path", required=True)
    bootstrap.add_argument("--cloud-folder-token", required=True)
    bootstrap.add_argument("--sync-mode", choices=MODE_CHOICES, default="download_only")
    bootstrap.add_argument("--download-value", type=float, default=1.0)
    bootstrap.add_argument("--download-unit", choices=UNIT_CHOICES, default="days")
    bootstrap.add_argument("--download-time", default="01:00")
    bootstrap.add_argument("--run-now", action="store_true", help="创建后立即触发一次同步")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        base_url = validate_base_url(
            args.base_url,
            allow_remote=bool(getattr(args, "allow_remote_base_url", False)),
        )
        if args.command == "check":
            result = do_check(base_url)
        elif args.command == "configure-download":
            result = do_configure_download(
                base_url=base_url,
                value=float(args.download_value),
                unit=str(args.download_unit),
                daily_time=str(args.download_time),
            )
        elif args.command == "create-task":
            result = do_create_task(
                base_url=base_url,
                name=str(args.name),
                local_path=str(args.local_path),
                cloud_folder_token=str(args.cloud_folder_token),
                sync_mode=str(args.sync_mode),
            )
        elif args.command == "run-task":
            result = do_run_task(base_url, str(args.task_id))
        elif args.command == "bootstrap-daily":
            result = do_bootstrap_daily(
                base_url=base_url,
                name=str(args.name),
                local_path=str(args.local_path),
                cloud_folder_token=str(args.cloud_folder_token),
                sync_mode=str(args.sync_mode),
                download_value=float(args.download_value),
                download_unit=str(args.download_unit),
                download_time=str(args.download_time),
                run_now=bool(args.run_now),
            )
        else:
            parser.error(f"未知命令: {args.command}")
            return 2
    except Exception as exc:  # noqa: BLE001
        print(
            json.dumps(
                {"ok": False, "error": f"{type(exc).__name__}: {exc}"},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
