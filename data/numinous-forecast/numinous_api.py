# pyright: reportMissingImports=false
# pyright: reportMissingModuleSource=false

import base64
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

DEFAULT_BASE_URL = "https://api.numinouslabs.io"
JOBS_PATH = "/api/v1/forecasters/prediction-jobs"


class NuminousError(RuntimeError):
    pass


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def env_prefer_lane() -> str:
    """
    'auto' (default) | 'evm' | 'svm'
    """
    v = os.environ.get("NUMINOUS_X402_PREFER", "").strip().lower()
    return v or "auto"


def env_evm_private_key() -> str:
    """Return an EVM private key normalized to 0x-prefixed 32-byte hex.

    Accepts either:
    - 0x + 64 hex chars
    - 64 hex chars (will be prefixed with 0x)

    Any other format is returned as-is (and will likely fail downstream), but this
    normalization covers the most common footgun: forgetting the 0x prefix.
    """
    raw = os.environ.get("NUMINOUS_X402_EVM_PRIVATE_KEY", "").strip()
    if not raw:
        return ""
    v = raw
    if len(v) == 64:
        try:
            int(v, 16)
            return "0x" + v
        except Exception:
            return raw
    if v.startswith("0x") and len(v) == 66:
        try:
            int(v[2:], 16)
            return v
        except Exception:
            return raw
    return raw


def env_svm_private_key() -> str:
    return os.environ.get("NUMINOUS_X402_SVM_PRIVATE_KEY", "").strip()


def normalize_topics(topics: Optional[str]) -> Optional[list[str]]:
    if topics is None:
        return None
    t = topics.strip()
    if not t:
        return None
    parts = [p.strip() for p in t.replace(",", " ").split()]
    out = [p for p in parts if p]
    return out or None


def parse_cutoff_iso(s: str) -> str:
    v = s.strip()
    if not v:
        raise ValueError("cutoff is required")
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    dt = datetime.fromisoformat(v)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _b64json_decode(value: str) -> dict:
    raw = base64.b64decode(value)
    return json.loads(raw.decode("utf-8"))


def _header_get(headers: Any, name: str) -> Optional[str]:
    if headers is None:
        return None
    try:
        v = headers.get(name)
        return v if v is not None else None
    except Exception:
        pass
    try:
        for k, v in dict(headers).items():
            if str(k).lower() == name.lower():
                return str(v)
    except Exception:
        return None
    return None


def decode_payment_required(headers: Any) -> Optional[dict]:
    v = _header_get(headers, "payment-required")
    if not v:
        return None
    try:
        return _b64json_decode(v)
    except Exception as e:
        raise NuminousError(f"Failed to decode payment-required header: {e}") from e


def _summarize_accepts(accepts: list[Any]) -> dict:
    out: list[dict] = []
    for opt in accepts:
        if isinstance(opt, dict):
            out.append(
                {
                    "scheme": opt.get("scheme"),
                    "network": opt.get("network"),
                    "asset": opt.get("asset"),
                    "amount": opt.get("amount"),
                    "payTo": opt.get("payTo"),
                }
            )
        else:
            # pydantic models from x402
            out.append(
                {
                    "scheme": getattr(opt, "scheme", None),
                    "network": getattr(opt, "network", None),
                    "asset": getattr(opt, "asset", None),
                    "amount": getattr(opt, "amount", None),
                    "payTo": getattr(opt, "pay_to", None)
                    or getattr(opt, "payTo", None),
                }
            )

    return {"accepts": out}


def _choose_lane(accepts: list[Any]) -> str:
    prefer = env_prefer_lane()
    has_evm = bool(env_evm_private_key())
    has_svm = bool(env_svm_private_key())

    networks: list[str] = []
    for opt in accepts:
        if isinstance(opt, dict):
            networks.append(str(opt.get("network") or ""))
        else:
            networks.append(str(getattr(opt, "network", "") or ""))
    supports_evm = any(n.startswith("eip155:") for n in networks)
    supports_svm = any(n.startswith("solana:") for n in networks)

    if prefer == "evm":
        if not has_evm:
            raise NuminousError(
                "Missing NUMINOUS_X402_EVM_PRIVATE_KEY (required when NUMINOUS_X402_PREFER=evm)"
            )
        if not supports_evm:
            raise NuminousError(f"No EVM payment option offered (networks={networks})")
        return "evm"

    if prefer == "svm":
        if not has_svm:
            raise NuminousError(
                "Missing NUMINOUS_X402_SVM_PRIVATE_KEY (required when NUMINOUS_X402_PREFER=svm)"
            )
        if not supports_svm:
            raise NuminousError(
                f"No Solana payment option offered (networks={networks})"
            )
        return "svm"

    # auto
    if has_evm and supports_evm:
        return "evm"
    if has_svm and supports_svm:
        return "svm"

    if not has_evm and not has_svm:
        raise NuminousError(
            "Payment required (x402). Set NUMINOUS_X402_EVM_PRIVATE_KEY and/or NUMINOUS_X402_SVM_PRIVATE_KEY."
        )
    raise NuminousError(
        f"No compatible payment lane (prefer={prefer}, networks={networks})"
    )


def _build_x402_client_sync(lane: str):
    """
    Build a sync x402 client configured for either EVM or SVM exact payments.
    """
    from x402 import x402ClientSync

    client = x402ClientSync()
    if lane == "evm":
        from eth_account import Account
        from x402.mechanisms.evm import EthAccountSigner
        from x402.mechanisms.evm.exact.register import register_exact_evm_client

        pk = env_evm_private_key()
        if not pk:
            raise NuminousError("Missing NUMINOUS_X402_EVM_PRIVATE_KEY")
        account = Account.from_key(pk)
        return register_exact_evm_client(client, EthAccountSigner(account))

    if lane == "svm":
        from x402.mechanisms.svm import KeypairSigner
        from x402.mechanisms.svm.exact.register import register_exact_svm_client

        pk = env_svm_private_key()
        if not pk:
            raise NuminousError("Missing NUMINOUS_X402_SVM_PRIVATE_KEY")
        signer = KeypairSigner.from_base58(pk)
        return register_exact_svm_client(client, signer)

    raise NuminousError(f"Unknown lane: {lane}")


@dataclass(frozen=True)
class PollConfig:
    poll_interval_s: float = 5.0
    poll_timeout_s: float = 300.0
    initial_delay_s: float = 2.0


def _extract_prediction_id(created: dict) -> str:
    prediction_id = created.get("prediction_id") or created.get("predictionId")
    if not prediction_id:
        raise NuminousError(f"Unexpected create response: {created}")
    return str(prediction_id)


def _create_job_paid(base_url: str, payload: dict, timeout_s: float) -> dict:
    import httpx
    from x402.http import (
        PAYMENT_REQUIRED_HEADER,
        PAYMENT_SIGNATURE_HEADER,
        decode_payment_required_header,
        encode_payment_signature_header,
    )

    create_url = base_url.rstrip("/") + JOBS_PATH

    # Step 1: no-payment request, expect 402 + payment-required header
    with httpx.Client(timeout=timeout_s) as client:
        raw = client.post(create_url, json=payload)
        if raw.status_code != 402:
            # If this endpoint ever allows free calls, still handle it.
            try:
                return raw.json()
            except Exception as e:
                raise NuminousError(
                    f"Unexpected status {raw.status_code}: {e} body={raw.text[:500]}"
                ) from e

        header_value = raw.headers.get(PAYMENT_REQUIRED_HEADER) or raw.headers.get(
            "payment-required"
        )
        if not header_value:
            raise NuminousError("Got 402 but no payment-required header was present.")

        payment_required = decode_payment_required_header(header_value)
        accepts = list(getattr(payment_required, "accepts", []) or [])
        if not accepts:
            raise NuminousError("payment-required had no accepts options.")

        # Decide which wallet/signer to use
        try:
            lane = _choose_lane(accepts)
        except NuminousError as e:
            raise NuminousError(
                f"{e} payment_required={_summarize_accepts(accepts)}"
            ) from e

        # Filter accepts to the chosen lane so the client doesn't pick the wrong one.
        if lane == "evm":
            accepts = [
                opt
                for opt in accepts
                if str(getattr(opt, "network", "") or "").startswith("eip155:")
            ]
        else:
            accepts = [
                opt
                for opt in accepts
                if str(getattr(opt, "network", "") or "").startswith("solana:")
            ]
        payment_required.accepts = accepts  # pydantic model is mutable by default here

        x402_client = _build_x402_client_sync(lane)
        payment_payload = x402_client.create_payment_payload(payment_required)
        sig_header_value = encode_payment_signature_header(payment_payload)

        # Step 2: pay+retry with PAYMENT-SIGNATURE header
        paid = client.post(
            create_url,
            json=payload,
            headers={PAYMENT_SIGNATURE_HEADER: sig_header_value},
        )
        if paid.status_code >= 400:
            pr2_header = paid.headers.get(PAYMENT_REQUIRED_HEADER) or paid.headers.get(
                "payment-required"
            )
            if pr2_header:
                try:
                    pr2 = decode_payment_required_header(pr2_header)
                    pr2_accepts = list(getattr(pr2, "accepts", []) or [])
                except Exception:
                    pr2_accepts = []
            else:
                pr2_accepts = []
            raise NuminousError(
                f"x402 paid request failed (status={paid.status_code}). "
                f"payment_required={_summarize_accepts(pr2_accepts) if pr2_accepts else None} "
                f"body={paid.text[:500]}"
            )

        try:
            return paid.json()
        except Exception as e:
            raise NuminousError(
                f"Paid response was not JSON: {e} body={paid.text[:500]}"
            ) from e


def _poll_job(base_url: str, prediction_id: str, poll: PollConfig) -> dict:
    import httpx

    url = base_url.rstrip("/") + JOBS_PATH.rstrip("/") + "/" + str(prediction_id)
    if poll.initial_delay_s > 0:
        time.sleep(poll.initial_delay_s)

    start = time.time()
    last: Optional[dict] = None
    with httpx.Client(timeout=30.0) as client:
        while (time.time() - start) < poll.poll_timeout_s:
            time.sleep(poll.poll_interval_s)
            resp = client.get(url)
            try:
                data = resp.json()
            except Exception:
                raise NuminousError(
                    f"Polling returned non-JSON (status={resp.status_code}): {resp.text[:500]}"
                )
            last = data
            st = str((data.get("status") or "")).upper()
            if st == "COMPLETED" and data.get("result"):
                return {"ok": True, "fetched_at": _iso_now(), "job": data}
            if st == "FAILED":
                return {
                    "ok": False,
                    "fetched_at": _iso_now(),
                    "job": data,
                    "error": data.get("error") or "Prediction job failed",
                }

    return {
        "ok": False,
        "fetched_at": _iso_now(),
        "job": last,
        "error": f"Prediction job timed out after {poll.poll_timeout_s:.0f}s",
    }


def predict_job(
    base_url: str,
    forecaster_name: str,
    title: Optional[str],
    description: Optional[str],
    cutoff_iso: Optional[str],
    topics: Optional[list[str]],
    query: Optional[str],
    poll: PollConfig = PollConfig(),
) -> dict:
    """
    Create a prediction job (paid via x402) and poll until completion.
    Returns the completed job payload (including result).
    """
    payload: Dict[str, Any]

    if query:
        payload = {
            "forecaster_name": forecaster_name,
            "query": query,
        }
        if topics:
            payload["topics"] = topics
    else:
        if not (title and description and cutoff_iso):
            raise ValueError(
                "title, description, and cutoff are required when not using query mode"
            )
        payload = {
            "forecaster_name": forecaster_name,
            "title": title,
            "description": description,
            "cutoff": cutoff_iso,
        }
        if topics:
            payload["topics"] = topics

    created = _create_job_paid(base_url, payload, timeout_s=60.0)
    prediction_id = _extract_prediction_id(created)
    return _poll_job(base_url, prediction_id, poll=poll)
