from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .bark_api import BarkClient
from .config_manager import ConfigError, ConfigManager
from .content_parser import ContentParser, ContentType
from .history_manager import HistoryManager, HistoryError, new_history_record
from .user_manager import UserError, UserManager
from .utils import Preview, build_preview, compact_kv, new_push_id, to_bool


@dataclass(frozen=True)
class CommandResult:
    success: bool
    message: str
    data: dict[str, Any] | None = None

    def format_text(self) -> str:
        lines: list[str] = [self.message]
        if self.data:
            for k, v in self.data.items():
                lines.append(f"{k}：{v}")
        return "\n".join(lines)


class BarkPushService:
    def __init__(self, config_path: Path | None = None) -> None:
        self._config_mgr = ConfigManager(config_path=config_path)
        self._user_mgr = UserManager(self._config_mgr)
        self._content = ContentParser()
        history_path = self._config_mgr.state_dir / "history.json"
        self._history = HistoryManager(history_path=history_path, limit=self._config_mgr.config.history_limit)
        self._api = BarkClient(base_url=self._config_mgr.config.default_push_url)

    def list_users(self) -> CommandResult:
        aliases = self._config_mgr.list_user_aliases()
        return CommandResult(success=True, message="用户列表", data={"users": ", ".join(aliases) if aliases else "(空)"})

    def list_groups(self) -> CommandResult:
        groups = self._config_mgr.list_groups()
        return CommandResult(success=True, message="分组列表", data={"groups": ", ".join(groups) if groups else "(空)"})

    def list_history(self, limit: int = 20) -> CommandResult:
        records = self._history.list_recent(limit=limit)
        if not records:
            return CommandResult(success=True, message="历史记录为空")
        items = []
        for r in records:
            users = ",".join(r.user_aliases)
            items.append(f"{r.id} [{users}] {r.title}")
        return CommandResult(success=True, message="历史记录", data={"items": "\n".join(items)})

    def help(self) -> CommandResult:
        params = [
            "level：passive/active/time-sensitive/critical",
            "volume：0-10（critical 时生效）",
            "badge：角标数字",
            "call：1/0",
            "autoCopy：1/0",
            "copy：复制内容",
            "sound：铃声名称",
            "icon：图标 URL",
            "group：分组（需在配置 groups 中）",
            "isArchive：1/0",
            "action：none 或自定义动作字符串",
        ]
        return CommandResult(
            success=True,
            message="Bark Push 帮助",
            data={
                "用法": "bark-push --user <name|name1,name2|all> --content <文本|链接|图片> [--title 标题] [参数...]",
                "支持参数": "\n".join(params),
            },
        )

    def push(
        self,
        *,
        user: str | None,
        content: str | None,
        title: str | None,
        subtitle: str | None,
        group: str | None,
        update_id: str | None = None,
        delete_id: str | None = None,
        overrides: dict[str, Any] | None = None,
    ) -> CommandResult:
        try:
            users = self._user_mgr.resolve(user)
        except UserError as e:
            return self._error("推送指令错误", str(e), {}, Preview(kind="text", text=""))

        if update_id and not self._config_mgr.config.enable_update:
            return self._error("推送指令错误", "未启用更新功能（enable_update=false）", {}, Preview(kind="text", text=""))
        if delete_id and not self._config_mgr.config.enable_update:
            return self._error("推送指令错误", "未启用删除功能（enable_update=false）", {}, Preview(kind="text", text=""))

        target_id = update_id or delete_id
        if target_id:
            return self._push_update_or_delete(
                push_id=target_id,
                users=users,
                content=content,
                title=title,
                subtitle=subtitle,
                group=group,
                delete=bool(delete_id),
                overrides=overrides or {},
            )

        parsed = self._content.parse(content or "")
        auto_title, auto_subtitle = self._content.auto_title_subtitle(parsed)
        final_title = title if (title and title.strip()) else auto_title
        final_subtitle = subtitle if (subtitle and subtitle.strip()) else ("" if (title and title.strip()) else auto_subtitle)

        params = self._build_params(group=group, overrides=overrides or {})
        payload = self._build_payload(
            push_id=new_push_id(),
            title=final_title,
            subtitle=final_subtitle,
            parsed=parsed,
            params=params,
        )

        return self._send_to_users(users=users, push_id=payload["id"], payload=payload, parsed_params=params, parsed=parsed)

    def _push_update_or_delete(
        self,
        *,
        push_id: str,
        users: Any,
        content: str | None,
        title: str | None,
        subtitle: str | None,
        group: str | None,
        delete: bool,
        overrides: dict[str, Any],
    ) -> CommandResult:
        missing_users = [a for a in users.aliases if not self._history.has_user(push_id, a)]
        if missing_users:
            return CommandResult(
                success=False,
                message="未推送过这个消息",
                data={"id": push_id, "users": ", ".join(missing_users)},
            )

        parsed = self._content.parse(content or "")
        auto_title, auto_subtitle = self._content.auto_title_subtitle(parsed)
        final_title = title if (title and title.strip()) else auto_title
        final_subtitle = subtitle if (subtitle and subtitle.strip()) else ("" if (title and title.strip()) else auto_subtitle)

        params = self._build_params(group=group, overrides=overrides)
        payload = self._build_payload(
            push_id=push_id,
            title=final_title,
            subtitle=final_subtitle,
            parsed=parsed,
            params=params,
        )
        if delete:
            payload["delete"] = "1"

        result = self._send_to_users(users=users, push_id=push_id, payload=payload, parsed_params=params, parsed=parsed)
        if result.success and not delete:
            self._history.mark_updated(push_id)
        return result

    def _build_params(self, *, group: str | None, overrides: dict[str, Any]) -> dict[str, Any]:
        merged = self._config_mgr.merge_params(overrides)
        if group and group.strip():
            requested = group.strip()
            if self._config_mgr.is_group_valid(requested):
                merged["group"] = requested
        else:
            if not self._config_mgr.is_group_valid(str(merged.get("group", ""))):
                merged["group"] = self._config_mgr.config.defaults.group
        return self._normalize_params(merged)

    def _normalize_params(self, params: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for k, v in params.items():
            if k in {"call", "autoCopy", "isArchive"}:
                b = to_bool(v)
                if b is None:
                    continue
                out[k] = 1 if b else 0
            elif k in {"badge", "volume"}:
                try:
                    out[k] = int(v)
                except Exception:
                    continue
            else:
                out[k] = v
        return out

    def _build_payload(
        self,
        *,
        push_id: str,
        title: str,
        subtitle: str,
        parsed: Any,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"id": push_id, "title": title, "subtitle": subtitle}

        if parsed.content_type == ContentType.IMAGE_ONLY:
            payload["image"] = parsed.images[0] if parsed.images else ""
        elif parsed.content_type == ContentType.URL_ONLY:
            payload["url"] = parsed.urls[0] if parsed.urls else ""
        elif parsed.content_type == ContentType.TEXT_ONLY:
            payload["body"] = parsed.text
        else:
            payload["markdown"] = parsed.markdown or ""

        payload.update(params)
        return compact_kv(payload.items())

    def _send_to_users(
        self,
        *,
        users: Any,
        push_id: str,
        payload: dict[str, Any],
        parsed_params: dict[str, Any],
        parsed: Any,
    ) -> CommandResult:
        success_users: list[str] = []
        failed_users: list[str] = []
        errors: dict[str, str] = {}
        last_resp: dict[str, Any] | None = None

        for alias, device_key in zip(users.aliases, users.device_keys):
            single_payload = dict(payload)
            single_payload["device_key"] = device_key
            single_payload["_use_push_path"] = True
            resp = self._api.push_json(single_payload)
            last_resp = resp.data or last_resp
            if resp.ok:
                success_users.append(alias)
            else:
                failed_users.append(alias)
                errors[alias] = resp.error or "未知错误"

        status = "success"
        if failed_users and success_users:
            status = "partial_success"
        elif failed_users and not success_users:
            status = "failed"

        preview = build_preview(
            body=str(payload.get("body") or ""),
            markdown=str(payload.get("markdown") or "") if "markdown" in payload else None,
            url=str(payload.get("url") or "") if "url" in payload else None,
            image=str(payload.get("image") or "") if "image" in payload else None,
        )

        if self._config_mgr.config.enable_update:
            try:
                record = new_history_record(
                    push_id=push_id,
                    device_keys=list(users.device_keys),
                    user_aliases=list(users.aliases),
                    title=str(payload.get("title") or ""),
                    subtitle=str(payload.get("subtitle") or ""),
                    body=str(payload.get("body") or payload.get("markdown") or ""),
                    content_type=str(parsed.content_type.value),
                    parameters=parsed_params,
                    status=status,
                    success_count=len(success_users),
                    failed_count=len(failed_users),
                    failed_users=failed_users,
                    error_messages=errors,
                    bark_response=last_resp,
                )
                self._history.upsert(record)
            except (HistoryError, Exception):
                pass

        data = {
            "id": push_id,
            "成功用户": ", ".join(success_users) if success_users else "(无)",
            "失败用户": ", ".join(failed_users) if failed_users else "(无)",
            "解析参数": self._render_param_summary(parsed_params),
            "内容简略": preview.text,
        }
        if status == "success":
            return CommandResult(success=True, message="推送成功", data=data)
        if status == "partial_success":
            data["失败原因"] = self._render_errors(errors)
            return CommandResult(success=False, message="推送部分失败", data=data)
        data["失败原因"] = self._render_errors(errors)
        return CommandResult(success=False, message="推送失败", data=data)

    def _render_errors(self, errors: dict[str, str]) -> str:
        if not errors:
            return ""
        parts = []
        for k, v in errors.items():
            short = (v or "").strip().replace("\n", " ")
            parts.append(f"{k}: {short[:80]}")
        return "; ".join(parts)

    def _render_param_summary(self, params: dict[str, Any]) -> str:
        keys = ["level", "volume", "badge", "call", "autoCopy", "copy", "sound", "icon", "group", "isArchive", "action"]
        parts = []
        for k in keys:
            if k in params:
                parts.append(f"{k}={params[k]}")
        return ", ".join(parts)

    def _error(self, title: str, reason: str, params: dict[str, Any], preview: Preview) -> CommandResult:
        return CommandResult(
            success=False,
            message=f"{title}：{reason}",
            data={"解析参数": self._render_param_summary(params), "内容简略": preview.text},
        )


def handle_cli_args(args: Any) -> CommandResult:
    service = BarkPushService(config_path=Path(args.config).resolve() if getattr(args, "config", None) else None)

    if getattr(args, "list_users", False):
        return service.list_users()
    if getattr(args, "list_groups", False):
        return service.list_groups()
    if getattr(args, "list_history", False):
        return service.list_history(limit=int(getattr(args, "history_limit", 20) or 20))
    if getattr(args, "help", False):
        return service.help()

    def _empty_to_none(value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    overrides = {
        "level": _empty_to_none(getattr(args, "level", None)),
        "volume": _empty_to_none(getattr(args, "volume", None)),
        "badge": _empty_to_none(getattr(args, "badge", None)),
        "call": _empty_to_none(getattr(args, "call", None)),
        "autoCopy": _empty_to_none(getattr(args, "autoCopy", None)),
        "copy": _empty_to_none(getattr(args, "copy", None)),
        "sound": _empty_to_none(getattr(args, "sound", None)),
        "icon": _empty_to_none(getattr(args, "icon", None)),
        "isArchive": _empty_to_none(getattr(args, "isArchive", None)),
        "action": _empty_to_none(getattr(args, "action", None)),
        "ciphertext": _empty_to_none(getattr(args, "ciphertext", None)),
    }

    return service.push(
        user=getattr(args, "user", None),
        content=getattr(args, "content", None),
        title=getattr(args, "title", None),
        subtitle=getattr(args, "subtitle", None),
        group=getattr(args, "group", None),
        update_id=getattr(args, "update", None),
        delete_id=getattr(args, "delete", None),
        overrides=overrides,
    )
