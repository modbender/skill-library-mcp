from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BarkDefaults:
    level: str = "active"
    volume: int = 10
    badge: int = 1
    call: bool = False
    autoCopy: bool = False
    copy: str = ""
    sound: str = "bell"
    icon: str = ""
    group: str = "default"
    isArchive: bool = True
    action: str = ""


@dataclass(frozen=True)
class BarkConfig:
    default_push_url: str
    users: dict[str, str]
    defaults: BarkDefaults
    groups: list[str]
    history_limit: int
    enable_update: bool
    ciphertext: str


class ConfigError(Exception):
    pass


class ConfigManager:
    def __init__(self, config_path: Path | None = None, state_dir: Path | None = None) -> None:
        self._state_dir = state_dir or self._default_state_dir()
        self._config_path = config_path or self._resolve_config_path()
        self._config = self._load_or_create(self._config_path)

    @property
    def state_dir(self) -> Path:
        return self._state_dir

    @property
    def config_path(self) -> Path:
        return self._config_path

    @property
    def config(self) -> BarkConfig:
        return self._config

    def get_user_device_key(self, alias_or_key: str) -> str:
        key = alias_or_key.strip()
        if not key:
            raise ConfigError("用户不能为空")
        mapped = self._config.users.get(key)
        if mapped:
            return mapped
        if self._config.users:
            device_keys = {v for v in self._config.users.values()}
            if key in device_keys:
                raise ConfigError("禁止直接传入 device_key，请使用用户别名")
        if self._config.users:
            aliases = ", ".join(sorted(self._config.users.keys()))
            raise ConfigError(f"未找到用户别名：{key}，可选用户：{aliases}")
        raise ConfigError("未配置任何用户，请先在 config.json 的 users 中添加用户别名")

    def list_user_aliases(self) -> list[str]:
        return sorted(self._config.users.keys())

    def list_groups(self) -> list[str]:
        return list(self._config.groups)

    def is_group_valid(self, group: str) -> bool:
        return group in set(self._config.groups)

    def merge_params(self, overrides: dict[str, Any]) -> dict[str, Any]:
        base = {
            "level": self._config.defaults.level,
            "volume": self._config.defaults.volume,
            "badge": self._config.defaults.badge,
            "call": self._config.defaults.call,
            "autoCopy": self._config.defaults.autoCopy,
            "copy": self._config.defaults.copy,
            "sound": self._config.defaults.sound,
            "icon": self._config.defaults.icon,
            "group": self._config.defaults.group,
            "ciphertext": self._config.ciphertext,
            "isArchive": self._config.defaults.isArchive,
            "action": self._config.defaults.action,
        }
        for k, v in overrides.items():
            if v is None:
                continue
            base[k] = v
        return base

    def _default_state_dir(self) -> Path:
        env = os.environ.get("BARK_PUSH_STATE_DIR", "").strip()
        if env:
            return Path(env).expanduser().resolve()
        return (Path.home() / ".bark-push").resolve()

    def _resolve_config_path(self) -> Path:
        env = os.environ.get("BARK_PUSH_CONFIG", "").strip()
        if env:
            return Path(env).expanduser().resolve()
        cwd_candidate = Path.cwd() / "config.json"
        if cwd_candidate.exists():
            return cwd_candidate.resolve()
        nested_candidate = Path.cwd() / "config" / "config.json"
        if nested_candidate.exists():
            return nested_candidate.resolve()
        home_candidate = self._state_dir / "config.json"
        return home_candidate.resolve()

    def _load_or_create(self, path: Path) -> BarkConfig:
        self._state_dir.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            self._write_default_config(path)
        raw = self._read_json(path)
        return self._parse_config(raw)

    def _read_json(self, path: Path) -> dict[str, Any]:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as e:
            raise ConfigError(f"配置文件不存在：{path}") from e
        except json.JSONDecodeError as e:
            raise ConfigError(f"配置文件格式错误：{path}，{e}") from e
        except OSError as e:
            raise ConfigError(f"读取配置文件失败：{path}，{e}") from e

    def _write_default_config(self, path: Path) -> None:
        default = {
            "default_push_url": "https://api.day.app",
            "users": {},
            "ciphertext": "",
            "defaults": {
                "level": "active",
                "volume": 10,
                "badge": 1,
                "sound": "bell",
                "icon": "",
                "group": "default",
                "call": False,
                "autoCopy": False,
                "copy": "",
                "isArchive": True,
                "action": "",
            },
            "groups": ["default"],
            "history_limit": 100,
            "enable_update": True,
        }
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(default, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as e:
            raise ConfigError(f"创建默认配置失败：{path}，{e}") from e

    def _parse_config(self, raw: dict[str, Any]) -> BarkConfig:
        # 优先读取环境变量中的敏感信息
        env_users_json = os.environ.get("BARK_USERS")
        if env_users_json:
            try:
                env_users = json.loads(env_users_json)
                if isinstance(env_users, dict):
                    current_users = raw.get("users", {})
                    if not isinstance(current_users, dict):
                        current_users = {}
                    current_users.update(env_users)
                    raw["users"] = current_users
            except json.JSONDecodeError:
                pass  # 忽略格式错误的环境变量

        env_ciphertext = os.environ.get("BARK_CIPHERTEXT")
        if env_ciphertext:
            raw["ciphertext"] = env_ciphertext

        def _require_str(source: dict[str, Any], name: str, default: str = "") -> str:
            if name in source and not isinstance(source.get(name), str):
                raise ConfigError(f"配置 {name} 必须为字符串")
            return str(source.get(name, default)).strip()

        def _require_bool(source: dict[str, Any], name: str, default: bool) -> bool:
            if name in source and not isinstance(source.get(name), bool):
                raise ConfigError(f"配置 {name} 必须为布尔值")
            return bool(source.get(name, default))

        def _require_int(source: dict[str, Any], name: str, default: int) -> int:
            if name in source:
                value = source.get(name)
                if not isinstance(value, int) or isinstance(value, bool):
                    raise ConfigError(f"配置 {name} 必须为整数")
                return int(value)
            return int(default)

        default_push_url = _require_str(raw, "default_push_url", "https://api.day.app") or "https://api.day.app"
        users = raw.get("users", {}) or {}
        if not isinstance(users, dict):
            raise ConfigError("配置 users 必须为对象")
        users_map: dict[str, str] = {}
        for k, v in users.items():
            if not isinstance(v, str):
                raise ConfigError("配置 users 的值必须为字符串")
            users_map[str(k)] = v

        ciphertext = _require_str(raw, "ciphertext", "")

        defaults_raw = raw.get("defaults", {}) or {}
        if not isinstance(defaults_raw, dict):
            raise ConfigError("配置 defaults 必须为对象")
        level = _require_str(defaults_raw, "level", "active")
        volume = _require_int(defaults_raw, "volume", 10)
        badge = _require_int(defaults_raw, "badge", 1)
        call = _require_bool(defaults_raw, "call", False)
        auto_copy = _require_bool(defaults_raw, "autoCopy", False)
        copy = _require_str(defaults_raw, "copy", "")
        sound = _require_str(defaults_raw, "sound", "bell")
        icon = _require_str(defaults_raw, "icon", "")
        group = _require_str(defaults_raw, "group", "default")
        is_archive = _require_bool(defaults_raw, "isArchive", True)
        action = _require_str(defaults_raw, "action", "")
        defaults = BarkDefaults(
            level=level,
            volume=volume,
            badge=badge,
            call=call,
            autoCopy=auto_copy,
            copy=copy,
            sound=sound,
            icon=icon,
            group=group,
            isArchive=is_archive,
            action=action,
        )

        groups_raw = raw.get("groups", None)
        if groups_raw is None:
            groups = [defaults.group]
        elif isinstance(groups_raw, list):
            groups = [str(x) for x in groups_raw if str(x).strip()]
        else:
            raise ConfigError("配置 groups 必须为数组")
        if not groups:
            raise ConfigError("配置 groups 不能为空")
        if defaults.group not in groups:
            groups = [defaults.group] + groups

        history_limit = _require_int(raw, "history_limit", 100)
        if history_limit <= 0:
            raise ConfigError("配置 history_limit 必须为正整数")

        enable_update = _require_bool(raw, "enable_update", True)

        return BarkConfig(
            default_push_url=default_push_url,
            users=users_map,
            defaults=defaults,
            groups=groups,
            history_limit=history_limit,
            enable_update=enable_update,
            ciphertext=ciphertext,
        )
