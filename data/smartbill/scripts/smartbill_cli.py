#!/usr/bin/env python3
"""SmartBill API CLI helper for invoice workflows."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://ws.smartbill.ro/SBORO/api"
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_RETRIES = 2
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATE_FIELDS = {"issueDate", "dueDate", "deliveryDate", "paymentDate"}


class CliError(Exception):
    """Raised for user-facing CLI errors."""


class SmartBillApiError(Exception):
    """Raised when SmartBill responds with a non-success status."""

    def __init__(self, status_code: int, body: bytes, headers: Optional[Dict[str, str]] = None):
        self.status_code = status_code
        self.body = body or b""
        self.headers = headers or {}
        super().__init__(f"SmartBill API request failed with status {status_code}")

    @property
    def body_text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


@dataclass
class ClientConfig:
    username: str
    token: str
    base_url: str
    timeout_seconds: int
    retries: int

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "ClientConfig":
        username = args.username or os.getenv("SMARTBILL_USERNAME")
        token = args.token or os.getenv("SMARTBILL_TOKEN")
        base_url = args.base_url if args.base_url is not None else os.getenv("SMARTBILL_API_BASE", DEFAULT_BASE_URL)
        timeout_raw: Any = args.timeout_seconds if args.timeout_seconds is not None else os.getenv(
            "SMARTBILL_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS
        )
        retries_raw: Any = args.retries if args.retries is not None else os.getenv(
            "SMARTBILL_RETRIES", DEFAULT_RETRIES
        )

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

        if not username:
            raise CliError(
                "Missing SmartBill username. Set SMARTBILL_USERNAME or pass --username."
            )
        if not token:
            raise CliError(
                "Missing SmartBill token. Set SMARTBILL_TOKEN or pass --token."
            )
        if not base_url:
            raise CliError("SmartBill base URL cannot be empty.")
        if timeout <= 0:
            raise CliError("Timeout must be greater than 0 seconds.")
        if retries < 0:
            raise CliError("Retries must be 0 or greater.")

        return cls(
            username=username,
            token=token,
            base_url=base_url.rstrip("/"),
            timeout_seconds=timeout,
            retries=retries,
        )


class SmartBillClient:
    def __init__(self, config: ClientConfig):
        self.config = config
        auth_value = f"{config.username}:{config.token}".encode("utf-8")
        self._auth_header = f"Basic {base64.b64encode(auth_value).decode('ascii')}"

    def _request(
        self,
        method: str,
        path: str,
        query: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        accept: str = "application/json",
        expect_binary: bool = False,
    ) -> Tuple[Any, Dict[str, str]]:
        url = f"{self.config.base_url}{path}"
        if query:
            compact_query = {k: v for k, v in query.items() if v is not None}
            if compact_query:
                url = f"{url}?{urlencode(compact_query)}"

        payload: Optional[bytes] = None
        if json_body is not None:
            payload = json.dumps(json_body).encode("utf-8")

        for attempt in range(self.config.retries + 1):
            headers = {
                "Authorization": self._auth_header,
                "Accept": accept,
            }
            if payload is not None:
                headers["Content-Type"] = "application/json"

            # --- request debug log ---
            log_entry: Dict[str, Any] = {
                "smartbill_request": {
                    "attempt": attempt + 1,
                    "method": method,
                    "url": url,
                    "headers": {k: v for k, v in headers.items() if k != "Authorization"},
                }
            }
            if payload is not None:
                try:
                    log_entry["smartbill_request"]["body"] = json.loads(payload.decode("utf-8"))
                except Exception:
                    log_entry["smartbill_request"]["body"] = payload.decode("utf-8", errors="replace")
            print(json.dumps(log_entry, ensure_ascii=False), file=sys.stderr)

            request = Request(url=url, data=payload, headers=headers, method=method)
            try:
                with urlopen(request, timeout=self.config.timeout_seconds) as response:
                    response_body = response.read()
                    response_headers = dict(response.headers.items())

                    # --- response debug log ---
                    try:
                        response_body_log: Any = json.loads(response_body.decode("utf-8"))
                    except Exception:
                        response_body_log = response_body.decode("utf-8", errors="replace") if not expect_binary else f"<binary {len(response_body)} bytes>"
                    print(json.dumps({
                        "smartbill_response": {
                            "status": response.status,
                            "headers": response_headers,
                            "body": response_body_log,
                        }
                    }, ensure_ascii=False), file=sys.stderr)

                    if expect_binary:
                        return response_body, response_headers

                    if not response_body:
                        return {}, response_headers

                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        return json.loads(response_body.decode("utf-8")), response_headers

                    # API may return a plain string even when JSON is requested.
                    text_body = response_body.decode("utf-8", errors="replace")
                    try:
                        return json.loads(text_body), response_headers
                    except json.JSONDecodeError:
                        return {"raw": text_body}, response_headers
            except HTTPError as exc:
                error_body = exc.read()
                error_headers = dict(exc.headers.items())
                # --- error response debug log ---
                try:
                    error_body_log: Any = json.loads(error_body.decode("utf-8"))
                except Exception:
                    error_body_log = error_body.decode("utf-8", errors="replace")
                print(json.dumps({
                    "smartbill_response": {
                        "status": exc.code,
                        "headers": error_headers,
                        "body": error_body_log,
                    }
                }, ensure_ascii=False), file=sys.stderr)
                if exc.code in RETRYABLE_STATUS_CODES and attempt < self.config.retries:
                    time.sleep(2 ** attempt)
                    continue
                raise SmartBillApiError(exc.code, error_body, error_headers) from exc
            except URLError as exc:
                print(json.dumps({"smartbill_error": {"attempt": attempt + 1, "reason": str(exc.reason)}}, ensure_ascii=False), file=sys.stderr)
                if attempt < self.config.retries:
                    time.sleep(2 ** attempt)
                    continue
                raise CliError(f"Network error calling SmartBill: {exc.reason}") from exc

        raise CliError("Request failed after retries.")

    def create_invoice(self, invoice: Dict[str, Any]) -> Tuple[Any, Dict[str, str]]:
        """Send invoice object directly to POST /invoice (no wrapper key)."""
        return self._request(
            method="POST",
            path="/invoice",
            json_body=invoice,
            accept="application/json",
            expect_binary=False,
        )

    def get_series(self, cif: str, doc_type: Optional[str]) -> Tuple[Any, Dict[str, str]]:
        return self._request(
            method="GET",
            path="/series",
            query={"cif": cif, "type": doc_type},
            accept="application/json",
            expect_binary=False,
        )

    def download_invoice_pdf(self, cif: str, series_name: str, number: str) -> Tuple[bytes, Dict[str, str]]:
        data, headers = self._request(
            method="GET",
            path="/invoice/pdf",
            query={"cif": cif, "seriesName": series_name, "number": number},
            accept="application/octet-stream",
            expect_binary=True,
        )
        return data, headers


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise CliError(f"Input file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CliError(f"Invalid JSON in {path}: {exc}") from exc


def normalize_invoice_payload(
    raw_payload: Dict[str, Any],
    company_vat_code: Optional[str],
    force_draft: bool,
) -> Dict[str, Any]:
    # Accept either a bare invoice object or one wrapped under an "invoice" key.
    invoice = raw_payload.get("invoice", raw_payload)
    if not isinstance(invoice, dict):
        raise CliError("Invalid invoice payload. Expected object or {\"invoice\": {...}}.")

    # Copy through serialization to avoid mutating caller-owned nested objects.
    invoice = json.loads(json.dumps(invoice))

    if company_vat_code and not invoice.get("companyVatCode"):
        invoice["companyVatCode"] = company_vat_code
    if "isDraft" not in invoice:
        invoice["isDraft"] = False
    if force_draft:
        invoice["isDraft"] = True

    # Return the invoice object directly — the SmartBill API does not use a wrapper key.
    return invoice


def validate_invoice_payload(invoice: Dict[str, Any]) -> Tuple[list[str], list[str]]:
    """Validate a bare invoice object (not wrapped under an 'invoice' key)."""
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(invoice, dict):
        return ["payload must be an invoice object"], []

    if not invoice.get("companyVatCode"):
        errors.append("companyVatCode is required.")

    client = invoice.get("client")
    if not isinstance(client, dict):
        errors.append("client must be an object.")
    elif not client.get("name"):
        errors.append("client.name is required.")

    products = invoice.get("products")
    if not isinstance(products, list) or not products:
        errors.append("products must be a non-empty array.")
    else:
        for index, product in enumerate(products, start=1):
            if not isinstance(product, dict):
                errors.append(f"products[{index}] must be an object.")
                continue
            for key in ("name", "measuringUnitName"):
                if not product.get(key):
                    errors.append(f"products[{index}].{key} is required.")
            for key in ("quantity", "price"):
                if key not in product:
                    errors.append(f"products[{index}].{key} is required.")

    for field in DATE_FIELDS:
        if field in invoice and invoice[field] and not DATE_RE.match(str(invoice[field])):
            errors.append(f"{field} must be YYYY-MM-DD.")

    if not invoice.get("seriesName"):
        warnings.append("seriesName is not set; SmartBill default series will be used.")

    if invoice.get("isDraft") is False:
        warnings.append("isDraft is false; this will issue a final invoice.")

    return errors, warnings


def resolve_cif(args: argparse.Namespace, invoice: Optional[Dict[str, Any]] = None) -> str:
    cif = args.cif or os.getenv("SMARTBILL_COMPANY_VAT_CODE")
    if not cif and isinstance(invoice, dict):
        cif = invoice.get("companyVatCode")
    if not cif:
        raise CliError(
            "Missing company VAT code (CIF). Set SMARTBILL_COMPANY_VAT_CODE, pass --cif, "
            "or include companyVatCode in payload."
        )
    return str(cif)


def extract_rate_limits(headers: Dict[str, str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for key in ("X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"):
        value = headers.get(key)
        if value is not None:
            out[key] = value
    return out


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def run_validate_payload(args: argparse.Namespace) -> int:
    raw = load_json(args.input)
    invoice = normalize_invoice_payload(raw, args.cif, args.force_draft)
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


def run_create_invoice(args: argparse.Namespace) -> int:
    raw = load_json(args.input)
    invoice = normalize_invoice_payload(raw, args.cif, args.force_draft)
    errors, warnings = validate_invoice_payload(invoice)
    if errors:
        raise CliError("Payload validation failed:\n- " + "\n- ".join(errors))
    if warnings:
        print("Warnings:", file=sys.stderr)
        for warning in warnings:
            print(f"- {warning}", file=sys.stderr)

    is_draft = bool(invoice.get("isDraft"))
    if not is_draft and not args.allow_final and not args.dry_run:
        raise CliError(
            "Refusing to issue final invoice without --allow-final. "
            "Use --force-draft for safe testing."
        )

    if args.dry_run:
        print_json({"dryRun": True, "payload": invoice})
        return 0

    config = ClientConfig.from_args(args)
    client = SmartBillClient(config)
    response, headers = client.create_invoice(invoice)

    print_json(
        {
            "ok": True,
            "draft": is_draft,
            "response": response,
            "rateLimits": extract_rate_limits(headers),
        }
    )
    return 0


def run_get_series(args: argparse.Namespace) -> int:
    config = ClientConfig.from_args(args)
    client = SmartBillClient(config)
    cif = resolve_cif(args)
    response, headers = client.get_series(cif=cif, doc_type=args.type)
    print_json(
        {
            "ok": True,
            "cif": cif,
            "response": response,
            "rateLimits": extract_rate_limits(headers),
        }
    )
    return 0


def run_download_invoice_pdf(args: argparse.Namespace) -> int:
    config = ClientConfig.from_args(args)
    client = SmartBillClient(config)
    cif = resolve_cif(args)
    pdf_data, headers = client.download_invoice_pdf(
        cif=cif,
        series_name=args.series_name,
        number=args.number,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(pdf_data)
    print_json(
        {
            "ok": True,
            "cif": cif,
            "seriesName": args.series_name,
            "number": args.number,
            "outputPath": str(args.output),
            "sizeBytes": len(pdf_data),
            "rateLimits": extract_rate_limits(headers),
        }
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SmartBill API CLI for invoice automation."
    )
    parser.add_argument("--username", help="SmartBill login email. Defaults to SMARTBILL_USERNAME.")
    parser.add_argument("--token", help="SmartBill API token. Defaults to SMARTBILL_TOKEN.")
    parser.add_argument(
        "--base-url",
        help=f"SmartBill API base URL. Default: {DEFAULT_BASE_URL}",
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

    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate-payload",
        help="Validate and normalize invoice payload without calling SmartBill.",
    )
    validate_parser.add_argument("--input", type=Path, required=True, help="Path to invoice JSON payload.")
    validate_parser.add_argument("--cif", help="Company VAT code (CIF) override.")
    validate_parser.add_argument(
        "--force-draft",
        action="store_true",
        help="Force invoice.isDraft=true in normalized payload.",
    )
    validate_parser.add_argument(
        "--show-payload",
        action="store_true",
        help="Include normalized payload in output.",
    )
    validate_parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as validation failures.",
    )
    validate_parser.set_defaults(func=run_validate_payload)

    create_parser = subparsers.add_parser(
        "create-invoice",
        help="Create an invoice in SmartBill.",
    )
    create_parser.add_argument("--input", type=Path, required=True, help="Path to invoice JSON payload.")
    create_parser.add_argument("--cif", help="Company VAT code (CIF) override.")
    create_parser.add_argument(
        "--force-draft",
        action="store_true",
        help="Force invoice.isDraft=true before sending request.",
    )
    create_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print normalized payload without API request.",
    )
    create_parser.add_argument(
        "--allow-final",
        action="store_true",
        help="Allow creating final invoices (invoice.isDraft=false).",
    )
    create_parser.set_defaults(func=run_create_invoice)

    series_parser = subparsers.add_parser(
        "get-series",
        help="List document series configured in SmartBill.",
    )
    series_parser.add_argument("--cif", help="Company VAT code (CIF).")
    series_parser.add_argument(
        "--type",
        help="Document type filter for SmartBill /series endpoint.",
    )
    series_parser.set_defaults(func=run_get_series)

    pdf_parser = subparsers.add_parser(
        "download-invoice-pdf",
        help="Download an invoice PDF by series and number.",
    )
    pdf_parser.add_argument("--cif", help="Company VAT code (CIF).")
    pdf_parser.add_argument("--series-name", required=True, help="Invoice series name.")
    pdf_parser.add_argument("--number", required=True, help="Invoice number.")
    pdf_parser.add_argument("--output", type=Path, required=True, help="Output PDF path.")
    pdf_parser.set_defaults(func=run_download_invoice_pdf)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args)
    except CliError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except SmartBillApiError as exc:
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
