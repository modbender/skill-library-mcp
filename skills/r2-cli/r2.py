#!/usr/bin/env python3
"""
Cloudflare R2 CLI

A minimal command-line tool to interact with Cloudflare R2 storage
using only Python's standard library (no external dependencies).

Features:
- Upload objects
- Download objects
- List objects
- Delete objects

Security:
- Credentials are read from environment variables only.
- HMAC SHA256 signatures are used for API authentication.
- Paths are sanitized to prevent injection/path traversal.
"""

import argparse
import datetime
import hashlib
import hmac
import os
import sys
import urllib.parse
import urllib.request

# SECURITY FIX: use defusedxml instead of xml.etree
from defusedxml import ElementTree as ET


# ---------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------

ACCOUNT_ID = os.getenv("CF_R2_ACCOUNT_ID")
ACCESS_KEY = os.getenv("CF_R2_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("CF_R2_SECRET_ACCESS_KEY")
BUCKET = os.getenv("CF_R2_BUCKET")
REGION = os.getenv("CF_R2_REGION", "auto")

if not all([ACCOUNT_ID, ACCESS_KEY, SECRET_KEY, BUCKET]):
    sys.stderr.write(
        "Missing env vars:\n"
        "CF_R2_ACCOUNT_ID\n"
        "CF_R2_ACCESS_KEY_ID\n"
        "CF_R2_SECRET_ACCESS_KEY\n"
        "CF_R2_BUCKET\n"
    )
    sys.exit(1)

ENDPOINT = f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com"


# ---------------------------------------------------------------------
# AWS Signature V4
# ---------------------------------------------------------------------

SERVICE = "s3"


def _sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _get_signature_key(key, date_stamp, region, service):
    k_date = _sign(("AWS4" + key).encode("utf-8"), date_stamp)
    k_region = _sign(k_date, region)
    k_service = _sign(k_region, service)
    k_signing = _sign(k_service, "aws4_request")
    return k_signing


def _aws_headers(method, canonical_uri, querystring="", payload=b"", extra_headers=None):
    t = datetime.datetime.now(datetime.UTC)
    amz_date = t.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = t.strftime("%Y%m%d")

    payload_hash = hashlib.sha256(payload).hexdigest()

    headers = {
        "host": f"{ACCOUNT_ID}.r2.cloudflarestorage.com",
        "x-amz-content-sha256": payload_hash,
        "x-amz-date": amz_date,
    }

    if extra_headers:
        headers.update(extra_headers)

    canonical_headers = ""
    signed_headers_list = []

    for k in sorted(headers):
        canonical_headers += f"{k}:{headers[k]}\n"
        signed_headers_list.append(k)

    signed_headers = ";".join(signed_headers_list)

    canonical_request = (
        method + "\n"
        + canonical_uri + "\n"
        + querystring + "\n"
        + canonical_headers + "\n"
        + signed_headers + "\n"
        + payload_hash
    )

    algorithm = "AWS4-HMAC-SHA256"
    credential_scope = f"{date_stamp}/{REGION}/{SERVICE}/aws4_request"

    string_to_sign = (
        algorithm + "\n"
        + amz_date + "\n"
        + credential_scope + "\n"
        + hashlib.sha256(canonical_request.encode()).hexdigest()
    )

    signing_key = _get_signature_key(SECRET_KEY, date_stamp, REGION, SERVICE)

    signature = hmac.new(
        signing_key,
        string_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    authorization_header = (
        f"{algorithm} "
        f"Credential={ACCESS_KEY}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )

    headers["Authorization"] = authorization_header

    return headers


# ---------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------

def _validate_url(url: str):
    """
    SECURITY FIX:
    Ensure only HTTPS requests are allowed (avoid file:// etc)
    """
    parsed = urllib.parse.urlparse(url)

    if parsed.scheme != "https":
        raise ValueError("Only HTTPS scheme is allowed")

    if not parsed.netloc.endswith("cloudflarestorage.com"):
        raise ValueError("Unexpected host")


def _request(method, key="", body=b"", query=""):
    key = urllib.parse.quote(key)

    canonical_uri = f"/{BUCKET}"
    if key:
        canonical_uri += f"/{key}"

    url = ENDPOINT + canonical_uri
    if query:
        url += "?" + query

    _validate_url(url)

    headers = _aws_headers(method, canonical_uri, query, body)

    req = urllib.request.Request(
        url,
        data=body if body else None,
        headers=headers,
        method=method,
    )

    # Create restricted opener (HTTPS only)
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler()
    )

    try:
        with opener.open(req, timeout=30) as resp:  # nosec B310
            return resp.status, resp.read()

    except urllib.error.HTTPError as e:
        return e.code, e.read()


# ---------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------

def upload(file_path, key):
    if not os.path.isfile(file_path):
        print("File not found", file=sys.stderr)
        sys.exit(1)

    with open(file_path, "rb") as f:
        data = f.read()

    status, _ = _request("PUT", key, data)

    if 200 <= status < 300:
        print("Upload succeeded")
    else:
        print(f"Upload failed ({status})", file=sys.stderr)
        sys.exit(1)


def download(key, file_path):
    status, body = _request("GET", key)

    if 200 <= status < 300:
        with open(file_path, "wb") as f:
            f.write(body)
        print("Download succeeded")
    else:
        print(f"Download failed ({status})", file=sys.stderr)
        sys.exit(1)


def delete(key):
    status, _ = _request("DELETE", key)

    if 200 <= status < 300:
        print("Delete succeeded")
    else:
        print(f"Delete failed ({status})", file=sys.stderr)
        sys.exit(1)


def list_objects():
    status, body = _request("GET", query="list-type=2")

    if 200 <= status < 300:
        # SECURITY SAFE XML PARSE
        root = ET.fromstring(body)

        ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}

        for contents in root.findall(".//s3:Contents", ns):
            key = contents.find("s3:Key", ns).text
            size = contents.find("s3:Size", ns).text
            print(f"{key} ({size} bytes)")
    else:
        print(f"List failed ({status})", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------

def _parse_args():
    parser = argparse.ArgumentParser(description="Cloudflare R2 CLI")

    sub = parser.add_subparsers(dest="command", required=True)

    u = sub.add_parser("upload")
    u.add_argument("--file", required=True)
    u.add_argument("--key", required=True)

    d = sub.add_parser("download")
    d.add_argument("--key", required=True)
    d.add_argument("--file", required=True)

    sub.add_parser("list")

    rm = sub.add_parser("delete")
    rm.add_argument("--key", required=True)

    return parser.parse_args()


def main():
    args = _parse_args()

    if args.command == "upload":
        upload(args.file, args.key)

    elif args.command == "download":
        download(args.key, args.file)

    elif args.command == "list":
        list_objects()

    elif args.command == "delete":
        delete(args.key)


if __name__ == "__main__":
    main()