"""
Feishu wiki/doc publisher for video analysis results.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import os
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class FeishuPublishError(RuntimeError):
    """Raised when publishing to Feishu fails."""


@dataclass
class FeishuCredentials:
    """Resolved Feishu app credentials and API domain."""

    app_id: str
    app_secret: str
    domain: str


class FeishuPublisher:
    """Publish markdown content to a Feishu wiki doc."""

    _UNSUPPORTED_BLOCK_TYPES = {32}

    def __init__(
        self,
        *,
        space_id: Optional[str],
        parent_node_token: Optional[str],
        config_path: Optional[str] = None,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        domain: Optional[str] = None,
        openclaw_config_path: Optional[str] = None,
        timeout_seconds: float = 30.0,
    ):
        self.space_id = (space_id or "").strip()
        self.parent_node_token = (parent_node_token or "").strip()
        self.config_path = Path(config_path).resolve() if config_path else None
        self.app_id = (app_id or "").strip()
        self.app_secret = (app_secret or "").strip()
        self.domain = (domain or "").strip()
        self.openclaw_config_path = (
            Path(openclaw_config_path).resolve() if openclaw_config_path else None
        )
        self.timeout_seconds = timeout_seconds

        self._tenant_access_token: Optional[str] = None

    def publish(self, *, video_title: str, markdown_content: str) -> Dict[str, Any]:
        """Create a wiki doc with video title and write markdown content into it."""
        title = (video_title or "").strip()
        if not title:
            raise FeishuPublishError("video_title is empty, cannot create Feishu doc")

        content = (markdown_content or "").strip()
        if not content:
            raise FeishuPublishError("markdown content is empty, cannot publish")

        space_id, parent_node_token = self._resolve_target_location()
        credentials = self._resolve_credentials()
        api_base = self._domain_to_api_base(credentials.domain)

        token = self._get_tenant_access_token(
            api_base=api_base,
            app_id=credentials.app_id,
            app_secret=credentials.app_secret,
        )

        node = self._create_wiki_doc(
            api_base=api_base,
            access_token=token,
            space_id=space_id,
            parent_node_token=parent_node_token,
            title=title,
        )

        doc_token = str(node.get("obj_token") or "").strip()
        if not doc_token:
            raise FeishuPublishError("Failed to get doc token from wiki create response")

        write_result = self._write_doc_markdown(
            api_base=api_base,
            access_token=token,
            doc_token=doc_token,
            markdown=content,
        )

        return {
            "enabled": True,
            "success": True,
            "space_id": space_id,
            "parent_node_token": parent_node_token,
            "node_token": node.get("node_token"),
            "doc_token": doc_token,
            "doc_url": self._doc_url(credentials.domain, doc_token),
            "write": write_result,
        }

    def _resolve_target_location(self) -> Tuple[str, str]:
        """Resolve target wiki space/parent from args > env > skill config."""
        config_space = ""
        config_parent = ""

        if self.config_path and self.config_path.exists():
            try:
                cfg = json.loads(self.config_path.read_text(encoding="utf-8"))
                feishu_cfg = cfg.get("feishu", {}) if isinstance(cfg, dict) else {}
                if isinstance(feishu_cfg, dict):
                    config_space = str(feishu_cfg.get("space_id") or "").strip()
                    config_parent = str(feishu_cfg.get("parent_node_token") or "").strip()
            except Exception:
                # Do not block analysis for config parsing issues.
                pass

        space_id = (
            self.space_id
            or os.getenv("FEISHU_SPACE_ID", "").strip()
            or config_space
        )
        parent_node_token = (
            self.parent_node_token
            or os.getenv("FEISHU_PARENT_NODE_TOKEN", "").strip()
            or config_parent
        )

        if not space_id:
            raise FeishuPublishError(
                "Missing Feishu space_id. Provide feishu_space_id parameter, "
                "FEISHU_SPACE_ID env, or config.json feishu.space_id"
            )

        if not parent_node_token:
            raise FeishuPublishError(
                "Missing Feishu parent_node_token. Provide feishu_parent_node_token "
                "parameter, FEISHU_PARENT_NODE_TOKEN env, or config.json "
                "feishu.parent_node_token"
            )

        return space_id, parent_node_token

    def _resolve_credentials(self) -> FeishuCredentials:
        """Resolve app credentials from args > env > openclaw.json."""
        app_id = self.app_id or os.getenv("FEISHU_APP_ID", "").strip()
        app_secret = self.app_secret or os.getenv("FEISHU_APP_SECRET", "").strip()
        domain = self.domain or os.getenv("FEISHU_DOMAIN", "").strip()

        if not app_id or not app_secret or not domain:
            ocfg = self._read_openclaw_feishu_config()
            app_id = app_id or str(ocfg.get("appId") or "").strip()
            app_secret = app_secret or str(ocfg.get("appSecret") or "").strip()
            domain = domain or str(ocfg.get("domain") or "").strip()

        if not app_id or not app_secret:
            raise FeishuPublishError(
                "Missing Feishu app credentials. Set FEISHU_APP_ID/FEISHU_APP_SECRET "
                "or configure channels.feishu.appId/appSecret in openclaw.json"
            )

        return FeishuCredentials(
            app_id=app_id,
            app_secret=app_secret,
            domain=domain or "feishu",
        )

    def _read_openclaw_feishu_config(self) -> Dict[str, Any]:
        """Best-effort parse Feishu account settings from openclaw.json."""
        cfg_path = self.openclaw_config_path or self._default_openclaw_config_path()
        if not cfg_path.exists():
            return {}

        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

        channels = data.get("channels", {}) if isinstance(data, dict) else {}
        feishu_cfg = channels.get("feishu", {}) if isinstance(channels, dict) else {}
        if not isinstance(feishu_cfg, dict):
            return {}

        merged: Dict[str, Any] = dict(feishu_cfg)
        accounts = feishu_cfg.get("accounts")
        if isinstance(accounts, dict) and accounts:
            preferred_account = os.getenv("FEISHU_ACCOUNT_ID", "").strip()
            account_cfg = accounts.get(preferred_account)
            if not isinstance(account_cfg, dict):
                first_key = next(iter(accounts.keys()))
                account_cfg = accounts.get(first_key)
            if isinstance(account_cfg, dict):
                merged.update(account_cfg)

        return merged

    @staticmethod
    def _default_openclaw_config_path() -> Path:
        openclaw_home = os.getenv("OPENCLAW_HOME", "").strip()
        if openclaw_home:
            return Path(openclaw_home).expanduser().resolve() / "openclaw.json"
        return Path.home().resolve() / ".openclaw" / "openclaw.json"

    @staticmethod
    def _domain_to_api_base(domain: str) -> str:
        value = (domain or "feishu").strip().lower().rstrip("/")
        if value.startswith("http://") or value.startswith("https://"):
            return value
        if value == "lark":
            return "https://open.larksuite.com"
        return "https://open.feishu.cn"

    @staticmethod
    def _doc_url(domain: str, doc_token: str) -> str:
        domain_value = (domain or "feishu").strip().lower()
        if domain_value == "lark":
            return f"https://www.larksuite.com/docx/{doc_token}"
        return f"https://feishu.cn/docx/{doc_token}"

    def _get_tenant_access_token(self, *, api_base: str, app_id: str, app_secret: str) -> str:
        if self._tenant_access_token:
            return self._tenant_access_token

        data = self._request_json(
            method="POST",
            url=f"{api_base}/open-apis/auth/v3/tenant_access_token/internal",
            payload={"app_id": app_id, "app_secret": app_secret},
            access_token=None,
        )

        token = str(data.get("tenant_access_token") or "").strip()
        if not token:
            raise FeishuPublishError("Failed to get tenant_access_token")

        self._tenant_access_token = token
        return token

    def _create_wiki_doc(
        self,
        *,
        api_base: str,
        access_token: str,
        space_id: str,
        parent_node_token: str,
        title: str,
    ) -> Dict[str, Any]:
        data = self._request_json(
            method="POST",
            url=(
                f"{api_base}/open-apis/wiki/v2/spaces/"
                f"{quote(space_id, safe='')}/nodes"
            ),
            payload={
                "obj_type": "docx",
                "node_type": "origin",
                "title": title,
                "parent_node_token": parent_node_token,
            },
            access_token=access_token,
        )

        node = data.get("node") if isinstance(data, dict) else None
        if not isinstance(node, dict):
            raise FeishuPublishError("Invalid wiki create response: missing node")
        return node

    def _write_doc_markdown(
        self,
        *,
        api_base: str,
        access_token: str,
        doc_token: str,
        markdown: str,
    ) -> Dict[str, Any]:
        deleted = self._clear_document_content(
            api_base=api_base,
            access_token=access_token,
            doc_token=doc_token,
        )

        blocks, first_level_ids = self._convert_markdown_to_blocks(
            api_base=api_base,
            access_token=access_token,
            markdown=markdown,
        )
        if not blocks:
            return {
                "success": True,
                "blocks_deleted": deleted,
                "blocks_added": 0,
                "skipped_block_types": [],
            }

        sorted_blocks = self._sort_blocks_by_first_level(blocks, first_level_ids)
        cleaned_blocks, skipped = self._clean_blocks_for_insert(sorted_blocks)

        if not cleaned_blocks:
            return {
                "success": True,
                "blocks_deleted": deleted,
                "blocks_added": 0,
                "skipped_block_types": skipped,
            }

        inserted = self._insert_blocks(
            api_base=api_base,
            access_token=access_token,
            doc_token=doc_token,
            blocks=cleaned_blocks,
        )

        return {
            "success": True,
            "blocks_deleted": deleted,
            "blocks_added": len(inserted),
            "skipped_block_types": skipped,
        }

    def _clear_document_content(
        self,
        *,
        api_base: str,
        access_token: str,
        doc_token: str,
    ) -> int:
        blocks = self._list_all_blocks(
            api_base=api_base,
            access_token=access_token,
            doc_token=doc_token,
        )

        top_level_count = 0
        for block in blocks:
            if str(block.get("parent_id") or "") == doc_token and block.get("block_type") != 1:
                top_level_count += 1

        if top_level_count == 0:
            return 0

        self._request_json(
            method="DELETE",
            url=(
                f"{api_base}/open-apis/docx/v1/documents/{quote(doc_token, safe='')}/"
                f"blocks/{quote(doc_token, safe='')}/children/batch_delete"
            ),
            payload={"start_index": 0, "end_index": top_level_count},
            access_token=access_token,
        )

        return top_level_count

    def _list_all_blocks(
        self,
        *,
        api_base: str,
        access_token: str,
        doc_token: str,
    ) -> List[Dict[str, Any]]:
        all_blocks: List[Dict[str, Any]] = []
        page_token = ""

        while True:
            params: Dict[str, Any] = {"page_size": 500}
            if page_token:
                params["page_token"] = page_token

            data = self._request_json(
                method="GET",
                url=f"{api_base}/open-apis/docx/v1/documents/{quote(doc_token, safe='')}/blocks",
                payload=None,
                access_token=access_token,
                params=params,
            )

            items = data.get("items") if isinstance(data, dict) else None
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        all_blocks.append(item)

            has_more = bool(data.get("has_more")) if isinstance(data, dict) else False
            next_token = ""
            if isinstance(data, dict):
                next_token = str(
                    data.get("page_token") or data.get("next_page_token") or ""
                ).strip()

            if not has_more or not next_token:
                break

            page_token = next_token

        return all_blocks

    def _convert_markdown_to_blocks(
        self,
        *,
        api_base: str,
        access_token: str,
        markdown: str,
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        data = self._request_json(
            method="POST",
            url=f"{api_base}/open-apis/docx/v1/documents/blocks/convert",
            payload={"content_type": "markdown", "content": markdown},
            access_token=access_token,
        )

        blocks_raw = data.get("blocks") if isinstance(data, dict) else None
        ids_raw = data.get("first_level_block_ids") if isinstance(data, dict) else None

        blocks: List[Dict[str, Any]] = []
        if isinstance(blocks_raw, list):
            for block in blocks_raw:
                if isinstance(block, dict):
                    blocks.append(block)

        first_level_ids: List[str] = []
        if isinstance(ids_raw, list):
            for block_id in ids_raw:
                first_level_ids.append(str(block_id))

        return blocks, first_level_ids

    @staticmethod
    def _sort_blocks_by_first_level(
        blocks: List[Dict[str, Any]], first_level_ids: List[str]
    ) -> List[Dict[str, Any]]:
        if not first_level_ids:
            return blocks

        block_map = {str(block.get("block_id")): block for block in blocks}
        sorted_blocks: List[Dict[str, Any]] = []
        seen = set()

        for block_id in first_level_ids:
            block = block_map.get(block_id)
            if block is not None:
                sorted_blocks.append(block)
                seen.add(block_id)

        for block in blocks:
            block_id = str(block.get("block_id"))
            if block_id not in seen:
                sorted_blocks.append(block)

        return sorted_blocks

    def _clean_blocks_for_insert(
        self, blocks: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        cleaned: List[Dict[str, Any]] = []
        skipped: List[str] = []

        for block in blocks:
            block_type = int(block.get("block_type") or 0)
            if block_type in self._UNSUPPORTED_BLOCK_TYPES:
                skipped.append(str(block_type))
                continue

            if block_type == 31 and isinstance(block.get("table"), dict):
                table = dict(block["table"])
                table.pop("merge_info", None)
                new_block = dict(block)
                new_block["table"] = table
                cleaned.append(new_block)
                continue

            cleaned.append(block)

        return cleaned, skipped

    def _insert_blocks(
        self,
        *,
        api_base: str,
        access_token: str,
        doc_token: str,
        blocks: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        data = self._request_json(
            method="POST",
            url=(
                f"{api_base}/open-apis/docx/v1/documents/{quote(doc_token, safe='')}/"
                f"blocks/{quote(doc_token, safe='')}/children"
            ),
            payload={"children": blocks},
            access_token=access_token,
        )

        children = data.get("children") if isinstance(data, dict) else None
        if isinstance(children, list):
            return [child for child in children if isinstance(child, dict)]
        return []

    def _request_json(
        self,
        *,
        method: str,
        url: str,
        payload: Optional[Dict[str, Any]],
        access_token: Optional[str],
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if params:
            query = urlencode(params)
            url = f"{url}?{query}"

        headers = {
            "Content-Type": "application/json; charset=utf-8",
        }
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        body = None
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        request = Request(url=url, data=body, headers=headers, method=method)

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
            raise FeishuPublishError(
                f"Feishu API HTTP {exc.code}: {error_body or exc.reason}"
            ) from exc
        except URLError as exc:
            raise FeishuPublishError(f"Feishu API network error: {exc.reason}") from exc

        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError as exc:
            raise FeishuPublishError(f"Invalid JSON response from Feishu API: {raw}") from exc

        code = int(parsed.get("code", 0)) if isinstance(parsed, dict) else -1
        if code != 0:
            msg = parsed.get("msg", "") if isinstance(parsed, dict) else ""
            raise FeishuPublishError(f"Feishu API error code={code}, msg={msg}")

        data = parsed.get("data") if isinstance(parsed, dict) else {}
        return data if isinstance(data, dict) else {}
