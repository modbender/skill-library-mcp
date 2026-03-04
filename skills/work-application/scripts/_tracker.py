"""
_tracker.py - Application tracking for the work-application skill.
Manages candidatures.md with add/list/update operations. Stdlib only.

Storage is delegated to _storage.py (local or Nextcloud).

Usage:
    from _tracker import log_application, list_applications, update_status
"""

import re
from datetime import datetime

_CANDIDATURES_NAME = "candidatures.md"

# Kept for init.py backward compat
from pathlib import Path
CANDIDATURES_FILE = Path.home() / ".openclaw" / "data" / "work-application" / _CANDIDATURES_NAME

_LEGEND = """\

---

**Legende statuts :** ⏳ en attente | 📞 entretien / call | 🤝 negociation | ✅ offre recue | ❌ refus | 🚫 desistement / cloture
"""

_HEADER = """\
# Suivi des candidatures

| Date | Entreprise | Poste | Lieu | Type | Salaire | Source | Contact | Email | Tel | Statut | Action | Prevu | Offre | Notes |
|------|------------|-------|------|------|---------|--------|---------|-------|-----|--------|--------|-------|-------|-------|
"""

_STATUS_ICONS = {
    "en_attente":   "\u23f3",
    "entretien":    "\U0001f4de",
    "negociation":  "\U0001f91d",
    "offre":        "\u2705",
    "refus":        "\u274c",
    "desistement":  "\U0001f6ab",
}

_STATUS_LABELS = {
    "\u23f3": "en_attente",
    "\U0001f4de": "entretien",
    "\U0001f91d": "negociation",
    "\u2705": "offre",
    "\u274c": "refus",
    "\U0001f6ab": "desistement",
}


def _store():
    from _storage import get_storage
    return get_storage()


def _ensure_file():
    """Create candidatures.md with header if it doesn't exist."""
    store = _store()
    if not store.exists(_CANDIDATURES_NAME):
        store.write_text(_CANDIDATURES_NAME, _HEADER)


def _parse_rows() -> list[dict]:
    """Parse all table rows from candidatures.md."""
    _ensure_file()
    content = _store().read_text(_CANDIDATURES_NAME)
    rows = []

    for line in content.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if "---" in line or "Entreprise" in line:
            continue
        cols = [c.strip() for c in line.split("|")]
        # Remove empty first/last from split
        cols = [c for c in cols if c or cols.index(c) not in (0, len(cols) - 1)]
        if len(cols) < 5:
            continue

        # Pad to 15 columns
        while len(cols) < 15:
            cols.append("")

        rows.append({
            "date":       cols[0],
            "company":    cols[1],
            "position":   cols[2],
            "location":   cols[3],
            "type":       cols[4],
            "salary":     cols[5],
            "source":     cols[6],
            "contact":    cols[7],
            "email":      cols[8],
            "phone":      cols[9],
            "status":     cols[10],
            "action":     cols[11],
            "planned":    cols[12],
            "offer_url":  cols[13],
            "notes":      cols[14],
        })

    return rows


def _row_to_line(row: dict) -> str:
    """Format a row dict as a Markdown table line."""
    def _v(key, required=False):
        val = row.get(key, "")
        if not val or val.strip() == "-":
            return "" if required else "\\-"
        return val

    cols = [
        _v("date", required=True),
        _v("company", required=True),
        _v("position", required=True),
        _v("location"),
        _v("type"),
        _v("salary"),
        _v("source"),
        _v("contact"),
        _v("email"),
        _v("phone"),
        row.get("status", "⏳"),
        _v("action"),
        _v("planned"),
        _v("offer_url"),
        _v("notes"),
    ]
    return "| " + " | ".join(cols) + " |"


def _write_all(rows: list[dict]):
    """Rewrite the entire candidatures file (used by update_status)."""
    lines = [_HEADER.rstrip()]
    for row in rows:
        lines.append(_row_to_line(row))
    _store().write_text(_CANDIDATURES_NAME, "\n".join(lines) + "\n")


def log_application(
    company: str,
    position: str,
    location: str = "",
    type_: str = "CDI",
    salary: str = "",
    source: str = "",
    url: str = "",
    contact: str = "",
    email: str = "",
    phone: str = "",
    notes: str = "",
) -> None:
    """Add a new application entry by appending a single line."""
    _ensure_file()
    now = datetime.now()
    offer_link = f"[Lien]({url})" if url else ""

    row = {
        "date":      now.strftime("%d/%m"),
        "company":   company.replace("|", "-"),
        "position":  position.replace("|", "-"),
        "location":  location.replace("|", "-"),
        "type":      type_,
        "salary":    salary.replace("|", "-"),
        "source":    source.replace("|", "-"),
        "contact":   contact.replace("|", "-"),
        "email":     email.replace("|", "-"),
        "phone":     phone.replace("|", "-"),
        "status":    "\u23f3",
        "action":    "-",
        "planned":   "-",
        "offer_url": offer_link,
        "notes":     notes.replace("|", "-"),
    }

    _store().append_text(_CANDIDATURES_NAME, _row_to_line(row) + "\n")


def list_applications(status: str = None) -> list[dict]:
    """
    List all applications, optionally filtered by status.
    Status can be: en_attente, entretien, negociation, offre, refus, desistement
    """
    rows = _parse_rows()

    if status:
        icon = _STATUS_ICONS.get(status, status)
        rows = [r for r in rows if r.get("status", "").strip() == icon]

    return rows


def update_status(company: str, new_status: str) -> bool:
    """
    Update the status of an application by company name.
    Returns True if found and updated, False otherwise.
    Requires full rewrite since we modify a line in the middle.
    """
    icon = _STATUS_ICONS.get(new_status, new_status)
    rows = _parse_rows()
    found = False

    company_lower = company.lower().strip()
    for row in rows:
        if row.get("company", "").lower().strip() == company_lower:
            row["status"] = icon
            found = True
            break

    if found:
        _write_all(rows)

    return found


def get_already_applied() -> set:
    """
    Get set of (company, position) tuples for deduplication with scraper.
    Company and position are normalized (lowercase, stripped of accents/special chars).
    """
    rows = _parse_rows()
    applied = set()

    for row in rows:
        company = _normalize(row.get("company", ""))
        position = _normalize(row.get("position", ""))
        if company and position:
            applied.add(f"{company}:{position}")

    return applied


def _normalize(text: str) -> str:
    """Normalize string for comparison: lowercase, no accents, alphanumeric only."""
    import unicodedata
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = re.sub(r"[\u0300-\u036f]", "", text)
    text = re.sub(r"[^a-z0-9]", "", text)
    return text
