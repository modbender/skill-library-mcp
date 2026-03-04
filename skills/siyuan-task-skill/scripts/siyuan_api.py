#!/usr/bin/env python3
"""SiYuan Note API Client - Base module for all SiYuan API operations."""

import json
import urllib.request
import urllib.error
from pathlib import Path


def load_config():
    """Load configuration from config.env file."""
    config = {}
    config_path = Path(__file__).parent.parent / "config.env"
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    return config


class SiYuanClient:
    """HTTP client for SiYuan Note API."""

    def __init__(self, config=None):
        cfg = config or load_config()
        self.base_url = cfg["SIYUAN_API_URL"]
        self.token = cfg["SIYUAN_API_TOKEN"]
        self.notebook_id = cfg.get("SIYUAN_NOTEBOOK_ID", "")
        if not self.notebook_id and cfg.get("SIYUAN_NOTEBOOK_NAME"):
            self.notebook_id = self._resolve_notebook_id(cfg["SIYUAN_NOTEBOOK_NAME"])

    def _resolve_notebook_id(self, name):
        """Find notebook ID by name."""
        r = self._post("/api/notebook/lsNotebooks")
        if r["code"] == 0:
            for nb in r["data"]["notebooks"]:
                if nb["name"] == name and not nb.get("closed"):
                    return nb["id"]
        raise RuntimeError(f"Notebook '{name}' not found")

    def _post(self, endpoint, payload=None):
        """Send POST request to SiYuan API."""
        url = f"{self.base_url}{endpoint}"
        data = json.dumps(payload or {}).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Token {self.token}")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            return {"code": -1, "msg": str(e), "data": None}
        return result

    # ── Notebook ──

    def list_notebooks(self):
        return self._post("/api/notebook/lsNotebooks")

    # ── SQL ──

    def sql_query(self, stmt):
        return self._post("/api/query/sql", {"stmt": stmt})

    # ── Document ──

    def create_doc(self, path, markdown=""):
        return self._post("/api/filetree/createDocWithMd", {
            "notebook": self.notebook_id,
            "path": path,
            "markdown": markdown,
        })

    def remove_doc(self, path):
        return self._post("/api/filetree/removeDoc", {
            "notebook": self.notebook_id,
            "path": path,
        })

    def remove_doc_by_id(self, doc_id):
        return self._post("/api/filetree/removeDocByID", {"id": doc_id})

    def rename_doc_by_id(self, doc_id, title):
        return self._post("/api/filetree/renameDocByID", {"id": doc_id, "title": title})

    def export_md(self, doc_id):
        return self._post("/api/export/exportMdContent", {"id": doc_id})

    # ── Block ──

    def append_block(self, parent_id, markdown):
        return self._post("/api/block/appendBlock", {
            "dataType": "markdown",
            "data": markdown,
            "parentID": parent_id,
        })

    def prepend_block(self, parent_id, markdown):
        return self._post("/api/block/prependBlock", {
            "dataType": "markdown",
            "data": markdown,
            "parentID": parent_id,
        })

    def insert_block(self, markdown, previous_id="", parent_id=""):
        return self._post("/api/block/insertBlock", {
            "dataType": "markdown",
            "data": markdown,
            "previousID": previous_id,
            "parentID": parent_id,
        })

    def update_block(self, block_id, markdown):
        return self._post("/api/block/updateBlock", {
            "dataType": "markdown",
            "data": markdown,
            "id": block_id,
        })

    def delete_block(self, block_id):
        return self._post("/api/block/deleteBlock", {"id": block_id})

    def get_block_kramdown(self, block_id):
        return self._post("/api/block/getBlockKramdown", {"id": block_id})

    def get_child_blocks(self, block_id):
        return self._post("/api/block/getChildBlocks", {"id": block_id})

    # ── Attributes ──

    def set_block_attrs(self, block_id, attrs):
        return self._post("/api/attr/setBlockAttrs", {
            "id": block_id,
            "attrs": attrs,
        })

    def get_block_attrs(self, block_id):
        return self._post("/api/attr/getBlockAttrs", {"id": block_id})

    # ── Asset ──

    def upload_asset(self, file_path, assets_dir="/assets/"):
        """Upload a file to SiYuan assets via multipart/form-data."""
        from pathlib import Path as P
        fp = P(file_path)
        boundary = "----SiYuanUploadBoundary"
        with open(fp, "rb") as f:
            file_data = f.read()
        body = b""
        body += f"--{boundary}\r\n".encode()
        body += b"Content-Disposition: form-data; name=\"assetsDirPath\"\r\n\r\n"
        body += f"{assets_dir}\r\n".encode()
        body += f"--{boundary}\r\n".encode()
        body += f"Content-Disposition: form-data; name=\"file[]\"; filename=\"{fp.name}\"\r\n".encode()
        body += b"Content-Type: application/octet-stream\r\n\r\n"
        body += file_data
        body += b"\r\n"
        body += f"--{boundary}--\r\n".encode()
        url = f"{self.base_url}/api/asset/upload"
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        req.add_header("Authorization", f"Token {self.token}")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            return {"code": -1, "msg": str(e), "data": None}
        return result

    # ── File ──

    def get_file(self, path):
        """Get a file from SiYuan data directory. Returns parsed JSON for .json files."""
        return self._post("/api/file/getFile", {"path": path})

    def put_file(self, path, data):
        """Write a file to SiYuan data directory via multipart/form-data."""
        filename = path.rsplit("/", 1)[-1]
        file_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        boundary = "----SiYuanPutFileBoundary"
        body = b""
        body += f"--{boundary}\r\n".encode()
        body += b"Content-Disposition: form-data; name=\"path\"\r\n\r\n"
        body += f"{path}\r\n".encode()
        body += f"--{boundary}\r\n".encode()
        body += (f"Content-Disposition: form-data; name=\"file\"; "
                 f"filename=\"{filename}\"\r\n").encode()
        body += b"Content-Type: application/json\r\n\r\n"
        body += file_bytes
        body += b"\r\n"
        body += f"--{boundary}--\r\n".encode()
        url = f"{self.base_url}/api/file/putFile"
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type",
                       f"multipart/form-data; boundary={boundary}")
        req.add_header("Authorization", f"Token {self.token}")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            return {"code": -1, "msg": str(e), "data": None}
        return result

    # ── Notification ──

    def push_msg(self, msg, timeout=7000):
        return self._post("/api/notification/pushMsg", {
            "msg": msg,
            "timeout": timeout,
        })

    def push_err_msg(self, msg, timeout=7000):
        return self._post("/api/notification/pushErrMsg", {
            "msg": msg,
            "timeout": timeout,
        })
