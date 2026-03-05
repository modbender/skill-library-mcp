#!/usr/bin/env python3
"""Detect signature blocks with NanoPDF and create a DocuSign envelope."""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def read_env(name: str, required: bool = True, default: str = "") -> str:
    value = os.getenv(name, default).strip()
    if required and not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def http_json(url: str, method: str, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = Request(url=url, method=method, data=data)
    req.add_header("Content-Type", "application/json")
    for key, value in headers.items():
        req.add_header(key, value)
    try:
        with urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {details}") from exc
    except URLError as exc:
        raise RuntimeError(f"Network error for {url}: {exc}") from exc


def load_signers(path: Path) -> List[Dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not raw:
        raise ValueError("Signer file must contain a non-empty JSON array.")
    signers: List[Dict[str, Any]] = []
    for idx, signer in enumerate(raw, start=1):
        if not isinstance(signer, dict):
            raise ValueError(f"Signer at index {idx - 1} is not an object.")
        name = str(signer.get("name", "")).strip()
        email = str(signer.get("email", "")).strip()
        if not name or not email:
            raise ValueError(f"Signer at index {idx - 1} must include non-empty name and email.")
        signers.append(
            {
                "key": str(signer.get("key", "")).strip(),
                "name": name,
                "email": email,
                "routing_order": int(signer.get("routing_order", idx)),
            }
        )
    return signers


def extract_signature_blocks(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    blocks = response.get("blocks", [])
    if not isinstance(blocks, list):
        raise ValueError("NanoPDF response must contain a list in `blocks`.")

    normalized: List[Dict[str, Any]] = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        if str(block.get("type", "")).lower() != "signature":
            continue
        try:
            page = int(block["page"])
            x = float(block["x"])
            y = float(block["y"])
        except (KeyError, ValueError, TypeError):
            continue
        normalized.append(
            {
                "id": str(block.get("id", "")).strip(),
                "page": page,
                "x": x,
                "y": y,
                "width": float(block.get("width", 160)),
                "height": float(block.get("height", 36)),
                "signer_key": str(block.get("signer_key", "")).strip(),
                "confidence": block.get("confidence"),
            }
        )

    if not normalized:
        raise ValueError("No signature blocks found in NanoPDF response.")
    return normalized


def map_blocks_to_signers(
    signers: List[Dict[str, Any]],
    blocks: List[Dict[str, Any]],
) -> List[Tuple[Dict[str, Any], List[Dict[str, Any]]]]:
    by_key: Dict[str, Dict[str, Any]] = {}
    for signer in signers:
        if signer["key"]:
            by_key[signer["key"]] = signer

    assignments: Dict[str, List[Dict[str, Any]]] = {signer["email"]: [] for signer in signers}
    unassigned: List[Dict[str, Any]] = []

    for block in blocks:
        signer_key = block["signer_key"]
        if signer_key and signer_key in by_key:
            signer = by_key[signer_key]
            assignments[signer["email"]].append(block)
        else:
            unassigned.append(block)

    signer_idx = 0
    for block in unassigned:
        signer = signers[signer_idx % len(signers)]
        assignments[signer["email"]].append(block)
        signer_idx += 1

    mapped: List[Tuple[Dict[str, Any], List[Dict[str, Any]]]] = []
    for signer in signers:
        signer_blocks = assignments[signer["email"]]
        if not signer_blocks:
            raise ValueError(
                f"Signer {signer['email']} has no assigned signature blocks. "
                "Provide signer_key values in NanoPDF output or adjust signer list/order."
            )
        mapped.append((signer, signer_blocks))
    return mapped


def to_docusign_payload(
    *,
    pdf_path: Path,
    pdf_b64: str,
    mapped: List[Tuple[Dict[str, Any], List[Dict[str, Any]]]],
    subject: str,
    message: str,
    status: str,
    scale: float,
) -> Dict[str, Any]:
    docusign_signers: List[Dict[str, Any]] = []

    for idx, (signer, blocks) in enumerate(mapped, start=1):
        tabs: List[Dict[str, str]] = []
        for block in blocks:
            tabs.append(
                {
                    "documentId": "1",
                    "pageNumber": str(block["page"]),
                    "xPosition": str(max(1, int(round(block["x"] * scale)))),
                    "yPosition": str(max(1, int(round(block["y"] * scale)))),
                }
            )

        docusign_signers.append(
            {
                "name": signer["name"],
                "email": signer["email"],
                "recipientId": str(idx),
                "routingOrder": str(signer["routing_order"]),
                "tabs": {"signHereTabs": tabs},
            }
        )

    payload: Dict[str, Any] = {
        "emailSubject": subject,
        "documents": [
            {
                "documentBase64": pdf_b64,
                "name": pdf_path.name,
                "fileExtension": "pdf",
                "documentId": "1",
            }
        ],
        "recipients": {"signers": docusign_signers},
        "status": status,
    }
    if message:
        payload["emailBlurb"] = message
    return payload


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Detect signature blocks with NanoPDF and send/create a DocuSign envelope."
    )
    p.add_argument("--pdf", required=True, help="Agreement PDF path")
    p.add_argument("--signers-json", required=True, help="Path to signer JSON array")
    p.add_argument("--subject", default="", help="DocuSign email subject override")
    p.add_argument("--message", default="", help="DocuSign email body")
    p.add_argument("--status", default="sent", choices=["sent", "created"], help="Envelope status")
    p.add_argument(
        "--scale",
        type=float,
        default=1.333333,
        help="Multiply NanoPDF coordinates before building DocuSign tabs",
    )
    p.add_argument(
        "--output-dir",
        default="output/openclaw-agreements",
        help="Directory for debug payload/output JSON files",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    pdf_path = Path(args.pdf)
    signer_path = Path(args.signers_json)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if not signer_path.exists():
        raise FileNotFoundError(f"Signer JSON not found: {signer_path}")

    nanopdf_base = read_env("NANOPDF_BASE_URL")
    nanopdf_key = read_env("NANOPDF_API_KEY")
    nanopdf_detect_path = read_env("NANOPDF_DETECT_PATH", required=False, default="/v1/signature-blocks")

    docusign_base = read_env("DOCUSIGN_BASE_URL")
    docusign_account_id = read_env("DOCUSIGN_ACCOUNT_ID")
    docusign_token = read_env("DOCUSIGN_ACCESS_TOKEN")

    subject = args.subject.strip() or read_env(
        "DOCUSIGN_ENVELOPE_SUBJECT",
        required=False,
        default=f"Please sign: {pdf_path.name}",
    )

    message = args.message.strip() or read_env("DOCUSIGN_ENVELOPE_BODY", required=False, default="")

    pdf_bytes = pdf_path.read_bytes()
    pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")

    signers = load_signers(signer_path)

    detect_url = f"{nanopdf_base.rstrip('/')}/{nanopdf_detect_path.lstrip('/')}"
    nanopdf_payload = {
        "document_name": pdf_path.name,
        "document_base64": pdf_b64,
        "labels": ["signature"],
    }
    nanopdf_response = http_json(
        url=detect_url,
        method="POST",
        payload=nanopdf_payload,
        headers={"Authorization": f"Bearer {nanopdf_key}"},
    )

    blocks = extract_signature_blocks(nanopdf_response)
    mapped = map_blocks_to_signers(signers, blocks)

    docusign_payload = to_docusign_payload(
        pdf_path=pdf_path,
        pdf_b64=pdf_b64,
        mapped=mapped,
        subject=subject,
        message=message,
        status=args.status,
        scale=args.scale,
    )

    envelope_url = f"{docusign_base.rstrip('/')}/restapi/v2.1/accounts/{docusign_account_id}/envelopes"
    envelope_result = http_json(
        url=envelope_url,
        method="POST",
        payload=docusign_payload,
        headers={"Authorization": f"Bearer {docusign_token}"},
    )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "nanopdf_blocks.json").write_text(json.dumps(blocks, indent=2), encoding="utf-8")
    (out_dir / "docusign_payload.json").write_text(
        json.dumps(docusign_payload, indent=2),
        encoding="utf-8",
    )
    (out_dir / "envelope_result.json").write_text(
        json.dumps(envelope_result, indent=2),
        encoding="utf-8",
    )

    envelope_id = envelope_result.get("envelopeId", "<unknown>")
    print(f"Envelope created: {envelope_id}")
    print(f"Artifacts written to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
