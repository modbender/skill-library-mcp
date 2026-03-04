#!/usr/bin/env python3
"""
nextcloud.py - Nextcloud client (WebDAV + OCS) for OpenClaw
Skill: nextcloud | https://clawhub.ai

Zero external dependencies - stdlib only (urllib, xml, json).

Config  : ~/.openclaw/config/nextcloud/config.json
Secrets : ~/.openclaw/secrets/nextcloud_creds  (NC_URL, NC_USER, NC_APP_KEY)
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _retry import with_retry

# ─── Paths ─────────────────────────────────────────────────────────────────────

SKILL_DIR    = Path(__file__).resolve().parent.parent   # skills/nextcloud/
_CONFIG_DIR  = Path.home() / ".openclaw" / "config" / "nextcloud"
CONFIG_FILE  = _CONFIG_DIR / "config.json"
CREDS_FILE   = Path.home() / ".openclaw" / "secrets" / "nextcloud_creds"

_DEFAULT_CONFIG = {
    "base_path": "/",
    "allow_write": False,
    "allow_delete": False,
    "readonly_mode": False,
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
    for k in ("NC_URL", "NC_USER", "NC_APP_KEY"):
        if k in os.environ:
            creds[k] = os.environ[k]
    return creds


# ─── Exceptions ────────────────────────────────────────────────────────────────

class NextcloudError(RuntimeError):
    pass

class NextcloudAPIError(NextcloudError):
    pass

class PermissionDeniedError(NextcloudError):
    pass


# ─── Client ────────────────────────────────────────────────────────────────────

class NextcloudClient:
    """
    Full Nextcloud client: WebDAV file ops + OCS sharing/user/tags.
    All write operations respect config.json restrictions.
    Zero external dependencies - uses urllib (stdlib).
    """

    def __init__(self, url: str = None, user: str = None, password: str = None):
        creds = _load_creds()
        self.cfg = _load_config()
        self.base_url  = (url      or creds.get("NC_URL",  "")).rstrip("/")
        self.user      = (user     or creds.get("NC_USER", ""))
        self.password  = (password or creds.get("NC_APP_KEY", ""))
        if not all([self.base_url, self.user, self.password]):
            raise NextcloudError(
                "Credentials missing. Set NC_URL / NC_USER / NC_APP_KEY in "
                f"{CREDS_FILE} or as environment variables."
            )
        self.dav_root  = f"{self.base_url}/remote.php/dav/files/{quote(self.user)}"
        self.ocs_root  = f"{self.base_url}/ocs/v2.php"
        self.dav_tags  = f"{self.base_url}/remote.php/dav"
        # Pre-compute Basic Auth header
        cred_bytes = f"{self.user}:{self.password}".encode("utf-8")
        self._auth_header = "Basic " + base64.b64encode(cred_bytes).decode("ascii")

    # ── HTTP transport ──────────────────────────────────────────────────────

    def _request(self, method: str, url: str, data: bytes = None,
                 headers: dict = None) -> tuple:
        """
        Generic HTTP request via urllib. Returns (status_code, headers, body_bytes).
        Raises NextcloudError on HTTP errors (except expected status codes).
        """
        hdrs = {
            "Authorization": self._auth_header,
            "OCS-APIRequest": "true",
            "Accept": "application/json",
        }
        if headers:
            hdrs.update(headers)
        req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
        try:
            def _do():
                with urllib.request.urlopen(req) as resp:
                    body = resp.read()
                    return resp.status, dict(resp.headers), body
            return with_retry(_do)
        except urllib.error.HTTPError as exc:
            body = exc.read()
            return exc.code, dict(exc.headers), body

    def _request_ok(self, method: str, url: str, data: bytes = None,
                    headers: dict = None, accept: tuple = (200, 201, 204, 207)) -> tuple:
        """Request that raises on unexpected status codes."""
        status, resp_headers, body = self._request(method, url, data, headers)
        if status not in accept:
            detail = body.decode("utf-8", errors="replace")[:300]
            raise NextcloudAPIError(f"HTTP {status} {method} {url}: {detail}")
        return status, resp_headers, body

    # ── Helpers ────────────────────────────────────────────────────────────

    def _dav(self, path: str) -> str:
        """Absolute WebDAV URL for a user-relative path."""
        if not path.startswith("/"):
            path = "/" + path
        # encode each segment, keep /
        enc = "/".join(quote(seg, safe="") for seg in path.split("/"))
        return self.dav_root + enc

    def _enforce_base(self, path: str) -> str:
        """Ensure path stays inside config base_path."""
        base = self.cfg.get("base_path", "/").rstrip("/")
        if not base or base == "/":
            return path
        p = path if path.startswith("/") else "/" + path
        if not p.startswith(base):
            raise PermissionDeniedError(
                f"Path '{path}' is outside allowed base_path '{base}'"
            )
        return path

    def _check_write(self):
        if self.cfg.get("readonly_mode"):
            raise PermissionDeniedError("readonly_mode is enabled in config.json")
        if not self.cfg.get("allow_write", False):
            raise PermissionDeniedError("allow_write is disabled in config.json")

    def _check_delete(self):
        if self.cfg.get("readonly_mode"):
            raise PermissionDeniedError("readonly_mode is enabled in config.json")
        if not self.cfg.get("allow_delete", False):
            raise PermissionDeniedError("allow_delete is disabled in config.json")

    # ── Directories ────────────────────────────────────────────────────────

    def mkdir(self, path: str) -> bool:
        """Create directory (MKCOL), recursively creates parents."""
        self._check_write()
        self._enforce_base(path)
        parts = Path(path.lstrip("/")).parts
        current = ""
        for part in parts:
            current = current + "/" + part
            status, _, _ = self._request("MKCOL", self._dav(current))
            if status not in (201, 405):   # 405 = already exists
                raise NextcloudError(f"MKCOL {current} failed with HTTP {status}")
        return True

    def rename(self, old_path: str, new_path: str) -> bool:
        """Rename or move a resource (MOVE)."""
        self._check_write()
        self._enforce_base(old_path)
        dst_url = self._dav(new_path)
        self._request_ok(
            "MOVE", self._dav(old_path),
            headers={"Destination": dst_url, "Overwrite": "T"},
            accept=(200, 201, 204),
        )
        return True

    def copy(self, src_path: str, dst_path: str, overwrite: bool = True) -> bool:
        """Copy a resource to a new location (COPY)."""
        self._check_write()
        self._enforce_base(src_path)
        dst_url = self._dav(dst_path)
        self._request_ok(
            "COPY", self._dav(src_path),
            headers={
                "Destination": dst_url,
                "Overwrite": "T" if overwrite else "F",
                "Depth": "infinity",
            },
            accept=(200, 201, 204),
        )
        return True

    # ── Files ──────────────────────────────────────────────────────────────

    def write_file(self, path: str, content, content_type: str = "text/plain; charset=utf-8") -> bool:
        """Create or overwrite a file (PUT). Creates parent dirs if needed."""
        self._check_write()
        self._enforce_base(path)
        parent = str(Path(path).parent)
        if parent and parent not in (".", "/"):
            try:
                self.mkdir(parent)
            except Exception:
                pass
        if isinstance(content, str):
            content = content.encode("utf-8")
        self._request_ok(
            "PUT", self._dav(path), data=content,
            headers={"Content-Type": content_type},
            accept=(200, 201, 204),
        )
        return True

    def read_file(self, path: str) -> str:
        """Read a text file (GET)."""
        _, _, body = self._request_ok("GET", self._dav(path))
        return body.decode("utf-8")

    def read_file_bytes(self, path: str) -> bytes:
        """Read a binary file (GET)."""
        _, _, body = self._request_ok("GET", self._dav(path))
        return body

    def delete(self, path: str) -> bool:
        """Delete a file or directory (DELETE)."""
        self._check_delete()
        self._enforce_base(path)
        self._request_ok("DELETE", self._dav(path), accept=(200, 204))
        return True

    def exists(self, path: str) -> bool:
        """Check if a path exists."""
        status, _, _ = self._request("HEAD", self._dav(path))
        return status == 200

    def set_favorite(self, path: str, state: bool = True) -> bool:
        """Toggle favorite flag via PROPPATCH (oc:favorite)."""
        self._enforce_base(path)
        value = "1" if state else "0"
        body = f'''<?xml version="1.0"?>
<d:propertyupdate xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns">
  <d:set>
    <d:prop><oc:favorite>{value}</oc:favorite></d:prop>
  </d:set>
</d:propertyupdate>'''
        self._request_ok(
            "PROPPATCH", self._dav(path),
            data=body.encode("utf-8"),
            headers={"Content-Type": "application/xml"},
            accept=(200, 207),
        )
        return True

    def append_to_file(self, path: str, content: str) -> bool:
        """Append text to an existing file (read then write)."""
        try:
            existing = self.read_file(path)
        except Exception:
            existing = ""
        return self.write_file(path, existing + content)

    # ── Directory listing ──────────────────────────────────────────────────

    def list_dir(self, path: str = "/", depth: int = 1) -> list:
        """List directory contents (PROPFIND). Returns list of dicts."""
        url = self._dav(path)
        body = '''<?xml version="1.0" encoding="UTF-8"?>
<d:propfind xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns" xmlns:nc="http://nextcloud.org/ns">
  <d:prop>
    <d:getlastmodified/>
    <d:getcontentlength/>
    <d:getcontenttype/>
    <oc:permissions/>
    <d:resourcetype/>
    <d:getetag/>
    <oc:size/>
    <oc:favorite/>
    <oc:fileid/>
  </d:prop>
</d:propfind>'''
        _, _, resp_body = self._request_ok(
            "PROPFIND", url, data=body.encode("utf-8"),
            headers={"Depth": str(depth), "Content-Type": "application/xml"},
            accept=(200, 207),
        )
        return self._parse_propfind(resp_body.decode("utf-8"), path)

    def _parse_propfind(self, xml_text: str, base_path: str) -> list:
        ns = {
            "d":  "DAV:",
            "oc": "http://owncloud.org/ns",
            "nc": "http://nextcloud.org/ns",
        }
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            raise NextcloudError(f"PROPFIND parse error: {e}")

        dav_prefix = f"/remote.php/dav/files/{quote(self.user)}"
        results = []
        base_enc = "/".join(quote(s, safe="") for s in base_path.split("/"))

        for response in root.findall("d:response", ns):
            href = response.findtext("d:href", "", ns)
            rel  = href.replace(dav_prefix, "").rstrip("/") or "/"
            if rel.rstrip("/") == base_enc.rstrip("/"):
                continue
            props = response.find(".//d:prop", ns)
            if props is None:
                continue
            is_dir = props.find("d:resourcetype/d:collection", ns) is not None
            size   = int(props.findtext("oc:size", "0", ns)
                         or props.findtext("d:getcontentlength", "0", ns) or 0)
            results.append({
                "name":         Path(rel).name,
                "path":         rel,
                "is_dir":       is_dir,
                "size":         size,
                "last_modified": props.findtext("d:getlastmodified", "", ns),
                "etag":         props.findtext("d:getetag", "", ns).strip('"'),
                "content_type": props.findtext("d:getcontenttype", "", ns),
                "permissions":  props.findtext("oc:permissions", "", ns),
                "file_id":      props.findtext("oc:fileid", "", ns),
                "favorite":     props.findtext("oc:favorite", "0", ns) == "1",
            })
        return results

    # ── Search ─────────────────────────────────────────────────────────────

    def search(self, query: str, path: str = "/", limit: int = 30) -> list:
        """
        Full-text search via WebDAV SEARCH (DASL basic-search).
        Returns same dict format as list_dir.
        """
        scope_url = self._dav(path)
        body = f'''<?xml version="1.0" encoding="UTF-8"?>
<d:searchrequest xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns">
  <d:basicsearch>
    <d:select>
      <d:prop>
        <d:getlastmodified/>
        <d:getcontentlength/>
        <d:getcontenttype/>
        <d:resourcetype/>
        <d:getetag/>
        <oc:fileid/>
        <oc:permissions/>
        <oc:size/>
      </d:prop>
    </d:select>
    <d:from>
      <d:scope>
        <d:href>{scope_url}</d:href>
        <d:depth>infinity</d:depth>
      </d:scope>
    </d:from>
    <d:where>
      <d:like>
        <d:prop><d:displayname/></d:prop>
        <d:literal>%{query}%</d:literal>
      </d:like>
    </d:where>
    <d:limit><d:nresults>{limit}</d:nresults></d:limit>
  </d:basicsearch>
</d:searchrequest>'''
        _, _, resp_body = self._request_ok(
            "SEARCH", f"{self.base_url}/remote.php/dav",
            data=body.encode("utf-8"),
            headers={"Content-Type": "application/xml"},
            accept=(200, 207),
        )
        return self._parse_propfind(resp_body.decode("utf-8"), path)

    # ── OCS: User & capabilities ───────────────────────────────────────────

    def get_user_info(self) -> dict:
        """Return current user's profile (OCS)."""
        _, _, body = self._request_ok("GET", f"{self.ocs_root}/cloud/user")
        return json.loads(body.decode("utf-8")).get("ocs", {}).get("data", {})

    def get_quota(self) -> dict:
        """Return storage quota info."""
        info = self.get_user_info()
        return info.get("quota", {})

    def get_capabilities(self) -> dict:
        """Return server capabilities."""
        _, _, body = self._request_ok("GET", f"{self.ocs_root}/cloud/capabilities")
        return json.loads(body.decode("utf-8")).get("ocs", {}).get("data", {})

    # ── OCS: Tags (systemtags) ─────────────────────────────────────────────

    def get_tags(self) -> list:
        """List all system tags."""
        body = '''<?xml version="1.0" encoding="UTF-8"?>
<d:propfind xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns">
  <d:prop>
    <oc:id/>
    <oc:display-name/>
    <oc:user-visible/>
    <oc:user-assignable/>
  </d:prop>
</d:propfind>'''
        _, _, resp_body = self._request_ok(
            "PROPFIND", f"{self.dav_tags}/systemtags/",
            data=body.encode("utf-8"),
            headers={"Depth": "1", "Content-Type": "application/xml"},
            accept=(200, 207),
        )
        ns = {"d": "DAV:", "oc": "http://owncloud.org/ns"}
        root = ET.fromstring(resp_body.decode("utf-8"))
        tags = []
        for resp in root.findall("d:response", ns):
            props = resp.find(".//d:prop", ns)
            if props is None:
                continue
            tag_id = props.findtext("oc:id", "", ns)
            if not tag_id:
                continue
            tags.append({
                "id": tag_id,
                "name": props.findtext("oc:display-name", "", ns),
                "user_visible": props.findtext("oc:user-visible", "true", ns) == "true",
                "user_assignable": props.findtext("oc:user-assignable", "true", ns) == "true",
            })
        return tags

    def create_tag(self, name: str, user_visible: bool = True, user_assignable: bool = True) -> dict:
        """Create a new system tag."""
        self._check_write()
        payload = json.dumps({
            "name": name,
            "userVisible": user_visible,
            "userAssignable": user_assignable,
        }).encode("utf-8")
        _, resp_headers, _ = self._request_ok(
            "POST", f"{self.dav_tags}/systemtags/",
            data=payload,
            headers={"Content-Type": "application/json"},
            accept=(201,),
        )
        # Tag ID is in the Location header
        location = resp_headers.get("Content-Location", resp_headers.get("Location", ""))
        tag_id = location.rstrip("/").split("/")[-1] if location else None
        return {"id": tag_id, "name": name}

    def assign_tag(self, file_id: str, tag_id: str) -> bool:
        """Assign an existing system tag to a file (by file_id from list_dir)."""
        self._check_write()
        status, _, _ = self._request(
            "PUT", f"{self.dav_tags}/systemtags-relations/files/{file_id}/{tag_id}"
        )
        if status not in (201, 409):   # 409 = already assigned
            raise NextcloudError(f"assign_tag failed with HTTP {status}")
        return True

    def remove_tag(self, file_id: str, tag_id: str) -> bool:
        """Remove a tag assignment from a file."""
        self._check_delete()
        self._request_ok(
            "DELETE", f"{self.dav_tags}/systemtags-relations/files/{file_id}/{tag_id}",
            accept=(200, 204),
        )
        return True

    # ── JSON helpers ───────────────────────────────────────────────────────

    def read_json(self, path: str):
        return json.loads(self.read_file(path))

    def write_json(self, path: str, data, indent: int = 2) -> bool:
        return self.write_file(
            path,
            json.dumps(data, ensure_ascii=False, indent=indent),
            "application/json",
        )


# ─── CLI ───────────────────────────────────────────────────────────────────────

def _cli():
    import argparse

    p = argparse.ArgumentParser(
        description="Nextcloud CLI - WebDAV + OCS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Credentials: ~/.openclaw/secrets/nextcloud_creds (NC_URL / NC_USER / NC_APP_KEY)"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    def _add(name, help_):
        return sub.add_parser(name, help=help_)

    sp = _add("mkdir",  "Create a directory (recursive)");  sp.add_argument("path")
    sp = _add("rename", "Rename / move");                    sp.add_argument("old"); sp.add_argument("new")
    sp = _add("copy",   "Copy to new location");             sp.add_argument("src"); sp.add_argument("dst")
    sp = _add("delete", "Delete file or directory");         sp.add_argument("path")
    sp = _add("exists", "Check if path exists (exit 0/1)");  sp.add_argument("path")

    sp = _add("write",  "Write a file (stdin or --content or --file)")
    sp.add_argument("path")
    sp.add_argument("--content", "-c", default=None)
    sp.add_argument("--file",    "-f", default=None)
    sp.add_argument("--append",  "-a", action="store_true",
                    help="Append to existing file instead of overwriting")

    sp = _add("read",   "Print a file");                     sp.add_argument("path")

    sp = _add("ls",     "List a directory")
    sp.add_argument("path", nargs="?", default="/")
    sp.add_argument("--depth",  type=int, default=1)
    sp.add_argument("--human",  action="store_true", help="Human-readable output (default: JSON)")

    sp = _add("search", "Search by filename")
    sp.add_argument("query")
    sp.add_argument("--path",  default="/")
    sp.add_argument("--limit", type=int, default=30)

    sp = _add("favorite",   "Set/unset favorite");  sp.add_argument("path"); sp.add_argument("--off", action="store_true")

    sp = _add("tags",         "List all system tags")
    sp = _add("tag-create",   "Create a system tag"); sp.add_argument("name")
    sp = _add("tag-assign",   "Assign tag to file");  sp.add_argument("file_id"); sp.add_argument("tag_id")
    sp = _add("tag-remove",   "Remove tag from file"); sp.add_argument("file_id"); sp.add_argument("tag_id")

    sp = _add("user",   "Show current user info")
    sp = _add("quota",  "Show storage quota")
    sp = _add("caps",   "Show server capabilities")
    sp = _add("config", "Show active config (config.json + creds source)")

    args = p.parse_args()
    nc   = NextcloudClient()

    def jout(obj):
        print(json.dumps(obj, ensure_ascii=False, indent=2))

    if args.cmd == "mkdir":
        nc.mkdir(args.path); jout({"ok": True, "action": "mkdir", "path": args.path})

    elif args.cmd == "rename":
        nc.rename(args.old, args.new); jout({"ok": True, "action": "rename", "old": args.old, "new": args.new})

    elif args.cmd == "copy":
        nc.copy(args.src, args.dst); jout({"ok": True, "action": "copy", "src": args.src, "dst": args.dst})

    elif args.cmd == "delete":
        nc.delete(args.path); jout({"ok": True, "action": "delete", "path": args.path})

    elif args.cmd == "exists":
        ok = nc.exists(args.path)
        jout({"exists": ok, "path": args.path})
        sys.exit(0 if ok else 1)

    elif args.cmd == "write":
        if args.file:
            content = Path(args.file).read_text()
        elif args.content is not None:
            content = args.content
        else:
            content = sys.stdin.read()
        if args.append:
            nc.append_to_file(args.path, content)
            jout({"ok": True, "action": "append", "path": args.path, "bytes": len(content.encode())})
        else:
            nc.write_file(args.path, content)
            jout({"ok": True, "action": "write", "path": args.path, "bytes": len(content.encode())})

    elif args.cmd == "read":
        print(nc.read_file(args.path))

    elif args.cmd == "ls":
        items = nc.list_dir(args.path, depth=args.depth)
        if args.human:
            for item in items:
                icon = "📁" if item["is_dir"] else "📄"
                fav  = "★ " if item["favorite"] else "  "
                size = f"{item['size']:>12,d}" if not item["is_dir"] else "            "
                print(f"{icon} {fav}{size}  {item['name']}")
        else:
            jout(items)

    elif args.cmd == "search":
        jout(nc.search(args.query, path=args.path, limit=args.limit))

    elif args.cmd == "favorite":
        nc.set_favorite(args.path, state=not args.off)
        jout({"ok": True, "action": "favorite", "path": args.path, "state": not args.off})

    elif args.cmd == "tags":
        jout(nc.get_tags())

    elif args.cmd == "tag-create":
        jout(nc.create_tag(args.name))

    elif args.cmd == "tag-assign":
        nc.assign_tag(args.file_id, args.tag_id)
        jout({"ok": True, "action": "tag-assign", "file_id": args.file_id, "tag_id": args.tag_id})

    elif args.cmd == "tag-remove":
        nc.remove_tag(args.file_id, args.tag_id)
        jout({"ok": True, "action": "tag-remove", "file_id": args.file_id, "tag_id": args.tag_id})

    elif args.cmd == "user":
        jout(nc.get_user_info())

    elif args.cmd == "quota":
        jout(nc.get_quota())

    elif args.cmd == "caps":
        jout(nc.get_capabilities())

    elif args.cmd == "config":
        jout({
            "config_file": str(CONFIG_FILE),
            "config_file_exists": CONFIG_FILE.exists(),
            "creds_file": str(CREDS_FILE),
            "creds_file_exists": CREDS_FILE.exists(),
            "active_config": nc.cfg,
            "base_url": nc.base_url,
            "user": nc.user,
        })


if __name__ == "__main__":
    _cli()
