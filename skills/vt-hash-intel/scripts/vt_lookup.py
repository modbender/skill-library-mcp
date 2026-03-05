#!/usr/bin/env python3
"""
VirusTotal IOC Lookup Script for OpenClaw — vt-hash-intel skill
Queries VT API v3 for file hashes, URLs, domains, and IP addresses.

Usage:
    python3 vt_lookup.py <ioc>                     # Single IOC (auto-detect type)
    python3 vt_lookup.py <ioc1> <ioc2> ...         # Batch lookup
    python3 vt_lookup.py --stdin                   # Read IOCs from stdin
    python3 vt_lookup.py --file iocs.txt           # Read IOCs from file
    python3 vt_lookup.py --type hash <value>       # Force IOC type

Environment:
    VT_API_KEY - VirusTotal API key (required)

Output: JSON to stdout
"""

import os
import sys
import json
import re
import time
import hashlib
import base64
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
VT_API_BASE = "https://www.virustotal.com/api/v3"
RATE_LIMIT_DELAY = 16   # seconds between requests (free tier = 4/min)
MAX_DETECTIONS_IN_OUTPUT = 30
MAX_RETRIES = 2
RETRY_WAIT = 60


# ---------------------------------------------------------------------------
# IOC type detection
# ---------------------------------------------------------------------------
HASH_PATTERNS = {
    "md5":    re.compile(r"^[a-fA-F0-9]{32}$"),
    "sha1":   re.compile(r"^[a-fA-F0-9]{40}$"),
    "sha256": re.compile(r"^[a-fA-F0-9]{64}$"),
}

IPV4_PATTERN = re.compile(
    r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$"
)

# Simple domain pattern (not starting with http, contains at least one dot)
DOMAIN_PATTERN = re.compile(
    r"^(?!http)[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$"
)

URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)


def detect_ioc_type(value):
    # type: (str) -> Tuple[str, Optional[str]]
    """
    Detect IOC type from the value.
    Returns: (ioc_type, hash_subtype)
      ioc_type: "hash" | "url" | "domain" | "ip" | "unknown"
      hash_subtype: "md5" | "sha1" | "sha256" | None
    """
    value = value.strip()

    # Check hash first
    for hash_name, pattern in HASH_PATTERNS.items():
        if pattern.match(value):
            return ("hash", hash_name)

    # Check URL
    if URL_PATTERN.match(value):
        return ("url", None)

    # Check IPv4
    if IPV4_PATTERN.match(value):
        return ("ip", None)

    # Check domain
    if DOMAIN_PATTERN.match(value):
        return ("domain", None)

    return ("unknown", None)


def get_vt_url_id(url_string):
    # type: (str) -> str
    """
    VT API requires URL identifier = base64url(url) without padding.
    See: https://docs.virustotal.com/reference/url
    """
    url_bytes = url_string.encode("utf-8")
    url_id = base64.urlsafe_b64encode(url_bytes).rstrip(b"=").decode("ascii")
    return url_id


# ---------------------------------------------------------------------------
# API interaction
# ---------------------------------------------------------------------------
def get_api_key():
    # type: () -> str
    key = os.environ.get("VT_API_KEY", "").strip()
    if not key:
        raise EnvironmentError(
            "VT_API_KEY environment variable is not set. "
            "Get your free key at https://www.virustotal.com/gui/my-apikey"
        )
    return key


def vt_api_get(endpoint, api_key):
    # type: (str, str) -> Dict[str, Any]
    """
    Generic GET request to VT API v3 with retry on 429.
    """
    url = "{}{}".format(VT_API_BASE, endpoint)
    req = urllib.request.Request(url, headers={
        "x-apikey": api_key,
        "Accept": "application/json",
    })

    for attempt in range(MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode()
            except Exception:
                pass

            if e.code == 404:
                return {"error": "NotFoundError", "message": "Not found in VirusTotal database"}
            elif e.code == 401:
                return {"error": "AuthenticationError", "message": "Invalid or missing API key"}
            elif e.code == 429:
                if attempt < MAX_RETRIES:
                    sys.stderr.write(
                        "[vt-hash-intel] Rate limited, waiting {}s ({}/{})...\n".format(
                            RETRY_WAIT, attempt + 1, MAX_RETRIES
                        )
                    )
                    time.sleep(RETRY_WAIT)
                    continue
                return {"error": "QuotaExceededError", "message": "API rate limit exceeded after retries"}
            else:
                return {"error": "HTTPError_{}".format(e.code), "message": body[:500]}
        except urllib.error.URLError as e:
            return {"error": "ConnectionError", "message": str(e.reason)}
        except Exception as e:
            return {"error": "UnexpectedError", "message": str(e)}

    return {"error": "UnexpectedError", "message": "Max retries exceeded"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def parse_timestamp(ts):
    # type: (Any) -> Optional[str]
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, TypeError, OSError):
        return str(ts)


def format_size(size_bytes):
    # type: (int) -> str
    if size_bytes < 1024:
        return "{} B".format(size_bytes)
    elif size_bytes < 1024 * 1024:
        return "{:.1f} KB".format(size_bytes / 1024)
    elif size_bytes < 1024 * 1024 * 1024:
        return "{:.1f} MB".format(size_bytes / (1024 * 1024))
    else:
        return "{:.2f} GB".format(size_bytes / (1024 * 1024 * 1024))


def classify_threat(malicious, suspicious):
    # type: (int, int) -> Tuple[str, str]
    if malicious == 0 and suspicious == 0:
        return ("clean", "✅")
    elif malicious <= 5:
        return ("low", "⚠️")
    elif malicious <= 15:
        return ("medium", "🟠")
    else:
        return ("high", "🔴")


def extract_analysis_stats(attrs):
    # type: (Dict[str, Any]) -> Dict[str, Any]
    """Extract last_analysis_stats and detection list from attributes."""
    stats = attrs.get("last_analysis_stats", {})
    malicious = stats.get("malicious", 0)
    suspicious = stats.get("suspicious", 0)
    undetected = stats.get("undetected", 0)
    harmless = stats.get("harmless", 0)
    timeout = stats.get("timeout", 0)
    failure = stats.get("failure", 0)
    type_unsupported = stats.get("type-unsupported", 0)

    total = malicious + suspicious + undetected + harmless + timeout + failure + type_unsupported

    # Engine detections
    last_analysis = attrs.get("last_analysis_results", {})
    detections = []
    for engine_name, result in last_analysis.items():
        cat = result.get("category", "")
        if cat in ("malicious", "suspicious"):
            detections.append({
                "engine": engine_name,
                "category": cat,
                "result": result.get("result", ""),
            })

    detections.sort(key=lambda d: (0 if d["category"] == "malicious" else 1, d["engine"]))
    total_detecting = len(detections)
    if len(detections) > MAX_DETECTIONS_IN_OUTPUT:
        detections = detections[:MAX_DETECTIONS_IN_OUTPUT]

    threat_level, threat_emoji = classify_threat(malicious, suspicious)

    return {
        "detection_stats": {
            "malicious": malicious,
            "suspicious": suspicious,
            "undetected": undetected,
            "harmless": harmless,
            "timeout": timeout,
            "failure": failure,
            "type_unsupported": type_unsupported,
        },
        "detection_ratio": "{}/{}".format(malicious, total),
        "total_detecting_engines": total_detecting,
        "threat_level": threat_level,
        "threat_emoji": threat_emoji,
        "detections": detections,
    }


# ---------------------------------------------------------------------------
# Parsers for each IOC type
# ---------------------------------------------------------------------------
def parse_hash_report(raw, queried_value):
    # type: (Dict[str, Any], str) -> Dict[str, Any]
    if "error" in raw and "data" not in raw:
        return {
            "ioc": queried_value,
            "ioc_type": "hash",
            "error": raw.get("error"),
            "error_message": raw.get("message", ""),
        }

    attrs = raw.get("data", {}).get("attributes", {})

    sha256 = attrs.get("sha256", "")
    sha1 = attrs.get("sha1", "")
    md5 = attrs.get("md5", "")
    file_size = attrs.get("size")
    file_type = attrs.get("type_description") or attrs.get("type_tag", "unknown")
    magic = attrs.get("magic", "")
    meaningful_name = attrs.get("meaningful_name", "")
    names = attrs.get("names", [])
    file_name = meaningful_name or (names[0] if names else "unknown")

    # Threat classification
    popular_threat = attrs.get("popular_threat_classification", {})
    threat_label = popular_threat.get("suggested_threat_label", None)
    popular_threat_name = None
    top_names = popular_threat.get("popular_threat_name")
    if isinstance(top_names, list) and top_names:
        popular_threat_name = top_names[0].get("value", None)
    popular_threat_category = None
    top_cats = popular_threat.get("popular_threat_category")
    if isinstance(top_cats, list) and top_cats:
        popular_threat_category = top_cats[0].get("value", None)

    # YARA
    crowdsourced_yara = []
    for yr in attrs.get("crowdsourced_yara_results", [])[:10]:
        rule_name = yr.get("rule_name", "")
        source = yr.get("source", "")
        if rule_name:
            crowdsourced_yara.append("{} ({})".format(rule_name, source) if source else rule_name)

    # Sandbox
    sandbox_verdicts = {}
    for sb_name, sb_data in attrs.get("sandbox_verdicts", {}).items():
        if isinstance(sb_data, dict):
            sandbox_verdicts[sb_name] = sb_data.get("category", "unknown")

    # Sigma
    sigma_rules = []
    for sr in attrs.get("sigma_analysis_results", [])[:10]:
        rule_title = sr.get("rule_title", "")
        rule_level = sr.get("rule_level", "")
        if rule_title:
            sigma_rules.append("{} [{}]".format(rule_title, rule_level) if rule_level else rule_title)

    analysis = extract_analysis_stats(attrs)

    result = {
        "ioc": queried_value,
        "ioc_type": "hash",
        "sha256": sha256,
        "sha1": sha1,
        "md5": md5,
        "file_name": file_name,
        "all_names": names[:10],
        "file_type": file_type,
        "magic": magic,
        "file_size": file_size,
        "file_size_human": format_size(file_size) if file_size else None,
        "first_seen": parse_timestamp(attrs.get("first_submission_date")),
        "last_analysis_date": parse_timestamp(attrs.get("last_analysis_date")),
        "threat_label": threat_label,
        "popular_threat_name": popular_threat_name,
        "popular_threat_category": popular_threat_category,
        "tags": attrs.get("tags", []),
        "crowdsourced_yara": crowdsourced_yara,
        "sigma_rules": sigma_rules,
        "sandbox_verdicts": sandbox_verdicts,
        "reputation": attrs.get("reputation", 0),
        "vt_link": "https://www.virustotal.com/gui/file/{}".format(sha256) if sha256 else None,
        "error": None,
    }
    result.update(analysis)
    return result


def parse_url_report(raw, queried_value):
    # type: (Dict[str, Any], str) -> Dict[str, Any]
    if "error" in raw and "data" not in raw:
        return {
            "ioc": queried_value,
            "ioc_type": "url",
            "error": raw.get("error"),
            "error_message": raw.get("message", ""),
        }

    attrs = raw.get("data", {}).get("attributes", {})
    url_id = raw.get("data", {}).get("id", "")

    analysis = extract_analysis_stats(attrs)

    # URL-specific categories
    categories = attrs.get("categories", {})

    result = {
        "ioc": queried_value,
        "ioc_type": "url",
        "url": attrs.get("url", queried_value),
        "final_url": attrs.get("last_final_url", ""),
        "title": attrs.get("title", ""),
        "first_seen": parse_timestamp(attrs.get("first_submission_date")),
        "last_analysis_date": parse_timestamp(attrs.get("last_analysis_date")),
        "categories": categories,
        "reputation": attrs.get("reputation", 0),
        "tags": attrs.get("tags", []),
        "http_response_code": attrs.get("last_http_response_content_length"),
        "vt_link": "https://www.virustotal.com/gui/url/{}".format(url_id) if url_id else None,
        "error": None,
    }
    result.update(analysis)
    return result


def parse_domain_report(raw, queried_value):
    # type: (Dict[str, Any], str) -> Dict[str, Any]
    if "error" in raw and "data" not in raw:
        return {
            "ioc": queried_value,
            "ioc_type": "domain",
            "error": raw.get("error"),
            "error_message": raw.get("message", ""),
        }

    attrs = raw.get("data", {}).get("attributes", {})

    analysis = extract_analysis_stats(attrs)

    # Domain-specific fields
    whois = attrs.get("whois", "")
    registrar = attrs.get("registrar", "")
    creation_date = parse_timestamp(attrs.get("creation_date"))
    last_update_date = parse_timestamp(attrs.get("last_update_date"))
    categories = attrs.get("categories", {})
    popularity_ranks = attrs.get("popularity_ranks", {})

    # DNS records
    last_dns_records = attrs.get("last_dns_records", [])
    dns_summary = []
    for rec in last_dns_records[:20]:
        rtype = rec.get("type", "")
        value = rec.get("value", "")
        if rtype and value:
            dns_summary.append({"type": rtype, "value": value})

    result = {
        "ioc": queried_value,
        "ioc_type": "domain",
        "domain": queried_value,
        "registrar": registrar,
        "creation_date": creation_date,
        "last_update_date": last_update_date,
        "last_analysis_date": parse_timestamp(attrs.get("last_analysis_date")),
        "categories": categories,
        "popularity_ranks": popularity_ranks,
        "dns_records": dns_summary,
        "reputation": attrs.get("reputation", 0),
        "tags": attrs.get("tags", []),
        "vt_link": "https://www.virustotal.com/gui/domain/{}".format(queried_value),
        "error": None,
    }
    result.update(analysis)
    return result


def parse_ip_report(raw, queried_value):
    # type: (Dict[str, Any], str) -> Dict[str, Any]
    if "error" in raw and "data" not in raw:
        return {
            "ioc": queried_value,
            "ioc_type": "ip",
            "error": raw.get("error"),
            "error_message": raw.get("message", ""),
        }

    attrs = raw.get("data", {}).get("attributes", {})

    analysis = extract_analysis_stats(attrs)

    # IP-specific fields
    asn = attrs.get("asn", "")
    as_owner = attrs.get("as_owner", "")
    country = attrs.get("country", "")
    network = attrs.get("network", "")
    whois = attrs.get("whois", "")

    result = {
        "ioc": queried_value,
        "ioc_type": "ip",
        "ip": queried_value,
        "asn": asn,
        "as_owner": as_owner,
        "country": country,
        "network": network,
        "last_analysis_date": parse_timestamp(attrs.get("last_analysis_date")),
        "reputation": attrs.get("reputation", 0),
        "tags": attrs.get("tags", []),
        "vt_link": "https://www.virustotal.com/gui/ip-address/{}".format(queried_value),
        "error": None,
    }
    result.update(analysis)
    return result


# ---------------------------------------------------------------------------
# Main lookup dispatcher
# ---------------------------------------------------------------------------
def lookup_ioc(value, api_key, force_type=None):
    # type: (str, str, Optional[str]) -> Dict[str, Any]
    """Detect IOC type and perform the appropriate VT lookup."""
    value = value.strip()

    if force_type:
        ioc_type = force_type
        hash_subtype = None
    else:
        ioc_type, hash_subtype = detect_ioc_type(value)

    if ioc_type == "unknown":
        return {
            "ioc": value,
            "ioc_type": "unknown",
            "error": "UnrecognizedIOC",
            "error_message": "Cannot determine IOC type for '{}'. Expected: hash (MD5/SHA1/SHA256), URL (http://...), domain, or IPv4 address.".format(value),
        }

    if ioc_type == "hash":
        raw = vt_api_get("/files/{}".format(value), api_key)
        return parse_hash_report(raw, value)

    elif ioc_type == "url":
        url_id = get_vt_url_id(value)
        raw = vt_api_get("/urls/{}".format(url_id), api_key)
        return parse_url_report(raw, value)

    elif ioc_type == "domain":
        raw = vt_api_get("/domains/{}".format(value), api_key)
        return parse_domain_report(raw, value)

    elif ioc_type == "ip":
        raw = vt_api_get("/ip_addresses/{}".format(value), api_key)
        return parse_ip_report(raw, value)

    else:
        return {
            "ioc": value,
            "ioc_type": ioc_type,
            "error": "UnsupportedType",
            "error_message": "IOC type '{}' is not yet supported.".format(ioc_type),
        }


def read_iocs_from_file(filepath):
    # type: (str) -> List[str]
    iocs = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                token = line.split()[0]
                # Strip common defanging: hxxp -> http, [.] -> .
                token = token.replace("hxxp", "http").replace("hXXp", "http")
                token = token.replace("[.]", ".").replace("[:]", ":")
                iocs.append(token)
    return iocs


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        sys.exit(0)

    iocs = []  # type: List[str]
    force_type = None  # type: Optional[str]

    # Check for --type flag
    if args[0] == "--type":
        if len(args) < 3:
            print(json.dumps({"error": "Usage: --type <hash|url|domain|ip> <value>"}))
            sys.exit(1)
        force_type = args[1]
        iocs = [a.strip() for a in args[2:] if a.strip()]
    elif args[0] == "--stdin":
        for line in sys.stdin:
            line = line.strip()
            if line and not line.startswith("#"):
                token = line.split()[0]
                token = token.replace("hxxp", "http").replace("hXXp", "http")
                token = token.replace("[.]", ".").replace("[:]", ":")
                iocs.append(token)
    elif args[0] == "--file":
        if len(args) < 2:
            print(json.dumps({"error": "Missing filename after --file"}))
            sys.exit(1)
        iocs = read_iocs_from_file(args[1])
    else:
        iocs = [a.strip() for a in args if a.strip()]
        # Defang
        iocs = [
            i.replace("hxxp", "http").replace("hXXp", "http")
             .replace("[.]", ".").replace("[:]", ":")
            for i in iocs
        ]

    if not iocs:
        print(json.dumps({"error": "No IOCs provided"}))
        sys.exit(1)

    # Deduplicate
    seen = set()  # type: set
    unique_iocs = []  # type: List[str]
    for i in iocs:
        key = i.lower()
        if key not in seen:
            seen.add(key)
            unique_iocs.append(i)
    iocs = unique_iocs

    try:
        api_key = get_api_key()
    except EnvironmentError as e:
        print(json.dumps({"error": "AuthenticationError", "message": str(e)}))
        sys.exit(1)

    results = []  # type: List[Dict[str, Any]]
    total = len(iocs)

    for idx, ioc_value in enumerate(iocs):
        if total > 1:
            sys.stderr.write("[vt-hash-intel] Querying {}/{}: {}\n".format(idx + 1, total, ioc_value))

        result = lookup_ioc(ioc_value, api_key, force_type=force_type)
        results.append(result)

        if idx < total - 1:
            time.sleep(RATE_LIMIT_DELAY)

    if len(results) == 1:
        print(json.dumps(results[0], indent=2, ensure_ascii=False))
    else:
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
