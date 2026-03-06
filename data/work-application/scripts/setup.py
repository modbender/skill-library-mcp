#!/usr/bin/env python3
"""
setup.py - Interactive setup wizard for the work-application skill.
Run this after installing the skill to configure your master profile and behavior.

Usage: python3 scripts/setup.py
       python3 scripts/setup.py --cleanup
"""

import csv
import io
import json
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _profile import (
    load_config,
    save_config,
    MASTER_PROFILE_FILE,
    _DATA_DIR,
    _CONFIG_DIR,
    CONFIG_FILE,
    _DEFAULT_CONFIG,
)

SKILL_DIR = Path(__file__).resolve().parent.parent

# ── Date parsing helpers ─────────────────────────────────────────────────────

_MONTH_MAP = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "may": "05", "jun": "06", "jul": "07", "aug": "08",
    "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}


def _parse_linkedin_date(raw: str) -> str:
    """Convert LinkedIn date formats to YYYY-MM.

    Handles: 'Mon YYYY' (e.g. 'Jan 2020'), 'YYYY' alone, or empty string.
    """
    raw = raw.strip()
    if not raw:
        return ""
    parts = raw.split()
    if len(parts) == 2:
        month_key = parts[0][:3].lower()
        month = _MONTH_MAP.get(month_key, "01")
        return f"{parts[1]}-{month}"
    if len(parts) == 1 and parts[0].isdigit():
        return parts[0]
    return raw


# ── Interactive input helpers ────────────────────────────────────────────────

def _ask(prompt: str, default: str = "") -> str:
    display = f"[{default}] " if default else ""
    try:
        val = input(f"  {prompt} {display}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(0)
    return val if val else default


def _ask_bool(prompt: str, default: bool, hint: str = "") -> bool:
    default_str = "Y/n" if default else "y/N"
    hint_str = f"  ({hint})" if hint else ""
    try:
        val = input(f"  {prompt}{hint_str} [{default_str}]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(0)
    return val.startswith("y") if val else default


def _ask_multiline(prompt: str) -> list[str]:
    """Collect lines until an empty line is entered. Returns list of non-empty strings."""
    print(f"  {prompt}")
    lines = []
    while True:
        try:
            line = input("  > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            sys.exit(0)
        if not line:
            break
        lines.append(line)
    return lines


def _load_existing_config() -> dict:
    cfg = dict(_DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        try:
            cfg.update(json.loads(CONFIG_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass
    return cfg


# ── Empty profile template ───────────────────────────────────────────────────

def _empty_profile() -> dict:
    """Return a blank profile with the full expected structure."""
    return {
        "identity": {
            "firstName": "",
            "lastName": "",
            "title": "",
            "location": "",
            "linkedin": "",
            "github": "",
            "contact": {
                "cdi": {"email": "", "phone": ""},
                "freelance": {"email": "", "phone": ""},
            },
        },
        "summary": {
            "default": "",
            "variants": {"tech": "", "management": "", "consultant": ""},
        },
        "writing_style": "professionnel",
        "hard_skills": [],
        "soft_skills": [],
        "experiences": [],
        "education": [],
        "certifications": [],
        "languages": [],
        "projects": [],
    }


def _save_profile(profile: dict) -> None:
    """Write profile dict to the master profile file."""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    MASTER_PROFILE_FILE.write_text(
        json.dumps(profile, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


# ── LinkedIn ZIP import ──────────────────────────────────────────────────────

def _read_linkedin_csv(zf: zipfile.ZipFile, filename: str) -> list[dict]:
    """Read a CSV from the LinkedIn ZIP, handling BOM and skipping the note row.

    LinkedIn RGPD exports have a note line before the actual CSV header.
    Returns a list of dicts (one per data row), or [] if the file is absent.
    """
    # Find the file inside the ZIP (may be in a subdirectory)
    matching = [n for n in zf.namelist() if n.endswith(filename)]
    if not matching:
        return []
    raw = zf.read(matching[0])
    text = raw.decode("utf-8-sig")
    lines = text.splitlines()
    if len(lines) < 2:
        return []
    # Skip the first line (LinkedIn note) - the real header is on line index 1
    csv_text = "\n".join(lines[1:])
    reader = csv.DictReader(io.StringIO(csv_text))
    return list(reader)


def _import_linkedin(zip_path: Path) -> dict:
    """Parse a LinkedIn RGPD ZIP and return a populated profile dict."""
    profile = _empty_profile()

    with zipfile.ZipFile(str(zip_path), "r") as zf:
        # ── Profile.csv ──────────────────────────────────────────────
        for row in _read_linkedin_csv(zf, "Profile.csv"):
            profile["identity"]["firstName"] = row.get("First Name", "")
            profile["identity"]["lastName"] = row.get("Last Name", "")
            profile["identity"]["title"] = row.get("Headline", "")
            profile["identity"]["location"] = row.get("Geo Location", "")
            profile["summary"]["default"] = row.get("Summary", "")
            websites = row.get("Websites", "")
            if websites:
                for url in websites.split(","):
                    url = url.strip()
                    if "linkedin.com" in url:
                        profile["identity"]["linkedin"] = url
                    elif "github.com" in url:
                        profile["identity"]["github"] = url

        # ── Positions.csv ────────────────────────────────────────────
        for row in _read_linkedin_csv(zf, "Positions.csv"):
            end_raw = row.get("Finished On", "").strip()
            profile["experiences"].append({
                "title": row.get("Title", ""),
                "company": row.get("Company Name", ""),
                "location": row.get("Location", ""),
                "startDate": _parse_linkedin_date(row.get("Started On", "")),
                "endDate": "present" if not end_raw else _parse_linkedin_date(end_raw),
                "description": row.get("Description", ""),
                "achievements": [],
            })

        # ── Skills.csv ───────────────────────────────────────────────
        for row in _read_linkedin_csv(zf, "Skills.csv"):
            name = row.get("Name", "").strip()
            if name:
                profile["hard_skills"].append({
                    "name": name,
                    "level": 3,
                    "category": "",
                    "keywords": [name],
                })

        # ── Education.csv ────────────────────────────────────────────
        for row in _read_linkedin_csv(zf, "Education.csv"):
            profile["education"].append({
                "degree": row.get("Degree Name", ""),
                "field": row.get("Notes", ""),
                "institution": row.get("School Name", ""),
                "year": _parse_linkedin_date(row.get("End Date", "")),
            })

        # ── Certifications.csv ───────────────────────────────────────
        for row in _read_linkedin_csv(zf, "Certifications.csv"):
            profile["certifications"].append({
                "name": row.get("Name", ""),
                "authority": row.get("Authority", ""),
                "year": _parse_linkedin_date(row.get("Started On", "")),
            })

        # ── Languages.csv ────────────────────────────────────────────
        for row in _read_linkedin_csv(zf, "Languages.csv"):
            profile["languages"].append({
                "name": row.get("Name", ""),
                "level": row.get("Proficiency", ""),
            })

    return profile


def _linkedin_import_flow() -> None:
    """Choice 2: import from a LinkedIn RGPD ZIP export."""
    print()
    src = _ask("Path to LinkedIn ZIP (Basic_LinkedInDataExport_*.zip)")
    if not src:
        print("  No path provided. Skipping.")
        return
    zip_path = Path(src).expanduser().resolve()
    if not zip_path.exists():
        print(f"  ✗ File not found: {zip_path}")
        return
    if not zipfile.is_zipfile(str(zip_path)):
        print(f"  ✗ Not a valid ZIP file: {zip_path}")
        return

    print("  Parsing LinkedIn export...", end=" ", flush=True)
    try:
        profile = _import_linkedin(zip_path)
    except Exception as e:
        print(f"\n  ✗ Error parsing ZIP: {e}")
        return

    n_exp = len(profile["experiences"])
    n_skills = len(profile["hard_skills"])
    n_edu = len(profile["education"])
    n_cert = len(profile["certifications"])
    n_lang = len(profile["languages"])
    print("done.")
    print(
        f"\n  Import: {n_exp} experiences, {n_skills} skills, "
        f"{n_edu} formations, {n_cert} certifications, {n_lang} langues"
    )

    # ── Post-import enrichment ───────────────────────────────────────────
    if _ask_bool("\n  Enrichir le profil importe ?", default=True):
        _enrich_profile(profile)

    _save_profile(profile)
    print(f"\n  ✓ Profile created at {MASTER_PROFILE_FILE}")


def _enrich_profile(profile: dict) -> None:
    """Post-import enrichment: contacts, skill levels, achievements."""

    # ── Contacts ─────────────────────────────────────────────────────────
    print("\n  ● Contacts CDI/Freelance (LinkedIn n'exporte pas cette info)\n")
    profile["identity"]["contact"]["cdi"]["email"] = _ask("Email CDI")
    profile["identity"]["contact"]["cdi"]["phone"] = _ask("Tel CDI")
    if _ask_bool("Ajouter un contact freelance ?", default=False):
        profile["identity"]["contact"]["freelance"]["email"] = _ask("Email Freelance")
        profile["identity"]["contact"]["freelance"]["phone"] = _ask("Tel Freelance")

    # ── Hard skills levels & categories ──────────────────────────────────
    if profile["hard_skills"] and _ask_bool(
        "\n  Ajuster niveaux et categories des hard skills ?", default=True
    ):
        print()
        for i, skill in enumerate(profile["hard_skills"], 1):
            level = _ask(
                f"[{i}] {skill['name']} - niveau (1-5)",
                default=str(skill["level"]),
            )
            try:
                skill["level"] = int(level)
            except ValueError:
                pass
            cat = _ask(f"    categorie", default=skill["category"])
            skill["category"] = cat
            kw = _ask(
                f"    keywords (virgule)",
                default=", ".join(skill["keywords"]),
            )
            skill["keywords"] = [k.strip() for k in kw.split(",") if k.strip()]

    # ── Achievements ─────────────────────────────────────────────────────
    if profile["experiences"] and _ask_bool(
        "\n  Ajouter des achievements aux experiences ?", default=False
    ):
        print()
        for exp in profile["experiences"]:
            label = f"{exp['title']} @ {exp['company']}"
            print(f"  ● {label}")
            achievements = _ask_multiline("    Achievements (un par ligne, ligne vide pour finir):")
            exp["achievements"] = achievements

    # ── Summary variants ─────────────────────────────────────────────────
    if _ask_bool("\n  Ajouter des variantes de resume ?", default=False):
        for variant in ("tech", "management", "consultant"):
            val = _ask(f"Resume {variant} (vide = skip)")
            if val:
                profile["summary"]["variants"][variant] = val

    # ── Soft skills ──────────────────────────────────────────────────────
    if _ask_bool("\n  Ajouter des soft skills ?", default=False):
        _collect_soft_skills(profile)

    # ── Projects ─────────────────────────────────────────────────────────
    if _ask_bool("\n  Ajouter des projets ?", default=False):
        _collect_projects(profile)


# ── Interactive wizard (choice 3) ────────────────────────────────────────────

def _interactive_wizard() -> None:
    """Choice 3: create a complete profile interactively, section by section."""
    profile = _empty_profile()
    print()

    # ── Section 1: Identity ──────────────────────────────────────────────
    print("  ── Section 1/9 - Identite ──\n")
    profile["identity"]["firstName"] = _ask("Prenom")
    profile["identity"]["lastName"] = _ask("Nom")
    profile["identity"]["title"] = _ask("Titre professionnel")
    profile["identity"]["location"] = _ask("Localisation")
    profile["identity"]["linkedin"] = _ask("LinkedIn URL (optionnel)")
    profile["identity"]["github"] = _ask("GitHub URL (optionnel)")
    print("\n  Contact CDI:")
    profile["identity"]["contact"]["cdi"]["email"] = _ask("Email CDI")
    profile["identity"]["contact"]["cdi"]["phone"] = _ask("Tel CDI")
    if _ask_bool("Ajouter un contact freelance ?", default=False):
        profile["identity"]["contact"]["freelance"]["email"] = _ask("Email Freelance")
        profile["identity"]["contact"]["freelance"]["phone"] = _ask("Tel Freelance")

    # ── Section 2: Summary ───────────────────────────────────────────────
    print("\n  ── Section 2/9 - Resume ──\n")
    profile["summary"]["default"] = _ask("Resume par defaut")
    for variant in ("tech", "management", "consultant"):
        val = _ask(f"Variante {variant} (vide = skip)")
        if val:
            profile["summary"]["variants"][variant] = val

    # ── Section 3: Hard Skills ───────────────────────────────────────────
    print("\n  ── Section 3/9 - Hard Skills ──\n")
    _collect_hard_skills(profile)

    # ── Section 4: Soft Skills ───────────────────────────────────────────
    print("\n  ── Section 4/9 - Soft Skills ──\n")
    _collect_soft_skills(profile)

    # ── Section 5: Experiences ───────────────────────────────────────────
    print("\n  ── Section 5/9 - Experiences ──\n")
    _collect_experiences(profile)

    # ── Section 6: Education ─────────────────────────────────────────────
    print("\n  ── Section 6/9 - Formation ──\n")
    _collect_education(profile)

    # ── Section 7: Certifications ────────────────────────────────────────
    print("\n  ── Section 7/9 - Certifications ──\n")
    _collect_certifications(profile)

    # ── Section 8: Languages ─────────────────────────────────────────────
    print("\n  ── Section 8/9 - Langues ──\n")
    _collect_languages(profile)

    # ── Section 9: Projects ──────────────────────────────────────────────
    print("\n  ── Section 9/9 - Projets (optionnel) ──\n")
    _collect_projects(profile)

    _save_profile(profile)
    print(f"\n  ✓ Profil complet cree : {MASTER_PROFILE_FILE}")


# ── Collection helpers (used by both wizard and enrichment) ──────────────────

def _collect_hard_skills(profile: dict) -> None:
    while _ask_bool("Ajouter une competence ?", default=True):
        name = _ask("Nom")
        if not name:
            continue
        category = _ask("Categorie (Virtualisation/Systemes/DevOps/...)")
        level = _ask("Niveau (1-5)", default="3")
        try:
            level_int = int(level)
        except ValueError:
            level_int = 3
        kw = _ask("Keywords (virgule)", default=name)
        profile["hard_skills"].append({
            "name": name,
            "level": level_int,
            "category": category,
            "keywords": [k.strip() for k in kw.split(",") if k.strip()],
        })


def _collect_soft_skills(profile: dict) -> None:
    while _ask_bool("Ajouter un soft skill ?", default=True):
        name = _ask("Nom")
        if not name:
            continue
        kw = _ask("Keywords (virgule, optionnel)", default=name)
        profile["soft_skills"].append({
            "name": name,
            "keywords": [k.strip() for k in kw.split(",") if k.strip()],
        })


def _collect_experiences(profile: dict) -> None:
    while _ask_bool("Ajouter une experience ?", default=True):
        title = _ask("Titre du poste")
        if not title:
            continue
        company = _ask("Entreprise")
        location = _ask("Lieu")
        start = _ask("Date debut (YYYY-MM)")
        end = _ask("Date fin (YYYY-MM ou 'present')")
        description = _ask("Description courte")
        achievements = _ask_multiline("Achievements (un par ligne, ligne vide pour finir):")
        profile["experiences"].append({
            "title": title,
            "company": company,
            "location": location,
            "startDate": start,
            "endDate": end,
            "description": description,
            "achievements": achievements,
        })


def _collect_education(profile: dict) -> None:
    while _ask_bool("Ajouter une formation ?", default=True):
        degree = _ask("Diplome")
        if not degree:
            continue
        field = _ask("Domaine")
        institution = _ask("Etablissement")
        year = _ask("Annee")
        profile["education"].append({
            "degree": degree,
            "field": field,
            "institution": institution,
            "year": year,
        })


def _collect_certifications(profile: dict) -> None:
    while _ask_bool("Ajouter une certification ?", default=True):
        name = _ask("Nom")
        if not name:
            continue
        authority = _ask("Organisme")
        year = _ask("Annee")
        profile["certifications"].append({
            "name": name,
            "authority": authority,
            "year": year,
        })


def _collect_languages(profile: dict) -> None:
    while _ask_bool("Ajouter une langue ?", default=True):
        name = _ask("Langue")
        if not name:
            continue
        level = _ask("Niveau (natif/courant/intermediaire/notions)")
        profile["languages"].append({
            "name": name,
            "level": level,
        })


def _collect_projects(profile: dict) -> None:
    while _ask_bool("Ajouter un projet ?", default=False):
        name = _ask("Nom du projet")
        if not name:
            continue
        description = _ask("Description")
        url = _ask("URL (optionnel)")
        project = {"name": name, "description": description}
        if url:
            project["url"] = url
        profile["projects"].append(project)


# ── Scraper platform configuration ───────────────────────────────────────────

_PLATFORMS = ("lehibou", "free-work", "wttj", "apec", "hellowork")


def _configure_scraper_platforms(cfg: dict) -> None:
    """Toggle scraper platforms on/off interactively."""
    scraper = cfg.setdefault("scraper", {})
    enabled = scraper.get("platforms", [])

    print("  Activer les plateformes de scraping :\n")
    new_enabled = []
    for platform in _PLATFORMS:
        default_on = platform in enabled
        if _ask_bool(f"{platform}", default=default_on):
            new_enabled.append(platform)

    scraper["platforms"] = new_enabled

    if new_enabled:
        print(f"\n  ✓ Plateformes actives : {', '.join(new_enabled)}")
    else:
        print("\n  ✗ Aucune plateforme activee.")


def _configure_searches(cfg: dict) -> None:
    """Add/remove searches interactively."""
    scraper = cfg.setdefault("scraper", {})
    searches = scraper.setdefault("searches", [])

    # Show existing searches
    if searches:
        print(f"\n  Recherches actuelles ({len(searches)}) :\n")
        for i, s in enumerate(searches, 1):
            params = s.get("params", {})
            query = params.get("query", "?")
            loc = params.get("location", params.get("radius", ""))
            loc_str = f" | {loc}" if loc else ""
            print(f"    {i}. [{s.get('platform','?')}] {s.get('name', query)} - {query}{loc_str}")
    else:
        print("\n  Aucune recherche configuree.")

    # Remove searches
    if searches and _ask_bool("\n  Supprimer des recherches ?", default=False):
        indices = _ask("  Numeros a supprimer (virgule, ex: 1,3)").strip()
        to_remove = set()
        for part in indices.split(","):
            part = part.strip()
            if part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(searches):
                    to_remove.add(idx)
        searches[:] = [s for i, s in enumerate(searches) if i not in to_remove]
        print(f"  ✓ {len(to_remove)} recherche(s) supprimee(s). Total : {len(searches)}")

    # Add new searches
    print()
    while _ask_bool("  Ajouter une recherche ?", default=len(searches) == 0):
        print()
        # Platform selection
        print("  Plateformes disponibles :")
        for i, p in enumerate(_PLATFORMS, 1):
            print(f"    {i}. {p}")
        choice = _ask("  Plateforme (num ou nom)", default="3")
        if choice.isdigit() and 1 <= int(choice) <= len(_PLATFORMS):
            platform = _PLATFORMS[int(choice) - 1]
        elif choice in _PLATFORMS:
            platform = choice
        else:
            print("  Plateforme invalide, skip.")
            continue

        query = _ask("  Requete (ex: devops, ingenieur systemes)")
        if not query:
            print("  Requete vide, skip.")
            continue

        name = _ask("  Nom de la recherche", default=f"{query.title()} {platform.title()}")

        params: dict = {"query": query}

        if platform in ("wttj", "apec", "hellowork", "lehibou"):
            location = _ask("  Localisation (ex: Paris, France / IDF)", default="Paris, France")
            if location:
                params["location"] = location

        if platform in ("wttj", "lehibou"):
            radius = _ask("  Rayon (km)", default="30")
            if radius.isdigit():
                params["radius"] = int(radius) if platform == "wttj" else radius

        if platform == "free-work":
            contracts = _ask(
                "  Type de contrat (contractor/cdi/all)", default="contractor"
            ).lower()
            if contracts in ("contractor", "cdi", "all"):
                params["contracts"] = contracts

        searches.append({"name": name, "platform": platform, "params": params})
        print(f"  ✓ Recherche ajoutee : [{platform}] {name}")
        print()

    scraper["searches"] = searches
    print(f"\n  ✓ {len(searches)} recherche(s) configuree(s).")


def _configure_filters(cfg: dict) -> None:
    """Configure scraper filters interactively."""
    scraper = cfg.setdefault("scraper", {})
    filters = scraper.setdefault("filters", {})

    print("\n  Filtres de recherche :\n")

    # Salary / TJM thresholds
    min_tjm = _ask("  TJM minimum (EUR/j, 0 = pas de filtre)", default=str(filters.get("minTJM", 0)))
    filters["minTJM"] = int(min_tjm) if min_tjm.isdigit() else 0

    min_sal = _ask("  Salaire CDI minimum (EUR/an, 0 = pas de filtre)", default=str(filters.get("minSalary", 0)))
    filters["minSalary"] = int(min_sal) if min_sal.isdigit() else 0

    max_age = _ask("  Age max des offres (jours)", default=str(filters.get("maxAge", 7)))
    filters["maxAge"] = int(max_age) if max_age.isdigit() else 7

    # Location allowlist
    current_locs = filters.get("locations", [])
    print(f"\n  Zones autorisees (liste blanche, vide = toutes) : {', '.join(current_locs) or 'aucune (toutes)'}")
    if _ask_bool("  Modifier la liste blanche ?", default=False):
        raw = _ask("  Zones autorisees (virgule, ex: Paris,91,Essonne,Massy)", default=", ".join(current_locs))
        filters["locations"] = [z.strip() for z in raw.split(",") if z.strip()]

    # Location blocklist
    current_excl = filters.get("excludeLocations", [])
    print(f"\n  Zones exclues : {', '.join(current_excl) or 'aucune'}")
    if _ask_bool("  Modifier la liste d'exclusion ?", default=False):
        raw = _ask("  Zones exclues (virgule)", default=", ".join(current_excl))
        filters["excludeLocations"] = [z.strip() for z in raw.split(",") if z.strip()]

    # Company blocklist
    current_comp = filters.get("excludeCompanies", [])
    print(f"\n  Entreprises exclues : {', '.join(current_comp) or 'aucune'}")
    if _ask_bool("  Modifier les entreprises exclues ?", default=False):
        raw = _ask("  Entreprises exclues (virgule)", default=", ".join(current_comp))
        filters["excludeCompanies"] = [c.strip() for c in raw.split(",") if c.strip()]

    scraper["filters"] = filters
    print("\n  ✓ Filtres mis a jour.")


# ── Main setup flow ──────────────────────────────────────────────────────────

def main():
    print("┌─────────────────────────────────────────┐")
    print("│   Work-Application Skill - Setup         │")
    print("└─────────────────────────────────────────┘")

    # ── Step 1/5: Master Profile ──────────────────────────────────────────────
    print("\n● Step 1/5 - Master Profile\n")

    if MASTER_PROFILE_FILE.exists():
        print(f"  Existing master profile found: {MASTER_PROFILE_FILE}")
        if not _ask_bool("Update master profile?", default=False):
            print("  → Keeping existing master profile.")
        else:
            _setup_master_profile()
    else:
        _setup_master_profile()

    # ── Step 2/5: Permissions ─────────────────────────────────────────────────
    print("\n● Step 2/5 - Permissions\n")
    print("  Configure what operations the agent is allowed to perform.\n")

    cfg = _load_existing_config()

    cfg["allow_write"] = _ask_bool(
        "Allow modifying the master profile?",
        default=cfg.get("allow_write", False),
        hint="false = read-only profile",
    )
    cfg["allow_export"] = _ask_bool(
        "Allow generating HTML/PDF exports?",
        default=cfg.get("allow_export", False),
    )
    cfg["allow_scrape"] = _ask_bool(
        "Allow running the job scraper?",
        default=cfg.get("allow_scrape", False),
        hint="requires Playwright installed",
    )
    cfg["allow_tracking"] = _ask_bool(
        "Allow logging candidatures?",
        default=cfg.get("allow_tracking", False),
    )
    cfg["readonly_mode"] = _ask_bool(
        "Enable readonly mode? (overrides all above)",
        default=cfg.get("readonly_mode", False),
    )

    # ── Step 3/5: Defaults ────────────────────────────────────────────────────
    print("\n● Step 3/5 - Defaults\n")

    template_choices = ("classic", "modern-sidebar", "two-column", "creative")
    template_input = _ask(
        f"Default template ({', '.join(template_choices)})",
        default=cfg.get("default_template", "classic"),
    ).lower()
    cfg["default_template"] = template_input if template_input in template_choices else "classic"

    cfg["default_color"] = _ask(
        "Default accent color (hex)",
        default=cfg.get("default_color", "#2563eb"),
    )

    lang_choices = ("fr", "en")
    lang_input = _ask(
        f"Default language ({', '.join(lang_choices)})",
        default=cfg.get("default_lang", "fr"),
    ).lower()
    cfg["default_lang"] = lang_input if lang_input in lang_choices else "fr"

    # Report mode
    current_report = cfg.get("report_mode", "analysis")
    print("\n  Mode rapport (analyse d'offre individuelle) :\n")
    print("    1. Analyse seule")
    print("    2. CV adapte + analyse (genere un CV adapte pour chaque offre analysee)")
    default_report = "1" if current_report == "analysis" else "2"
    report_choice = _ask("Choix", default=default_report)
    cfg["report_mode"] = "cv+analysis" if report_choice == "2" else "analysis"

    # ── Step 4/5: Storage ────────────────────────────────────────────────────
    print("\n● Step 4/5 - Stockage\n")

    storage_cfg = cfg.get("storage", {})
    current_backend = storage_cfg.get("backend", "local")

    # Check if nextcloud skill is available
    nc_skill_path = SKILL_DIR.parent / "nextcloud-files" / "scripts" / "nextcloud.py"
    nc_available = nc_skill_path.exists()

    if nc_available:
        print("    1. Local (~/.openclaw/data/)")
        print("    2. Nextcloud (skill nextcloud detecte)")
        storage_choice = _ask("Stockage", default="1" if current_backend == "local" else "2")

        if storage_choice == "2":
            default_path = storage_cfg.get("path", "/OpenClaw/work-application")
            remote_path = _ask("Chemin distant Nextcloud", default=default_path)
            cfg["storage"] = {"backend": "nextcloud", "path": remote_path}
            print(f"  ✓ Stockage Nextcloud : {remote_path}")
        else:
            cfg["storage"] = {"backend": "local", "path": storage_cfg.get("path", "/OpenClaw/work-application")}
            print("  ✓ Stockage local")
    else:
        cfg["storage"] = {"backend": "local", "path": storage_cfg.get("path", "/OpenClaw/work-application")}
        print("  Stockage : local (skill nextcloud non detecte)")

    # ── Step 5/5: Scraper Config ──────────────────────────────────────────────
    if cfg["allow_scrape"]:
        print("\n● Step 5/5 - Scraper Config\n")

        # Check Playwright availability
        print("  Checking Playwright installation...", end=" ", flush=True)
        try:
            import playwright  # noqa: F401
            print("✓ Playwright is installed.")
        except ImportError:
            print("✗ Playwright is NOT installed.")
            print("\n  To install Playwright, run:")
            print("    pip install playwright playwright-stealth && playwright install chromium")
            print()

        # Configure searches
        print("\n  ── Requetes de recherche ──\n")
        _configure_searches(cfg)

        # Configure filters
        print("\n  ── Filtres ──")
        _configure_filters(cfg)

        # Configure platforms
        print("\n  ── Plateformes ──")
        _configure_scraper_platforms(cfg)
    else:
        print("\n  (Scraper step skipped - allow_scrape is false)")

    # ── Save ──────────────────────────────────────────────────────────────────
    save_config(cfg)
    print(f"\n  ✓ Config saved to {CONFIG_FILE}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n┌─────────────────────────────────────────┐")
    print("│   Setup complete ✓                      │")
    print("└─────────────────────────────────────────┘")

    profile_exists = MASTER_PROFILE_FILE.exists()
    print(f"\n  Profile          : {MASTER_PROFILE_FILE} {'(exists)' if profile_exists else '(missing!)'}")

    ro = cfg["readonly_mode"]
    print(f"  Allow write      : {'✓' if cfg['allow_write']    and not ro else '✗'}")
    print(f"  Allow export     : {'✓' if cfg['allow_export']   and not ro else '✗'}")
    print(f"  Allow scrape     : {'✓' if cfg['allow_scrape']   and not ro else '✗'}")
    print(f"  Allow tracking   : {'✓' if cfg['allow_tracking'] and not ro else '✗'}")
    print(f"  Default template : {cfg['default_template']}")
    print(f"  Default color    : {cfg['default_color']}")
    print(f"  Default lang     : {cfg['default_lang']}")
    st = cfg.get("storage", {})
    if st.get("backend") == "nextcloud":
        print(f"  Storage          : Nextcloud ({st.get('path', '?')})")
    else:
        print(f"  Storage          : local")
    print(f"  Readonly         : {'⚠ ON - all writes blocked' if ro else '✗ off'}")
    print()
    print("  Run init.py to validate that everything works:")
    print("    python3 scripts/init.py")
    print()


def _setup_master_profile():
    """Set up the master profile by copying, importing from LinkedIn, or creating interactively."""
    print("  How would you like to set up your master profile?\n")
    print("    1. Copy an existing profile-master.json file")
    print("    2. Import from a LinkedIn RGPD export (ZIP)")
    print("    3. Create a complete profile interactively")
    choice = _ask("Choice", default="1")

    if choice == "1":
        src = _ask("Path to existing profile-master.json")
        if not src:
            print("  No path provided. Skipping.")
            return
        src_path = Path(src).expanduser().resolve()
        if not src_path.exists():
            print(f"  ✗ File not found: {src_path}")
            return
        # Validate JSON
        try:
            content = src_path.read_text(encoding="utf-8")
            json.loads(content)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  ✗ Invalid JSON: {e}")
            return
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src_path), str(MASTER_PROFILE_FILE))
        print(f"  ✓ Copied to {MASTER_PROFILE_FILE}")

    elif choice == "2":
        _linkedin_import_flow()

    elif choice == "3":
        _interactive_wizard()

    else:
        print("  Invalid choice. Skipping master profile setup.")


def cleanup():
    """Remove all persistent files written by this skill (profile + config)."""
    print("Removing work-application skill persistent files...")
    removed = []
    for path in [CONFIG_FILE, MASTER_PROFILE_FILE]:
        if path.exists():
            path.unlink()
            removed.append(str(path))
    for d in [_CONFIG_DIR, _DATA_DIR]:
        try:
            d.rmdir()  # removes dir only if empty
        except OSError:
            pass
    if removed:
        for p in removed:
            print(f"  Removed: {p}")
        print("Done. Re-run setup.py to reconfigure.")
    else:
        print("  Nothing to remove.")


if __name__ == "__main__":
    if "--cleanup" in sys.argv:
        cleanup()
    else:
        main()
