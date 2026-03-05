#!/usr/bin/env python3
"""
ghost.py - Ghost CMS Admin API client for OpenClaw
Skill: ghost | https://clawhub.ai

Supports Ghost Admin API v5.x (self-hosted and Ghost Pro).
Auth: JWT generated from Admin API Key (no external dependencies).

Config  : ~/.openclaw/config/ghost/config.json
Secrets : ~/.openclaw/secrets/ghost_creds  (GHOST_URL, GHOST_ADMIN_KEY)

GHOST_ADMIN_KEY format: <id>:<secret_hex>
  → Ghost Admin → Integrations → Add custom integration → Admin API Key
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jwt_utils import make_jwt as _make_jwt
from _retry import with_retry

# ─── Paths ─────────────────────────────────────────────────────────────────────

SKILL_DIR    = Path(__file__).resolve().parent.parent
_CONFIG_DIR  = Path.home() / ".openclaw" / "config" / "ghost"
CONFIG_FILE  = _CONFIG_DIR / "config.json"
CREDS_FILE   = Path.home() / ".openclaw" / "secrets" / "ghost_creds"

_DEFAULT_CONFIG = {
    "allow_publish":       False,
    "allow_delete":        False,
    "allow_member_access": False,
    "default_status":      "draft",
    "default_tags":        [],
    "readonly_mode":       False,
}

# ─── Config & credentials ──────────────────────────────────────────────────────

def _load_config() -> dict:
    cfg = dict(_DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        try:
            cfg.update(json.loads(CONFIG_FILE.read_text()))
        except Exception:
            pass
    return cfg


def _load_creds() -> dict:
    creds = {}
    if CREDS_FILE.exists():
        for line in CREDS_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                creds[k.strip()] = v.strip()
    for k in ("GHOST_URL", "GHOST_ADMIN_KEY"):
        if k in os.environ:
            creds[k] = os.environ[k]
    return creds


# ─── Exceptions ────────────────────────────────────────────────────────────────

class GhostError(RuntimeError):
    pass

class GhostAPIError(GhostError):
    pass

class PermissionDeniedError(GhostError):
    pass


# ─── Client ────────────────────────────────────────────────────────────────────

class GhostClient:
    """
    Ghost Admin API v5 client.
    All write/delete/publish operations respect config.json restrictions.
    JWT tokens are generated fresh per request (5-min TTL, stateless).
    """

    def __init__(self, url: str = None, admin_key: str = None):
        creds = _load_creds()
        self.cfg      = _load_config()
        raw_url       = url       or creds.get("GHOST_URL",       "")
        raw_key       = admin_key or creds.get("GHOST_ADMIN_KEY", "")
        if not raw_url or not raw_key:
            raise GhostError(
                "Credentials missing. Set GHOST_URL / GHOST_ADMIN_KEY in "
                f"{CREDS_FILE} or as environment variables."
            )
        self.base_url = raw_url.rstrip("/")
        self.api_url  = f"{self.base_url}/ghost/api/admin"
        parts = raw_key.split(":")
        if len(parts) != 2:
            raise GhostError(
                "GHOST_ADMIN_KEY must be in format 'id:secret_hex' "
                "(found in Ghost Admin → Integrations)"
            )
        self._key_id, self._secret_hex = parts

    def _headers(self) -> dict:
        """Fresh JWT headers for every request."""
        token = _make_jwt(self._key_id, self._secret_hex)
        return {
            "Authorization": f"Ghost {token}",
            "Content-Type":  "application/json",
            "Accept-Version": "v5.0",
        }

    def _request(self, method: str, endpoint: str, payload: dict = None,
                 params: dict = None) -> dict:
        """Generic HTTP request using stdlib urllib."""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        if params:
            filtered = {k: v for k, v in params.items() if v is not None}
            if filtered:
                url += "?" + urllib.parse.urlencode(filtered)
        headers = self._headers()
        body = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            def _do():
                with urllib.request.urlopen(req) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            return with_retry(_do)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GhostAPIError(f"HTTP {exc.code} {method} {endpoint}: {detail[:300]}")
        except urllib.error.URLError as exc:
            raise GhostAPIError(f"Network error {method} {endpoint}: {exc.reason}")

    def _get(self, endpoint: str, params: dict = None) -> dict:
        return self._request("GET", endpoint, params=params)

    def _post(self, endpoint: str, payload: dict, params: dict = None) -> dict:
        self._check_write()
        return self._request("POST", endpoint, payload=payload, params=params)

    def _put(self, endpoint: str, payload: dict, params: dict = None) -> dict:
        self._check_write()
        return self._request("PUT", endpoint, payload=payload, params=params)

    def _delete(self, endpoint: str) -> bool:
        self._check_delete()
        self._request("DELETE", endpoint)
        return True

    # ── Config enforcement ─────────────────────────────────────────────────────

    def _check_write(self):
        if self.cfg.get("readonly_mode"):
            raise PermissionDeniedError("readonly_mode is enabled in config.json")

    def _check_delete(self):
        if self.cfg.get("readonly_mode"):
            raise PermissionDeniedError("readonly_mode is enabled in config.json")
        if not self.cfg.get("allow_delete", False):
            raise PermissionDeniedError("allow_delete is disabled in config.json")

    def _check_members(self):
        if not self.cfg.get("allow_member_access", False):
            raise PermissionDeniedError("allow_member_access is disabled in config.json")

    def _resolve_status(self, requested_status: str) -> str:
        """Enforce allow_publish: if False, cap status at 'draft'."""
        if requested_status == "published" and not self.cfg.get("allow_publish", False):
            return "draft"
        if requested_status is None:
            return self.cfg.get("default_status", "draft")
        return requested_status

    def _apply_default_tags(self, tags: list) -> list:
        """Merge default_tags from config into the tag list."""
        defaults = self.cfg.get("default_tags", [])
        if not defaults:
            return tags or []
        existing_names = {t.get("name", "").lower() for t in (tags or [])}
        for dt in defaults:
            name = dt if isinstance(dt, str) else dt.get("name", "")
            if name.lower() not in existing_names:
                (tags := (tags or [])).append({"name": name})
        return tags or []

    # ── Site ───────────────────────────────────────────────────────────────────

    def get_site(self) -> dict:
        """Return site metadata."""
        return self._get("site").get("site", {})

    # ── Posts ──────────────────────────────────────────────────────────────────

    def list_posts(
        self,
        limit: int = 15,
        page: int = 1,
        status: str = "all",
        tag: str = None,
        order: str = "published_at desc",
        fields: str = None,
    ) -> dict:
        """
        List posts. Returns {posts: [...], meta: {pagination: {...}}}.
        status: 'published' | 'draft' | 'scheduled' | 'all'
        """
        params = {"limit": limit, "page": page, "order": order}
        if status != "all": params["filter"] = f"status:{status}"
        if tag:             params["filter"] = (params.get("filter", "") + f"+tag:{tag}").lstrip("+")
        if fields:          params["fields"] = fields
        return self._get("posts", params)

    def get_post(self, id_or_slug: str) -> dict:
        """Get a single post by ID or slug."""
        # Try by ID first, then by slug
        if len(id_or_slug) == 24 and id_or_slug.isalnum():
            return self._get(f"posts/{id_or_slug}").get("posts", [{}])[0]
        return self._get(f"posts/slug/{id_or_slug}").get("posts", [{}])[0]

    def create_post(
        self,
        title: str,
        html: str = None,
        lexical: str = None,
        status: str = None,
        tags: list = None,
        featured: bool = False,
        custom_excerpt: str = None,
        meta_title: str = None,
        meta_description: str = None,
        slug: str = None,
        published_at: str = None,
        og_title: str = None,
        og_description: str = None,
        twitter_title: str = None,
        twitter_description: str = None,
        feature_image: str = None,
        **extra,
    ) -> dict:
        """Create a new post. Returns the created post dict."""
        post = {
            "title":   title,
            "status":  self._resolve_status(status),
            "featured": featured,
            "tags":    self._apply_default_tags(tags),
        }
        if html            is not None: post["html"]             = html
        if lexical         is not None: post["lexical"]          = lexical
        if custom_excerpt  is not None: post["custom_excerpt"]   = custom_excerpt
        if meta_title      is not None: post["meta_title"]       = meta_title
        if meta_description is not None: post["meta_description"] = meta_description
        if slug            is not None: post["slug"]             = slug
        if published_at    is not None: post["published_at"]     = published_at
        if og_title        is not None: post["og_title"]         = og_title
        if og_description  is not None: post["og_description"]   = og_description
        if twitter_title   is not None: post["twitter_title"]    = twitter_title
        if twitter_description is not None: post["twitter_description"] = twitter_description
        if feature_image   is not None: post["feature_image"]    = feature_image
        post.update(extra)
        params = {"source": "html"} if html is not None else None
        result = self._post("posts", {"posts": [post]}, params=params)
        return result.get("posts", [{}])[0]

    def update_post(self, post_id: str, updated_at: str = None, **fields) -> dict:
        """
        Update a post. updated_at is required by Ghost to prevent conflicts.
        If not provided, it's fetched automatically.
        Pass ?source=html automatically when an html field is included.
        """
        if updated_at is None:
            existing = self.get_post(post_id)
            updated_at = existing.get("updated_at")
        if "status" in fields:
            fields["status"] = self._resolve_status(fields["status"])
        payload = {"updated_at": updated_at, **fields}
        params = {"source": "html"} if "html" in fields else None
        result  = self._put(f"posts/{post_id}", {"posts": [payload]}, params=params)
        return result.get("posts", [{}])[0]

    def delete_post(self, post_id: str) -> bool:
        """Delete a post permanently."""
        return self._delete(f"posts/{post_id}")

    def publish_post(self, post_id: str) -> dict:
        """Publish a draft post."""
        if not self.cfg.get("allow_publish", False):
            raise PermissionDeniedError("allow_publish is disabled in config.json")
        return self.update_post(post_id, status="published")

    def unpublish_post(self, post_id: str) -> dict:
        """Revert a published post to draft."""
        return self.update_post(post_id, status="draft")

    # ── Pages ──────────────────────────────────────────────────────────────────
    # Ghost pages share the same schema as posts, just different endpoint.

    def list_pages(self, limit: int = 15, page: int = 1, status: str = "all") -> dict:
        params = {"limit": limit, "page": page}
        if status != "all": params["filter"] = f"status:{status}"
        return self._get("pages", params)

    def get_page(self, id_or_slug: str) -> dict:
        if len(id_or_slug) == 24 and id_or_slug.isalnum():
            return self._get(f"pages/{id_or_slug}").get("pages", [{}])[0]
        return self._get(f"pages/slug/{id_or_slug}").get("pages", [{}])[0]

    def create_page(self, title: str, html: str = None, status: str = None, **fields) -> dict:
        page = {
            "title":  title,
            "status": self._resolve_status(status),
        }
        if html is not None: page["html"] = html
        page.update(fields)
        params = {"source": "html"} if html is not None else None
        return self._post("pages", {"pages": [page]}, params=params).get("pages", [{}])[0]

    def update_page(self, page_id: str, updated_at: str = None, **fields) -> dict:
        if updated_at is None:
            updated_at = self.get_page(page_id).get("updated_at")
        if "status" in fields:
            fields["status"] = self._resolve_status(fields["status"])
        params = {"source": "html"} if "html" in fields else None
        return self._put(f"pages/{page_id}", {"pages": [{"updated_at": updated_at, **fields}]}, params=params).get("pages", [{}])[0]

    def delete_page(self, page_id: str) -> bool:
        return self._delete(f"pages/{page_id}")

    def publish_page(self, page_id: str) -> dict:
        if not self.cfg.get("allow_publish", False):
            raise PermissionDeniedError("allow_publish is disabled in config.json")
        return self.update_page(page_id, status="published")

    def unpublish_page(self, page_id: str) -> dict:
        return self.update_page(page_id, status="draft")

    # ── Tags ───────────────────────────────────────────────────────────────────

    def list_tags(self, limit: int = 50, page: int = 1, include_count: bool = True) -> dict:
        params = {"limit": limit, "page": page}
        if include_count: params["include"] = "count.posts"
        return self._get("tags", params)

    def get_tag(self, id_or_slug: str) -> dict:
        if len(id_or_slug) == 24 and id_or_slug.isalnum():
            return self._get(f"tags/{id_or_slug}").get("tags", [{}])[0]
        return self._get(f"tags/slug/{id_or_slug}").get("tags", [{}])[0]

    def create_tag(
        self,
        name: str,
        slug: str = None,
        description: str = None,
        meta_title: str = None,
        meta_description: str = None,
        accent_color: str = None,
    ) -> dict:
        tag = {"name": name}
        if slug:             tag["slug"]             = slug
        if description:      tag["description"]      = description
        if meta_title:       tag["meta_title"]       = meta_title
        if meta_description: tag["meta_description"] = meta_description
        if accent_color:     tag["accent_color"]     = accent_color
        return self._post("tags", {"tags": [tag]}).get("tags", [{}])[0]

    def update_tag(self, tag_id: str, **fields) -> dict:
        return self._put(f"tags/{tag_id}", {"tags": [fields]}).get("tags", [{}])[0]

    def delete_tag(self, tag_id: str) -> bool:
        return self._delete(f"tags/{tag_id}")

    # ── Images ─────────────────────────────────────────────────────────────────

    def upload_image(self, file_path: str, alt_text: str = None, ref: str = None) -> dict:
        """
        Upload an image to Ghost. Returns {url, ref}.
        Supports: jpg, jpeg, png, gif, svg, webp
        """
        self._check_write()
        path = Path(file_path)
        mime_map = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png",  ".gif":  "image/gif",
            ".svg": "image/svg+xml", ".webp": "image/webp",
        }
        mime = mime_map.get(path.suffix.lower(), "application/octet-stream")
        boundary = f"----GhostUpload{int(time.time() * 1000)}"
        file_bytes = path.read_bytes()
        parts = []
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; "
            f'name="file"; filename="{path.name}"\r\n'
            f"Content-Type: {mime}\r\n\r\n".encode()
            + file_bytes + b"\r\n"
        )
        for field, value in [("alt", alt_text), ("ref", ref)]:
            if value:
                parts.append(
                    f"--{boundary}\r\nContent-Disposition: form-data; "
                    f'name="{field}"\r\n\r\n{value}\r\n'.encode()
                )
        parts.append(f"--{boundary}--\r\n".encode())
        body = b"".join(parts)
        token = _make_jwt(self._key_id, self._secret_hex)
        headers = {
            "Authorization": f"Ghost {token}",
            "Accept-Version": "v5.0",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        }
        url = f"{self.api_url}/images/upload"
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            def _do():
                with urllib.request.urlopen(req) as resp:
                    return json.loads(resp.read().decode("utf-8")).get("images", [{}])[0]
            return with_retry(_do)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GhostAPIError(f"HTTP {exc.code} image upload: {detail[:300]}")

    # ── Members ────────────────────────────────────────────────────────────────

    def list_members(self, limit: int = 15, page: int = 1, filter_str: str = None) -> dict:
        """List members. Requires allow_member_access: true in config."""
        self._check_members()
        params = {"limit": limit, "page": page}
        if filter_str: params["filter"] = filter_str
        return self._get("members", params)

    def get_member(self, member_id: str) -> dict:
        self._check_members()
        return self._get(f"members/{member_id}").get("members", [{}])[0]

    def create_member(self, email: str, name: str = None, **fields) -> dict:
        self._check_members()
        member = {"email": email}
        if name: member["name"] = name
        member.update(fields)
        return self._post("members", {"members": [member]}).get("members", [{}])[0]

    def update_member(self, member_id: str, **fields) -> dict:
        self._check_members()
        return self._put(f"members/{member_id}", {"members": [fields]}).get("members", [{}])[0]

    def delete_member(self, member_id: str) -> bool:
        self._check_members()
        self._check_delete()
        return self._delete(f"members/{member_id}")

    # ── Newsletters ────────────────────────────────────────────────────────────

    def list_newsletters(self, limit: int = 15) -> dict:
        return self._get("newsletters", {"limit": limit})

    def get_newsletter(self, newsletter_id: str) -> dict:
        return self._get(f"newsletters/{newsletter_id}").get("newsletters", [{}])[0]

    # ── Tiers ──────────────────────────────────────────────────────────────────

    def list_tiers(self, include: str = "monthly_price,yearly_price,benefits") -> dict:
        return self._get("tiers", {"limit": "all", "include": include})

    # ── Users (read-only) ──────────────────────────────────────────────────────

    def list_users(self, limit: int = 15) -> dict:
        return self._get("users", {"limit": limit})

    def get_user(self, user_id: str = "me") -> dict:
        return self._get(f"users/{user_id}").get("users", [{}])[0]

    # ── Config info ────────────────────────────────────────────────────────────

    def get_config_info(self) -> dict:
        return {
            "config_file":        str(CONFIG_FILE),
            "config_file_exists": CONFIG_FILE.exists(),
            "creds_file":         str(CREDS_FILE),
            "creds_file_exists":  CREDS_FILE.exists(),
            "active_config":      self.cfg,
            "ghost_url":          self.base_url,
            "key_id":             self._key_id,
        }


# ─── CLI ───────────────────────────────────────────────────────────────────────

def _cli():
    import argparse

    p = argparse.ArgumentParser(
        description="Ghost Admin API CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Credentials: ~/.openclaw/secrets/ghost_creds (GHOST_URL / GHOST_ADMIN_KEY)"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    def _add(name, help_):
        return sub.add_parser(name, help=help_)

    # Site
    _add("site",       "Show site info")
    _add("config",     "Show active config + creds source")

    # Posts
    sp = _add("posts",         "List posts")
    sp.add_argument("--limit",  type=int, default=15)
    sp.add_argument("--page",   type=int, default=1)
    sp.add_argument("--status", default="all")
    sp.add_argument("--tag",    default=None)
    sp.add_argument("--fields", default=None)

    sp = _add("post",          "Get a post by ID or slug"); sp.add_argument("id_or_slug")

    sp = _add("post-create",   "Create a post")
    sp.add_argument("title")
    sp.add_argument("--html",           default=None)
    sp.add_argument("--html-file",      default=None, help="Read HTML from file")
    sp.add_argument("--status",         default=None, help="draft|published|scheduled")
    sp.add_argument("--tags",           default=None, help="Comma-separated tag names")
    sp.add_argument("--featured",       action="store_true")
    sp.add_argument("--excerpt",        default=None)
    sp.add_argument("--meta-title",     default=None)
    sp.add_argument("--meta-desc",      default=None)
    sp.add_argument("--slug",           default=None)
    sp.add_argument("--feature-image",  default=None, help="URL of the feature/hero image")

    sp = _add("post-update",   "Update a post"); sp.add_argument("post_id"); sp.add_argument("--fields-json", required=True)
    sp = _add("post-delete",   "Delete a post"); sp.add_argument("post_id")
    sp = _add("post-publish",  "Publish a post"); sp.add_argument("post_id")
    sp = _add("post-unpublish","Revert post to draft"); sp.add_argument("post_id")

    # Pages
    sp = _add("pages",         "List pages"); sp.add_argument("--limit", type=int, default=15); sp.add_argument("--status", default="all")
    sp = _add("page",          "Get a page"); sp.add_argument("id_or_slug")
    sp = _add("page-create",   "Create a page"); sp.add_argument("title"); sp.add_argument("--html", default=None); sp.add_argument("--status", default=None)
    sp = _add("page-update",   "Update a page"); sp.add_argument("page_id"); sp.add_argument("--fields-json", required=True)
    sp = _add("page-delete",   "Delete a page"); sp.add_argument("page_id")
    sp = _add("page-publish",  "Publish a page"); sp.add_argument("page_id")
    sp = _add("page-unpublish","Revert page to draft"); sp.add_argument("page_id")

    # Tags
    sp = _add("tags",          "List tags"); sp.add_argument("--limit", type=int, default=50)
    sp = _add("tag",           "Get a tag"); sp.add_argument("id_or_slug")
    sp = _add("tag-create",    "Create a tag"); sp.add_argument("name"); sp.add_argument("--slug", default=None); sp.add_argument("--desc", default=None)
    sp = _add("tag-update",    "Update a tag"); sp.add_argument("tag_id"); sp.add_argument("--fields-json", required=True)
    sp = _add("tag-delete",    "Delete a tag"); sp.add_argument("tag_id")

    # Images
    sp = _add("image-upload",  "Upload an image"); sp.add_argument("file"); sp.add_argument("--alt", default=None); sp.add_argument("--ref", default=None)

    # Members
    sp = _add("members",       "List members (requires allow_member_access)"); sp.add_argument("--limit", type=int, default=15)
    sp = _add("member",        "Get a member"); sp.add_argument("member_id")

    # Newsletters
    _add("newsletters",        "List newsletters")

    # Tiers
    _add("tiers",              "List tiers/plans")

    # Users
    _add("me",                 "Show current API user")

    args = p.parse_args()
    gc   = GhostClient()

    def jout(obj):
        print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))

    if args.cmd == "site":
        jout(gc.get_site())

    elif args.cmd == "config":
        jout(gc.get_config_info())

    elif args.cmd == "posts":
        jout(gc.list_posts(limit=args.limit, page=args.page, status=args.status,
                           tag=args.tag, fields=args.fields))

    elif args.cmd == "post":
        jout(gc.get_post(args.id_or_slug))

    elif args.cmd == "post-create":
        html = args.html
        if args.html_file:
            html = Path(args.html_file).read_text()
        tags = [{"name": t.strip()} for t in args.tags.split(",")] if args.tags else None
        jout(gc.create_post(
            title=args.title, html=html, status=args.status, tags=tags,
            featured=args.featured, custom_excerpt=args.excerpt,
            meta_title=args.meta_title, meta_description=args.meta_desc,
            slug=args.slug,
            feature_image=args.feature_image,
        ))

    elif args.cmd == "post-update":
        fields = json.loads(args.fields_json)
        jout(gc.update_post(args.post_id, **fields))

    elif args.cmd == "post-delete":
        gc.delete_post(args.post_id); jout({"ok": True, "action": "delete", "resource": "post", "id": args.post_id})

    elif args.cmd == "post-publish":
        jout(gc.publish_post(args.post_id))

    elif args.cmd == "post-unpublish":
        jout(gc.unpublish_post(args.post_id))

    elif args.cmd == "pages":
        jout(gc.list_pages(limit=args.limit, status=args.status))

    elif args.cmd == "page":
        jout(gc.get_page(args.id_or_slug))

    elif args.cmd == "page-create":
        jout(gc.create_page(title=args.title, html=args.html, status=args.status))

    elif args.cmd == "page-update":
        jout(gc.update_page(args.page_id, **json.loads(args.fields_json)))

    elif args.cmd == "page-delete":
        gc.delete_page(args.page_id); jout({"ok": True, "action": "delete", "resource": "page", "id": args.page_id})

    elif args.cmd == "page-publish":
        jout(gc.publish_page(args.page_id))

    elif args.cmd == "page-unpublish":
        jout(gc.unpublish_page(args.page_id))

    elif args.cmd == "tags":
        jout(gc.list_tags(limit=args.limit))

    elif args.cmd == "tag":
        jout(gc.get_tag(args.id_or_slug))

    elif args.cmd == "tag-create":
        jout(gc.create_tag(args.name, slug=args.slug, description=args.desc))

    elif args.cmd == "tag-update":
        jout(gc.update_tag(args.tag_id, **json.loads(args.fields_json)))

    elif args.cmd == "tag-delete":
        gc.delete_tag(args.tag_id); jout({"ok": True, "action": "delete", "resource": "tag", "id": args.tag_id})

    elif args.cmd == "image-upload":
        jout(gc.upload_image(args.file, alt_text=args.alt, ref=args.ref))

    elif args.cmd == "members":
        jout(gc.list_members(limit=args.limit))

    elif args.cmd == "member":
        jout(gc.get_member(args.member_id))

    elif args.cmd == "newsletters":
        jout(gc.list_newsletters())

    elif args.cmd == "tiers":
        jout(gc.list_tiers())

    elif args.cmd == "me":
        jout(gc.get_user("me"))


if __name__ == "__main__":
    _cli()
