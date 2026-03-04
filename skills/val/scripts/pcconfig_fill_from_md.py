#!/usr/bin/env python3
"""pcconfig_fill_from_md.py

Apply a Markdown "fill sheet" to the Notion PCConfig data source.

Input:
- Read Markdown from stdin (same format as the user's pasted sheet)

Behavior:
- Parse sections like:
  ## 1-1 NVIDIA GeForce GTX 1050 2GB（RECRYZEN）
  - Identifier（型番）: ...
  - PC: ...
  - Installed（true/false）: t/f
  ...
- Find matching PCConfig row by:
  1) Identifier exact match (best-effort normalization), else
  2) (PC + Category + normalized Name)
  3) fallback: normalized Name only (if unique)
- Patch only missing fields in PCConfig (do not overwrite populated values)
- Output:
  - summary of patched/unchanged/unmatched
  - remaining markdown with items still unmatched or still missing fields

Notes:
- Notion API key: ~/.config/notion/api_key
- PCConfig data_source_id: 2fb44994-92c3-8059-8e34-000b086a0041

"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from dataclasses import dataclass, field

NOTION_VERSION = "2025-09-03"
NOTION_API = "https://api.notion.com/v1"
PCCONFIG_DS = "2fb44994-92c3-8059-8e34-000b086a0041"

PC_ALIASES = {
    "ryzenrec": "RECRYZEN",
    "recryzen": "RECRYZEN",
}

STATUS_ALIASES = {
    "insyalled": "Installed",
    "installed": "Installed",
    "purchased": "Purchased",
    "arrived": "Arrived",
    "planned": "Planned",
    "retired": "Retired",
    "sold": "Sold",
}

BOOL_ALIASES_TRUE = {"t", "true", "yes", "y", "1", "on"}
BOOL_ALIASES_FALSE = {"f", "false", "no", "n", "0", "off"}


def read_api_key() -> str:
    p = os.path.expanduser("~/.config/notion/api_key")
    return open(p, "r", encoding="utf-8").read().strip()


def notion_req(method: str, path: str, body: dict | None = None):
    key = read_api_key()
    url = NOTION_API + path
    data = None
    headers = {
        "Authorization": f"Bearer {key}",
        "Notion-Version": NOTION_VERSION,
    }
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(url, method=method, data=data, headers=headers)
    with urllib.request.urlopen(r, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw) if raw else {}


def rt_plain(props: dict, name: str) -> str:
    v = props.get(name)
    if not v:
        return ""
    t = v.get("type")
    if t == "rich_text":
        return "".join([x.get("plain_text", "") for x in (v.get("rich_text") or [])]).strip()
    if t == "title":
        return "".join([x.get("plain_text", "") for x in (v.get("title") or [])]).strip()
    return ""


def sel_name(props: dict, name: str) -> str:
    v = props.get(name)
    if not v:
        return ""
    t = v.get("type")
    if t == "select":
        s = v.get("select")
        return (s or {}).get("name", "") if s else ""
    if t == "status":
        s = v.get("status")
        return (s or {}).get("name", "") if s else ""
    return ""


def num_val(props: dict, name: str):
    v = props.get(name)
    if not v:
        return None
    if v.get("type") == "number":
        return v.get("number")
    return None


def chk_val(props: dict, name: str):
    v = props.get(name)
    if not v:
        return None
    if v.get("type") == "checkbox":
        return bool(v.get("checkbox"))
    return None


def date_val(props: dict, name: str):
    v = props.get(name)
    if not v:
        return None
    if v.get("type") == "date":
        d = v.get("date")
        return (d or {}).get("start") if d else None
    return None


def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def norm_key(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def clean_identifier(s: str) -> str:
    s = norm_ws(s)
    # remove leading numbering like "1 Palit ..."
    s = re.sub(r"^\d+\s+", "", s)
    # strip markdown bold
    s = s.replace("**", "")
    return s


def parse_bool(s: str):
    v = norm_key(s)
    if v in BOOL_ALIASES_TRUE:
        return True
    if v in BOOL_ALIASES_FALSE:
        return False
    return None


def parse_price(s: str):
    s = s.replace("**", "")
    s = s.strip()
    s = re.sub(r"[^0-9,]", "", s)
    if not s:
        return None
    return int(s.replace(",", ""))


def parse_pc(s: str) -> str:
    s = norm_ws(s)
    # keep only first token before spaces/date annotations
    s = s.split()[0]
    base = norm_key(s)
    return PC_ALIASES.get(base, s)


def parse_status(s: str) -> str | None:
    s = norm_ws(s)
    if not s or s.lower().startswith("unassigned"):
        return None
    k = norm_key(s)
    return STATUS_ALIASES.get(k, s)


@dataclass
class FillItem:
    heading: str
    name: str
    fields: dict = field(default_factory=dict)
    raw_lines: list[str] = field(default_factory=list)


FIELD_MAP = {
    "identifier": "Identifier",
    "spec": "Spec",
    "qty": "Qty",
    "pc": "PC",
    "installed": "Installed",
    "active": "Active",
    "status": "Status",
    "purchase date": "Purchase Date",
    "purchase vendor": "Purchase Vendor",
    "purchase price": "Purchase Price",
    "notes": "Notes",
    "category": "Category",
}


def parse_md(md: str) -> list[FillItem]:
    lines = md.splitlines()
    items: list[FillItem] = []
    cur: FillItem | None = None

    for line in lines:
        if line.startswith("## "):
            # start new item
            if cur:
                items.append(cur)
            heading = line[3:].strip()
            # name = heading without leading numbering and parenthetical
            name = re.sub(r"^\d+[\-\d]*\s+", "", heading)
            name = re.sub(r"（.*?）", "", name).strip()
            cur = FillItem(heading=heading, name=name, fields={}, raw_lines=[line])
            continue

        if cur is None:
            continue

        cur.raw_lines.append(line)
        m = re.match(r"^\s*-\s*([^:]+):\s*(.*)$", line)
        if not m:
            continue
        key_raw, val = m.group(1).strip(), m.group(2).strip()
        key_norm = norm_key(key_raw)
        # Normalize Japanese labels to our canonical
        key_norm = (
            key_norm
            .replace("（", "(")
            .replace("）", ")")
        )
        # collapse variants
        if key_norm.startswith("identifier"):
            cur.fields["Identifier"] = clean_identifier(val)
        elif key_norm.startswith("spec"):
            if val:
                cur.fields["Spec"] = val
        elif key_norm.startswith("qty"):
            try:
                cur.fields["Qty"] = int(re.sub(r"[^0-9]", "", val) or "0")
            except Exception:
                pass
        elif key_norm.startswith("pc"):
            if val:
                cur.fields["PC"] = parse_pc(val)
        elif key_norm.startswith("installed"):
            b = parse_bool(val)
            if b is not None:
                cur.fields["Installed"] = b
        elif key_norm.startswith("active"):
            b = parse_bool(val)
            if b is not None:
                cur.fields["Active"] = b
        elif key_norm.startswith("status"):
            st = parse_status(val)
            if st:
                cur.fields["Status"] = st
        elif key_norm.startswith("purchase date"):
            if re.match(r"^\d{4}-\d{2}-\d{2}$", val):
                cur.fields["Purchase Date"] = val
        elif key_norm.startswith("purchase vendor"):
            if val:
                cur.fields["Purchase Vendor"] = val
        elif key_norm.startswith("purchase price"):
            pr = parse_price(val)
            if pr is not None:
                cur.fields["Purchase Price"] = pr
        elif key_norm.startswith("notes"):
            if val:
                cur.fields["Notes"] = val
        elif key_norm.startswith("category"):
            if val:
                cur.fields["Category"] = val

    if cur:
        items.append(cur)

    return items


def query_all(ds_id: str, page_size: int = 100):
    out = []
    cursor = None
    while True:
        payload = {"page_size": page_size}
        if cursor:
            payload["start_cursor"] = cursor
        j = notion_req("POST", f"/data_sources/{ds_id}/query", payload)
        out.extend(j.get("results", []))
        if not j.get("has_more"):
            break
        cursor = j.get("next_cursor")
        if not cursor:
            break
        if len(out) > 5000:
            break
    return out


def build_patch(fill: dict, main_props: dict):
    patch = {}

    def set_rich_text(field: str, value: str):
        patch[field] = {"rich_text": [{"type": "text", "text": {"content": value}}]}

    def set_number(field: str, value):
        patch[field] = {"number": float(value)}

    def set_date(field: str, value: str):
        patch[field] = {"date": {"start": value}}

    def set_checkbox(field: str, value: bool):
        patch[field] = {"checkbox": bool(value)}

    def set_select(field: str, value: str):
        patch[field] = {"select": {"name": value}}

    def set_status(field: str, value: str):
        patch[field] = {"status": {"name": value}}

    # Rich text
    for f in ["Notes", "Identifier", "Spec", "Purchase Vendor"]:
        fv = fill.get(f)
        mv = rt_plain(main_props, f)
        if fv and not mv:
            set_rich_text(f, str(fv))

    # number
    for f in ["Qty", "Purchase Price"]:
        fv = fill.get(f)
        mv = num_val(main_props, f)
        if fv is not None and mv is None:
            set_number(f, fv)

    # date
    fv = fill.get("Purchase Date")
    mv = date_val(main_props, "Purchase Date")
    if fv and not mv:
        set_date("Purchase Date", fv)

    # checkboxes: only set true if fill true and main false/None
    for f in ["Installed", "Active"]:
        fv = fill.get(f)
        mv = chk_val(main_props, f)
        if fv is True and (mv is False or mv is None):
            set_checkbox(f, True)

    # PC / Category: only if missing
    fv = fill.get("PC")
    mv = sel_name(main_props, "PC")
    if fv and not mv:
        set_select("PC", fv)

    fv = fill.get("Category")
    mv = sel_name(main_props, "Category")
    if fv and not mv:
        set_select("Category", fv)

    # Status
    fv = fill.get("Status")
    mv = sel_name(main_props, "Status")
    if fv and not mv:
        set_status("Status", fv)

    return patch


def main():
    md = sys.stdin.read()
    items = parse_md(md)

    main_rows = query_all(PCCONFIG_DS)

    # Build indexes
    by_ident = {}
    by_tuple = {}
    by_name = {}

    for r in main_rows:
        props = r.get("properties") or {}
        ident = clean_identifier(rt_plain(props, "Identifier"))
        name = norm_key(rt_plain(props, "Name"))
        pc = sel_name(props, "PC")
        cat = sel_name(props, "Category")
        if ident:
            by_ident.setdefault(ident, []).append(r)
        if pc and cat and name:
            by_tuple.setdefault((pc, cat, name), []).append(r)
        if name:
            by_name.setdefault(name, []).append(r)

    patched = 0
    nochange = 0
    unmatched = 0
    remaining: list[FillItem] = []

    for it in items:
        fill = dict(it.fields)
        # derive category from section headers if missing (GPU/RAM/PSU etc)
        if "Category" not in fill:
            h = it.heading.lower()
            if "gpu" in h or "geforce" in h or "rtx" in h or "gtx" in h:
                fill["Category"] = "GPU"
            elif "ram" in h or "ddr" in h:
                fill["Category"] = "RAM"
            elif "psu" in h or "krpw" in h or "rm1200" in h:
                fill["Category"] = "PSU"
            elif "nvme" in h or "m.2" in h or "ssd" in h or "plextor" in h:
                # could be SATA SSD too, but assume NVMe for these entries
                fill["Category"] = "NVMe SSD"

        ident = clean_identifier(fill.get("Identifier", ""))
        name_key = norm_key(it.name)
        pc = fill.get("PC")
        cat = fill.get("Category")

        target = None
        if ident and ident in by_ident and len(by_ident[ident]) == 1:
            target = by_ident[ident][0]
        elif pc and cat and (pc, cat, name_key) in by_tuple and len(by_tuple[(pc, cat, name_key)]) == 1:
            target = by_tuple[(pc, cat, name_key)][0]
        elif name_key in by_name and len(by_name[name_key]) == 1:
            target = by_name[name_key][0]

        if not target:
            unmatched += 1
            remaining.append(it)
            continue

        tprops = target.get("properties") or {}
        patch = build_patch(fill, tprops)

        if patch:
            patched += 1
            notion_req("PATCH", f"/pages/{target['id']}", {"properties": patch})
        else:
            nochange += 1

        # If after patch there are still fill fields that are blank in main, keep it.
        # (We don't re-fetch; approximate: if fill had values for fields that main already had, we consider done.)
        # Keep only if it was unmatched.

    # Produce remaining markdown
    out_lines = ["# PCConfig穴埋めシート（残り）", "", "（PCConfigへ反映できなかった／マッチできなかった項目のみ）", ""]
    for it in remaining:
        # Skip non-item headings like "記入ルール"
        if it.heading.strip() in ("記入ルール",):
            continue
        out_lines.append(f"## {it.heading}")
        for line in it.raw_lines[1:]:
            out_lines.append(line)
        out_lines.append("")

    sys.stderr.write(f"patched={patched} nochange={nochange} unmatched={unmatched} total_items={len(items)}\n")
    print("\n".join(out_lines))


if __name__ == "__main__":
    main()
