import os
import socket
import ssl
import sys
import xmlrpc.client
from typing import Any, Dict, Iterable, List, Optional

import requests


class OdooConnectionError(ConnectionError):
    pass


class _TimeoutTransport(xmlrpc.client.Transport):
    def __init__(self, timeout: int = 30, use_datetime: bool = False):
        super().__init__(use_datetime=use_datetime)
        self.timeout = timeout

    def make_connection(self, host):
        conn = super().make_connection(host)
        conn.timeout = self.timeout
        return conn


class _SafeTimeoutTransport(xmlrpc.client.SafeTransport):
    def __init__(self, timeout: int = 30, context: Optional[ssl.SSLContext] = None, use_datetime: bool = False):
        super().__init__(use_datetime=use_datetime, context=context)
        self.timeout = timeout

    def make_connection(self, host):
        conn = super().make_connection(host)
        conn.timeout = self.timeout
        return conn


class OdooClient:
    SAFE_METHODS = {
        "search",
        "search_read",
        "read",
        "search_count",
        "fields_get",
        "name_search",
        "context_get",
        "default_get",
    }

    BLOCKED_METHODS = {
        "create",
        "write",
        "unlink",
        "copy",
        "action_post",
        "action_confirm",
        "button_validate",
    }

    def __init__(
        self,
        url: str,
        db: str,
        username: str,
        password: str,
        *,
        timeout: int = 30,
        retries: int = 2,
        verify_ssl: bool = True,
        context: Optional[Dict[str, Any]] = None,
        rpc_backend: str = "xmlrpc",
    ):
        self.url = (url or "").rstrip("/")
        self.db = db
        self.username = username
        self.password = password
        self.timeout = timeout
        self.retries = retries
        self.verify_ssl = verify_ssl
        self.context = context or {}
        self.rpc_backend = (rpc_backend or "xmlrpc").lower()

        if self.rpc_backend not in {"xmlrpc", "json2"}:
            raise ValueError("rpc_backend must be one of: xmlrpc, json2")

        if not self.url:
            raise ValueError("ODOO_URL is required")

        self.uid: Optional[int] = None
        self.common = None
        self.models = None

        if self.rpc_backend == "xmlrpc":
            transport = self._build_transport(timeout=timeout, verify_ssl=verify_ssl)
            self.common = xmlrpc.client.ServerProxy(
                f"{self.url}/xmlrpc/2/common",
                allow_none=True,
                transport=transport,
            )
            self.models = xmlrpc.client.ServerProxy(
                f"{self.url}/xmlrpc/2/object",
                allow_none=True,
                transport=transport,
            )

    @classmethod
    def from_env(
        cls,
        *,
        timeout: int = 30,
        retries: int = 2,
        verify_ssl: bool = True,
        context: Optional[Dict[str, Any]] = None,
        rpc_backend: str = "xmlrpc",
    ) -> "OdooClient":
        url = os.getenv("ODOO_URL")
        db = os.getenv("ODOO_DB")
        user = os.getenv("ODOO_USER")
        pwd = os.getenv("ODOO_PASSWORD")

        if not all([url, db, user, pwd]):
            raise ValueError("Missing Odoo credentials in environment variables")

        return cls(
            url=url,
            db=db,
            username=user,
            password=pwd,
            timeout=timeout,
            retries=retries,
            verify_ssl=verify_ssl,
            context=context,
            rpc_backend=rpc_backend,
        )

    def _build_transport(self, timeout: int, verify_ssl: bool):
        is_https = self.url.startswith("https://")
        if is_https:
            ssl_context = None
            if not verify_ssl:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            return _SafeTimeoutTransport(timeout=timeout, context=ssl_context)
        return _TimeoutTransport(timeout=timeout)

    def _headers(self):
        return {
            "Authorization": f"bearer {self.password}",
            "X-Odoo-Database": self.db,
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "autonomous-cfo/1.0",
        }

    def _json2_call(self, model: str, method: str, payload: Optional[Dict[str, Any]] = None):
        payload = payload or {}
        if self.context:
            merged_context = dict(payload.get("context", {}))
            merged_context.update(self.context)
            payload["context"] = merged_context

        url = f"{self.url}/json/2/{model}/{method}"
        last_error = None
        attempts = max(0, int(self.retries)) + 1

        for _ in range(attempts):
            try:
                resp = requests.post(
                    url=url,
                    headers=self._headers(),
                    json=payload,
                    timeout=self.timeout,
                    verify=self.verify_ssl,
                )
                if resp.status_code >= 400:
                    raise OdooConnectionError(f"JSON-2 call failed ({resp.status_code}): {resp.text[:800]}")
                return resp.json()
            except (requests.Timeout, requests.ConnectionError, OSError, socket.timeout) as e:
                last_error = e
                continue
            except Exception as e:
                last_error = e
                break

        raise OdooConnectionError(f"JSON-2 call failed ({model}.{method}): {last_error}")

    def version(self) -> Dict[str, Any]:
        if self.rpc_backend == "xmlrpc":
            try:
                return self.common.version()
            except Exception as e:
                raise OdooConnectionError(f"Odoo version check failed: {e}")

        try:
            resp = requests.get(f"{self.url}/web/version", timeout=self.timeout, verify=self.verify_ssl)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise OdooConnectionError(f"Odoo version check failed: {e}")

    def authenticate(self, force: bool = False) -> bool:
        if self.uid and not force:
            return True

        if self.rpc_backend == "xmlrpc":
            try:
                uid = self.common.authenticate(self.db, self.username, self.password, {})
                self.uid = uid or None
                return bool(self.uid)
            except Exception as e:
                raise OdooConnectionError(f"Odoo authentication failed: {e}")

        try:
            ctx = self._json2_call("res.users", "context_get", {})
            self.uid = int(ctx.get("uid", 1)) if isinstance(ctx, dict) else 1
            return True
        except Exception as e:
            raise OdooConnectionError(f"Odoo JSON-2 authentication failed: {e}")

    def _ensure_auth(self):
        if not self.uid and not self.authenticate():
            raise OdooConnectionError("Authentication failed")

    def _assert_read_only_method(self, method: str):
        m = (method or "").strip().lower()
        if m in self.BLOCKED_METHODS:
            raise PermissionError(f"Blocked mutating method: {method}")
        if m not in self.SAFE_METHODS:
            raise PermissionError(
                f"Method not allowed in read-only mode: {method}. Allowed: {sorted(self.SAFE_METHODS)}"
            )

    def execute_kw(self, model: str, method: str, *args, **kwargs):
        self._ensure_auth()
        self._assert_read_only_method(method)

        if self.rpc_backend == "json2":
            payload: Dict[str, Any] = dict(kwargs) if kwargs else {}
            if method in {"search", "search_read"} and len(args) >= 1:
                payload.setdefault("domain", args[0])
            elif method == "read" and len(args) >= 1:
                payload.setdefault("ids", list(args[0]))
                if len(args) >= 2:
                    payload.setdefault("fields", args[1])
            elif method == "fields_get" and len(args) == 0:
                pass
            elif method == "create" and len(args) >= 1:
                payload.setdefault("values", args[0])
            elif method == "write" and len(args) >= 2:
                payload.setdefault("ids", list(args[0]))
                payload.setdefault("values", args[1])
            elif method == "unlink" and len(args) >= 1:
                payload.setdefault("ids", list(args[0]))
            elif method == "search_count" and len(args) >= 1:
                payload.setdefault("domain", args[0])
            else:
                raise ValueError(f"JSON-2 execute_kw cannot safely map positional args for {model}.{method}; use dedicated helper")

            return self._json2_call(model, method, payload)

        call_kwargs = dict(kwargs) if kwargs else {}
        if self.context:
            merged_ctx = dict(call_kwargs.get("context", {}))
            merged_ctx.update(self.context)
            call_kwargs["context"] = merged_ctx

        last_error = None
        attempts = max(0, int(self.retries)) + 1
        for _ in range(attempts):
            try:
                return self.models.execute_kw(
                    self.db,
                    self.uid,
                    self.password,
                    model,
                    method,
                    args,
                    call_kwargs,
                )
            except (socket.timeout, TimeoutError, OSError, xmlrpc.client.ProtocolError) as e:
                last_error = e
                continue
            except xmlrpc.client.Fault:
                raise
            except Exception as e:
                last_error = e
                break

        raise OdooConnectionError(f"execute_kw failed ({model}.{method}): {last_error}")

    def execute(self, model: str, method: str, *args, **kwargs):
        return self.execute_kw(model, method, *args, **kwargs)

    def search(self, model: str, domain: Optional[List] = None, *, limit: Optional[int] = None, offset: int = 0, order: Optional[str] = None):
        domain = domain or []
        kw = {"offset": offset}
        if limit is not None:
            kw["limit"] = limit
        if order:
            kw["order"] = order
        return self.execute_kw(model, "search", domain, **kw)

    def read(self, model: str, ids: Iterable[int], fields: Optional[List[str]] = None):
        if self.rpc_backend == "json2":
            payload: Dict[str, Any] = {"ids": list(ids)}
            if fields:
                payload["fields"] = fields
            return self._json2_call(model, "read", payload)

        kw = {}
        if fields:
            kw["fields"] = fields
        return self.execute_kw(model, "read", list(ids), **kw)

    def search_read(self, model: str, domain: Optional[List] = None, fields: Optional[List[str]] = None, limit: Optional[int] = None, offset: int = 0, order: Optional[str] = None):
        domain = domain or []
        kwargs: Dict[str, Any] = {"offset": offset}
        if fields:
            kwargs["fields"] = fields
        if limit is not None:
            kwargs["limit"] = limit
        if order:
            kwargs["order"] = order

        if self.rpc_backend == "json2":
            kwargs["domain"] = domain
            return self._json2_call(model, "search_read", kwargs)

        return self.execute_kw(model, "search_read", domain, **kwargs)

    def search_read_all(
        self,
        model: str,
        domain: Optional[List] = None,
        fields: Optional[List[str]] = None,
        *,
        order: Optional[str] = None,
        batch_size: int = 500,
    ) -> List[Dict[str, Any]]:
        domain = domain or []
        offset = 0
        rows: List[Dict[str, Any]] = []

        while True:
            chunk = self.search_read(
                model,
                domain=domain,
                fields=fields,
                limit=batch_size,
                offset=offset,
                order=order,
            )
            if not chunk:
                break
            rows.extend(chunk)
            if len(chunk) < batch_size:
                break
            offset += batch_size

        return rows

    def create(self, model: str, values: Dict[str, Any]):
        raise PermissionError("create is disabled: skill is enforced read-only")

    def write(self, model: str, ids: Iterable[int], values: Dict[str, Any]):
        raise PermissionError("write is disabled: skill is enforced read-only")

    def unlink(self, model: str, ids: Iterable[int]):
        raise PermissionError("unlink is disabled: skill is enforced read-only")

    def get_fields(self, model: str, attributes: Optional[List[str]] = None):
        attributes = attributes or ["string", "help", "type", "relation"]
        if self.rpc_backend == "json2":
            return self._json2_call(model, "fields_get", {"attributes": attributes})
        return self.execute_kw(model, "fields_get", [], attributes=attributes)

    def call_raw(self, model: str, method: str, payload: Optional[Dict[str, Any]] = None):
        """Advanced read-only escape hatch for power users."""
        self._ensure_auth()
        self._assert_read_only_method(method)
        payload = payload or {}

        if self.rpc_backend == "json2":
            return self._json2_call(model, method, payload)

        # xmlrpc fallback: support args/kwargs style payload
        args = payload.get("args", [])
        kwargs = payload.get("kwargs", {})
        if not isinstance(args, list):
            raise ValueError("payload.args must be a list for xmlrpc backend")
        if not isinstance(kwargs, dict):
            raise ValueError("payload.kwargs must be an object/dict for xmlrpc backend")
        return self.execute_kw(model, method, *args, **kwargs)


if __name__ == "__main__":
    from src.runtime_env import load_env_file

    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
    load_env_file(env_path)

    backend = os.getenv("ODOO_RPC_BACKEND", "xmlrpc")

    try:
        client = OdooClient.from_env(rpc_backend=backend)
    except Exception as e:
        print(f"Missing/invalid environment variables: {e}")
        sys.exit(1)

    try:
        version = client.version()
        print(f"✅ Connected. Backend={client.rpc_backend}. Server version: {version}")
        if client.authenticate():
            print(f"✅ Authenticated successfully! UID: {client.uid}")
            partners = client.search_read("res.partner", limit=5, fields=["name", "email"])
            print(f"Fetched {len(partners)} partners.")
            for p in partners:
                print(f"- {p['name']} ({p.get('email') or 'No email'})")
        else:
            print("❌ Authentication failed.")
            sys.exit(2)
    except Exception as e:
        print(f"❌ Odoo connection failed: {e}")
        sys.exit(2)
