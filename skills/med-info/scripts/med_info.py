#!/usr/bin/env python3
"""med_info.py

API-only medication info retriever.

Sources:
- RxNorm (RxNav): name normalization to RxCUI
- openFDA: drug label + NDC directory
- MedlinePlus Connect: patient-friendly links/summaries by RxCUI

Usage:
  python3 scripts/med_info.py "ibuprofen" [--json]
  python3 scripts/med_info.py "00093-1045-56" [--json]

Env:
  OPENFDA_API_KEY (optional)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple


USER_AGENT = "clawdbot-med-info/0.4 (+https://clawhub.ai/DuncanDobbins/med-info)"
TIMEOUT_S = 20

# Best-effort request traceability. Stores *redacted* URLs (api_key removed).
URL_LOG: List[str] = []

# Local cache for bulky public datasets.
CACHE_DIR = Path(os.environ.get("MED_INFO_CACHE_DIR", os.path.expanduser("~/.cache/med-info")))


def ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def cache_path(*parts: str) -> Path:
    ensure_cache_dir()
    return CACHE_DIR.joinpath(*parts)


def cache_is_fresh(p: Path, max_age_days: int) -> bool:
    if not p.exists():
        return False
    age_s = time.time() - p.stat().st_mtime
    return age_s <= max_age_days * 86400


def download_to(url: str, dest: Path) -> None:
    ensure_cache_dir()
    _log_url(url)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        data = resp.read()
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(dest)


def _redact_url(url: str) -> str:
    try:
        p = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qsl(p.query, keep_blank_values=True)
        qs2 = [(k, v) for (k, v) in qs if k.lower() != "api_key"]
        return urllib.parse.urlunparse((p.scheme, p.netloc, p.path, p.params, urllib.parse.urlencode(qs2), p.fragment))
    except Exception:
        return url


def _log_url(url: str) -> None:
    URL_LOG.append(_redact_url(url))


def http_get_json(url: str, headers: Optional[Dict[str, str]] = None, *, allow_404: bool = False) -> Any:
    _log_url(url)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            data = resp.read()
        return json.loads(data.decode("utf-8"))
    except urllib.error.HTTPError as e:
        if allow_404 and e.code == 404:
            # openFDA returns 404 when there are no matches.
            return {"results": []}
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        raise RuntimeError(f"HTTP {e.code} for {url}: {body[:500]}") from e


def is_probable_ndc(s: str) -> bool:
    s = s.strip()
    # Common patterns: 4-4, 5-3-2, 5-4-1, etc. Also allow digits-only 10/11.
    if re.fullmatch(r"\d{10,11}", s):
        return True
    if re.fullmatch(r"\d{4,5}-\d{3,4}(-\d{1,2})?", s):
        return True
    return False


def ndc_normalize_hyphenated_to_11(ndc: str) -> Optional[str]:
    """Normalize a hyphenated 10-digit NDC into NDC-11 (5-4-2) when possible.

    Rules (FDA standard):
    - 4-4-2 -> pad labeler to 5 (leading zero)
    - 5-3-2 -> pad product to 4 (leading zero)
    - 5-4-1 -> pad package to 2 (leading zero)

    Returns None if the format is not recognized.
    """
    s = re.sub(r"[^0-9-]", "", (ndc or "").strip())
    parts = [p for p in s.split("-") if p]
    if len(parts) != 3:
        return None

    a, b, c = parts
    if not (a.isdigit() and b.isdigit() and c.isdigit()):
        return None

    la, lb, lc = len(a), len(b), len(c)

    # 4-4-2
    if (la, lb, lc) == (4, 4, 2):
        return "0" + a + b + c
    # 5-3-2
    if (la, lb, lc) == (5, 3, 2):
        return a + "0" + b + c
    # 5-4-1
    if (la, lb, lc) == (5, 4, 1):
        return a + b + "0" + c

    # Already 5-4-2?
    if (la, lb, lc) == (5, 4, 2):
        return a + b + c

    return None


def ndc11_candidates_from_10digits(ndc10: str) -> List[Dict[str, str]]:
    """Generate best-effort NDC-11 candidates from 10 digits with unknown hyphenation."""
    d = re.sub(r"\D", "", (ndc10 or "").strip())
    if len(d) != 10:
        return []

    # Candidate schemas for 10-digit NDCs.
    # A) 4-4-2 -> pad labeler
    a = "0" + d

    # B) 5-3-2 -> pad product
    b = d[:5] + "0" + d[5:]

    # C) 5-4-1 -> pad package
    c = d[:9] + "0" + d[9:]

    out = [
        {"ndc11": a, "schema": "4-4-2"},
        {"ndc11": b, "schema": "5-3-2"},
        {"ndc11": c, "schema": "5-4-1"},
    ]

    # Deduplicate (some weird numbers may collide).
    seen = set()
    uniq = []
    for x in out:
        if x["ndc11"] in seen:
            continue
        seen.add(x["ndc11"])
        uniq.append(x)
    return uniq


def ndc_normalize_input(ndc: str) -> Dict[str, Any]:
    """Return a normalization object for an NDC input.

    Output keys:
    - input
    - digits
    - ndc11 (when determinable)
    - ndc11_candidates (when ambiguous)
    """
    s = (ndc or "").strip()
    digits = re.sub(r"\D", "", s)

    norm: Dict[str, Any] = {"input": s, "digits": digits, "ndc11": None, "ndc11_candidates": []}

    if re.fullmatch(r"\d{11}", digits):
        norm["ndc11"] = digits
        return norm

    # If hyphenated, try exact normalization.
    if "-" in s:
        ndc11 = ndc_normalize_hyphenated_to_11(s)
        if ndc11 and re.fullmatch(r"\d{11}", ndc11):
            norm["ndc11"] = ndc11
            return norm

    # Digits-only 10-digit NDC is ambiguous, provide candidates.
    if re.fullmatch(r"\d{10}", digits):
        norm["ndc11_candidates"] = ndc11_candidates_from_10digits(digits)
        return norm

    return norm


def is_uuid_like(s: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", s.strip()))


def rxnorm_approximate(term: str, max_entries: int = 5) -> List[Dict[str, Any]]:
    # Docs: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getApproximateMatch.html
    qs = urllib.parse.urlencode({"term": term, "maxEntries": str(max_entries), "option": "1"})
    url = f"https://rxnav.nlm.nih.gov/REST/approximateTerm.json?{qs}"
    j = http_get_json(url)
    cand = j.get("approximateGroup", {}).get("candidate", [])
    if isinstance(cand, dict):
        cand = [cand]
    return cand


def rxnorm_name_for_rxcui(rxcui: str) -> Optional[str]:
    url = f"https://rxnav.nlm.nih.gov/REST/rxcui/{urllib.parse.quote(rxcui)}/properties.json"
    j = http_get_json(url)
    props = j.get("properties") or {}
    return props.get("name")


def openfda_url(path: str, query: str, limit: int = 1) -> str:
    base = f"https://api.fda.gov{path}.json"
    params = {"search": query, "limit": str(limit)}
    api_key = os.environ.get("OPENFDA_API_KEY")
    if api_key:
        params["api_key"] = api_key
    return base + "?" + urllib.parse.urlencode(params)


# openFDA `search` uses a query syntax (Lucene-like). Treat all user-controlled input as untrusted.
# We always wrap values in double-quotes and escape dangerous characters so the value is interpreted
# literally, preventing query injection (e.g. closing quotes and adding OR clauses).
_OPENFDA_CTRL_RE = re.compile(r"[\x00-\x1f\x7f]")


def openfda_escape_value(value: str) -> str:
    v = (value or "").strip()
    v = _OPENFDA_CTRL_RE.sub(" ", v)
    # Escape backslashes first, then quotes.
    v = v.replace("\\", "\\\\").replace('"', '\\"')
    return v


def openfda_qstr(value: str) -> str:
    return '"' + openfda_escape_value(value) + '"'


def openfda_qdigits(value: str, *, min_len: int = 1, max_len: int = 32) -> Optional[str]:
    d = re.sub(r"\D", "", (value or ""))
    if not d:
        return None
    if len(d) < min_len or len(d) > max_len:
        return None
    return d


def openfda_label_by_rxcui(rxcui: str) -> Optional[Dict[str, Any]]:
    r = openfda_qdigits(rxcui, min_len=1, max_len=16)
    if not r:
        return None
    q = f"openfda.rxcui:{openfda_qstr(r)}"
    url = openfda_url("/drug/label", q, limit=1)
    j = http_get_json(url, allow_404=True)
    res = j.get("results")
    if not res:
        return None
    return res[0]


def _as_list(x: Any) -> List[Any]:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def openfda_label_candidates(name: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Return candidate openFDA labels for a query, sorted best-first.

    Used for disambiguation and robust fallback when RxCUI search fails.
    """
    nm = _norm(name)
    q = (
        f"(openfda.generic_name:{openfda_qstr(name)} "
        f"OR openfda.substance_name:{openfda_qstr(name)} "
        f"OR openfda.brand_name:{openfda_qstr(name)})"
    )
    url = openfda_url("/drug/label", q, limit=limit)
    j = http_get_json(url, allow_404=True)
    res = j.get("results") or []
    if not res:
        return []

    def score_label(label: Dict[str, Any]) -> Tuple[int, str]:
        of = label.get("openfda") or {}
        subs = [_norm(str(x)) for x in _as_list(of.get("substance_name")) if str(x).strip()]
        gens = [_norm(str(x)) for x in _as_list(of.get("generic_name")) if str(x).strip()]
        brands = [_norm(str(x)) for x in _as_list(of.get("brand_name")) if str(x).strip()]

        s = 0

        # Prefer single-ingredient labels when the query looks like a single ingredient.
        looks_combo = any(tok in nm for tok in [" and ", "/", "+"])
        if not looks_combo:
            if len(subs) == 1:
                s += 50
            elif len(subs) > 1:
                s -= 30

        if nm in subs:
            s += 60
        if nm in gens:
            s += 40
        if nm in brands:
            s += 10

        # Prefer newer effective_time when scores tie.
        et = str(label.get("effective_time") or "")
        return (s, et)

    return sorted(res, key=score_label, reverse=True)


def openfda_label_by_generic_name(name: str) -> Optional[Dict[str, Any]]:
    # Backwards-compatible helper: pick the best candidate.
    cands = openfda_label_candidates(name, limit=10)
    return cands[0] if cands else None


def openfda_label_by_set_id(set_id: str) -> Optional[Dict[str, Any]]:
    # openFDA drug/label supports set_id queries.
    sid = (set_id or "").strip()
    if not is_uuid_like(sid):
        return None
    q = f"set_id:{openfda_qstr(sid)}"
    url = openfda_url("/drug/label", q, limit=1)
    j = http_get_json(url, allow_404=True)
    res = j.get("results")
    if not res:
        return None
    return res[0]


def openfda_ndc_lookup(ndc: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Lookup an NDC in openFDA drug/ndc.

    Notes:
    - `product_ndc` is a top-level field.
    - `package_ndc` lives under `packaging[].package_ndc`.
    """
    ndc = (ndc or "").strip()
    # Treat NDC input as untrusted. Keep only digits and hyphens.
    ndc = re.sub(r"[^0-9-]", "", ndc)
    parts = [p for p in ndc.split("-") if p]

    product_ndc = None
    package_ndc = None

    if len(parts) == 3:
        package_ndc = ndc
        product_ndc = f"{parts[0]}-{parts[1]}"
    elif len(parts) == 2:
        product_ndc = ndc

    terms: List[str] = []
    if product_ndc:
        terms.append(f"product_ndc:{openfda_qstr(product_ndc)}")
    if package_ndc:
        terms.append(f"packaging.package_ndc:{openfda_qstr(package_ndc)}")

    if not terms:
        # Fallback: best-effort exact match against both fields.
        terms = [f"product_ndc:{openfda_qstr(ndc)}", f"packaging.package_ndc:{openfda_qstr(ndc)}"]

    q = "(" + " OR ".join(terms) + ")"
    url = openfda_url("/drug/ndc", q, limit=limit)
    j = http_get_json(url, allow_404=True)
    res = j.get("results")
    return res or []


def compact_openfda_ndc_result(r: Dict[str, Any], *, include_packaging: bool = True) -> Dict[str, Any]:
    """Return a compact, pharmacist-friendly shape for openFDA drug/ndc results."""
    pkgs_in = r.get("packaging") or []
    pkgs_out = []
    if include_packaging and isinstance(pkgs_in, list):
        for p in pkgs_in:
            if not isinstance(p, dict):
                continue
            pkgs_out.append({
                "package_ndc": p.get("package_ndc"),
                "description": p.get("description"),
                "marketing_start_date": p.get("marketing_start_date"),
                "marketing_end_date": p.get("marketing_end_date"),
                "sample_package": p.get("sample_package"),
            })

    active = []
    for ai in (r.get("active_ingredients") or []):
        if isinstance(ai, dict):
            active.append({"name": ai.get("name"), "strength": ai.get("strength")})

    return {
        "product_ndc": r.get("product_ndc"),
        "product_type": r.get("product_type"),
        "marketing_category": r.get("marketing_category"),
        "application_number": r.get("application_number"),
        "brand_name": r.get("brand_name"),
        "generic_name": r.get("generic_name"),
        "labeler_name": r.get("labeler_name"),
        "dosage_form": r.get("dosage_form"),
        "route": r.get("route"),
        "active_ingredients": active,
        "marketing_start_date": r.get("marketing_start_date"),
        "marketing_end_date": r.get("marketing_end_date"),
        "listing_expiration_date": r.get("listing_expiration_date"),
        "packaging": pkgs_out,
        "openfda": r.get("openfda") or {},
    }


def openfda_enforcement_search(search: str, limit: int = 5) -> List[Dict[str, Any]]:
    url = openfda_url("/drug/enforcement", search, limit=limit)
    j = http_get_json(url, allow_404=True)
    return j.get("results") or []


def openfda_shortages_search(search: str, limit: int = 5) -> List[Dict[str, Any]]:
    # Note: endpoint path is /drug/shortages (not /drug/drugshortages)
    url = openfda_url("/drug/shortages", search, limit=limit)
    j = http_get_json(url, allow_404=True)
    return j.get("results") or []


def openfda_event_count(search: str, count_field: str, limit: int = 10) -> List[Dict[str, Any]]:
    base = "https://api.fda.gov/drug/event.json"
    params = {
        "search": search,
        "count": count_field,
        "limit": str(limit),
    }
    api_key = os.environ.get("OPENFDA_API_KEY")
    if api_key:
        params["api_key"] = api_key
    url = base + "?" + urllib.parse.urlencode(params)
    j = http_get_json(url, allow_404=True)
    return j.get("results") or []


def rxclass_by_rxcui(rxcui: str) -> List[Dict[str, Any]]:
    # https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json?rxcui=...
    url = "https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json?" + urllib.parse.urlencode({"rxcui": rxcui})
    j = http_get_json(url)
    classes = (((j or {}).get("rxclassDrugInfoList") or {}).get("rxclassDrugInfo")) or []
    if isinstance(classes, dict):
        classes = [classes]
    out = []
    for c in classes:
        ci = c.get("rxclassMinConceptItem") or {}
        out.append({
            "classId": ci.get("classId"),
            "className": ci.get("className"),
            "classType": ci.get("classType"),
            "relaSource": ci.get("relaSource"),
        })
    return out


def rxnav_interactions_by_rxcui(rxcui: str) -> List[Dict[str, Any]]:
    """Return a compact interaction list from RxNav.

    Docs: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getInteraction.html

    Note: RxNav interaction results can be large and a bit nested.
    We keep a stable compact shape: [{"severity","description","minConcept","sourceConcept"}...]
    """
    url = "https://rxnav.nlm.nih.gov/REST/interaction/interaction.json?" + urllib.parse.urlencode({"rxcui": rxcui})
    j = http_get_json(url)
    groups = (((j or {}).get("interactionTypeGroup")) or [])
    if isinstance(groups, dict):
        groups = [groups]

    out: List[Dict[str, Any]] = []

    for g in groups:
        itypes = (g or {}).get("interactionType") or []
        if isinstance(itypes, dict):
            itypes = [itypes]
        for it in itypes:
            pairs = (it or {}).get("interactionPair") or []
            if isinstance(pairs, dict):
                pairs = [pairs]
            for p in pairs:
                desc = p.get("description")
                sev = p.get("severity")

                # source/min concepts are sometimes present.
                src = p.get("interactionConcept") or []
                if isinstance(src, dict):
                    src = [src]
                min_concept = None
                src_concept = None
                if src:
                    # Try to pull the minConceptItem for both sides when possible.
                    try:
                        # There are usually two concepts; keep both in a compact form.
                        items = []
                        for c in src[:2]:
                            mi = (c.get("minConceptItem") or {}) if isinstance(c, dict) else {}
                            if mi:
                                items.append({"rxcui": mi.get("rxcui"), "name": mi.get("name"), "tty": mi.get("tty")})
                        if items:
                            min_concept = items
                    except Exception:
                        pass

                if desc or sev or min_concept:
                    out.append({
                        "severity": sev,
                        "description": desc,
                        "concepts": min_concept,
                    })

    # Best-effort stable sort: severe first, then alpha.
    sev_rank = {"high": 0, "severe": 0, "moderate": 1, "medium": 1, "low": 2, "minor": 2, None: 3, "": 3}

    def k(x: Dict[str, Any]) -> Tuple[int, str]:
        sev = (x.get("severity") or "").strip().lower()
        return (sev_rank.get(sev, 3), (x.get("description") or ""))

    return sorted(out, key=k)


def pubchem_compound_properties(name: str) -> Optional[Dict[str, Any]]:
    """Fetch a minimal PubChem property block for a compound name.

    PUG REST: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
    """
    nm = (name or "").strip()
    if not nm:
        return None

    props = [
        "MolecularFormula",
        "MolecularWeight",
        "IUPACName",
        "InChIKey",
        "IsomericSMILES",
    ]
    path = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{urllib.parse.quote(nm)}/property/{','.join(props)}/JSON"

    try:
        j = http_get_json(path, allow_404=False)
    except Exception:
        return None

    tbl = (((j or {}).get("PropertyTable")) or {}).get("Properties") or []
    if isinstance(tbl, dict):
        tbl = [tbl]
    if not tbl:
        return None

    # Return first match.
    p0 = tbl[0]
    out = {k: p0.get(k) for k in ["CID"] + props if p0.get(k) is not None}
    return out or None


def dailymed_history(setid: str) -> Dict[str, Any]:
    # Note: /spls/{setid}.json returns 415, so use /history.json + /media.json.
    url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{urllib.parse.quote(setid)}/history.json"
    return http_get_json(url)


def dailymed_media(setid: str) -> Dict[str, Any]:
    url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{urllib.parse.quote(setid)}/media.json"
    return http_get_json(url)


def dailymed_enrich(setid: str, media_max: int = 10) -> Dict[str, Any]:
    hist = dailymed_history(setid)
    med = dailymed_media(setid)
    out: Dict[str, Any] = {
        "setid": setid,
        "history": (hist.get("data") or {}).get("history") or [],
        "media": (med.get("data") or {}).get("media") or [],
        "spl_version": (med.get("data") or {}).get("spl_version"),
        "published_date": (med.get("data") or {}).get("published_date"),
        "title": (med.get("data") or {}).get("title"),
    }
    if media_max is not None:
        try:
            out["media"] = out["media"][: int(media_max)]
        except Exception:
            pass
    return out


def orangebook_load(max_age_days: int = 30) -> List[Dict[str, str]]:
    """Load Orange Book products.txt as a list of dicts."""
    p_zip = cache_path("orangebook", "orangebook.zip")
    p_products = cache_path("orangebook", "products.txt")

    if not cache_is_fresh(p_products, max_age_days):
        # Download zip
        url = "https://www.fda.gov/media/76860/download?attachment"
        download_to(url, p_zip)
        with zipfile.ZipFile(p_zip) as z:
            with z.open("products.txt") as f:
                p_products.write_bytes(f.read())

    raw = p_products.read_bytes().decode("latin1", errors="replace")
    lines = raw.splitlines()
    if not lines:
        return []
    header = lines[0].split("~")
    out: List[Dict[str, str]] = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("~")
        # pad
        if len(parts) < len(header):
            parts = parts + [""] * (len(header) - len(parts))
        row = {header[i]: parts[i] for i in range(len(header))}
        out.append(row)
    return out


def orangebook_search(term: str, max_results: int = 10) -> List[Dict[str, Any]]:
    term_n = _norm(term)
    if not term_n:
        return []
    rows = orangebook_load(max_age_days=30)

    hits: List[Dict[str, Any]] = []
    for r in rows:
        ing = _norm(r.get("Ingredient", ""))
        trade = _norm(r.get("Trade_Name", ""))
        if term_n in ing or term_n in trade:
            hits.append({
                "ingredient": r.get("Ingredient"),
                "trade_name": r.get("Trade_Name"),
                "strength": r.get("Strength"),
                "df_route": r.get("DF;Route"),
                "applicant": r.get("Applicant_Full_Name") or r.get("Applicant"),
                "appl_type": r.get("Appl_Type"),
                "appl_no": r.get("Appl_No"),
                "product_no": r.get("Product_No"),
                "te_code": r.get("TE_Code"),
                "rld": r.get("RLD"),
                "rs": r.get("RS"),
                "type": r.get("Type"),
            })
            if len(hits) >= max_results:
                break
    return hits


def purplebook_download_latest(max_age_days: int = 30) -> Path:
    """Download a Purple Book monthly CSV, returning the cached path."""

    def looks_like_csv(p: Path) -> bool:
        try:
            head = p.read_text(encoding="utf-8", errors="replace")[:5000]
        except Exception:
            return False
        if "<!DOCTYPE html>" in head or head.lstrip().startswith("<"):
            return False
        return "N/R/U,Applicant,BLA Number" in head

    # Try current month and walk backwards up to 18 months.
    months = [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ]

    now = time.localtime()
    y = now.tm_year
    m = now.tm_mon - 1

    for back in range(0, 18):
        yy = y
        mm = m - back
        while mm < 0:
            mm += 12
            yy -= 1
        month = months[mm]
        url = f"https://purplebooksearch.fda.gov/files/{yy}/purplebook-search-{month}-data-download.csv"
        dest = cache_path("purplebook", f"{yy}-{month}.csv")
        if cache_is_fresh(dest, max_age_days):
            if looks_like_csv(dest):
                return dest
            try:
                dest.unlink(missing_ok=True)
            except Exception:
                pass
        try:
            download_to(url, dest)

            # Validate we actually got the CSV, not an HTML error page.
            # Some months return a generic HTML app shell instead of the data export.
            if not looks_like_csv(dest):
                raise RuntimeError("Purple Book download missing expected CSV header")

            return dest
        except Exception:
            try:
                dest.unlink(missing_ok=True)
            except Exception:
                pass
            continue

    raise RuntimeError("Unable to download Purple Book CSV (tried 18 months)")


def purplebook_load(max_age_days: int = 30) -> List[Dict[str, str]]:
    p = purplebook_download_latest(max_age_days=max_age_days)
    text = p.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    rows: List[Dict[str, str]] = []
    header: Optional[List[str]] = None

    for line in lines:
        if not line.strip():
            continue
        if line.startswith("N/R/U,Applicant,BLA Number"):
            header = next(csv.reader([line]))
            continue
        if header is None:
            continue
        parts = next(csv.reader([line]))
        if len(parts) < len(header):
            parts = parts + [""] * (len(header) - len(parts))
        row = {header[i].strip(): parts[i].strip() for i in range(len(header))}
        # Skip empty rows
        if not any(row.values()):
            continue
        rows.append(row)

    return rows


def purplebook_search(term: str, max_results: int = 10) -> List[Dict[str, Any]]:
    term_n = _norm(term)
    if not term_n:
        return []
    rows = purplebook_load(max_age_days=30)
    hits: List[Dict[str, Any]] = []
    seen: set = set()

    fields = [
        "Proprietary Name",
        "Proper Name",
        "Ref. Product Proprietary Name",
        "Ref. Product Proper Name",
        "Applicant",
    ]

    for r in rows:
        blob = " ".join([_norm(r.get(f, "")) for f in fields])
        if term_n in blob:
            row = {
                "applicant": r.get("Applicant"),
                "bla_number": r.get("BLA Number"),
                "proprietary_name": r.get("Proprietary Name"),
                "proper_name": r.get("Proper Name"),
                "bla_type": r.get("BLA Type"),
                "strength": r.get("Strength"),
                "dosage_form": r.get("Dosage Form"),
                "route": r.get("Route of Administration"),
                "presentation": r.get("Product Presentation"),
                "marketing_status": r.get("Marketing Status"),
                "licensure": r.get("Licensure"),
                "approval_date": r.get("Approval Date"),
                "ref_product_proper_name": r.get("Ref. Product Proper Name"),
                "ref_product_proprietary_name": r.get("Ref. Product Proprietary Name"),
                "interchangeable": r.get("Interchangeable"),
            }
            key = (
                (row.get("bla_number") or ""),
                _norm(row.get("proprietary_name") or ""),
                _norm(row.get("proper_name") or ""),
                _norm(row.get("applicant") or ""),
            )
            if key in seen:
                continue
            seen.add(key)
            hits.append(row)
            if len(hits) >= max_results:
                break

    return hits


def medlineplus_by_rxcui(rxcui: str) -> Dict[str, Any]:
    # RxNorm OID: 2.16.840.1.113883.6.88
    params = {
        "knowledgeResponseType": "application/json",
        "mainSearchCriteria.v.cs": "2.16.840.1.113883.6.88",
        "mainSearchCriteria.v.c": rxcui,
        "informationRecipient.languageCode.c": "en",
    }
    url = "https://connect.medlineplus.gov/service?" + urllib.parse.urlencode(params)
    return http_get_json(url)


def _http_get_text(url: str, headers: Optional[Dict[str, str]] = None, *, max_bytes: int = 2_000_000) -> str:
    """Fetch a URL as text (best-effort)."""
    _log_url(url)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        data = resp.read(max_bytes)
    return data.decode("utf-8", errors="replace")


def guess_controlled_substance_schedule(text_fields: Dict[str, str]) -> Dict[str, Any]:
    """Best-effort CSA schedule guess from label text.

    This is intentionally conservative and should be treated as a hint only.
    """
    combined = "\n\n".join(text_fields.values())

    pats = [
        re.compile(r"\bSchedule\s*(I|II|III|IV|V|1|2|3|4|5)\b", re.IGNORECASE),
        re.compile(r"\bC-?(I|II|III|IV|V)\b", re.IGNORECASE),
    ]

    for pat in pats:
        m = pat.search(combined)
        if not m:
            continue
        raw = (m.group(1) or "").upper()
        # Normalize digits to roman-ish output.
        digit_map = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
        sched = digit_map.get(raw, raw)
        start = max(0, m.start() - 60)
        end = min(len(combined), m.end() + 60)
        snip = re.sub(r"\s+", " ", combined[start:end]).strip()
        return {"schedule_guess": sched, "evidence": snip}

    return {"schedule_guess": None, "evidence": None}


def build_safety_flags(label: Dict[str, Any], text_fields: Dict[str, str]) -> Dict[str, Any]:
    sections = (label or {}).get("sections") or {}

    boxed = sections.get("boxed_warning")
    cs = guess_controlled_substance_schedule(text_fields)

    # Medication Guide / Patient information is sometimes present as separate label fields.
    mg_present = any(k.lower().startswith("medication_guide") for k in text_fields.keys())

    return {
        "boxed_warning_present": bool(boxed and str(boxed).strip()),
        "boxed_warning_excerpt": _compact(boxed, max_len=240) if boxed else None,
        "controlled_substance_schedule_guess": cs.get("schedule_guess"),
        "controlled_substance_evidence": cs.get("evidence"),
        "medication_guide_field_present": mg_present,
    }


NIOSH_HAZARDOUS_DOC_URL = "https://www.cdc.gov/niosh/docs/2025-103/default.html"
NIOSH_HAZARDOUS_PDF_URL = "https://www.cdc.gov/niosh/docs/2025-103/pdfs/2025-103.pdf"


def _have_pdftotext() -> bool:
    return shutil.which("pdftotext") is not None


def _niosh_norm(s: str) -> str:
    x = (s or "").lower()
    x = re.sub(r"[^a-z0-9]+", " ", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x


def parse_niosh_hazardous_pdf_text(text: str) -> List[Dict[str, Any]]:
    """Parse NIOSH 2024 hazardous drug list tables out of pdftotext output."""
    lines = [ln.strip() for ln in (text or "").splitlines()]

    records: List[Dict[str, Any]] = []
    current_table: Optional[int] = None
    pending_name: List[str] = []

    def is_header_line(ln: str) -> bool:
        return ln in {
            "Drug",
            "AHFS Classifcation",
            "AHFS Classification",
            "MSHI",
            "Biologics",
            "Biologics License",
            "Application",
            "Only Developmental and/",
            "or Reproductive Hazard†",
            "IARC and NTP Classifcation",
            "IARC and NTP Classification",
        }

    def looks_like_ahfs(ln: str) -> bool:
        return bool(re.match(r"^\d{1,2}:\d{2}", ln))

    def take_yesno(start_i: int, n: int = 2) -> List[str]:
        out: List[str] = []
        k = start_i
        while k < len(lines) and len(out) < n:
            if lines[k] in ("Yes", "No"):
                out.append(lines[k])
            k += 1
        return out

    i = 0
    while i < len(lines):
        ln = lines[i]

        if ln.startswith("Table 1"):
            current_table = 1
            pending_name = []
            i += 1
            continue

        if ln.startswith("Table 2"):
            current_table = 2
            pending_name = []
            i += 1
            continue

        if current_table in (1, 2):
            if not ln or is_header_line(ln):
                pending_name = []
                i += 1
                continue

            if ln in ("Yes", "No") or re.fullmatch(r"\d+", ln):
                i += 1
                continue

            # If we hit AHFS classification, finalize a record.
            if looks_like_ahfs(ln):
                drug = re.sub(r"\s+", " ", " ".join(pending_name)).strip()
                pending_name = []

                # Consume multi-line AHFS classification until blank line.
                ahfs_parts = [ln]
                j = i + 1
                while j < len(lines) and lines[j] and lines[j] not in ("Yes", "No") and not lines[j].startswith("Table "):
                    # Stop if the next line looks like a new drug name (lowercase word) and we've already got a reasonable AHFS.
                    if re.match(r"^[a-z0-9][a-z0-9\-\s]+$", lines[j]) and not re.search(r"\d", lines[j]):
                        break
                    ahfs_parts.append(lines[j])
                    j += 1
                ahfs = re.sub(r"\s+", " ", " ".join(ahfs_parts)).strip()

                yn = take_yesno(j, n=2)

                rec: Dict[str, Any] = {
                    "drug": drug,
                    "table": current_table,
                    "ahfs": ahfs,
                }
                if current_table == 1:
                    rec["mshi"] = yn[0] if len(yn) > 0 else None
                    rec["biologics"] = yn[1] if len(yn) > 1 else None
                else:
                    rec["biologics_license_application"] = yn[0] if len(yn) > 0 else None
                    rec["only_developmental_or_reproductive_hazard"] = yn[1] if len(yn) > 1 else None

                if drug:
                    records.append(rec)

                i = j
                continue

            # Otherwise, treat as part of a drug name (keep short, low-noise lines).
            lower = ln.lower()
            if any(x in lower for x in ["te drugs", "tese drugs", "drugs reviewed", "table abbreviations", "foreword", "contents"]):
                pending_name = []
                i += 1
                continue

            # Keep at most 3 lines for multi-line drug names.
            if len(ln) <= 60:
                pending_name.append(ln)
                pending_name = pending_name[-3:]

        i += 1

    # Deduplicate by normalized name + table.
    seen = set()
    uniq: List[Dict[str, Any]] = []
    for r in records:
        key = (_niosh_norm(r.get("drug") or ""), r.get("table"))
        if key in seen or not key[0]:
            continue
        seen.add(key)
        uniq.append(r)

    return uniq


def niosh_hazardous_load(max_age_days: int = 90) -> Dict[str, Any]:
    """Load and cache parsed NIOSH hazardous drug list records."""
    p_json = cache_path("niosh", "2025-103.parsed.json")
    if cache_is_fresh(p_json, max_age_days):
        try:
            return json.loads(p_json.read_text(encoding="utf-8"))
        except Exception:
            pass

    if not _have_pdftotext():
        return {
            "ok": False,
            "reason": "pdftotext not installed",
            "doc_url": NIOSH_HAZARDOUS_DOC_URL,
            "pdf_url": NIOSH_HAZARDOUS_PDF_URL,
            "records": [],
        }

    p_pdf = cache_path("niosh", "2025-103.pdf")
    if not cache_is_fresh(p_pdf, max_age_days):
        download_to(NIOSH_HAZARDOUS_PDF_URL, p_pdf)

    p_txt = cache_path("niosh", "2025-103.txt")
    if (not p_txt.exists()) or (p_txt.stat().st_mtime < p_pdf.stat().st_mtime):
        subprocess.run(["pdftotext", str(p_pdf), str(p_txt)], check=True)

    txt = p_txt.read_text(encoding="utf-8", errors="replace")
    records = parse_niosh_hazardous_pdf_text(txt)

    obj = {
        "ok": True,
        "doc_url": NIOSH_HAZARDOUS_DOC_URL,
        "pdf_url": NIOSH_HAZARDOUS_PDF_URL,
        "count": len(records),
        "records": records,
    }
    try:
        p_json.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except Exception:
        pass
    return obj


def niosh_hazardous_match(candidate_names: List[str]) -> Dict[str, Any]:
    """Match candidate drug names against NIOSH hazardous list (best-effort)."""
    cand = [c for c in (candidate_names or []) if c and str(c).strip()]
    cand_norm = {_niosh_norm(str(c)) for c in cand}

    data = niosh_hazardous_load(max_age_days=90)
    if not data.get("ok"):
        return {
            "ok": False,
            "reason": data.get("reason"),
            "doc_url": data.get("doc_url"),
            "pdf_url": data.get("pdf_url"),
            "matches": [],
        }

    matches = []
    for r in data.get("records") or []:
        rn = _niosh_norm(r.get("drug") or "")
        if not rn:
            continue
        if rn in cand_norm:
            matches.append(r)

    return {
        "ok": True,
        "doc_url": data.get("doc_url"),
        "pdf_url": data.get("pdf_url"),
        "matches": matches[:50],
        "note": "NIOSH list matching is best-effort; verify against the full NIOSH document.",
    }


FDA_REMS_INFO_URL = "https://www.fda.gov/drugs/drug-safety-and-availability/risk-evaluation-and-mitigation-strategies-rems"
FDA_REMS_DATABASE_URL = "https://www.accessdata.fda.gov/scripts/cder/rems/index.cfm"


def fda_rems_best_effort(candidate_names: List[str]) -> Dict[str, Any]:
    """Best-effort REMS program lookup.

    NOTE: FDA accessdata endpoints may return an "FDA apology" abuse-detection page for scripted access.
    We treat that as unavailable and return only links.
    """
    cand = [c for c in (candidate_names or []) if c and str(c).strip()]

    out = {
        "ok": False,
        "database_url": FDA_REMS_DATABASE_URL,
        "info_url": FDA_REMS_INFO_URL,
        "matches": [],
        "note": "Best-effort only. Verify on FDA REMS@FDA.",
    }

    try:
        html = _http_get_text(FDA_REMS_DATABASE_URL, max_bytes=2_000_000)
    except Exception as e:
        out["reason"] = f"fetch failed: {e}"
        return out

    low = html.lower()
    if "fda apology" in low or "excessive-requests-apology" in low or "abuse-detection" in low:
        out["reason"] = "blocked by FDA abuse-detection"
        return out

    # Parse entries like: ...REMS=17">Opioid Analgesic REMS</a>
    items = []
    for m in re.finditer(r"href=\"([^\"]*REMS=([0-9]+)[^\"]*)\"[^>]*>([^<]{1,200})</a>", html, re.IGNORECASE):
        href = m.group(1)
        rid = m.group(2)
        name = re.sub(r"\s+", " ", (m.group(3) or "")).strip()
        if not rid or not name:
            continue
        url = urllib.parse.urljoin(FDA_REMS_DATABASE_URL, href)
        items.append({"rems_id": rid, "name": name, "url": url})

    # Dedup by id.
    seen = set()
    uniq = []
    for it in items:
        if it["rems_id"] in seen:
            continue
        seen.add(it["rems_id"])
        uniq.append(it)

    # Match by simple containment.
    cand_n = [_niosh_norm(x) for x in cand]
    matches = []
    for it in uniq:
        nm = _niosh_norm(it.get("name") or "")
        if any(c and c in nm for c in cand_n):
            matches.append(it)

    out["ok"] = True
    out["matches"] = matches[:20]
    if not matches:
        out["reason"] = "no REMS name match"
    return out


def pick_best_candidate(candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not candidates:
        return None

    # Highest score, then lowest rank.
    def key(c: Dict[str, Any]) -> Tuple[float, int]:
        try:
            score = float(c.get("score") or 0)
        except Exception:
            score = 0.0
        try:
            rank = int(c.get("rank") or 999999)
        except Exception:
            rank = 999999
        # Lower rank is better, so invert it.
        return (score, -rank)

    return sorted(candidates, key=key, reverse=True)[0]


def label_section(label: Dict[str, Any], key: str) -> Optional[str]:
    v = label.get(key)
    if not v:
        return None
    if isinstance(v, list):
        # join paragraphs, preserve spacing.
        return "\n\n".join([str(x).strip() for x in v if str(x).strip()])
    return str(v).strip()


def daily_med_url_from_setid(setid: Optional[str]) -> Optional[str]:
    if not setid:
        return None
    return f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={urllib.parse.quote(setid)}"


def _first_of(v: Any) -> Optional[str]:
    if v is None:
        return None
    if isinstance(v, list):
        return str(v[0]) if v else None
    return str(v)


def label_candidate_summary(label: Dict[str, Any]) -> Dict[str, Any]:
    of = (label or {}).get("openfda") or {}
    setid = _first_of(of.get("spl_set_id"))
    return {
        "effective_time": label.get("effective_time"),
        "id": label.get("id"),
        "setid": setid,
        "dailymed": daily_med_url_from_setid(setid),
        "brand_name": _first_of(of.get("brand_name")),
        "generic_name": _first_of(of.get("generic_name")),
        "manufacturer_name": _first_of(of.get("manufacturer_name")),
        "route": _first_of(of.get("route")),
        "dosage_form": _first_of(of.get("dosage_form")),
        "substance_name": of.get("substance_name"),
        "product_ndc": _first_of(of.get("product_ndc")),
    }


def collect_text_fields(label: Dict[str, Any]) -> Dict[str, str]:
    """Flatten top-level textual fields from an openFDA label result.

    We only consider top-level keys where values are strings or lists of strings.
    """
    out: Dict[str, str] = {}
    for k, v in (label or {}).items():
        if k == "openfda":
            continue
        if isinstance(v, str):
            s = v.strip()
            if s:
                out[k] = s
        elif isinstance(v, list):
            parts = [str(x).strip() for x in v if str(x).strip()]
            if parts:
                out[k] = "\n\n".join(parts)
    return out


def find_hits(text_fields: Dict[str, str], keywords: List[str], max_total: int = 20) -> List[Dict[str, Any]]:
    """Return compact snippet hits across all fields."""
    hits: List[Dict[str, Any]] = []
    if not keywords:
        return hits

    kws = [k for k in (kw.strip() for kw in keywords) if k]
    if not kws:
        return hits

    for kw in kws:
        pat = re.compile(re.escape(kw), re.IGNORECASE)
        for field, text in text_fields.items():
            for m in pat.finditer(text):
                start = max(0, m.start() - 60)
                end = min(len(text), m.end() + 60)
                snippet = text[start:end].replace("\n", " ").strip()
                hits.append({
                    "keyword": kw,
                    "field": field,
                    "snippet": snippet,
                    "index": m.start(),
                })
                if len(hits) >= max_total:
                    return hits
    return hits


def _compact(s: Optional[str], max_len: int = 280) -> Optional[str]:
    if not s:
        return None
    x = re.sub(r"\s+", " ", str(s)).strip()
    if len(x) <= max_len:
        return x
    return x[: max_len - 1] + "…"


def _parse_sections(sections: List[str]) -> Optional[List[str]]:
    """Parse --sections.

    Accepts comma-separated values, repeatable.
    Returns None when no selection (meaning use defaults).
    """
    if not sections:
        return None
    out: List[str] = []
    for s in sections:
        for part in (p.strip() for p in str(s).split(",")):
            if part:
                out.append(part)
    if not out:
        return None
    if any(x.lower() == "all" for x in out):
        return [
            "boxed_warning",
            "indications_and_usage",
            "dosage_and_administration",
            "contraindications",
            "warnings_and_precautions",
            "drug_interactions",
            "adverse_reactions",
        ]
    return out


DEFAULT_SECTIONS_STANDARD = [
    "boxed_warning",
    "indications_and_usage",
    "dosage_and_administration",
    "contraindications",
    "warnings_and_precautions",
    "drug_interactions",
    "adverse_reactions",
]

# Pharmacist-facing bundle: still label-first, but covers the sections pharmacists reach for.
DEFAULT_SECTIONS_PHARMACIST = [
    "highlights_of_prescribing_information",
    "recent_major_changes",
    "boxed_warning",
    "indications_and_usage",
    "dosage_and_administration",
    "dosage_forms_and_strengths",
    "contraindications",
    "warnings_and_precautions",
    "drug_interactions",
    "adverse_reactions",
    "use_in_specific_populations",
    "patient_counseling_information",
    "how_supplied",
    "storage_and_handling",
]


def _compact_recall(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "recall_number": r.get("recall_number"),
        "status": r.get("status"),
        "classification": r.get("classification"),
        "recalling_firm": r.get("recalling_firm"),
        "product_description": r.get("product_description"),
        "reason_for_recall": r.get("reason_for_recall"),
        "recall_initiation_date": r.get("recall_initiation_date"),
        "report_date": r.get("report_date"),
        "termination_date": r.get("termination_date"),
    }


def _compact_shortage(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": r.get("status"),
        "generic_name": r.get("generic_name"),
        "brand_name": r.get("brand_name"),
        "presentation": r.get("presentation"),
        "package_ndc": r.get("package_ndc"),
        "shortage_reason": r.get("shortage_reason"),
        "availability": r.get("availability"),
        "company_name": r.get("company_name"),
        "update_date": r.get("update_date"),
        "initial_posting_date": r.get("initial_posting_date"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query", help="Drug name, NDC, or set_id")

    # Output / shaping
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    ap.add_argument("--brief", action="store_true", help="Compact human-readable output")
    ap.add_argument(
        "--profile",
        choices=["standard", "pharmacist"],
        default="standard",
        help="Output profile (default: standard). 'pharmacist' prints a broader, pharmacist-friendly section bundle.",
    )
    ap.add_argument("--pharmacist", action="store_true", help="Alias for --profile pharmacist")
    ap.add_argument(
        "--sections",
        action="append",
        default=[],
        metavar="S",
        help="Comma-separated label sections to print/return (repeatable). Use 'all' for standard full set.",
    )
    ap.add_argument("--print-url", action="store_true", help="Print redacted URLs queried")

    # Disambiguation
    ap.add_argument("--set-id", dest="set_id", help="Force a specific SPL set_id (UUID)")
    ap.add_argument("--candidates", action="store_true", help="Show label candidates for the query")
    ap.add_argument("--pick", type=int, help="Pick Nth candidate label (1-indexed)")

    # Extras
    ap.add_argument("--recalls", action="store_true", help="Include recent recall enforcement matches")
    ap.add_argument("--recalls-max", type=int, default=5, help="Max recall matches (default: 5)")

    ap.add_argument("--shortages", action="store_true", help="Include drug shortage matches")
    ap.add_argument("--shortages-max", type=int, default=5, help="Max shortage matches (default: 5)")

    ap.add_argument("--faers", action="store_true", help="Include FAERS adverse event reaction counts (signal only)")
    ap.add_argument("--faers-max", type=int, default=10, help="Max FAERS reactions to return (default: 10)")

    ap.add_argument("--rxclass", action="store_true", help="Include RxClass drug class info")
    ap.add_argument("--rxclass-max", type=int, default=15, help="Max RxClass items (default: 15)")

    ap.add_argument("--interactions", action="store_true", help="Include RxNav interaction list (signal only)")
    ap.add_argument("--interactions-max", type=int, default=20, help="Max interactions to return (default: 20)")

    ap.add_argument("--chem", action="store_true", help="Include PubChem chemical properties (best-effort)")

    ap.add_argument("--dailymed", action="store_true", help="Include DailyMed SPL metadata and media links")
    ap.add_argument("--dailymed-media-max", type=int, default=10, help="Max DailyMed media items (default: 10)")

    ap.add_argument("--images", action="store_true", help="Include DailyMed media images (pill/label images when available)")
    ap.add_argument("--rximage", action="store_true", help="Alias for --images (RxImage API was retired in 2021)")

    ap.add_argument("--orangebook", action="store_true", help="Lookup FDA Orange Book products (TE codes, NDA/ANDA)")
    ap.add_argument("--orangebook-max", type=int, default=10, help="Max Orange Book matches (default: 10)")

    ap.add_argument("--purplebook", action="store_true", help="Lookup FDA Purple Book biologics/biosimilars")
    ap.add_argument("--purplebook-max", type=int, default=10, help="Max Purple Book matches (default: 10)")

    # Pharmacist workflow helpers (best-effort)
    ap.add_argument(
        "--hazardous",
        action="store_true",
        help="Flag if the drug appears on the NIOSH hazardous drugs list (best-effort, cached).",
    )
    ap.add_argument(
        "--rems",
        action="store_true",
        help="Best-effort FDA REMS lookup/linking (may be blocked by FDA abuse-detection).",
    )

    # Keyword search
    ap.add_argument(
        "--find",
        action="append",
        default=[],
        metavar="KEYWORD",
        help="Find keyword in retrieved label text (repeatable, case-insensitive)",
    )
    ap.add_argument(
        "--find-max",
        type=int,
        default=20,
        help="Max total find hits to return (default: 20)",
    )

    args = ap.parse_args()

    # Shorthand alias.
    if getattr(args, "pharmacist", False):
        args.profile = "pharmacist"

    # RxImage API was retired, treat --rximage as an alias for DailyMed media images.
    if getattr(args, "rximage", False):
        args.images = True

    q = args.query.strip()

    out: Dict[str, Any] = {
        "input": {"query": q, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
        "rxnorm": {},
        "rxnav": {},
        "openfda": {},
        "pubchem": {},
        "medlineplus": {},
        "notes": [],
    }

    rxcui: Optional[str] = None
    rx_name: Optional[str] = None
    selected_sections: Optional[List[str]] = None

    try:
        selected_sections = _parse_sections(args.sections)
        out["input"]["sections"] = selected_sections

        ndc_set_id: Optional[str] = None

        forced_set_id = args.set_id or (q if is_uuid_like(q) else None)
        if forced_set_id:
            out["input"]["type"] = "set_id"
            ndc_set_id = forced_set_id
        elif is_probable_ndc(q):
            out["input"]["type"] = "ndc"
            ndc_results = openfda_ndc_lookup(q)
            out["openfda"]["ndc_results"] = ndc_results

            # If NDC response includes SPL set id and/or RxCUI, use it.
            for r in ndc_results:
                of = r.get("openfda") or {}

                spl_set = of.get("spl_set_id") or []
                if isinstance(spl_set, list) and spl_set:
                    ndc_set_id = str(spl_set[0])

                rxcuis = of.get("rxcui") or []
                if isinstance(rxcuis, list) and rxcuis and not rxcui:
                    rxcui = str(rxcuis[0])

                if ndc_set_id and rxcui:
                    break
        else:
            out["input"]["type"] = "name"

        # Resolve name to RxCUI (only when the input is a drug name).
        if out["input"].get("type") == "name" and not rxcui:
            cand = rxnorm_approximate(q, max_entries=5)
            out["rxnorm"]["candidates"] = cand
            best = pick_best_candidate(cand)
            if best:
                rxcui = str(best.get("rxcui")) if best.get("rxcui") else None
                out["rxnorm"]["best"] = best

        if rxcui or ndc_set_id:
            if rxcui:
                rx_name = rxnorm_name_for_rxcui(rxcui)
                out["rxnorm"]["rxcui"] = rxcui
                out["rxnorm"]["name"] = rx_name

            label_candidates: List[Dict[str, Any]] = []
            if out["input"].get("type") == "name" and (args.candidates or args.pick):
                term = rx_name or q
                label_candidates = openfda_label_candidates(term, limit=10)
                out["openfda"]["candidates"] = [label_candidate_summary(x) for x in label_candidates]

            label = None
            if ndc_set_id:
                out["openfda"]["ndc_set_id"] = ndc_set_id
                label = openfda_label_by_set_id(ndc_set_id)
                if not label:
                    out["notes"].append("No openFDA label found by set_id from NDC/set_id lookup.")

            if not label and args.pick and out["input"].get("type") == "name":
                if not label_candidates:
                    out["notes"].append("No label candidates available to pick from.")
                else:
                    idx = int(args.pick) - 1
                    if 0 <= idx < len(label_candidates):
                        label = label_candidates[idx]
                        out["openfda"]["picked"] = int(args.pick)
                    else:
                        out["notes"].append(f"--pick {args.pick} out of range (1..{len(label_candidates)}).")

            if not label and rxcui:
                label = openfda_label_by_rxcui(rxcui)

            if not label and rx_name:
                out["notes"].append("No openFDA label found by RxCUI, falling back to generic/substance/brand candidates.")
                if label_candidates:
                    label = label_candidates[0]
                else:
                    label = openfda_label_by_generic_name(rx_name)

            if label:
                setid = None
                openfda_block = label.get("openfda") or {}
                # openFDA label sometimes has spl_set_id in openfda
                spl_set_id = openfda_block.get("spl_set_id")
                if isinstance(spl_set_id, list) and spl_set_id:
                    setid = spl_set_id[0]

                section_keys = selected_sections or [
                    "boxed_warning",
                    "indications_and_usage",
                    "dosage_and_administration",
                    "contraindications",
                    "warnings_and_precautions",
                    "drug_interactions",
                    "adverse_reactions",
                ]
                sections = {k: label_section(label, k) for k in section_keys}

                label_obj: Dict[str, Any] = {
                    "effective_time": label.get("effective_time"),
                    "id": label.get("id"),
                    "setid": setid,
                    "dailymed": daily_med_url_from_setid(setid),
                    "openfda": {
                        "brand_name": openfda_block.get("brand_name"),
                        "generic_name": openfda_block.get("generic_name"),
                        "manufacturer_name": openfda_block.get("manufacturer_name"),
                        "product_ndc": openfda_block.get("product_ndc"),
                        "package_ndc": openfda_block.get("package_ndc"),
                        "route": openfda_block.get("route"),
                        "dosage_form": openfda_block.get("dosage_form"),
                        "substance_name": openfda_block.get("substance_name"),
                        "rxcui": openfda_block.get("rxcui"),
                    },
                    "sections": sections,
                }

                if args.find:
                    fields = collect_text_fields(label)
                    label_obj["find"] = {
                        "keywords": args.find,
                        "hits": find_hits(fields, args.find, max_total=max(1, int(args.find_max))),
                    }

                out["openfda"]["label"] = label_obj

                # Optional: recalls
                if args.recalls:
                    product_ndc0 = _first_of(openfda_block.get("product_ndc"))
                    brand0 = _first_of(openfda_block.get("brand_name"))
                    generic0 = _first_of(openfda_block.get("generic_name")) or rx_name or q

                    recall_queries: List[str] = []
                    if product_ndc0:
                        recall_queries.append(f"openfda.product_ndc:{openfda_qstr(product_ndc0)}")
                    if brand0:
                        recall_queries.append(f"product_description:{openfda_qstr(brand0)}")
                    if generic0:
                        recall_queries.append(f"product_description:{openfda_qstr(generic0)}")

                    recalls: List[Dict[str, Any]] = []
                    used_query = None
                    for rq in recall_queries:
                        rr = openfda_enforcement_search(rq, limit=max(1, int(args.recalls_max)))
                        if rr:
                            used_query = rq
                            recalls = rr
                            break
                    out["openfda"]["recalls"] = {
                        "query": used_query,
                        "results": [_compact_recall(r) for r in recalls],
                    }

                # Optional: shortages
                if args.shortages:
                    brand0 = _first_of(openfda_block.get("brand_name"))
                    generic0 = _first_of(openfda_block.get("generic_name")) or q

                    shortage_queries: List[str] = []
                    if generic0:
                        shortage_queries.append(f"generic_name:{openfda_qstr(generic0)}")
                    if brand0:
                        shortage_queries.append(f"brand_name:{openfda_qstr(brand0)}")
                    if q and q != generic0:
                        shortage_queries.append(f"generic_name:{openfda_qstr(q)}")
                        shortage_queries.append(f"brand_name:{openfda_qstr(q)}")

                    shortages: List[Dict[str, Any]] = []
                    used_query = None
                    for sq in shortage_queries:
                        sr = openfda_shortages_search(sq, limit=max(1, int(args.shortages_max)))
                        if sr:
                            used_query = sq
                            shortages = sr
                            break
                    out["openfda"]["shortages"] = {
                        "query": used_query,
                        "results": [_compact_shortage(r) for r in shortages],
                    }

                # Optional: FAERS signal (reaction counts)
                if args.faers:
                    brand0 = _first_of(openfda_block.get("brand_name"))
                    mp = (brand0 or (rx_name or q)).upper()
                    faers_q = f"patient.drug.medicinalproduct:{openfda_qstr(mp)}"
                    faers = openfda_event_count(
                        faers_q,
                        "patient.reaction.reactionmeddrapt.exact",
                        limit=max(1, int(args.faers_max)),
                    )
                    out["openfda"]["faers"] = {
                        "query": faers_q,
                        "reactions": faers,
                        "note": "FAERS is reporting data, not causality. Use as a signal only.",
                    }

                # Optional: RxClass
                if args.rxclass and rxcui:
                    classes = rxclass_by_rxcui(rxcui)
                    out["rxclass"] = classes[: max(1, int(args.rxclass_max))]

                # Optional: RxNav interactions
                if args.interactions and rxcui:
                    try:
                        inter = rxnav_interactions_by_rxcui(rxcui)
                        out["rxnav"]["interactions"] = {
                            "rxcui": rxcui,
                            "results": inter[: max(1, int(args.interactions_max))],
                            "note": "Interactions are informational and may be incomplete. Verify against official labeling and clinical references.",
                        }
                    except Exception as e:
                        out["notes"].append(f"RxNav interactions lookup failed: {e}")

                # Optional: PubChem chemical profile
                if args.chem:
                    # Prefer a generic/substance name for PubChem.
                    generic0 = _first_of(openfda_block.get("substance_name")) or _first_of(openfda_block.get("generic_name")) or rx_name or q
                    chem = pubchem_compound_properties(generic0)
                    if chem:
                        out["pubchem"]["compound"] = {
                            "query": generic0,
                            "properties": chem,
                            "url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{chem.get('CID')}" if chem.get("CID") else None,
                        }
                    else:
                        out["notes"].append("PubChem lookup returned no match (try a generic ingredient name).")

                # Optional: DailyMed metadata and media
                if (args.dailymed or args.images) and setid:
                    dm = dailymed_enrich(setid, media_max=max(1, int(args.dailymed_media_max)))
                    out["dailymed"] = dm
                    if args.images:
                        images = []
                        for m in (dm.get("media") or []):
                            mt = (m or {}).get("mime_type") or ""
                            if isinstance(mt, str) and mt.startswith("image/"):
                                images.append(m)
                        out["images"] = images[: max(1, int(args.dailymed_media_max))]
                elif (args.dailymed or args.images) and not setid:
                    out["notes"].append("DailyMed set_id not available for this label.")

                # Optional: Orange Book
                if args.orangebook:
                    term = _first_of(openfda_block.get("generic_name")) or rx_name or q
                    out["orangebook"] = orangebook_search(term, max_results=max(1, int(args.orangebook_max)))

                # Optional: Purple Book
                if args.purplebook:
                    term = _first_of(openfda_block.get("substance_name")) or _first_of(openfda_block.get("generic_name")) or rx_name or q
                    out["purplebook"] = purplebook_search(term, max_results=max(1, int(args.purplebook_max)))

            else:
                out["notes"].append("No openFDA label match found.")

            if rxcui:
                try:
                    mpl = medlineplus_by_rxcui(rxcui)
                    out["medlineplus"]["raw"] = mpl

                    # Extract a compact list of results.
                    feed = (mpl or {}).get("feed") or {}
                    entries = feed.get("entry") or []
                    if isinstance(entries, dict):
                        entries = [entries]
                    compact = []
                    for e in entries[:10]:
                        title = e.get("title")
                        if isinstance(title, dict):
                            title = title.get("_value") or title.get("value")
                        link = None
                        links = e.get("link") or []
                        if isinstance(links, dict):
                            links = [links]
                        for l in links:
                            href = l.get("href")
                            if href:
                                link = href
                                break
                        if title or link:
                            compact.append({"title": title, "url": link})
                    out["medlineplus"]["results"] = compact
                except Exception as e:
                    out["notes"].append(f"MedlinePlus Connect lookup failed: {e}")
        else:
            if out["input"].get("type") == "ndc":
                out["notes"].append("No openFDA NDC match found for that code.")
            else:
                out["notes"].append("Could not resolve RxCUI from input.")

    except Exception as e:
        out["error"] = str(e)

    if args.print_url or args.json:
        out.setdefault("debug", {})["urls"] = URL_LOG

    if args.json:
        sys.stdout.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
        return 0 if "error" not in out else 2

    # Human-readable.
    print(f"Query: {q}")
    if rxcui:
        print(f"RxCUI: {rxcui}" + (f" ({rx_name})" if rx_name else ""))
    else:
        print("RxCUI: (not resolved)")

    label_obj = out.get("openfda", {}).get("label")
    if label_obj:
        print("\nopenFDA label")
        et = label_obj.get("effective_time")
        if et:
            print(f"- effective_time: {et}")
        if label_obj.get("dailymed"):
            print(f"- DailyMed: {label_obj['dailymed']}")

        of = label_obj.get("openfda") or {}
        # Print a compact identifier line when available.
        brand = (of.get("brand_name") or [None])[0] if isinstance(of.get("brand_name"), list) else of.get("brand_name")
        generic = (of.get("generic_name") or [None])[0] if isinstance(of.get("generic_name"), list) else of.get("generic_name")
        mfr = (of.get("manufacturer_name") or [None])[0] if isinstance(of.get("manufacturer_name"), list) else of.get("manufacturer_name")
        if brand or generic or mfr:
            print(f"- product: {brand or ''} {('/ ' + generic) if generic else ''} {('(' + mfr + ')') if mfr else ''}".strip())

        sections = label_obj.get("sections") or {}
        order = [
            ("boxed_warning", "Boxed warning"),
            ("indications_and_usage", "Indications and usage"),
            ("dosage_and_administration", "Dosage and administration"),
            ("contraindications", "Contraindications"),
            ("warnings_and_precautions", "Warnings and precautions"),
            ("drug_interactions", "Drug interactions"),
            ("adverse_reactions", "Adverse reactions"),
        ]
        for k, title in order:
            txt = sections.get(k)
            if not txt:
                continue
            if args.brief:
                txt = _compact(txt, max_len=420) or txt
            print(f"\n{title}\n{txt}")

    # Disambiguation: candidates
    cands = out.get("openfda", {}).get("candidates")
    if args.candidates and cands:
        print("\nCandidates")
        for i, c in enumerate(cands[:10], start=1):
            prod = " / ".join([x for x in [c.get("brand_name"), c.get("generic_name")] if x])
            meta = " ".join([x for x in [c.get("dosage_form"), c.get("route")] if x])
            et = c.get("effective_time") or ""
            setid = c.get("setid") or ""
            dm = c.get("dailymed") or ""
            line = f"{i}. {prod}".strip()
            if meta:
                line += f" | {meta}"
            if et:
                line += f" | effective_time={et}"
            if setid:
                line += f" | set_id={setid}"
            if dm:
                line += f" | {dm}"
            print(f"- {line}")

    ndc_results = out.get("openfda", {}).get("ndc_results")
    if ndc_results:
        print("\nopenFDA NDC matches")
        for r in ndc_results[:5]:
            brand = r.get("brand_name")
            generic = r.get("generic_name")
            product_ndc = r.get("product_ndc")
            # package_ndc is nested under packaging[]
            pkgs = r.get("packaging") or []
            pkg_ndcs = []
            if isinstance(pkgs, list):
                for p in pkgs[:3]:
                    if isinstance(p, dict) and p.get("package_ndc"):
                        pkg_ndcs.append(p.get("package_ndc"))
            pkg_str = ",".join(pkg_ndcs)
            print(f"- {brand or ''} / {generic or ''} | product_ndc={product_ndc} | package_ndc={pkg_str}")

    recalls = out.get("openfda", {}).get("recalls")
    if args.recalls and recalls:
        print("\nRecalls")
        if recalls.get("query"):
            print(f"- query: {recalls['query']}")
        for r in (recalls.get("results") or [])[: int(args.recalls_max)]:
            rn = r.get("recall_number")
            cls = r.get("classification")
            st = r.get("status")
            reason = _compact(r.get("reason_for_recall"), 220)
            print(f"- {rn} | {cls} | {st} | {reason}")

    shortages = out.get("openfda", {}).get("shortages")
    if args.shortages and shortages:
        print("\nShortages")
        if shortages.get("query"):
            print(f"- query: {shortages['query']}")
        for r in (shortages.get("results") or [])[: int(args.shortages_max)]:
            gn = r.get("generic_name")
            pres = _compact(r.get("presentation"), 180)
            st = r.get("status")
            print(f"- {st} | {gn} | {pres}")

    faers = out.get("openfda", {}).get("faers")
    if args.faers and faers:
        print("\nFAERS (signal)")
        if faers.get("query"):
            print(f"- query: {faers['query']}")
        for r in (faers.get("reactions") or [])[: int(args.faers_max)]:
            term = r.get("term")
            cnt = r.get("count")
            print(f"- {term}: {cnt}")

    rxclass = out.get("rxclass")
    if args.rxclass and rxclass:
        print("\nRxClass")
        for c in rxclass[: int(args.rxclass_max)]:
            nm = c.get("className")
            ct = c.get("classType")
            src = c.get("relaSource")
            print(f"- {nm} ({ct}, {src})")

    inter = (out.get("rxnav") or {}).get("interactions")
    if args.interactions and inter:
        print("\nRxNav interactions (signal)")
        for r in (inter.get("results") or [])[: int(args.interactions_max)]:
            sev = (r or {}).get("severity") or ""
            desc = _compact((r or {}).get("description"), 260)
            print(f"- {sev}: {desc}".strip())

    chem = (out.get("pubchem") or {}).get("compound")
    if args.chem and chem:
        print("\nPubChem")
        props = (chem.get("properties") or {}) if isinstance(chem, dict) else {}
        cid = props.get("CID")
        mf = props.get("MolecularFormula")
        mw = props.get("MolecularWeight")
        inchikey = props.get("InChIKey")
        if cid:
            print(f"- CID: {cid}")
        if mf or mw:
            print(f"- formula: {mf or ''} | MW: {mw or ''}".strip())
        if inchikey:
            print(f"- InChIKey: {inchikey}")
        if chem.get("url"):
            print(f"- {chem.get('url')}")

    dm = out.get("dailymed")
    if (args.dailymed or args.images) and dm:
        print("\nDailyMed")
        if dm.get("title"):
            print(f"- title: {dm.get('title')}")
        if dm.get("published_date"):
            print(f"- published_date: {dm.get('published_date')}")
        if dm.get("spl_version") is not None:
            print(f"- spl_version: {dm.get('spl_version')}")
        hist = dm.get("history") or []
        if hist:
            # show newest first
            h0 = hist[0]
            print(f"- versions: {len(hist)} (latest spl_version={h0.get('spl_version')} published_date={h0.get('published_date')})")

    images = out.get("images")
    if args.images and images:
        print("\nImages")
        for im in images[: int(args.dailymed_media_max)]:
            print(f"- {(im or {}).get('name')}: {(im or {}).get('url')}")

    ob = out.get("orangebook")
    if args.orangebook and ob:
        print("\nOrange Book")
        for r in ob[: int(args.orangebook_max)]:
            tn = r.get("trade_name")
            ing = r.get("ingredient")
            te = r.get("te_code")
            appl = r.get("appl_type")
            no = r.get("appl_no")
            strength = r.get("strength")
            print(f"- {tn} | {ing} | {strength} | {appl}{no} | TE={te}")

    pb = out.get("purplebook")
    if args.purplebook and pb:
        print("\nPurple Book")
        for r in pb[: int(args.purplebook_max)]:
            pn = r.get("proprietary_name")
            pr = r.get("proper_name")
            bla = r.get("bla_number")
            bt = r.get("bla_type")
            inter = r.get("interchangeable")
            print(f"- {pn} | {pr} | BLA={bla} | {bt} | interchangeable={inter}")

    mpl_results = out.get("medlineplus", {}).get("results")
    if mpl_results:
        print("\nMedlinePlus")
        for r in mpl_results[:5]:
            t = (r or {}).get("title") or "(untitled)"
            u = (r or {}).get("url") or ""
            print(f"- {t}: {u}" if u else f"- {t}")

    # Keyword find results
    if label_obj and isinstance(label_obj, dict) and (label_obj.get("find") or {}).get("hits"):
        print("\nFind")
        hits = (label_obj.get("find") or {}).get("hits") or []
        for h in hits[: int(args.find_max) if getattr(args, 'find_max', None) else 20]:
            kw = h.get("keyword")
            field = h.get("field")
            snip = h.get("snippet")
            print(f"- {kw} [{field}]: {snip}")

    if args.print_url and URL_LOG:
        print("\nURLs")
        for u in URL_LOG:
            print(f"- {u}")

    if out.get("notes"):
        print("\nNotes")
        for n in out["notes"]:
            print(f"- {n}")

    if "error" in out:
        print(f"\nERROR: {out['error']}")

    return 0 if "error" not in out else 2


if __name__ == "__main__":
    raise SystemExit(main())
