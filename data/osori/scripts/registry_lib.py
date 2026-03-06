#!/usr/bin/env python3
"""Registry utilities for Osori.

Supports:
- Legacy array registry format (v0)
- Versioned object registry format (v1+)
- Automatic migration to current schema/version
- Atomic writes with backup + rollback fallback
"""

from __future__ import annotations

import copy
import datetime as dt
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

REGISTRY_SCHEMA = "osori.registry"
REGISTRY_VERSION = 2


@dataclass
class LoadResult:
    registry: Dict[str, Any]
    migrated: bool
    migration_notes: List[str]
    backup_path: str | None = None


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _local_today() -> str:
    return dt.date.today().isoformat()


def _default_roots() -> List[Dict[str, Any]]:
    return [{"key": "default", "label": "Default", "paths": []}]


def _empty_registry() -> Dict[str, Any]:
    return {
        "schema": REGISTRY_SCHEMA,
        "version": REGISTRY_VERSION,
        "updatedAt": _utc_now_iso(),
        "roots": _default_roots(),
        "projects": [],
        "aliases": {},
    }


def _normalize_tags(value: Any) -> List[str]:
    if isinstance(value, list):
        tags = [str(v).strip() for v in value if str(v).strip()]
        # stable de-dup
        deduped: List[str] = []
        seen = set()
        for t in tags:
            if t in seen:
                continue
            seen.add(t)
            deduped.append(t)
        return deduped
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def normalize_project(item: Any) -> Dict[str, Any] | None:
    if not isinstance(item, dict):
        return None

    name = str(item.get("name", "")).strip()
    path = str(item.get("path", "")).strip()
    if not name or not path:
        return None

    proj = {
        "name": name,
        "path": path,
        "repo": str(item.get("repo", "") or ""),
        "lang": str(item.get("lang", "unknown") or "unknown"),
        "tags": _normalize_tags(item.get("tags", [])),
        "description": str(item.get("description", "") or ""),
        "addedAt": str(item.get("addedAt") or _local_today()),
        "root": str(item.get("root", "default") or "default"),
        "favorite": bool(item.get("favorite", False)),
    }
    return proj


def _normalize_roots(value: Any) -> List[Dict[str, Any]]:
    roots: List[Dict[str, Any]] = []
    seen = set()

    if isinstance(value, list):
        for r in value:
            if not isinstance(r, dict):
                continue
            key = str(r.get("key", "")).strip() or "default"
            if key in seen:
                continue
            seen.add(key)
            label = str(r.get("label", "")).strip() or key.title()
            paths_raw = r.get("paths", [])
            paths = [str(p) for p in paths_raw if isinstance(p, str)] if isinstance(paths_raw, list) else []
            roots.append({"key": key, "label": label, "paths": paths})

    if "default" not in seen:
        roots.insert(0, {"key": "default", "label": "Default", "paths": []})
    return roots


def _migrate_legacy_array(payload: List[Any]) -> Tuple[Dict[str, Any], List[str]]:
    reg = _empty_registry()
    projects = []
    for item in payload:
        p = normalize_project(item)
        if p:
            projects.append(p)
    reg["projects"] = projects
    reg["updatedAt"] = _utc_now_iso()
    return reg, ["legacy-array -> v2"]


def _migrate_object(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    notes: List[str] = []

    reg = copy.deepcopy(payload)

    # schema/version defaults
    original_schema = reg.get("schema")
    if original_schema != REGISTRY_SCHEMA:
        notes.append(f"schema normalized ({original_schema!r} -> {REGISTRY_SCHEMA!r})")
        reg["schema"] = REGISTRY_SCHEMA

    try:
        version = int(reg.get("version", 1))
    except Exception:
        version = 1

    # normalize projects container
    raw_projects = reg.get("projects")
    if raw_projects is None:
        raw_projects = []
    if not isinstance(raw_projects, list):
        raw_projects = []
        notes.append("projects field normalized to []")

    projects = []
    for item in raw_projects:
        p = normalize_project(item)
        if p:
            projects.append(p)

    reg["projects"] = projects

    # normalize roots
    reg["roots"] = _normalize_roots(reg.get("roots"))
    root_keys = {r["key"] for r in reg["roots"]}
    for p in reg["projects"]:
        proj_root = p.get("root", "default") or "default"
        if proj_root not in root_keys:
            reg["roots"].append({"key": proj_root, "label": proj_root.title(), "paths": []})
            root_keys.add(proj_root)

    # normalize aliases
    reg["aliases"] = registry_aliases(reg)

    if version < REGISTRY_VERSION:
        notes.append(f"version migration v{version} -> v{REGISTRY_VERSION}")
        reg["version"] = REGISTRY_VERSION
    else:
        reg["version"] = version

    reg["updatedAt"] = _utc_now_iso()
    return reg, notes


def migrate_registry_payload(payload: Any) -> Tuple[Dict[str, Any], List[str]]:
    if isinstance(payload, list):
        return _migrate_legacy_array(payload)
    if isinstance(payload, dict):
        return _migrate_object(payload)
    raise ValueError("Unsupported registry format (expected list or object)")


def _timestamp_suffix() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def save_registry(path: str, registry: Dict[str, Any], make_backup: bool = True) -> str | None:
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)

    reg_copy = copy.deepcopy(registry)
    reg_copy.setdefault("schema", REGISTRY_SCHEMA)
    reg_copy.setdefault("version", REGISTRY_VERSION)
    reg_copy.setdefault("roots", _default_roots())
    reg_copy.setdefault("projects", [])
    reg_copy.setdefault("aliases", {})
    reg_copy["updatedAt"] = _utc_now_iso()

    backup_path: str | None = None
    tmp_path = None

    try:
        if make_backup and p.exists():
            backup_path = f"{p}.bak-{_timestamp_suffix()}"
            shutil.copy2(p, backup_path)

        fd, tmp_path = tempfile.mkstemp(prefix=".osori-registry-", suffix=".tmp", dir=str(p.parent))
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(reg_copy, f, indent=2, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())

        os.replace(tmp_path, p)
        tmp_path = None
        return backup_path

    except Exception:
        # rollback fallback
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, p)
        raise


def _handle_corruption(path: str) -> Tuple[Dict[str, Any], List[str], str | None]:
    p = Path(path).expanduser()
    notes = ["registry corrupted: initialized empty v2"]
    backup_path = None

    if p.exists():
        broken = f"{p}.broken-{_timestamp_suffix()}"
        shutil.copy2(p, broken)
        notes.append(f"corrupted backup saved: {broken}")

    reg = _empty_registry()
    backup_path = save_registry(str(p), reg, make_backup=True)
    return reg, notes, backup_path


def load_registry(path: str, auto_migrate: bool = True, make_backup_on_migrate: bool = True) -> LoadResult:
    p = Path(path).expanduser()

    if not p.exists():
        reg = _empty_registry()
        save_registry(str(p), reg, make_backup=False)
        return LoadResult(registry=reg, migrated=True, migration_notes=["registry created (v2)"], backup_path=None)

    try:
        with p.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception:
        reg, notes, backup = _handle_corruption(str(p))
        return LoadResult(registry=reg, migrated=True, migration_notes=notes, backup_path=backup)

    migrated_registry, notes = migrate_registry_payload(payload)

    migrated = bool(notes)
    backup_path = None

    if auto_migrate and migrated:
        backup_path = save_registry(str(p), migrated_registry, make_backup=make_backup_on_migrate)

    return LoadResult(
        registry=migrated_registry,
        migrated=migrated,
        migration_notes=notes,
        backup_path=backup_path,
    )


def registry_projects(registry: Dict[str, Any]) -> List[Dict[str, Any]]:
    projects = registry.get("projects", [])
    if not isinstance(projects, list):
        return []
    return projects


def registry_roots(registry: Dict[str, Any]) -> List[Dict[str, Any]]:
    return _normalize_roots(registry.get("roots", []))


def normalize_root_key(root_key: str | None) -> str | None:
    if root_key is None:
        return None
    key = str(root_key).strip()
    if not key:
        return None
    if key in {"all", "*"}:
        return None
    return key


def _normalize_alias_key(alias: str | None) -> str:
    if alias is None:
        return ""
    return str(alias).strip().lower()


def registry_aliases(registry: Dict[str, Any]) -> Dict[str, str]:
    raw = registry.get("aliases", {})
    if not isinstance(raw, dict):
        return {}

    out: Dict[str, str] = {}
    for k, v in raw.items():
        key = _normalize_alias_key(str(k))
        if not key:
            continue
        if not isinstance(v, str):
            continue
        target = v.strip()
        if not target:
            continue
        out[key] = target
    return out


def set_registry_aliases(registry: Dict[str, Any], aliases: Dict[str, str]) -> None:
    normalized = {}
    for k, v in aliases.items():
        key = _normalize_alias_key(k)
        target = str(v).strip()
        if not key or not target:
            continue
        normalized[key] = target
    registry["aliases"] = normalized
    registry["updatedAt"] = _utc_now_iso()


def resolve_alias(name_or_alias: str, registry: Dict[str, Any]) -> str:
    aliases = registry_aliases(registry)
    key = _normalize_alias_key(name_or_alias)
    if key in aliases:
        return aliases[key]
    return name_or_alias


def parse_env_search_paths(paths_env: str | None) -> List[str]:
    if not paths_env:
        return []
    return [p.strip() for p in str(paths_env).split(":") if p.strip()]


def search_paths_for_discovery(registry: Dict[str, Any], root_key: str | None = None, env_paths: str | None = None) -> List[str]:
    rk = normalize_root_key(root_key)
    roots = registry_roots(registry)

    ordered: List[str] = []

    if rk:
        for r in roots:
            if r.get("key") == rk:
                ordered.extend([p for p in r.get("paths", []) if isinstance(p, str) and p.strip()])
                break
    else:
        for r in roots:
            ordered.extend([p for p in r.get("paths", []) if isinstance(p, str) and p.strip()])

    ordered.extend(parse_env_search_paths(env_paths))

    # stable de-dup
    deduped: List[str] = []
    seen = set()
    for p in ordered:
        if p in seen:
            continue
        seen.add(p)
        deduped.append(p)

    return deduped


def filter_projects(projects: List[Dict[str, Any]], root_key: str | None = None, name_query: str | None = None) -> List[Dict[str, Any]]:
    selected = projects

    rk = normalize_root_key(root_key)
    if rk:
        selected = [p for p in selected if str(p.get("root", "default")) == rk]

    q = (name_query or "").strip().lower()
    if q:
        selected = [p for p in selected if q in str(p.get("name", "")).lower()]

    return selected


def ensure_root_exists(registry: Dict[str, Any], root_key: str | None) -> str:
    key = normalize_root_key(root_key) or "default"
    roots = registry_roots(registry)
    existing = {r.get("key") for r in roots}
    if key not in existing:
        roots.append({"key": key, "label": key.title(), "paths": []})
    registry["roots"] = roots
    return key


def set_registry_projects(registry: Dict[str, Any], projects: List[Dict[str, Any]]) -> None:
    registry["projects"] = projects
    registry["updatedAt"] = _utc_now_iso()


def parse_repo_from_remote(remote_url: str) -> str:
    # Supports both https://github.com/owner/repo(.git) and git@github.com:owner/repo.git
    if not remote_url:
        return ""
    url = remote_url.strip()

    marker = "github.com"
    if marker not in url:
        return ""

    # Normalize separator after domain to '/'
    after = url.split(marker, 1)[1]
    after = after.lstrip(":/")
    if after.endswith(".git"):
        after = after[:-4]

    parts = after.split("/")
    if len(parts) < 2:
        return ""

    owner, repo = parts[0], parts[1]
    if not owner or not repo:
        return ""
    return f"{owner}/{repo}"
