#!/usr/bin/env python3
"""Upload a local file to DogeCloud OSS and print public access information."""

import argparse
import hashlib
import hmac
import json
import os
import re
import sys
import urllib.parse
from datetime import UTC, datetime


def build_authorization(api_path: str, body: str, access_key: str, secret_key: str) -> str:
    sign_str = f"{api_path}\n{body}"
    sign = hmac.new(secret_key.encode("utf-8"), sign_str.encode("utf-8"), hashlib.sha1).hexdigest()
    return f"TOKEN {access_key}:{sign}"


def dogecloud_api(
    api_path: str,
    data: dict,
    access_key: str,
    secret_key: str,
    *,
    method: str = "POST",
    json_mode: bool = True,
    timeout: float = 20,
) -> dict:
    import requests

    method = method.upper()
    if method == "GET":
        body = ""
        content_type = "application/x-www-form-urlencoded"
    elif json_mode:
        body = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        content_type = "application/json"
    else:
        body = urllib.parse.urlencode(data)
        content_type = "application/x-www-form-urlencoded"

    authorization = build_authorization(api_path, body, access_key, secret_key)
    headers = {
        "Authorization": authorization,
        "Content-Type": content_type,
    }
    url = f"https://api.dogecloud.com{api_path}"
    if method == "GET":
        response = requests.get(url, headers=headers, timeout=timeout)
    else:
        response = requests.post(url, data=body.encode("utf-8"), headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.json()


def md5_file(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_public_candidates(object_key: str, s3_bucket: str, s3_endpoint: str, public_base_url: str | None) -> list[str]:
    encoded_key = urllib.parse.quote(object_key, safe="/")
    candidates: list[str] = []
    if public_base_url:
        candidates.append(f"{public_base_url.rstrip('/')}/{encoded_key}")

    if re.search(r"-\d+$", s3_bucket):
        test_domain = f"{s3_bucket.rsplit('-', 1)[0]}.oss.dogecdn.com"
        candidates.append(f"https://{test_domain}/{encoded_key}")

    parsed = urllib.parse.urlparse(s3_endpoint)
    host = parsed.netloc or s3_endpoint.replace("https://", "").replace("http://", "")
    if host:
        candidates.append(f"https://{s3_bucket}.{host}/{encoded_key}")

    deduped: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload a local file to DogeCloud OSS and print public access information.",
    )
    parser.add_argument("file", help="Local file path to upload.")
    parser.add_argument("--bucket", help="DogeCloud bucket name or s3Bucket value.")
    parser.add_argument("--key", help="Target object key in bucket. Defaults to local filename.")
    parser.add_argument("--prefix", help="Default object key prefix when --key is omitted.")
    parser.add_argument("--endpoint", help="Expected S3 endpoint URL for validation.")
    parser.add_argument("--public-base-url", help="Custom public domain base URL, e.g. https://cdn.example.com.")
    parser.add_argument(
        "--scope",
        help="Scope key for tmp token. Defaults to the final object key. Supports wildcard like uploads/*.",
    )
    parser.add_argument(
        "--channel",
        default="OSS_UPLOAD",
        choices=["OSS_UPLOAD", "OSS_FULL"],
        help="Tmp token channel type. Default keeps least-privilege upload permissions.",
    )
    parser.add_argument("--ttl", type=int, default=3600, help="Tmp token ttl seconds. Range: 0-7200.")
    parser.add_argument("--content-type", help="Optional Content-Type for upload.")
    parser.add_argument("--timeout", type=float, default=20, help="HTTP timeout seconds.")
    parser.add_argument("--access-key-env", default="DOGECLOUD_ACCESS_KEY", help="AccessKey env variable name.")
    parser.add_argument("--secret-key-env", default="DOGECLOUD_SECRET_KEY", help="SecretKey env variable name.")
    parser.add_argument("--compact", action="store_true", help="Print compact JSON.")
    return parser.parse_args()


def first_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


def normalize_prefix(prefix: str | None) -> str | None:
    if not prefix:
        return None
    normalized = prefix.strip().strip("/")
    return normalized or None


def resolve_bucket_name(bucket_value: str, access_key: str, secret_key: str, timeout: float) -> str:
    bucket_list = dogecloud_api(
        "/oss/bucket/list.json",
        {},
        access_key,
        secret_key,
        method="GET",
        json_mode=False,
        timeout=timeout,
    )
    if bucket_list.get("code") != 200:
        raise RuntimeError(f"bucket list api failed: {bucket_list.get('msg', 'unknown error')}")

    buckets = bucket_list.get("data", {}).get("buckets", [])
    by_name = {item.get("name"): item for item in buckets}
    by_s3_bucket = {item.get("s3Bucket"): item for item in buckets}

    if bucket_value in by_name:
        return bucket_value
    if bucket_value in by_s3_bucket:
        return by_s3_bucket[bucket_value]["name"]

    all_names = sorted([item.get("name") for item in buckets if item.get("name")])
    raise RuntimeError(f"unknown bucket '{bucket_value}'. available bucket names={all_names}")


def main() -> int:
    args = parse_args()
    try:
        import boto3
        from botocore.config import Config
    except ModuleNotFoundError as exc:
        raise RuntimeError("missing dependency: boto3. install with `pip install boto3`.") from exc

    if not (0 <= args.ttl <= 7200):
        raise ValueError("--ttl must be in range 0..7200.")

    file_path = os.path.abspath(args.file)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"file not found: {file_path}")

    access_key = first_env(args.access_key_env, "accessKey")
    secret_key = first_env(args.secret_key_env, "secretKey")
    bucket_input = args.bucket or first_env("DOGECLOUD_BUCKET", "bucket")
    endpoint_expected = args.endpoint or first_env("DOGECLOUD_ENDPOINT", "endpoint")
    public_base_url = args.public_base_url or first_env("DOGECLOUD_PUBLIC_BASE_URL", "publicBaseUrl")
    prefix = normalize_prefix(args.prefix or first_env("DOGECLOUD_PREFIX", "prefix"))

    missing_items = []
    if not access_key:
        missing_items.append("DOGECLOUD_ACCESS_KEY (or accessKey)")
    if not secret_key:
        missing_items.append("DOGECLOUD_SECRET_KEY (or secretKey)")
    if not bucket_input:
        missing_items.append("DOGECLOUD_BUCKET (or bucket)")
    if not endpoint_expected:
        missing_items.append("DOGECLOUD_ENDPOINT (or endpoint)")
    # publicBaseUrl is OPTIONAL: without it we can still upload, we just won't be able to promise a stable public URL.
    if not args.key and not prefix:
        missing_items.append("DOGECLOUD_PREFIX (or prefix), or pass --key")
    if missing_items:
        raise RuntimeError(
            "missing required settings: "
            + ", ".join(missing_items)
            + ". Provide env vars (recommended): DOGECLOUD_ACCESS_KEY, DOGECLOUD_SECRET_KEY, DOGECLOUD_BUCKET, DOGECLOUD_ENDPOINT, DOGECLOUD_PREFIX. "
            + "Optional for stable public links: DOGECLOUD_PUBLIC_BASE_URL.",
        )

    if not public_base_url:
        # Still proceed, but we'll only be able to output endpoint-style candidate URLs.
        public_base_url = None

    bucket_name = resolve_bucket_name(bucket_input, access_key, secret_key, args.timeout)
    if args.key:
        object_key = args.key
    else:
        object_key = f"{prefix}/{os.path.basename(file_path)}"
    scope_key = args.scope or object_key
    scope = f"{bucket_name}:{scope_key}"

    token_res = dogecloud_api(
        "/auth/tmp_token.json",
        {
            "channel": args.channel,
            "scopes": [scope],
            "ttl": args.ttl,
        },
        access_key,
        secret_key,
        json_mode=True,
        timeout=args.timeout,
    )

    if token_res.get("code") != 200:
        raise RuntimeError(f"tmp_token api failed: {token_res.get('msg', 'unknown error')}")

    data = token_res["data"]
    bucket_candidates = data.get("Buckets", [])
    bucket_info = next((b for b in bucket_candidates if b.get("name") == bucket_name), None)
    if not bucket_info and len(bucket_candidates) == 1:
        bucket_info = bucket_candidates[0]
    if not bucket_info:
        names = [b.get("name") for b in bucket_candidates]
        raise RuntimeError(f"cannot resolve bucket '{bucket_name}' from tmp token response buckets={names}")

    creds = data["Credentials"]
    s3_bucket = bucket_info["s3Bucket"]
    s3_endpoint = bucket_info["s3Endpoint"]
    if endpoint_expected.rstrip("/") != s3_endpoint.rstrip("/"):
        raise RuntimeError(f"endpoint mismatch: env={endpoint_expected} tmp_token={s3_endpoint}")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=creds["accessKeyId"],
        aws_secret_access_key=creds["secretAccessKey"],
        aws_session_token=creds["sessionToken"],
        endpoint_url=s3_endpoint,
        config=Config(s3={"addressing_style": "virtual"}),
    )

    upload_kwargs = {}
    if args.content_type:
        upload_kwargs["ExtraArgs"] = {"ContentType": args.content_type}
    s3.upload_file(file_path, s3_bucket, object_key, **upload_kwargs)

    candidates = build_public_candidates(object_key, s3_bucket, s3_endpoint, public_base_url)
    notes = [
        "Prefer a custom domain via --public-base-url for stable production links.",
        "Derived .oss.dogecdn.com test domains may expire (typically 30 days for test domains).",
    ]
    primary_url = candidates[0] if candidates else None

    result = {
        "bucket": bucket_name,
        "s3_bucket": s3_bucket,
        "s3_endpoint": s3_endpoint,
        "object_key": object_key,
        "file": {
            "path": file_path,
            "size_bytes": os.path.getsize(file_path),
            "md5": md5_file(file_path),
        },
        "tmp_token": {
            "channel": args.channel,
            "scope": scope,
            "expired_at": data.get("ExpiredAt"),
        },
        "public_info": {
            "primary_url": primary_url,
            "candidates": candidates,
            "notes": notes,
            "used_public_base_url": bool(public_base_url),
        },
        "uploaded_at_utc": datetime.now(UTC).isoformat(),
    }

    if args.compact:
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
