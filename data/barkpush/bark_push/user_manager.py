from __future__ import annotations

from dataclasses import dataclass

from .config_manager import ConfigManager, ConfigError


class UserError(Exception):
    pass


@dataclass(frozen=True)
class ResolvedUsers:
    aliases: list[str]
    device_keys: list[str]


class UserManager:
    def __init__(self, config: ConfigManager) -> None:
        self._config = config

    def resolve(self, user_arg: str | None) -> ResolvedUsers:
        if not user_arg or not str(user_arg).strip():
            aliases = self._config.list_user_aliases()
            if not aliases:
                raise UserError("未配置任何用户，请先在 config.json 的 users 中添加用户别名")
            raise UserError(f"必须指定推送用户或 all，可选用户：{', '.join(aliases)}")

        raw = str(user_arg).strip()
        if raw.lower() == "all":
            aliases = self._config.list_user_aliases()
            if not aliases:
                raise UserError("未配置任何用户，无法推送 all")
            keys = [self._config.get_user_device_key(a) for a in aliases]
            return ResolvedUsers(aliases=aliases, device_keys=keys)

        parts = [p.strip() for p in raw.split(",") if p.strip()]
        if not parts:
            raise UserError("用户参数为空")

        aliases: list[str] = []
        keys: list[str] = []
        for p in parts:
            try:
                k = self._config.get_user_device_key(p)
            except ConfigError as e:
                raise UserError(str(e)) from e
            aliases.append(p)
            keys.append(k)

        return ResolvedUsers(aliases=aliases, device_keys=keys)
