#!/usr/bin/env python3
"""FGO.ro API CLI helper for invoice workflows."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://api.fgo.ro/v1"
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_RETRIES = 2
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATE_FIELDS = {"DataEmitere", "DataScadenta"}

def _platform_url() -> Optional[str]:
    """Return FGO_PLATFORM_URL env var if set, otherwise None (field omitted)."""
    return os.getenv("FGO_PLATFORM_URL") or None


class CliError(Exception):
    """Raised for user-facing CLI errors."""


class FgoApiError(Exception):
    """Raised when FGO responds with a non-success status or Success=false."""

    def __init__(self, status_code: int, body: bytes, headers: Optional[Dict[str, str]] = None):
        self.status_code = status_code
        self.body = body or b""
        self.headers = headers or {}
        super().__init__(f"FGO API request failed with status {status_code}")

    @property
    def body_text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


def _sha1_upper(text: str) -> str:
    """Return uppercase SHA-1 hex digest of the UTF-8 encoded text."""
    return hashlib.sha1(text.encode("utf-8")).hexdigest().upper()


def _hash_emitere(cod_unic: str, cheie_privata: str, denumire_client: str) -> str:
    """Hash formula for invoice issuance: SHA1(CodUnic + CheiePrivata + DenumireClient)."""
    return _sha1_upper(cod_unic + cheie_privata + denumire_client)


def _hash_invoice_op(cod_unic: str, cheie_privata: str, numar_factura: str) -> str:
    """Hash formula for invoice operations (print/cancel/delete/etc.): SHA1(CodUnic + CheiePrivata + NumarFactura)."""
    return _sha1_upper(cod_unic + cheie_privata + numar_factura)


def _hash_articole(cod_unic: str, cheie_privata: str) -> str:
    """Hash formula for article operations: SHA1(CodUnic + CheiePrivata)."""
    return _sha1_upper(cod_unic + cheie_privata)


@dataclass
class ClientConfig:
    cod_unic: str
    cheie_privata: str
    base_url: str
    timeout_seconds: int
    retries: int
    debug: bool = False

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "ClientConfig":
        cod_unic = getattr(args, "cod_unic", None) or os.getenv("FGO_COD_UNIC")
        cheie_privata = getattr(args, "cheie_privata", None) or os.getenv("FGO_CHEIE_PRIVATA")
        base_url_arg = getattr(args, "base_url", None)
        base_url = base_url_arg if base_url_arg is not None else os.getenv("FGO_API_BASE", DEFAULT_BASE_URL)
        timeout_raw: Any = getattr(args, "timeout_seconds", None) or os.getenv(
            "FGO_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS
        )
        retries_raw: Any = getattr(args, "retries", None) or os.getenv(
            "FGO_RETRIES", DEFAULT_RETRIES
        )
        debug = getattr(args, "debug", False) or os.getenv("FGO_DEBUG", "").lower() in ("1", "true", "yes")

        try:
            timeout = int(timeout_raw)
        except (TypeError, ValueError) as exc:
            raise CliError(
                f"Invalid timeout value '{timeout_raw}'. Use integer seconds > 0."
            ) from exc
        try:
            retries = int(retries_raw)
        except (TypeError, ValueError) as exc:
            raise CliError(
                f"Invalid retries value '{retries_raw}'. Use integer >= 0."
            ) from exc

        if not cod_unic:
            raise CliError(
                "Missing FGO CodUnic (CUI). Set FGO_COD_UNIC or pass --cod-unic."
            )
        if not cheie_privata:
            raise CliError(
                "Missing FGO CheiePrivata. Set FGO_CHEIE_PRIVATA or pass --cheie-privata."
            )
        if not base_url:
            raise CliError("FGO base URL cannot be empty.")
        if timeout <= 0:
            raise CliError("Timeout must be greater than 0 seconds.")
        if retries < 0:
            raise CliError("Retries must be 0 or greater.")

        return cls(
            cod_unic=cod_unic,
            cheie_privata=cheie_privata,
            base_url=base_url.rstrip("/"),
            timeout_seconds=timeout,
            retries=retries,
            debug=debug,
        )


class FgoClient:
    def __init__(self, config: ClientConfig):
        self.config = config

    def _request(
        self,
        method: str,
        path: str,
        query: Optional[Dict[str, Any]] = None,
        form_body: Optional[Dict[str, Any]] = None,
        expect_binary: bool = False,
    ) -> Tuple[Any, Dict[str, str]]:
        url = f"{self.config.base_url}{path}"
        if query:
            compact_query = {k: v for k, v in query.items() if v is not None}
            if compact_query:
                url = f"{url}?{urlencode(compact_query)}"

        payload: Optional[bytes] = None
        content_type = "application/x-www-form-urlencoded"
        if form_body is not None:
            flat = _flatten_form(form_body)
            payload = urlencode(flat).encode("utf-8")

        for attempt in range(self.config.retries + 1):
            headers: Dict[str, str] = {
                "Accept": "application/json",
            }
            if payload is not None:
                headers["Content-Type"] = content_type

            if self.config.debug:
                log_entry: Dict[str, Any] = {
                    "fgo_request": {
                        "attempt": attempt + 1,
                        "method": method,
                        "url": url,
                        "headers": headers,
                    }
                }
                if payload is not None:
                    log_entry["fgo_request"]["body"] = payload.decode("utf-8", errors="replace")
                print(json.dumps(log_entry, ensure_ascii=False), file=sys.stderr)

            request = Request(url=url, data=payload, headers=headers, method=method)
            try:
                with urlopen(request, timeout=self.config.timeout_seconds) as response:
                    response_body = response.read()
                    response_headers = dict(response.headers.items())

                    if self.config.debug:
                        try:
                            response_body_log: Any = json.loads(response_body.decode("utf-8"))
                        except Exception:
                            response_body_log = (
                                response_body.decode("utf-8", errors="replace")
                                if not expect_binary
                                else f"<binary {len(response_body)} bytes>"
                            )
                        print(
                            json.dumps(
                                {
                                    "fgo_response": {
                                        "status": response.status,
                                        "headers": response_headers,
                                        "body": response_body_log,
                                    }
                                },
                                ensure_ascii=False,
                            ),
                            file=sys.stderr,
                        )

                    if expect_binary:
                        return response_body, response_headers

                    if not response_body:
                        return {}, response_headers

                    text_body = response_body.decode("utf-8", errors="replace")
                    try:
                        return json.loads(text_body), response_headers
                    except json.JSONDecodeError:
                        return {"raw": text_body}, response_headers

            except HTTPError as exc:
                error_body = exc.read()
                error_headers = dict(exc.headers.items())
                if self.config.debug:
                    try:
                        error_body_log: Any = json.loads(error_body.decode("utf-8"))
                    except Exception:
                        error_body_log = error_body.decode("utf-8", errors="replace")
                    print(
                        json.dumps(
                            {
                                "fgo_response": {
                                    "status": exc.code,
                                    "headers": error_headers,
                                    "body": error_body_log,
                                }
                            },
                            ensure_ascii=False,
                        ),
                        file=sys.stderr,
                    )
                if exc.code in RETRYABLE_STATUS_CODES and attempt < self.config.retries:
                    time.sleep(2**attempt)
                    continue
                raise FgoApiError(exc.code, error_body, error_headers) from exc
            except URLError as exc:
                if self.config.debug:
                    print(
                        json.dumps(
                            {"fgo_error": {"attempt": attempt + 1, "reason": str(exc.reason)}},
                            ensure_ascii=False,
                        ),
                        file=sys.stderr,
                    )
                if attempt < self.config.retries:
                    time.sleep(2**attempt)
                    continue
                raise CliError(f"Network error calling FGO: {exc.reason}") from exc

        raise CliError("Request failed after retries.")

    def emit_invoice(self, payload: Dict[str, Any]) -> Tuple[Any, Dict[str, str]]:
        """POST /factura/emitere"""
        return self._request("POST", "/factura/emitere", form_body=payload)

    def print_invoice(self, payload: Dict[str, Any]) -> Tuple[Any, Dict[str, str]]:
        """POST /factura/print"""
        return self._request("POST", "/factura/print", form_body=payload)

    def delete_invoice(self, payload: Dict[str, Any]) -> Tuple[Any, Dict[str, str]]:
        """POST /factura/stergere"""
        return self._request("POST", "/factura/stergere", form_body=payload)

    def cancel_invoice(self, payload: Dict[str, Any]) -> Tuple[Any, Dict[str, str]]:
        """POST /factura/anulare"""
        return self._request("POST", "/factura/anulare", form_body=payload)

    def get_status(self, payload: Dict[str, Any]) -> Tuple[Any, Dict[str, str]]:
        """POST /factura/getstatus"""
        return self._request("POST", "/factura/getstatus", form_body=payload)

    def add_payment(self, payload: Dict[str, Any]) -> Tuple[Any, Dict[str, str]]:
        """POST /factura/incasare"""
        return self._request("POST", "/factura/incasare", form_body=payload)

    def reverse_invoice(self, payload: Dict[str, Any]) -> Tuple[Any, Dict[str, str]]:
        """POST /factura/stornare"""
        return self._request("POST", "/factura/stornare", form_body=payload)

    def get_nomenclator(self, resource: str) -> Tuple[Any, Dict[str, str]]:
        """GET /nomenclator/<resource>"""
        return self._request("GET", f"/nomenclator/{resource}")


def _flatten_form(obj: Any, prefix: str = "") -> List[Tuple[str, str]]:
    """Flatten a nested dict/list into URL-encoded form key-value pairs.

    Nested dicts produce bracketed keys:   {"Client": {"Denumire": "X"}} -> Client[Denumire]=X
    Lists produce indexed bracketed keys:  {"Continut": [{...}]}         -> Continut[0][Field]=V
    """
    result: List[Tuple[str, str]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{prefix}[{key}]" if prefix else key
            result.extend(_flatten_form(value, full_key))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            full_key = f"{prefix}[{idx}]"
            result.extend(_flatten_form(item, full_key))
    elif obj is None:
        pass
    else:
        result.append((prefix, str(obj).lower() if isinstance(obj, bool) else str(obj)))
    return result


def _is_relative_to(path: Path, root: Path) -> bool:
    """Return True if path is equal to or beneath root (Python 3.8 compat)."""
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _safe_input_path(input_path: Path) -> Path:
    """Resolve and validate the JSON input path.

    Two controls are applied:

    1. Must have a .json suffix — prevents reading files that can never
       legitimately be invoice payloads (/etc/passwd, ~/.ssh/id_rsa, …).
    2. Must resolve within an OpenClaw-allowed root or the current working
       directory — prevents a prompt-injected agent from reading arbitrary
       files even when the extension check alone would pass.

    OpenClaw allowed roots (mirrors src/media/local-roots.ts):
      - /tmp/openclaw (and /tmp/openclaw-<uid> fallback)
      - ~/.openclaw/media
      - ~/.openclaw/agents
      - ~/.openclaw/workspace  (and ~/.openclaw/workspace-<profile> variants)
      - ~/.openclaw/sandboxes
      - current working directory

    Raises CliError for any path that violates either constraint.
    """
    cwd = Path.cwd().resolve()
    resolved = (cwd / input_path).resolve()

    if resolved.suffix.lower() != ".json":
        raise CliError(
            f"Input path '{input_path}' must have a .json extension."
        )

    state_dir = Path(
        os.environ.get("OPENCLAW_STATE_DIR", Path.home() / ".openclaw")
    ).resolve()

    allowed_roots = [
        cwd,
        Path("/tmp/openclaw"),
        Path(f"/tmp/openclaw-{os.getuid()}"),
        state_dir / "media",
        state_dir / "agents",
        state_dir / "workspace",
        state_dir / "sandboxes",
    ]

    if not any(
        _is_relative_to(resolved, root.resolve()) for root in allowed_roots
    ):
        raise CliError(
            f"Input path '{input_path}' is not under an allowed directory. "
            "Use a path beneath the current working directory or an "
            "OpenClaw media root (/tmp/openclaw, ~/.openclaw/workspace, etc.)."
        )

    return resolved


def load_json(path: Path) -> Dict[str, Any]:
    safe_path = _safe_input_path(path)
    if not safe_path.exists():
        raise CliError(f"Input file not found: {path}")
    try:
        return json.loads(safe_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CliError(f"Invalid JSON in {path}: {exc}") from exc


def normalize_invoice_payload(
    raw_payload: Dict[str, Any],
    cod_unic_override: Optional[str],
    cheie_privata: str,
) -> Dict[str, Any]:
    """Accept either a bare invoice object or one wrapped under an 'invoice' key.
    Injects CodUnic and computes Hash for emitere."""
    invoice = raw_payload.get("invoice", raw_payload)
    if not isinstance(invoice, dict):
        raise CliError("Invalid invoice payload. Expected object or {\"invoice\": {...}}.")

    # Deep-copy via serialization to avoid mutating caller-owned nested objects.
    invoice = json.loads(json.dumps(invoice))

    if cod_unic_override:
        invoice["CodUnic"] = cod_unic_override

    cod_unic = invoice.get("CodUnic", "")
    if not cod_unic:
        raise CliError("CodUnic is required in the payload or via --cod-unic / FGO_COD_UNIC.")

    # Compute hash for emitere: SHA1(CodUnic + CheiePrivata + DenumireClient)
    denumire_client = ""
    client = invoice.get("Client")
    if isinstance(client, dict):
        denumire_client = str(client.get("Denumire", ""))

    invoice["Hash"] = _hash_emitere(cod_unic, cheie_privata, denumire_client)
    if "PlatformaUrl" not in invoice:
        url = _platform_url()
        if url:
            invoice["PlatformaUrl"] = url

    return invoice


def validate_invoice_payload(invoice: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """Validate an invoice payload for /factura/emitere."""
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(invoice, dict):
        return ["payload must be an invoice object"], []

    if not invoice.get("CodUnic"):
        errors.append("CodUnic is required.")
    if not invoice.get("Hash"):
        errors.append("Hash is required (computed automatically from CodUnic + CheiePrivata + Client.Denumire).")
    if not invoice.get("Valuta"):
        errors.append("Valuta is required (e.g. 'RON', 'EUR').")
    if not invoice.get("TipFactura"):
        errors.append("TipFactura is required (e.g. 'Factura').")
    if not invoice.get("Serie"):
        errors.append("Serie is required (invoice series as configured in FGO -> Setari -> Serii Documente).")

    client = invoice.get("Client")
    if not isinstance(client, dict):
        errors.append("Client must be an object.")
    else:
        if not client.get("Tip"):
            errors.append("Client.Tip is required: 'PF' (individual) or 'PJ' (legal entity).")
        if not client.get("Tara"):
            errors.append("Client.Tara is required (country name, e.g. 'Romania').")
        tara = str(client.get("Tara", "")).upper()
        if tara in ("ROMANIA", "RO") and not client.get("Judet"):
            errors.append("Client.Judet is required when Client.Tara is Romania.")

    continut = invoice.get("Continut")
    if not isinstance(continut, list) or not continut:
        errors.append("Continut must be a non-empty array of line items.")
    else:
        for idx, item in enumerate(continut, start=1):
            if not isinstance(item, dict):
                errors.append(f"Continut[{idx}] must be an object.")
                continue
            if not item.get("CodArticol"):
                errors.append(f"Continut[{idx}].CodArticol is required.")
            if not item.get("UM"):
                errors.append(f"Continut[{idx}].UM (unit of measure) is required.")
            if "NrProduse" not in item:
                errors.append(f"Continut[{idx}].NrProduse (quantity) is required.")
            elif item["NrProduse"] == 0:
                errors.append(f"Continut[{idx}].NrProduse must not be 0.")
            if "CotaTVA" not in item:
                errors.append(f"Continut[{idx}].CotaTVA (VAT rate) is required.")
            has_pret_unitar = "PretUnitar" in item
            has_pret_total = "PretTotal" in item
            if not has_pret_unitar and not has_pret_total:
                errors.append(
                    f"Continut[{idx}] requires either PretUnitar (classic) or PretTotal (reverse calculation)."
                )
            if has_pret_unitar and has_pret_total:
                warnings.append(
                    f"Continut[{idx}] has both PretUnitar and PretTotal. "
                    "Remove one: PretUnitar for classic calculation, PretTotal for reverse."
                )

    for field in DATE_FIELDS:
        val = invoice.get(field)
        if val and not DATE_RE.match(str(val)):
            errors.append(f"{field} must be in yyyy-mm-dd format.")

    return errors, warnings


def resolve_cod_unic(args: argparse.Namespace, invoice: Optional[Dict[str, Any]] = None) -> str:
    cod_unic = getattr(args, "cod_unic", None) or os.getenv("FGO_COD_UNIC")
    if not cod_unic and isinstance(invoice, dict):
        cod_unic = invoice.get("CodUnic")
    if not cod_unic:
        raise CliError(
            "Missing CodUnic (CUI). Set FGO_COD_UNIC, pass --cod-unic, or include CodUnic in payload."
        )
    return str(cod_unic)


def resolve_cheie_privata(args: argparse.Namespace) -> str:
    cheie = getattr(args, "cheie_privata", None) or os.getenv("FGO_CHEIE_PRIVATA")
    if not cheie:
        raise CliError(
            "Missing CheiePrivata. Set FGO_CHEIE_PRIVATA or pass --cheie-privata."
        )
    return str(cheie)


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------


def run_validate_payload(args: argparse.Namespace) -> int:
    raw = load_json(args.input)
    cheie_privata = resolve_cheie_privata(args)
    invoice = normalize_invoice_payload(raw, getattr(args, "cod_unic", None), cheie_privata)
    errors, warnings = validate_invoice_payload(invoice)

    output = {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "normalizedPayload": invoice if args.show_payload else None,
    }
    print_json(output)

    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


def run_emit_invoice(args: argparse.Namespace) -> int:
    raw = load_json(args.input)
    cheie_privata = resolve_cheie_privata(args)
    invoice = normalize_invoice_payload(raw, getattr(args, "cod_unic", None), cheie_privata)
    errors, warnings = validate_invoice_payload(invoice)
    if errors:
        raise CliError("Payload validation failed:\n- " + "\n- ".join(errors))
    if warnings:
        print("Warnings:", file=sys.stderr)
        for warning in warnings:
            print(f"- {warning}", file=sys.stderr)

    if not args.allow_final and not args.dry_run:
        raise CliError(
            "Refusing to issue invoice without --allow-final. "
            "Use --dry-run to inspect the payload first."
        )

    if args.dry_run:
        print_json({"dryRun": True, "payload": invoice})
        return 0

    config = ClientConfig.from_args(args)
    client = FgoClient(config)
    response, _headers = client.emit_invoice(invoice)

    if isinstance(response, dict) and not response.get("Success", True):
        print_json({"ok": False, "response": response})
        return 3

    print_json({"ok": True, "response": response})
    return 0


def run_get_status(args: argparse.Namespace) -> int:
    config = ClientConfig.from_args(args)
    client = FgoClient(config)
    cod_unic = resolve_cod_unic(args)
    cheie_privata = resolve_cheie_privata(args)

    payload = {
        "CodUnic": cod_unic,
        "Hash": _hash_invoice_op(cod_unic, cheie_privata, args.numar),
        "Numar": args.numar,
        "Serie": args.serie,
        "PlatformaUrl": _platform_url(),
    }
    response, _headers = client.get_status(payload)
    print_json({"ok": True, "response": response})
    return 0


def run_print_invoice(args: argparse.Namespace) -> int:
    config = ClientConfig.from_args(args)
    client = FgoClient(config)
    cod_unic = resolve_cod_unic(args)
    cheie_privata = resolve_cheie_privata(args)

    payload = {
        "CodUnic": cod_unic,
        "Hash": _hash_invoice_op(cod_unic, cheie_privata, args.numar),
        "Numar": args.numar,
        "Serie": args.serie,
        "PlatformaUrl": _platform_url(),
    }
    response, _headers = client.print_invoice(payload)
    print_json({"ok": True, "response": response})
    return 0


def run_cancel_invoice(args: argparse.Namespace) -> int:
    config = ClientConfig.from_args(args)
    client = FgoClient(config)
    cod_unic = resolve_cod_unic(args)
    cheie_privata = resolve_cheie_privata(args)

    payload = {
        "CodUnic": cod_unic,
        "Hash": _hash_invoice_op(cod_unic, cheie_privata, args.numar),
        "Numar": args.numar,
        "Serie": args.serie,
        "PlatformaUrl": _platform_url(),
    }
    response, _headers = client.cancel_invoice(payload)
    print_json({"ok": True, "response": response})
    return 0


def run_delete_invoice(args: argparse.Namespace) -> int:
    config = ClientConfig.from_args(args)
    client = FgoClient(config)
    cod_unic = resolve_cod_unic(args)
    cheie_privata = resolve_cheie_privata(args)

    payload = {
        "CodUnic": cod_unic,
        "Hash": _hash_invoice_op(cod_unic, cheie_privata, args.numar),
        "Numar": args.numar,
        "Serie": args.serie,
        "PlatformaUrl": _platform_url(),
    }
    response, _headers = client.delete_invoice(payload)
    print_json({"ok": True, "response": response})
    return 0


def run_reverse_invoice(args: argparse.Namespace) -> int:
    config = ClientConfig.from_args(args)
    client = FgoClient(config)
    cod_unic = resolve_cod_unic(args)
    cheie_privata = resolve_cheie_privata(args)

    payload: Dict[str, Any] = {
        "CodUnic": cod_unic,
        "Hash": _hash_invoice_op(cod_unic, cheie_privata, args.numar),
        "Numar": args.numar,
        "Serie": args.serie,
        "PlatformaUrl": _platform_url(),
    }
    if args.serie_storno:
        payload["SerieStorno"] = args.serie_storno
    if args.numar_storno:
        payload["NumarStorno"] = args.numar_storno
    if args.data_emitere:
        payload["DataEmitere"] = args.data_emitere

    response, _headers = client.reverse_invoice(payload)
    print_json({"ok": True, "response": response})
    return 0


def run_get_nomenclator(args: argparse.Namespace) -> int:
    config = ClientConfig.from_args(args)
    client = FgoClient(config)
    response, _headers = client.get_nomenclator(args.resource)
    print_json({"ok": True, "resource": args.resource, "response": response})
    return 0


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="FGO.ro API CLI for invoice automation."
    )
    parser.add_argument("--cod-unic", help="Company CUI (CodUnic). Defaults to FGO_COD_UNIC.")
    parser.add_argument(
        "--cheie-privata",
        help="FGO private API key (CheiePrivata). Defaults to FGO_CHEIE_PRIVATA.",
    )
    parser.add_argument(
        "--base-url",
        help=f"FGO API base URL. Default: {DEFAULT_BASE_URL}",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        help=f"Request timeout in seconds. Default: {DEFAULT_TIMEOUT_SECONDS}",
    )
    parser.add_argument(
        "--retries",
        type=int,
        help=f"Retry count for transient errors. Default: {DEFAULT_RETRIES}",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print request/response payloads to stderr. Also enabled by FGO_DEBUG=1. Off by default.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # validate-payload
    validate_parser = subparsers.add_parser(
        "validate-payload",
        help="Validate and normalize invoice payload without calling FGO.",
    )
    validate_parser.add_argument("--input", type=Path, required=True, help="Path to invoice JSON payload.")
    validate_parser.add_argument(
        "--show-payload",
        action="store_true",
        help="Include normalized payload (with computed Hash) in output.",
    )
    validate_parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as validation failures.",
    )
    validate_parser.set_defaults(func=run_validate_payload)

    # emit-invoice
    emit_parser = subparsers.add_parser(
        "emit-invoice",
        help="Issue an invoice via POST /factura/emitere.",
    )
    emit_parser.add_argument("--input", type=Path, required=True, help="Path to invoice JSON payload.")
    emit_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print normalized payload without API request.",
    )
    emit_parser.add_argument(
        "--allow-final",
        action="store_true",
        help="Allow issuing a real invoice (required to call the FGO API).",
    )
    emit_parser.set_defaults(func=run_emit_invoice)

    # get-status
    status_parser = subparsers.add_parser(
        "get-status",
        help="Get invoice status via POST /factura/getstatus.",
    )
    status_parser.add_argument("--numar", required=True, help="Invoice number.")
    status_parser.add_argument("--serie", required=True, help="Invoice series.")
    status_parser.set_defaults(func=run_get_status)

    # print-invoice
    print_parser = subparsers.add_parser(
        "print-invoice",
        help="Get invoice print link via POST /factura/print.",
    )
    print_parser.add_argument("--numar", required=True, help="Invoice number.")
    print_parser.add_argument("--serie", required=True, help="Invoice series.")
    print_parser.set_defaults(func=run_print_invoice)

    # cancel-invoice
    cancel_parser = subparsers.add_parser(
        "cancel-invoice",
        help="Cancel an invoice via POST /factura/anulare.",
    )
    cancel_parser.add_argument("--numar", required=True, help="Invoice number.")
    cancel_parser.add_argument("--serie", required=True, help="Invoice series.")
    cancel_parser.set_defaults(func=run_cancel_invoice)

    # delete-invoice
    delete_parser = subparsers.add_parser(
        "delete-invoice",
        help="Delete an invoice via POST /factura/stergere.",
    )
    delete_parser.add_argument("--numar", required=True, help="Invoice number.")
    delete_parser.add_argument("--serie", required=True, help="Invoice series.")
    delete_parser.set_defaults(func=run_delete_invoice)

    # reverse-invoice (storno)
    reverse_parser = subparsers.add_parser(
        "reverse-invoice",
        help="Create a storno (reversal) invoice via POST /factura/stornare.",
    )
    reverse_parser.add_argument("--numar", required=True, help="Number of the invoice to reverse.")
    reverse_parser.add_argument("--serie", required=True, help="Series of the invoice to reverse.")
    reverse_parser.add_argument("--serie-storno", help="Series for the storno invoice (optional).")
    reverse_parser.add_argument("--numar-storno", help="Number for the storno invoice (optional).")
    reverse_parser.add_argument(
        "--data-emitere",
        help="Issue date for the storno invoice (yyyy-mm-dd). Default: current date.",
    )
    reverse_parser.set_defaults(func=run_reverse_invoice)

    # get-nomenclator
    nom_parser = subparsers.add_parser(
        "get-nomenclator",
        help="Fetch a nomenclature list (no auth required).",
    )
    nom_parser.add_argument(
        "resource",
        choices=["tara", "judet", "tva", "banca", "tipincasare", "tipfactura", "tipclient", "valuta"],
        help="Nomenclature resource to fetch.",
    )
    nom_parser.set_defaults(func=run_get_nomenclator)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args)
    except CliError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except FgoApiError as exc:
        body_text = exc.body_text
        body_obj: Any
        try:
            body_obj = json.loads(body_text)
        except json.JSONDecodeError:
            body_obj = body_text
        print_json(
            {
                "ok": False,
                "statusCode": exc.status_code,
                "response": body_obj,
            }
        )
        return 3


if __name__ == "__main__":
    sys.exit(main())
