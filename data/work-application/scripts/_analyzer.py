"""
_analyzer.py - Job analysis, scoring, and ranking for the work-application skill.
Port of analyze-jobs.js, filter-jobs.js, and deep-analyze.js. Stdlib only.
Deep analysis requires playwright (optional).

Usage:
    from _analyzer import score_job, rank_jobs, select_top, format_markdown
"""

import re
import unicodedata
from datetime import datetime

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

JOB_KEYWORDS = [
    {"pattern": r"vmware|vsphere|vxrail|esxi", "skill": "VMware", "weight": 5},
    {"pattern": r"proxmox", "skill": "Proxmox", "weight": 5},
    {"pattern": r"windows|ws2019|ws2022", "skill": "Windows Server", "weight": 5},
    {"pattern": r"linux|rhel|centos|debian|ubuntu", "skill": "Linux", "weight": 4},
    {"pattern": r"active.?directory|ad|ldap", "skill": "Active Directory", "weight": 5},
    {"pattern": r"devops|cicd|ci.?cd", "skill": "DevOps", "weight": 4},
    {"pattern": r"docker|container", "skill": "Docker", "weight": 4},
    {"pattern": r"kubernetes|k8s", "skill": "Kubernetes", "weight": 2},
    {"pattern": r"ansible|automation", "skill": "Ansible", "weight": 3},
    {"pattern": r"terraform|iac", "skill": "Terraform", "weight": 2},
    {"pattern": r"gitlab", "skill": "GitLab", "weight": 4},
    {"pattern": r"aws|amazon", "skill": "AWS", "weight": 2},
    {"pattern": r"azure|microsoft.?cloud", "skill": "Azure", "weight": 2},
    {"pattern": r"gcp|google.?cloud", "skill": "GCP", "weight": 1},
    {"pattern": r"sre|site.?reliability", "skill": "SRE", "weight": 4},
    {"pattern": r"sysops|system.?ops", "skill": "SysOps", "weight": 5},
    {"pattern": r"sysadmin|system.?admin", "skill": "SysAdmin", "weight": 5},
    {"pattern": r"ingénieur.?système|system.?engineer", "skill": "Ingenieur Systemes", "weight": 5},
    {"pattern": r"monitoring|supervision|nagios|zabbix|checkmk", "skill": "Supervision", "weight": 4},
    {"pattern": r"backup|veeam|sauvegarde", "skill": "Backup", "weight": 3},
    {"pattern": r"netapp|san|nas|stockage", "skill": "Stockage", "weight": 3},
    {"pattern": r"powershell|bash|script", "skill": "Scripting", "weight": 4},
    {"pattern": r"python", "skill": "Python", "weight": 3},
    {"pattern": r"mysql|postgresql|mariadb|bdd", "skill": "Bases de donnees", "weight": 4},
    {"pattern": r"nginx|apache|iis|web.?server", "skill": "Web Server", "weight": 4},
    {"pattern": r"firewall|security|sécurité|siem", "skill": "Securite", "weight": 4},
    {"pattern": r"vault|hashicorp", "skill": "HashiCorp", "weight": 3},
    {"pattern": r"production|mco|n2|n3", "skill": "Production", "weight": 5},
    {"pattern": r"infrastructure|infra", "skill": "Infrastructure", "weight": 5},
]

DISTANCES = {
    "dourdan": 0, "limours": 10, "rambouillet": 15, "ablis": 20,
    "chartres": 40, "palaiseau": 20, "saclay": 20, "orsay": 22,
    "massy": 25, "les ulis": 20, "evry": 30, "évry": 30,
    "versailles": 30, "velizy": 32, "vélizy": 32, "elancourt": 35,
    "guyancourt": 35, "saint-quentin-en-yvelines": 35,
    "buc": 30, "jouy-en-josas": 28, "gif-sur-yvette": 22,
    "les clayes": 40, "plaisir": 40, "paris": 50,
    "boulogne": 55, "issy": 52, "montrouge": 50, "malakoff": 50,
    "arcueil": 48, "gentilly": 48, "ivry": 50, "villejuif": 45,
    "rungis": 40, "orly": 38, "charenton": 55, "vincennes": 58,
    "fontenay": 60, "le plessis": 52, "sceaux": 42, "antony": 40,
    "chatenay": 42, "clamart": 48, "meudon": 50, "chatillon": 50,
    "vanves": 52, "télétravail": 0, "remote": 0, "full remote": 0,
}

POTENTIAL_GAPS = [
    {"pattern": r"kubernetes|k8s", "name": "Kubernetes", "have": 2},
    {"pattern": r"terraform", "name": "Terraform", "have": 2},
    {"pattern": r"aws|amazon web services", "name": "AWS", "have": 2},
    {"pattern": r"azure", "name": "Azure", "have": 2},
    {"pattern": r"gcp|google cloud", "name": "GCP", "have": 1},
    {"pattern": r"puppet|chef", "name": "Puppet/Chef", "have": 0},
    {"pattern": r"prometheus|grafana", "name": "Prometheus/Grafana", "have": 1},
    {"pattern": r"jenkins", "name": "Jenkins", "have": 1},
    {"pattern": r"nutanix", "name": "Nutanix", "have": 0},
    {"pattern": r"openstack", "name": "OpenStack", "have": 1},
]

# Key categories from the master profile hard_skills to match against
_KEY_CATEGORIES = [
    "Virtualisation", "Systemes", "DevOps", "Conteneurs",
    "Cloud", "Supervision", "Reseau", "Securite",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Normalize string for comparison: lowercase, no accents, alphanumeric only."""
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = re.sub(r"[\u0300-\u036f]", "", text)
    text = re.sub(r"[^a-z0-9]", "", text)
    return text


def parse_jobs_markdown(content: str) -> list[dict]:
    """
    Parse a jobs-found.md or similar markdown table file into job dicts.
    Port of parseJobs/parseMarkdown from the JS files.

    Expects a markdown table with columns like:
    | Titre | Entreprise | Lieu | Salaire | Type | URL |
    """
    jobs = []

    lines = content.splitlines()
    header_cols = []
    header_found = False

    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            continue

        cells = [c.strip() for c in line.split("|")]
        # Remove empty first/last from pipe split
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]

        if not cells:
            continue

        # Detect separator row (---|---|...)
        if all(re.match(r"^-+$", c.strip()) for c in cells if c.strip()):
            header_found = True
            continue

        # Detect header row
        if not header_found:
            header_cols = [c.strip().lower() for c in cells]
            continue

        # Data row
        if not header_cols:
            continue

        # Pad cells to match header length
        while len(cells) < len(header_cols):
            cells.append("")

        row = {}
        for i, col_name in enumerate(header_cols):
            row[col_name] = cells[i] if i < len(cells) else ""

        # Normalize to standard field names
        job = {}
        job["title"] = (
            row.get("titre", "")
            or row.get("title", "")
            or row.get("poste", "")
        )
        job["company"] = (
            row.get("entreprise", "")
            or row.get("company", "")
            or row.get("societe", "")
            or row.get("société", "")
        )
        job["location"] = (
            row.get("lieu", "")
            or row.get("location", "")
            or row.get("localisation", "")
        )
        job["salary"] = (
            row.get("salaire", "")
            or row.get("salary", "")
            or row.get("tjm", "")
            or row.get("remuneration", "")
            or row.get("rémunération", "")
        )
        job["type"] = (
            row.get("type", "")
            or row.get("contrat", "")
        )

        # Extract URL from markdown link [text](url) or plain url
        url_raw = (
            row.get("url", "")
            or row.get("lien", "")
            or row.get("link", "")
            or row.get("offre", "")
        )
        link_match = re.search(r"\[.*?\]\((.*?)\)", url_raw)
        if link_match:
            job["url"] = link_match.group(1)
        else:
            job["url"] = url_raw.strip()

        # Keep raw row data for anything extra
        job["_raw"] = row

        # Skip empty rows
        if not job["title"] and not job["company"]:
            continue

        jobs.append(job)

    return jobs


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def score_job(job: dict, master_profile: dict) -> dict:
    """
    Calculate match score for a job against the master profile.
    Port of calculateMatchScore from analyze-jobs.js.

    Returns:
        {
            "percentage": int,       # 0-100 match percentage
            "matched_skills": list,  # [{"name": str, "level": int}, ...]
            "score": int,            # raw score
        }
    """
    # Build search text from job fields
    search_text = " ".join([
        job.get("title", ""),
        job.get("company", ""),
        job.get("url", ""),
    ]).lower()

    matched_skills = []
    score = 0

    # Match against master_profile hard_skills keywords
    hard_skills = master_profile.get("hard_skills", [])
    for skill_cat in hard_skills:
        cat_name = skill_cat.get("category", "")
        # Only check key categories
        cat_normalized = _normalize(cat_name)
        is_key = any(_normalize(k) == cat_normalized for k in _KEY_CATEGORIES)
        if not is_key:
            continue

        keywords = skill_cat.get("keywords", [])
        if isinstance(keywords, list):
            for kw in keywords:
                if isinstance(kw, dict):
                    kw_name = kw.get("name", "")
                    kw_level = kw.get("level", 1)
                elif isinstance(kw, str):
                    kw_name = kw
                    kw_level = 1
                else:
                    continue

                if kw_name and re.search(
                    re.escape(kw_name), search_text, re.IGNORECASE
                ):
                    matched_skills.append({"name": kw_name, "level": kw_level})
                    score += kw_level

    # Match against JOB_KEYWORDS patterns for bonus scoring
    for entry in JOB_KEYWORDS:
        if re.search(entry["pattern"], search_text, re.IGNORECASE):
            # Avoid double-counting if already matched by profile keywords
            already = any(
                _normalize(m["name"]) == _normalize(entry["skill"])
                for m in matched_skills
            )
            if not already:
                matched_skills.append({
                    "name": entry["skill"],
                    "level": entry["weight"],
                })
            score += entry["weight"]

    # Calculate percentage (max possible = sum of all JOB_KEYWORDS weights)
    max_score = sum(e["weight"] for e in JOB_KEYWORDS)
    percentage = min(100, round(score / max_score * 100)) if max_score > 0 else 0

    return {
        "percentage": percentage,
        "matched_skills": matched_skills,
        "score": score,
    }


def estimate_distance(location: str, url: str = "") -> dict:
    """
    Estimate distance from Dourdan based on location string.
    Port of estimateDistance from analyze-jobs.js.

    Returns:
        {"km": int, "label": str}
    """
    combined = f"{location} {url}".lower()

    # Check for remote first
    if re.search(r"t[ée]l[ée]travail|remote|full.?remote", combined, re.IGNORECASE):
        return {"km": 0, "label": "Remote"}

    # Find the closest matching city
    best_km = 999
    best_label = "Inconnu"

    for city, km in DISTANCES.items():
        if city in ("télétravail", "remote", "full remote"):
            continue
        if re.search(re.escape(city), combined, re.IGNORECASE):
            if km < best_km:
                best_km = km
                best_label = city.title()

    if best_km == 999:
        return {"km": 999, "label": "Inconnu"}

    return {"km": best_km, "label": best_label}


def parse_salary(salary: str) -> dict:
    """
    Parse salary string into structured data.
    Port of parseSalary from analyze-jobs.js.

    Returns:
        {"value": int, "display": str, "type": str}
    Types: "tjm" (euros/jour), "salary" (k euros), "unknown".
    """
    if not salary:
        return {"value": 0, "display": "-", "type": "unknown"}

    text = salary.strip().lower()

    # TJM pattern: 500€/j, 500 €/jour, 500/j, etc.
    tjm_match = re.search(
        r"(\d{3,4})\s*[€e]?\s*/?\s*j(?:our)?", text, re.IGNORECASE
    )
    if tjm_match:
        value = int(tjm_match.group(1))
        return {"value": value, "display": f"{value} EUR/j", "type": "tjm"}

    # Salary range: 55-65k, 55k-65k, 55 - 65 k€, etc.
    range_match = re.search(
        r"(\d{2,3})\s*k?\s*[-–à]\s*(\d{2,3})\s*k?\s*[€e]?", text, re.IGNORECASE
    )
    if range_match:
        low = int(range_match.group(1))
        high = int(range_match.group(2))
        # Normalize: if values are > 200, they are raw amounts
        if low > 200:
            low = low // 1000
        if high > 200:
            high = high // 1000
        avg = (low + high) // 2
        return {"value": avg, "display": f"{low}-{high}k EUR", "type": "salary"}

    # Single salary: 55k€, 55 k€, 55000€, etc.
    single_match = re.search(r"(\d{2,3})\s*k\s*[€e]?", text, re.IGNORECASE)
    if single_match:
        value = int(single_match.group(1))
        return {"value": value, "display": f"{value}k EUR", "type": "salary"}

    # Raw number (could be annual salary in thousands)
    raw_match = re.search(r"(\d{4,6})", text)
    if raw_match:
        value = int(raw_match.group(1))
        if value >= 1000:
            value_k = value // 1000
            return {"value": value_k, "display": f"{value_k}k EUR", "type": "salary"}

    return {"value": 0, "display": "-", "type": "unknown"}


def detect_remote(title: str, location: str, salary: str = "") -> dict:
    """
    Detect remote work possibility from job fields.
    Port of detectRemote from analyze-jobs.js.

    Returns:
        {"value": int, "label": str}
    value is a boost score: 100 for full remote, 50 for partial, 0 for none.
    """
    combined = f"{title} {location} {salary}".lower()

    if re.search(r"full.?remote|100%.?remote|100%.?t[ée]l[ée]travail", combined, re.IGNORECASE):
        return {"value": 100, "label": "Full remote"}

    if re.search(
        r"t[ée]l[ée]travail|remote|hybride|hybrid|home.?office",
        combined, re.IGNORECASE,
    ):
        # Try to detect percentage/days
        days_match = re.search(r"(\d)\s*j(?:ours?)?\s*/?\s*(?:semaine|sem|s)", combined)
        if days_match:
            days = int(days_match.group(1))
            return {"value": days * 20, "label": f"{days}j/sem remote"}

        pct_match = re.search(r"(\d{1,3})\s*%", combined)
        if pct_match:
            pct = int(pct_match.group(1))
            return {"value": pct, "label": f"{pct}% remote"}

        return {"value": 50, "label": "Remote partiel"}

    return {"value": 0, "label": "Sur site"}


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------

def rank_jobs(jobs: list[dict], master_profile: dict) -> list[dict]:
    """
    Analyze and rank all jobs by composite score.
    Port of the main analysis loop from analyze-jobs.js.

    For each job, computes:
    - match: score_job result
    - distance: estimate_distance result
    - salary_parsed: parse_salary result
    - remote: detect_remote result
    - composite_score: weighted combination

    Returns jobs sorted by composite_score descending.
    """
    ranked = []

    for job in jobs:
        match = score_job(job, master_profile)
        distance = estimate_distance(
            job.get("location", ""), job.get("url", "")
        )
        salary_parsed = parse_salary(job.get("salary", ""))
        remote = detect_remote(
            job.get("title", ""),
            job.get("location", ""),
            job.get("salary", ""),
        )

        # Salary component: TJM normalized to comparable scale, salary in k
        if salary_parsed["type"] == "tjm":
            salary_component = min(100, salary_parsed["value"] // 5)
        elif salary_parsed["type"] == "salary":
            salary_component = min(100, salary_parsed["value"])
        else:
            salary_component = 0

        # Composite score
        distance_km = distance["km"] if distance["km"] < 999 else 100
        composite = (
            match["percentage"] * 2
            + salary_component
            + (100 - distance_km)
            + remote["value"]
        )

        enriched = dict(job)
        enriched["match"] = match
        enriched["distance"] = distance
        enriched["salary_parsed"] = salary_parsed
        enriched["remote"] = remote
        enriched["composite_score"] = composite

        ranked.append(enriched)

    # Sort by composite score descending
    ranked.sort(key=lambda j: j["composite_score"], reverse=True)

    return ranked


# ---------------------------------------------------------------------------
# Deep analysis (requires playwright)
# ---------------------------------------------------------------------------

def analyze_job_content(text: str, master_profile: dict) -> dict:
    """
    Analyze scraped job page content against the master profile.
    Port of analyzeJobContent from deep-analyze.js.

    Returns:
        {
            "matched_skills": list,   # [{"name": str, "level": int}, ...]
            "missing_skills": list,   # [{"name": str, "have": int}, ...]
            "salary": str|None,
            "remote": str,
            "experience": str|None,
            "match_percentage": int,
            "score": int,
        }
    """
    search_text = text.lower()
    matched_skills = []
    score = 0

    # Match against master profile hard_skills keywords
    hard_skills = master_profile.get("hard_skills", [])
    for skill_cat in hard_skills:
        cat_name = skill_cat.get("category", "")
        cat_normalized = _normalize(cat_name)
        is_key = any(_normalize(k) == cat_normalized for k in _KEY_CATEGORIES)
        if not is_key:
            continue

        keywords = skill_cat.get("keywords", [])
        if isinstance(keywords, list):
            for kw in keywords:
                if isinstance(kw, dict):
                    kw_name = kw.get("name", "")
                    kw_level = kw.get("level", 1)
                elif isinstance(kw, str):
                    kw_name = kw
                    kw_level = 1
                else:
                    continue

                if kw_name and re.search(
                    re.escape(kw_name), search_text, re.IGNORECASE
                ):
                    matched_skills.append({"name": kw_name, "level": kw_level})
                    score += kw_level

    # Match against JOB_KEYWORDS
    for entry in JOB_KEYWORDS:
        if re.search(entry["pattern"], search_text, re.IGNORECASE):
            already = any(
                _normalize(m["name"]) == _normalize(entry["skill"])
                for m in matched_skills
            )
            if not already:
                matched_skills.append({
                    "name": entry["skill"],
                    "level": entry["weight"],
                })
            score += entry["weight"]

    # Detect gaps
    missing_skills = []
    for gap in POTENTIAL_GAPS:
        if re.search(gap["pattern"], search_text, re.IGNORECASE):
            # Only flag as missing if we don't already match it strongly
            already_matched = any(
                _normalize(m["name"]) == _normalize(gap["name"])
                for m in matched_skills
            )
            if not already_matched or gap["have"] <= 1:
                missing_skills.append({
                    "name": gap["name"],
                    "have": gap["have"],
                })

    # Detect salary from content
    salary = None
    tjm_match = re.search(
        r"(\d{3,4})\s*[€e]?\s*/?\s*j(?:our)?", search_text, re.IGNORECASE
    )
    if tjm_match:
        salary = f"{tjm_match.group(1)} EUR/j"
    else:
        sal_match = re.search(
            r"(\d{2,3})\s*k?\s*[-–à]\s*(\d{2,3})\s*k?\s*[€e]?",
            search_text, re.IGNORECASE,
        )
        if sal_match:
            salary = f"{sal_match.group(1)}-{sal_match.group(2)}k EUR"

    # Detect remote
    remote = "Sur site"
    if re.search(r"full.?remote|100%.?remote", search_text, re.IGNORECASE):
        remote = "Full remote"
    elif re.search(
        r"t[ée]l[ée]travail|remote|hybride|hybrid",
        search_text, re.IGNORECASE,
    ):
        days_match = re.search(
            r"(\d)\s*j(?:ours?)?\s*/?\s*(?:semaine|sem|s)", search_text
        )
        if days_match:
            remote = f"{days_match.group(1)}j/sem remote"
        else:
            remote = "Remote partiel"

    # Detect experience requirement
    experience = None
    exp_match = re.search(
        r"(\d+)\s*(?:ans?|years?)\s*(?:d['\u2019]?\s*)?exp[ée]rience",
        search_text, re.IGNORECASE,
    )
    if exp_match:
        experience = f"{exp_match.group(1)} ans"
    else:
        exp_match2 = re.search(
            r"exp[ée]rience\s*(?:de\s*)?(\d+)\s*(?:ans?|years?)",
            search_text, re.IGNORECASE,
        )
        if exp_match2:
            experience = f"{exp_match2.group(1)} ans"

    # Calculate match percentage
    max_score = sum(e["weight"] for e in JOB_KEYWORDS)
    match_percentage = min(100, round(score / max_score * 100)) if max_score > 0 else 0

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "salary": salary,
        "remote": remote,
        "experience": experience,
        "match_percentage": match_percentage,
        "score": score,
    }


async def deep_analyze(
    jobs: list[dict],
    master_profile: dict,
    max_jobs: int = 30,
    on_progress=None,
) -> list[dict]:
    """
    Deep analyze jobs by scraping their actual pages.
    Port of deep-analyze.js main function.
    Requires playwright (optional dependency).

    For each job:
    1. Pre-score and sort by priority (title patterns + location boost)
    2. Take top *max_jobs*
    3. For each, scrape the actual job page content
    4. Run analyze_job_content on the scraped text
    5. Determine if freelance or CDI
    6. Return enriched jobs sorted by match percentage

    Parameters
    ----------
    jobs:
        List of job dicts (from parse_jobs_markdown or scraper).
    master_profile:
        The master profile dict.
    max_jobs:
        Maximum number of jobs to deep-analyze (default 30).
    on_progress:
        Optional callback ``(index, total, job, status_msg)`` for progress.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise ImportError(
            "Playwright is required for deep analysis.\n"
            "Install with: pip install playwright && playwright install chromium"
        )

    # Optional stealth plugin
    try:
        from playwright_stealth import stealth_async
    except ImportError:
        stealth_async = None

    # ------------------------------------------------------------------
    # Pre-score for prioritization (port of deep-analyze.js pre-filter)
    # ------------------------------------------------------------------
    priority_patterns = [
        (r"ingénieur.?syst[eè]me|system.?engineer", 10),
        (r"sysops|sysadmin|admin.*syst[eè]me", 10),
        (r"devops", 10),
        (r"sre|site.?reliability", 10),
        (r"vmware|virtualisation", 5),
        (r"infrastructure|infra", 7),
        (r"production|mco", 6),
        (r"tech.*lead", 5),
        (r"linux|windows.*server", 5),
    ]
    location_boost_patterns = [
        (r"limours|massy|palaiseau|[ée]vry|saclay|orsay|versailles|v[ée]lizy|elancourt", 15),
        (r"remote|t[ée]l[ée]travail|full.?remote", 10),
    ]

    scored_jobs = []
    for job in jobs:
        priority = 0
        title_lower = job.get("title", "").lower()
        loc_lower = (job.get("location", "") + " " + job.get("url", "")).lower()
        salary_text = job.get("salary", "").lower()

        for pat, boost in priority_patterns:
            if re.search(pat, title_lower, re.IGNORECASE):
                priority += boost

        for pat, boost in location_boost_patterns:
            if re.search(pat, loc_lower, re.IGNORECASE):
                priority += boost

        # Boost freelance with TJM
        if "€/j" in salary_text or "€⁄j" in salary_text:
            priority += 5

        scored_jobs.append((priority, job))

    # Sort by priority descending and take top N
    scored_jobs.sort(key=lambda x: x[0], reverse=True)
    top_jobs = [j for _, j in scored_jobs[:max_jobs]]

    # ------------------------------------------------------------------
    # Scrape and analyze each job
    # ------------------------------------------------------------------
    # CSS selectors to try for extracting the job description, ordered
    # from most specific to most generic (port of deep-analyze.js).
    _DESCRIPTION_SELECTORS = (
        "article",
        ".job-description",
        ".description",
        ".content",
        '[data-testid="job-section-description"]',
        ".job-detail",
        ".offer-content",
        ".mission-description",
        "main",
        '[role="main"]',
        "#job-description",
    )

    _JS_EXTRACT = """
        () => {
            const selectors = %s;
            let description = '';
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el && el.innerText && el.innerText.length > 200) {
                    description = el.innerText;
                    break;
                }
            }
            if (!description) {
                description = document.body.innerText || '';
            }
            return {
                fullText: (document.body.innerText || '').substring(0, 15000),
                description: description.substring(0, 10000)
            };
        }
    """ % str(list(_DESCRIPTION_SELECTORS))

    results = []
    lehibou_initialized = False

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
        )

        total = len(top_jobs)
        for idx, job in enumerate(top_jobs):
            url = job.get("url", "")
            if not url:
                continue

            title_short = job.get("title", "")[:40]
            platform = job.get("platform", job.get("_raw", {}).get("platform", ""))

            if on_progress:
                on_progress(idx + 1, total, job, f"{title_short}...")

            try:
                page = await context.new_page()

                # Apply stealth if available
                if stealth_async is not None:
                    await stealth_async(page)

                # Special handling for LeHibou (needs homepage visit first)
                if not lehibou_initialized and (
                    "lehibou" in platform.lower() or "lehibou.com" in url
                ):
                    await page.goto(
                        "https://www.lehibou.com",
                        wait_until="networkidle",
                        timeout=30000,
                    )
                    await page.wait_for_timeout(2000)
                    try:
                        btn = page.locator('[data-cky-tag="accept-button"]').first
                        if await btn.is_visible(timeout=2000):
                            await btn.click()
                    except Exception:
                        pass
                    await page.wait_for_timeout(1000)
                    lehibou_initialized = True

                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)

                # Extract content using platform-aware selectors
                content = await page.evaluate(_JS_EXTRACT)
                full_text = content.get("fullText", "")
                description = content.get("description", "")
                text_content = full_text + " " + description

                await page.close()
            except Exception:
                text_content = ""
                try:
                    await page.close()
                except Exception:
                    pass

            if not text_content or len(text_content) < 100:
                continue

            # Analyze the scraped content
            analysis = analyze_job_content(text_content, master_profile)

            # Determine contract type
            combined = (
                f"{job.get('title', '')} {job.get('type', '')} "
                f"{job.get('salary', '')} {text_content}"
            ).lower()
            is_freelance = (
                "lehibou" in (platform or "").lower()
                or "free-work" in (platform or "").lower()
                or "€/j" in job.get("salary", "")
                or "€⁄j" in job.get("salary", "")
                or re.search(
                    r"freelance|ind[ée]pendant|portage|tjm|mission\s",
                    combined, re.IGNORECASE,
                )
            )
            contract_type = "Freelance" if is_freelance else "CDI"

            enriched = dict(job)
            enriched["analysis"] = analysis
            enriched["contract_type"] = contract_type
            enriched["scraped_length"] = len(text_content)

            results.append(enriched)

            # Rate limiting between pages
            import asyncio as _asyncio
            await _asyncio.sleep(1.5)

        await browser.close()

    # Sort by match percentage descending
    results.sort(
        key=lambda j: j.get("analysis", {}).get("match_percentage", 0),
        reverse=True,
    )

    return results


# ---------------------------------------------------------------------------
# Selection
# ---------------------------------------------------------------------------

def select_top(
    jobs: list[dict],
    max_cdi: int = 15,
    max_freelance: int = 5,
) -> dict:
    """
    Split jobs into CDI and Freelance, take top N of each.

    Returns:
        {"cdi": list[dict], "freelance": list[dict]}
    """
    cdi = []
    freelance = []

    for job in jobs:
        # Determine type from multiple sources
        contract = (
            job.get("contract_type", "")
            or job.get("type", "")
        ).lower()
        salary_type = job.get("salary_parsed", {}).get("type", "")
        salary_text = job.get("salary", "").lower()
        title_text = job.get("title", "").lower()

        is_freelance = (
            "freelance" in contract
            or salary_type == "tjm"
            or re.search(
                r"freelance|ind[ée]pendant|portage|tjm",
                f"{salary_text} {title_text} {contract}",
                re.IGNORECASE,
            )
        )

        if is_freelance:
            freelance.append(job)
        else:
            cdi.append(job)

    return {
        "cdi": cdi[:max_cdi],
        "freelance": freelance[:max_freelance],
    }


# ---------------------------------------------------------------------------
# Markdown formatting
# ---------------------------------------------------------------------------

def format_markdown(
    jobs: list[dict],
    title: str = "Offres classees par pertinence",
) -> str:
    """
    Generate markdown report from ranked jobs.
    Port of the markdown output from analyze-jobs.js.

    Generates:
    - Header with date and profile info
    - Top 30 table (rank, match%, salary, distance, title, company, link)
    - Nearby section (< 35 km)
    - High TJM freelance section (>= 550 EUR/j)
    - High salary CDI section (>= 60k EUR)
    - Best match section (>= 40%)
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []

    lines.append(f"# {title}")
    lines.append(f"")
    lines.append(f"*Genere le {now} - {len(jobs)} offres analysees*")
    lines.append("")

    # Full results table
    lines.append(f"## Offres ({len(jobs)})")
    lines.append("")
    lines.append("| # | Match | Salaire | Distance | Titre | Entreprise | Lien |")
    lines.append("|---|-------|---------|----------|-------|------------|------|")

    for i, job in enumerate(jobs, 1):
        match_pct = job.get("match", {}).get("percentage", 0)
        salary_disp = job.get("salary_parsed", {}).get("display", "-")
        dist = job.get("distance", {})
        dist_label = dist.get("label", "?")
        dist_km = dist.get("km", 999)
        dist_str = f"{dist_km}km ({dist_label})" if dist_km < 999 else dist_label
        title_text = job.get("title", "-")
        company = job.get("company", "-")
        url = job.get("url", "")
        link = f"[Voir]({url})" if url else "-"

        lines.append(
            f"| {i} | {match_pct}% | {salary_disp} | {dist_str} "
            f"| {title_text} | {company} | {link} |"
        )

    lines.append("")

    # Nearby section (< 35 km)
    nearby = [j for j in jobs if j.get("distance", {}).get("km", 999) < 35]
    if nearby:
        lines.append("## Offres a proximite (< 35 km)")
        lines.append("")
        lines.append("| Match | Salaire | Distance | Titre | Entreprise | Lien |")
        lines.append("|-------|---------|----------|-------|------------|------|")
        for job in nearby[:20]:
            match_pct = job.get("match", {}).get("percentage", 0)
            salary_disp = job.get("salary_parsed", {}).get("display", "-")
            dist = job.get("distance", {})
            dist_str = f"{dist['km']}km ({dist['label']})"
            title_text = job.get("title", "-")
            company = job.get("company", "-")
            url = job.get("url", "")
            link = f"[Voir]({url})" if url else "-"
            lines.append(
                f"| {match_pct}% | {salary_disp} | {dist_str} "
                f"| {title_text} | {company} | {link} |"
            )
        lines.append("")

    # High TJM freelance section (>= 550 EUR/j)
    high_tjm = [
        j for j in jobs
        if j.get("salary_parsed", {}).get("type") == "tjm"
        and j.get("salary_parsed", {}).get("value", 0) >= 550
    ]
    if high_tjm:
        lines.append("## Freelance - TJM eleve (>= 550 EUR/j)")
        lines.append("")
        lines.append("| Match | TJM | Distance | Titre | Entreprise | Lien |")
        lines.append("|-------|-----|----------|-------|------------|------|")
        for job in high_tjm[:15]:
            match_pct = job.get("match", {}).get("percentage", 0)
            salary_disp = job.get("salary_parsed", {}).get("display", "-")
            dist = job.get("distance", {})
            dist_km = dist.get("km", 999)
            dist_str = f"{dist_km}km ({dist.get('label', '?')})" if dist_km < 999 else dist.get("label", "?")
            title_text = job.get("title", "-")
            company = job.get("company", "-")
            url = job.get("url", "")
            link = f"[Voir]({url})" if url else "-"
            lines.append(
                f"| {match_pct}% | {salary_disp} | {dist_str} "
                f"| {title_text} | {company} | {link} |"
            )
        lines.append("")

    # High salary CDI section (>= 60k EUR)
    high_salary = [
        j for j in jobs
        if j.get("salary_parsed", {}).get("type") == "salary"
        and j.get("salary_parsed", {}).get("value", 0) >= 60
    ]
    if high_salary:
        lines.append("## CDI - Salaire eleve (>= 60k EUR)")
        lines.append("")
        lines.append("| Match | Salaire | Distance | Titre | Entreprise | Lien |")
        lines.append("|-------|---------|----------|-------|------------|------|")
        for job in high_salary[:15]:
            match_pct = job.get("match", {}).get("percentage", 0)
            salary_disp = job.get("salary_parsed", {}).get("display", "-")
            dist = job.get("distance", {})
            dist_km = dist.get("km", 999)
            dist_str = f"{dist_km}km ({dist.get('label', '?')})" if dist_km < 999 else dist.get("label", "?")
            title_text = job.get("title", "-")
            company = job.get("company", "-")
            url = job.get("url", "")
            link = f"[Voir]({url})" if url else "-"
            lines.append(
                f"| {match_pct}% | {salary_disp} | {dist_str} "
                f"| {title_text} | {company} | {link} |"
            )
        lines.append("")

    # Best match section (>= 40%)
    best_match = [
        j for j in jobs
        if j.get("match", {}).get("percentage", 0) >= 40
    ]
    if best_match:
        lines.append("## Meilleure correspondance (>= 40%)")
        lines.append("")
        lines.append("| Match | Salaire | Distance | Remote | Titre | Entreprise | Lien |")
        lines.append("|-------|---------|----------|--------|-------|------------|------|")
        for job in best_match[:20]:
            match_pct = job.get("match", {}).get("percentage", 0)
            salary_disp = job.get("salary_parsed", {}).get("display", "-")
            dist = job.get("distance", {})
            dist_km = dist.get("km", 999)
            dist_str = f"{dist_km}km ({dist.get('label', '?')})" if dist_km < 999 else dist.get("label", "?")
            remote_label = job.get("remote", {}).get("label", "-")
            title_text = job.get("title", "-")
            company = job.get("company", "-")
            url = job.get("url", "")
            link = f"[Voir]({url})" if url else "-"
            lines.append(
                f"| {match_pct}% | {salary_disp} | {dist_str} | {remote_label} "
                f"| {title_text} | {company} | {link} |"
            )
        lines.append("")

    return "\n".join(lines)


def format_selected_markdown(selected: dict) -> str:
    """
    Generate detailed markdown for selected top jobs (CDI + Freelance).
    Port of the output from deep-analyze.js for jobs-selected.md.

    Args:
        selected: dict with "cdi" and "freelance" lists from select_top()

    Returns:
        Markdown string with detailed analysis for each selected job.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []

    lines.append("# Offres selectionnees - Analyse approfondie")
    lines.append("")
    lines.append(f"*Genere le {now}*")
    lines.append("")

    cdi_jobs = selected.get("cdi", [])
    freelance_jobs = selected.get("freelance", [])

    # CDI section
    if cdi_jobs:
        lines.append(f"## CDI - Top {len(cdi_jobs)}")
        lines.append("")

        for i, job in enumerate(cdi_jobs, 1):
            analysis = job.get("analysis", {})
            title_text = job.get("title", "-")
            company = job.get("company", "-")
            location = job.get("location", "-")
            url = job.get("url", "")

            match_pct = analysis.get("match_percentage", 0)
            if not match_pct:
                match_pct = job.get("match", {}).get("percentage", 0)

            lines.append(f"### {i}. {title_text} - {company}")
            lines.append("")

            if url:
                lines.append(f"- **Lien**: [{url}]({url})")
            lines.append(f"- **Lieu**: {location}")
            lines.append(f"- **Match**: {match_pct}%")

            # Salary
            sal = analysis.get("salary")
            if not sal:
                sal = job.get("salary_parsed", {}).get("display", "-")
            lines.append(f"- **Salaire**: {sal}")

            # Remote
            remote = analysis.get("remote", "")
            if not remote:
                remote = job.get("remote", {}).get("label", "-")
            lines.append(f"- **Remote**: {remote}")

            # Experience
            exp = analysis.get("experience")
            if exp:
                lines.append(f"- **Experience requise**: {exp}")

            # Matched skills
            matched = analysis.get("matched_skills", [])
            if matched:
                skill_names = [s["name"] for s in matched]
                lines.append(f"- **Competences matchees**: {', '.join(skill_names)}")

            # Missing skills / gaps
            missing = analysis.get("missing_skills", [])
            if missing:
                gap_names = [
                    f"{s['name']} (niveau {s['have']}/5)" for s in missing
                ]
                lines.append(f"- **Gaps identifies**: {', '.join(gap_names)}")

            lines.append("")

    # Freelance section
    if freelance_jobs:
        lines.append(f"## Freelance - Top {len(freelance_jobs)}")
        lines.append("")

        for i, job in enumerate(freelance_jobs, 1):
            analysis = job.get("analysis", {})
            title_text = job.get("title", "-")
            company = job.get("company", "-")
            location = job.get("location", "-")
            url = job.get("url", "")

            match_pct = analysis.get("match_percentage", 0)
            if not match_pct:
                match_pct = job.get("match", {}).get("percentage", 0)

            lines.append(f"### {i}. {title_text} - {company}")
            lines.append("")

            if url:
                lines.append(f"- **Lien**: [{url}]({url})")
            lines.append(f"- **Lieu**: {location}")
            lines.append(f"- **Match**: {match_pct}%")

            # Salary/TJM
            sal = analysis.get("salary")
            if not sal:
                sal = job.get("salary_parsed", {}).get("display", "-")
            lines.append(f"- **TJM**: {sal}")

            # Remote
            remote = analysis.get("remote", "")
            if not remote:
                remote = job.get("remote", {}).get("label", "-")
            lines.append(f"- **Remote**: {remote}")

            # Experience
            exp = analysis.get("experience")
            if exp:
                lines.append(f"- **Experience requise**: {exp}")

            # Matched skills
            matched = analysis.get("matched_skills", [])
            if matched:
                skill_names = [s["name"] for s in matched]
                lines.append(f"- **Competences matchees**: {', '.join(skill_names)}")

            # Missing skills / gaps
            missing = analysis.get("missing_skills", [])
            if missing:
                gap_names = [
                    f"{s['name']} (niveau {s['have']}/5)" for s in missing
                ]
                lines.append(f"- **Gaps identifies**: {', '.join(gap_names)}")

            lines.append("")

    if not cdi_jobs and not freelance_jobs:
        lines.append("*Aucune offre selectionnee.*")
        lines.append("")

    return "\n".join(lines)
