"""
_report.py - Job offer analysis report module for the work-application skill.

Generates a comprehensive report for a single job offer URL covering:
- Skills match analysis
- Company analysis
- Location analysis
- Salary analysis
- Overall recommendation score

Usage:
    from _report import generate_report, format_report_markdown, save_report
"""

import json
import re
import unicodedata
from datetime import datetime
from urllib.parse import quote

import _analyzer
from _storage import get_storage


# ---------------------------------------------------------------------------
# Country/region fallback tables for market data generation
# ---------------------------------------------------------------------------

_COUNTRY_MULTIPLIERS = {
    # (multiplier vs France IDF, currency)
    "france_idf":     (1.0,  "EUR"),
    "france_province": (0.85, "EUR"),
    "suisse":         (1.8,  "CHF"),
    "belgique":       (1.1,  "EUR"),
    "canada":         (1.0,  "CAD"),
    "usa":            (1.3,  "USD"),
    "uk":             (1.1,  "GBP"),
    "allemagne":      (1.05, "EUR"),
}

_BASE_CDI = {
    "devops":   {"junior": 40, "mid": 50, "senior": 60, "lead": 70},
    "sysadmin": {"junior": 35, "mid": 45, "senior": 55, "lead": 65},
    "sre":      {"junior": 42, "mid": 55, "senior": 65, "lead": 75},
    "cloud":    {"junior": 42, "mid": 52, "senior": 62, "lead": 72},
    "default":  {"junior": 38, "mid": 48, "senior": 58, "lead": 68},
}

_BASE_TJM = {
    "devops":   {"junior": 400, "mid": 550, "senior": 650, "lead": 750},
    "sysadmin": {"junior": 350, "mid": 500, "senior": 600, "lead": 700},
    "sre":      {"junior": 450, "mid": 600, "senior": 700, "lead": 800},
    "cloud":    {"junior": 420, "mid": 560, "senior": 660, "lead": 760},
    "default":  {"junior": 380, "mid": 520, "senior": 620, "lead": 720},
}

_MARKET_DATA_FILE = "market-data.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = re.sub(r"[\u0300-\u036f]", "", text)
    return text


def _detect_region(location: str) -> tuple[str, str]:
    """Detect country/region key and currency from a location string.

    Returns (region_key, currency).
    """
    loc = _normalize(location)

    if re.search(r"suisse|switzerland|zurich|geneve|bern|lausanne|basel", loc):
        return "suisse", "CHF"
    if re.search(r"belgique|belgium|bruxelles|brussels|liege|anvers", loc):
        return "belgique", "EUR"
    if re.search(r"canada|montreal|toronto|vancouver|ottawa", loc):
        return "canada", "CAD"
    if re.search(r"usa|united states|new york|san francisco|seattle|boston|chicago", loc):
        return "usa", "USD"
    if re.search(r"uk|united kingdom|london|manchester|birmingham|england", loc):
        return "uk", "GBP"
    if re.search(r"allemagne|germany|berlin|munich|frankfurt|hamburg", loc):
        return "allemagne", "EUR"

    # France detection
    if re.search(r"paris|ile.de.france|idf|la defense|boulogne|issy|nanterre|puteaux|levallois", loc):
        return "france_idf", "EUR"
    if re.search(r"france|lyon|marseille|toulouse|bordeaux|nantes|lille|strasbourg|rennes|montpellier", loc):
        return "france_province", "EUR"

    # Default to IDF France if location contains common IDF cities or is ambiguous
    if re.search(r"dourdan|evry|massy|versailles|saclay|orsay|palaiseau|velizy", loc):
        return "france_idf", "EUR"

    return "france_idf", "EUR"


def _generate_default_market_data(location: str) -> dict:
    """Generate default market data adapted to the user's region."""
    region_key, currency = _detect_region(location)
    multiplier, _ = _COUNTRY_MULTIPLIERS.get(region_key, (1.0, "EUR"))

    # Apply multiplier to base values
    salary_cdi = {}
    for role, levels in _BASE_CDI.items():
        salary_cdi[role] = {
            level: round(val * multiplier)
            for level, val in levels.items()
        }

    tjm = {}
    for role, levels in _BASE_TJM.items():
        tjm[role] = {
            level: round(val * multiplier / 10) * 10  # round to nearest 10
            for level, val in levels.items()
        }

    # Human-readable region label
    region_labels = {
        "france_idf": "Ile-de-France, France",
        "france_province": "Province, France",
        "suisse": "Suisse",
        "belgique": "Belgique",
        "canada": "Canada",
        "usa": "USA",
        "uk": "United Kingdom",
        "allemagne": "Allemagne",
    }

    return {
        "region": region_labels.get(region_key, location),
        "currency": currency,
        "generated": datetime.now().strftime("%Y-%m-%d"),
        "salary_cdi": salary_cdi,
        "tjm": tjm,
    }


def _load_market_data(master_profile: dict) -> dict:
    """Load or generate market data from storage."""
    store = get_storage()

    location = ""
    identity = master_profile.get("identity", {})
    if isinstance(identity, dict):
        location = identity.get("location", "")
    elif isinstance(master_profile.get("location"), str):
        location = master_profile["location"]

    if store.exists(_MARKET_DATA_FILE):
        try:
            data = store.read_json(_MARKET_DATA_FILE)
            region_key, _ = _detect_region(location)
            region_labels = {
                "france_idf": "Ile-de-France, France",
                "france_province": "Province, France",
                "suisse": "Suisse",
                "belgique": "Belgique",
                "canada": "Canada",
                "usa": "USA",
                "uk": "United Kingdom",
                "allemagne": "Allemagne",
            }
            expected_region = region_labels.get(region_key, location)
            if data.get("region") == expected_region:
                return data
        except Exception:
            pass

    # Generate and save
    data = _generate_default_market_data(location)
    try:
        store.ensure_dir()
        store.write_json(_MARKET_DATA_FILE, data)
    except Exception:
        pass
    return data


def _detect_role_family(text: str) -> str:
    """Classify job text into a role family for market salary lookup."""
    t = text.lower()
    if re.search(r"devops|ci.?cd|pipeline|deploy|release", t):
        return "devops"
    if re.search(r"sre|site.?reliability|observabilit", t):
        return "sre"
    if re.search(r"cloud|aws|azure|gcp|architect.*cloud", t):
        return "cloud"
    if re.search(r"sysadmin|system.?admin|ingenieur.?syst|system.?engineer|admin.*systeme", t):
        return "sysadmin"
    return "default"


def _extract_company_and_title(text: str, url: str) -> dict:
    """Extract company name and job title from scraped text and URL."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    title = ""
    company = ""

    # Try to get title from first meaningful line
    for line in lines[:10]:
        if len(line) > 10 and len(line) < 120 and not line.startswith("http"):
            title = line
            break

    # Try common patterns for company — use \b around "at" to avoid substring matches
    for line in lines[:30]:
        m = re.search(
            r"(?:chez|\bat\b|@|entreprise|company|companies|societe|société)\s*[:\-]?\s*(.+)",
            line, re.IGNORECASE,
        )
        if m:
            company = m.group(1).strip()[:60]
            break

    # Fallback: extract from URL path (handles /company/ and /companies/ — e.g. WTTJ)
    if not company:
        path_match = re.search(
            r"(?:compan(?:y|ies)|entreprise|societe)/([^/?#]+)", url, re.IGNORECASE
        )
        if path_match:
            slug = path_match.group(1)
            # Strip common locale suffixes (-fr, -france, -be, etc.)
            slug = re.sub(r"-(?:fr|be|ch|de|uk|es|it|france|belgium)$", "", slug, flags=re.IGNORECASE)
            company = slug.replace("-", " ").title()
        else:
            domain_match = re.search(r"https?://(?:www\.)?([^/]+)", url)
            if domain_match:
                company = domain_match.group(1)

    return {"title": title, "company": company}


async def _scrape_job_page(url: str) -> dict:
    """Scrape a job page using Playwright. Returns full_text, title, success."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise ImportError(
            "Playwright is required for report generation.\n"
            "Install with: pip install playwright && playwright install chromium"
        )

    try:
        from playwright_stealth import stealth_async
    except ImportError:
        stealth_async = None

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
                description: description.substring(0, 10000),
                title: document.title || ''
            };
        }
    """ % str(list(_DESCRIPTION_SELECTORS))

    result = {"full_text": "", "title": "", "success": False}

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

        try:
            page = await context.new_page()

            if stealth_async is not None:
                await stealth_async(page)

            # Handle cookie consent for common job boards
            if "lehibou" in url:
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

            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            # Accept cookies generically
            try:
                for selector in [
                    '[data-cky-tag="accept-button"]',
                    "#onetrust-accept-btn-handler",
                    ".didomi-continue-without-agreeing",
                    'button[id*="accept"]',
                    'button[class*="accept"]',
                ]:
                    btn = page.locator(selector).first
                    if await btn.is_visible(timeout=1000):
                        await btn.click()
                        await page.wait_for_timeout(500)
                        break
            except Exception:
                pass

            content = await page.evaluate(_JS_EXTRACT)
            full_text = content.get("fullText", "")
            description = content.get("description", "")
            page_title = content.get("title", "")

            result["full_text"] = full_text + " " + description
            result["title"] = page_title
            result["success"] = len(full_text) > 100

            await page.close()
        except Exception:
            try:
                await page.close()
            except Exception:
                pass

        await browser.close()

    return result


async def _scrape_company_reviews(company_name: str) -> dict:
    """Scrape Glassdoor FR / Indeed FR for company reviews.

    Fully graceful - never raises. Returns scraped data or empty defaults.
    Only called when allow_scrape=true.
    """
    result = {
        "glassdoor_rating": None,
        "indeed_rating": None,
        "scraped": False,
        "source": "",
    }

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return result

    try:
        from playwright_stealth import stealth_async
    except ImportError:
        stealth_async = None

    clean_name = re.sub(r"[^a-zA-Z0-9\s]", "", company_name).strip()
    if not clean_name:
        return result

    try:
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
            )

            sources = []

            # --- Glassdoor FR ---
            try:
                page = await context.new_page()
                if stealth_async:
                    await stealth_async(page)

                slug = quote(clean_name.replace(" ", "-"), safe="-")
                search_url = (
                    f"https://www.glassdoor.fr/Avis/"
                    f"{slug}-Avis-E0.htm"
                )
                await page.goto(search_url, wait_until="networkidle", timeout=20000)
                await page.wait_for_timeout(2000)

                # Try to extract rating
                rating_text = await page.evaluate("""
                    () => {
                        const el = document.querySelector('[data-test="rating-headline"]')
                            || document.querySelector('.rating-headline')
                            || document.querySelector('.v2__EIReviewsRatingsStylesV2__ratingNum');
                        return el ? el.innerText.trim() : '';
                    }
                """)
                if rating_text:
                    m = re.search(r"(\d[.,]\d)", rating_text)
                    if m:
                        result["glassdoor_rating"] = float(m.group(1).replace(",", "."))
                        sources.append("glassdoor")

                await page.close()
            except Exception:
                try:
                    await page.close()
                except Exception:
                    pass

            # --- Indeed FR ---
            try:
                page = await context.new_page()
                if stealth_async:
                    await stealth_async(page)

                slug = quote(clean_name.replace(" ", "-"), safe="-")
                search_url = (
                    f"https://fr.indeed.com/cmp/{slug}/reviews"
                )
                await page.goto(search_url, wait_until="networkidle", timeout=20000)
                await page.wait_for_timeout(2000)

                rating_text = await page.evaluate("""
                    () => {
                        const el = document.querySelector('[data-testid="rating-headline"]')
                            || document.querySelector('.cmp-header-rating-value')
                            || document.querySelector('[itemprop="ratingValue"]');
                        return el ? (el.innerText || el.getAttribute('content') || '').trim() : '';
                    }
                """)
                if rating_text:
                    m = re.search(r"(\d[.,]\d)", rating_text)
                    if m:
                        result["indeed_rating"] = float(m.group(1).replace(",", "."))
                        sources.append("indeed")

                await page.close()
            except Exception:
                try:
                    await page.close()
                except Exception:
                    pass

            await browser.close()

            if sources:
                result["scraped"] = True
                result["source"] = ", ".join(sources)

    except Exception:
        pass

    return result


# ---------------------------------------------------------------------------
# 4 analysis functions
# ---------------------------------------------------------------------------

def analyze_skills(job_text: str, master_profile: dict) -> dict:
    """Analyze skills match. Returns score 0-100 + details."""
    analysis = _analyzer.analyze_job_content(job_text, master_profile)

    matched = analysis.get("matched_skills", [])
    missing = analysis.get("missing_skills", [])

    # Classify relevance of matched skills
    for skill in matched:
        level = skill.get("level", 1)
        if level >= 4:
            skill["relevance"] = "core"
        elif level >= 2:
            skill["relevance"] = "important"
        else:
            skill["relevance"] = "bonus"

    # Classify criticality of missing skills
    for gap in missing:
        have = gap.get("have", 0)
        if have == 0:
            gap["criticality"] = "critique"
        elif have <= 1:
            gap["criticality"] = "important"
        else:
            gap["criticality"] = "mineur"

    # Bonus skills: profile has them but job doesn't require them
    job_lower = job_text.lower()
    bonus_skills = []
    hard_skills = master_profile.get("hard_skills", [])
    for skill_cat in hard_skills:
        name = skill_cat.get("name", "")
        keywords = skill_cat.get("keywords", [])
        found_in_job = False
        for kw in keywords:
            kw_str = kw if isinstance(kw, str) else kw.get("name", "")
            if kw_str and re.search(re.escape(kw_str), job_lower, re.IGNORECASE):
                found_in_job = True
                break
        if not found_in_job and name:
            already_matched = any(
                _normalize(m["name"]) == _normalize(name) for m in matched
            )
            if not already_matched:
                bonus_skills.append({"name": name, "level": skill_cat.get("level", 1)})

    # Experience comparison
    experience_required = analysis.get("experience")
    total_years = _compute_total_experience(master_profile)
    experience_match = None
    if experience_required:
        req_match = re.search(r"(\d+)", experience_required)
        if req_match:
            req_years = int(req_match.group(1))
            if total_years >= req_years:
                experience_match = "ok"
            elif total_years >= req_years - 2:
                experience_match = "proche"
            else:
                experience_match = "insuffisant"

    # Score calculation
    base = analysis.get("match_percentage", 0)
    # Penalty for critical missing skills
    critical_count = sum(1 for g in missing if g.get("criticality") == "critique")
    penalty = critical_count * 8
    # Bonus for experience match
    exp_bonus = 0
    if experience_match == "ok":
        exp_bonus = 10
    elif experience_match == "proche":
        exp_bonus = 5
    elif experience_match == "insuffisant":
        exp_bonus = -5

    score = max(0, min(100, base - penalty + exp_bonus))

    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "bonus_skills": bonus_skills[:10],
        "experience_required": experience_required,
        "experience_profile": f"{total_years} ans" if total_years else None,
        "experience_match": experience_match,
        "raw_match_percentage": base,
    }


def _compute_total_experience(master_profile: dict) -> int:
    """Compute total years of experience from the profile."""
    experiences = master_profile.get("experiences", [])
    if not experiences:
        return 0

    total_months = 0
    now = datetime.now()

    for exp in experiences:
        start = exp.get("startDate", "")
        end = exp.get("endDate", "")

        start_date = _parse_date(start)
        if not start_date:
            continue

        if end.lower() in ("present", "actuel", "en cours", ""):
            end_date = now
        else:
            end_date = _parse_date(end)
            if not end_date:
                end_date = now

        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        total_months += max(0, months)

    return total_months // 12


def _parse_date(date_str: str) -> datetime | None:
    """Parse a date string like 2020-01 or 2020."""
    if not date_str:
        return None
    date_str = date_str.strip()
    for fmt in ("%Y-%m", "%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def analyze_company(company_name: str, job_text: str, review_data: dict) -> dict:
    """Analyze company information. Returns score 0-100 + details."""
    text_lower = job_text.lower()

    # Detect company type
    company_type = "inconnu"
    if re.search(r"esn|ssii|ss2i|societe de services|consulting|conseil", text_lower):
        company_type = "ESN"
    elif re.search(r"startup|start.?up|jeune.?pousse|scale.?up", text_lower):
        company_type = "Startup"
    elif re.search(r"grand.?groupe|cac.?40|multinationale|international", text_lower):
        company_type = "Grand groupe"
    elif re.search(r"pme|tpe|petite.?entreprise", text_lower):
        company_type = "PME"
    elif re.search(r"editeur|saas|produit", text_lower):
        company_type = "Editeur"
    elif re.search(r"public|administration|collectivite|hopital|etat", text_lower):
        company_type = "Secteur public"

    # Detect sector
    sector = "inconnu"
    sector_patterns = [
        (r"banque|finance|assurance|fintech", "Finance"),
        (r"sante|pharma|medical|biotech", "Sante"),
        (r"telecom|operateur|reseau", "Telecom"),
        (r"industrie|manufactur|aeronauti|automobile|defense", "Industrie"),
        (r"retail|e.?commerce|distribution|logistique", "Retail/E-commerce"),
        (r"media|presse|edition|divertissement", "Media"),
        (r"energie|nucleaire|edf|engie|renouvelable", "Energie"),
        (r"transport|mobilite|sncf|ratp|aviation", "Transport"),
        (r"education|formation|universite|ecole", "Education"),
        (r"immobilier|construction|btp", "Immobilier/BTP"),
    ]
    for pat, label in sector_patterns:
        if re.search(pat, text_lower):
            sector = label
            break

    # Positive indicators in text
    positive_indicators = []
    negative_indicators = []

    positive_patterns = [
        (r"teletravail|remote|hybride", "Politique remote"),
        (r"formation|certif|montee.?en.?competences", "Formation proposee"),
        (r"interessement|participation|prime", "Avantages financiers"),
        (r"mutuelle|prevoyance|tickets.?restaurant|ce\b", "Avantages sociaux"),
        (r"agile|scrum|devops|ci.?cd", "Methodes modernes"),
        (r"open.?source|github|communaute", "Culture tech"),
    ]
    for pat, label in positive_patterns:
        if re.search(pat, text_lower):
            positive_indicators.append(label)

    negative_patterns = [
        (r"astreinte|on.?call|permanence|weekend", "Astreintes"),
        (r"deplacements?\s+frequent", "Deplacements frequents"),
        (r"confidentiel|secret|habilit", "Habilitation requise"),
    ]
    for pat, label in negative_patterns:
        if re.search(pat, text_lower):
            negative_indicators.append(label)

    # Score calculation: 50 base + 25 ratings + 25 text indicators
    score = 50

    # Ratings component (25 pts max)
    ratings_available = False
    avg_rating = 0
    rating_count = 0
    if review_data.get("glassdoor_rating"):
        avg_rating += review_data["glassdoor_rating"]
        rating_count += 1
        ratings_available = True
    if review_data.get("indeed_rating"):
        avg_rating += review_data["indeed_rating"]
        rating_count += 1
        ratings_available = True

    if ratings_available:
        avg_rating = avg_rating / rating_count
        # Map 1-5 rating to 0-25 score
        score += round((avg_rating - 1) * 25 / 4)
    else:
        score += 12  # neutral when no data

    # Text indicators component (25 pts max)
    indicator_score = len(positive_indicators) * 5 - len(negative_indicators) * 4
    score += max(0, min(25, indicator_score + 10))

    score = max(0, min(100, score))

    return {
        "score": score,
        "company_name": company_name,
        "company_type": company_type,
        "sector": sector,
        "glassdoor_rating": review_data.get("glassdoor_rating"),
        "indeed_rating": review_data.get("indeed_rating"),
        "ratings_scraped": review_data.get("scraped", False),
        "positive_indicators": positive_indicators,
        "negative_indicators": negative_indicators,
    }


def analyze_location(job_text: str, master_profile: dict) -> dict:
    """Analyze location and remote work. Returns score 0-100 + details."""
    # Get location from job text
    location_str = ""
    for line in job_text.split("\n")[:20]:
        m = re.search(
            r"(?:lieu|location|localisation|ville|site)\s*[:\-]\s*(.+)",
            line, re.IGNORECASE,
        )
        if m:
            location_str = m.group(1).strip()
            break

    if not location_str:
        # Try to detect city names directly
        loc_match = re.search(
            r"(?:paris|lyon|marseille|toulouse|bordeaux|nantes|lille|"
            r"strasbourg|rennes|montpellier|dourdan|massy|saclay|"
            r"versailles|velizy|evry|palaiseau|orsay|remote|"
            r"teletravail|full\s*remote)",
            job_text[:3000], re.IGNORECASE,
        )
        if loc_match:
            location_str = loc_match.group(0)

    distance = _analyzer.estimate_distance(location_str, "")

    # Remote detection from full text
    remote = _analyzer.detect_remote(
        job_text[:500],  # title area
        location_str,
        job_text[:2000],
    )

    # Scoring by distance tiers
    km = distance.get("km", 999)
    if remote.get("value", 0) >= 100:
        # Full remote
        base_score = 95
    elif km == 0:
        base_score = 95
    elif km <= 15:
        base_score = 90
    elif km <= 30:
        base_score = 75
    elif km <= 50:
        base_score = 55
    elif km <= 80:
        base_score = 35
    elif km < 999:
        base_score = 15
    else:
        base_score = 40  # unknown location

    # Remote bonus for partial remote
    remote_bonus = 0
    remote_value = remote.get("value", 0)
    if 0 < remote_value < 100:
        remote_bonus = 15

    score = min(100, base_score + remote_bonus)

    # Commute estimate
    commute = ""
    if km == 0:
        commute = "Pas de trajet"
    elif km < 999:
        if km <= 20:
            commute = f"~{km * 2} min en voiture"
        elif km <= 50:
            commute = f"~{km + 10} min en voiture"
        else:
            hours = round(km / 60, 1)
            commute = f"~{hours}h en voiture / transports"

    return {
        "score": score,
        "distance_km": km if km < 999 else None,
        "distance_label": distance.get("label", "Inconnu"),
        "remote": remote.get("label", "Sur site"),
        "remote_value": remote_value,
        "commute": commute,
        "location_detected": location_str,
    }


def analyze_salary(
    job_text: str,
    role_family: str,
    master_profile: dict,
    market_data: dict,
) -> dict:
    """Analyze salary against market rates. Returns score 0-100 + details."""
    # Parse salary from job text
    salary_parsed = _analyzer.parse_salary(job_text[:2000])

    # Also try to find salary in full text if not found
    if salary_parsed["type"] == "unknown":
        # Look for salary patterns in full text
        tjm_match = re.search(
            r"(\d{3,4})\s*[€e]?\s*/?\s*j(?:our)?", job_text, re.IGNORECASE
        )
        if tjm_match:
            val = int(tjm_match.group(1))
            salary_parsed = {"value": val, "display": f"{val} EUR/j", "type": "tjm"}
        else:
            sal_match = re.search(
                r"(\d{2,3})\s*k?\s*[-–à]\s*(\d{2,3})\s*k?\s*[€e]?",
                job_text, re.IGNORECASE,
            )
            if sal_match:
                low = int(sal_match.group(1))
                high = int(sal_match.group(2))
                if low > 200:
                    low = low // 1000
                if high > 200:
                    high = high // 1000
                avg = (low + high) // 2
                salary_parsed = {"value": avg, "display": f"{low}-{high}k EUR", "type": "salary"}

    # Get market references
    cdi_refs = market_data.get("salary_cdi", {}).get(role_family, market_data.get("salary_cdi", {}).get("default", {}))
    tjm_refs = market_data.get("tjm", {}).get(role_family, market_data.get("tjm", {}).get("default", {}))
    currency = market_data.get("currency", "EUR")

    # Determine experience level for market comparison
    total_years = _compute_total_experience(master_profile)
    if total_years >= 12:
        level = "lead"
    elif total_years >= 7:
        level = "senior"
    elif total_years >= 3:
        level = "mid"
    else:
        level = "junior"

    market_cdi = cdi_refs.get(level, 50)
    market_tjm = tjm_refs.get(level, 550)

    # CDI <-> TJM equivalence (218 working days, ~0.55 ratio for charges)
    cdi_to_tjm = lambda cdi_k: round(cdi_k * 1000 / 218 * 1.3 / 10) * 10
    tjm_to_cdi = lambda tjm: round(tjm * 218 * 0.55 / 1000)

    equivalence = {}
    market_position = None
    score = 50  # default when no salary found

    if salary_parsed["type"] == "tjm":
        tjm_val = salary_parsed["value"]
        equivalence["tjm"] = tjm_val
        equivalence["cdi_equivalent"] = tjm_to_cdi(tjm_val)
        equivalence["currency"] = currency

        # Score based on position vs market
        if market_tjm > 0:
            ratio = tjm_val / market_tjm
            if ratio >= 1.1:
                score = 90
                market_position = "au-dessus du marche"
            elif ratio >= 0.95:
                score = 75
                market_position = "dans le marche"
            elif ratio >= 0.85:
                score = 55
                market_position = "legerement sous le marche"
            elif ratio >= 0.7:
                score = 35
                market_position = "sous le marche"
            else:
                score = 15
                market_position = "nettement sous le marche"

    elif salary_parsed["type"] == "salary":
        cdi_val = salary_parsed["value"]
        equivalence["cdi"] = cdi_val
        equivalence["tjm_equivalent"] = cdi_to_tjm(cdi_val)
        equivalence["currency"] = currency

        if market_cdi > 0:
            ratio = cdi_val / market_cdi
            if ratio >= 1.1:
                score = 90
                market_position = "au-dessus du marche"
            elif ratio >= 0.95:
                score = 75
                market_position = "dans le marche"
            elif ratio >= 0.85:
                score = 55
                market_position = "legerement sous le marche"
            elif ratio >= 0.7:
                score = 35
                market_position = "sous le marche"
            else:
                score = 15
                market_position = "nettement sous le marche"

    else:
        market_position = "non communique"

    return {
        "score": score,
        "salary_parsed": salary_parsed,
        "market_cdi": market_cdi,
        "market_tjm": market_tjm,
        "market_level": level,
        "market_position": market_position,
        "equivalence": equivalence,
        "currency": currency,
        "role_family": role_family,
    }


# ---------------------------------------------------------------------------
# Overall score
# ---------------------------------------------------------------------------

def compute_overall_score(
    skills: dict,
    company: dict,
    location: dict,
    salary: dict,
) -> dict:
    """Compute weighted overall score and verdict."""
    s_skills = skills.get("score", 0)
    s_company = company.get("score", 0)
    s_location = location.get("score", 0)
    s_salary = salary.get("score", 0)

    # Weights: skills 40%, salary 25%, location 20%, company 15%
    overall = round(
        s_skills * 0.40
        + s_salary * 0.25
        + s_location * 0.20
        + s_company * 0.15
    )

    if overall >= 70:
        verdict = "Recommande"
        verdict_detail = "Cette offre presente un bon alignement avec votre profil."
    elif overall >= 45:
        verdict = "Possible avec reserves"
        verdict_detail = "Cette offre peut etre interessante mais comporte des points d'attention."
    else:
        verdict = "Non recommande"
        verdict_detail = "Cette offre presente trop de decalages avec votre profil."

    return {
        "score": overall,
        "verdict": verdict,
        "verdict_detail": verdict_detail,
        "weights": {
            "skills": {"score": s_skills, "weight": "40%"},
            "salary": {"score": s_salary, "weight": "25%"},
            "location": {"score": s_location, "weight": "20%"},
            "company": {"score": s_company, "weight": "15%"},
        },
    }


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

async def generate_report(
    url: str,
    master_profile: dict,
    config: dict,
    on_progress=None,
) -> dict:
    """Generate a full analysis report for a job offer URL.

    Parameters
    ----------
    url : str
        The job offer URL to analyze.
    master_profile : dict
        The master profile dict.
    config : dict
        The skill config dict.
    on_progress : callable, optional
        Callback ``(step, message)`` for progress reporting.

    Returns
    -------
    dict
        Full report with all analysis sections + metadata.
    """

    def progress(step, msg):
        if on_progress:
            on_progress(step, msg)

    # Step 1: Scrape the job page
    progress(1, "Scraping de la page de l'offre...")
    scraped = await _scrape_job_page(url)

    if not scraped["success"]:
        return {
            "success": False,
            "error": "Impossible de scraper la page de l'offre.",
            "url": url,
        }

    job_text = scraped["full_text"]

    # Step 2: Extract company + title
    progress(2, "Extraction des informations...")
    info = _extract_company_and_title(job_text, url)
    company_name = info["company"]
    job_title = info["title"] or scraped["title"]

    # Step 3: Scrape company reviews if allowed
    review_data = {
        "glassdoor_rating": None,
        "indeed_rating": None,
        "scraped": False,
        "source": "",
    }
    allow_scrape = config.get("allow_scrape", False)
    if allow_scrape and company_name:
        progress(3, f"Recherche d'avis sur {company_name}...")
        review_data = await _scrape_company_reviews(company_name)
    else:
        progress(3, "Scraping des avis desactive (allow_scrape=false)")

    # Step 4: Detect role family + load market data
    progress(4, "Analyse du poste...")
    role_family = _detect_role_family(job_text)
    market_data = _load_market_data(master_profile)

    # Step 5: Run the 4 analyses
    progress(5, "Analyse des competences...")
    skills_result = analyze_skills(job_text, master_profile)

    progress(6, "Analyse de l'entreprise...")
    company_result = analyze_company(company_name, job_text, review_data)

    progress(7, "Analyse de la localisation...")
    location_result = analyze_location(job_text, master_profile)

    progress(8, "Analyse du salaire...")
    salary_result = analyze_salary(job_text, role_family, master_profile, market_data)

    # Step 6: Overall score
    progress(9, "Calcul du score global...")
    overall = compute_overall_score(
        skills_result, company_result, location_result, salary_result
    )

    report = {
        "success": True,
        "url": url,
        "job_title": job_title,
        "company_name": company_name,
        "role_family": role_family,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "overall": overall,
        "skills": skills_result,
        "company": company_result,
        "location": location_result,
        "salary": salary_result,
        "market_data_region": market_data.get("region", ""),
        "allow_scrape": allow_scrape,
    }

    progress(10, "Rapport genere.")
    return report


# ---------------------------------------------------------------------------
# Markdown formatting
# ---------------------------------------------------------------------------

def format_report_markdown(report: dict) -> str:
    """Format a report dict as a markdown string."""
    if not report.get("success"):
        return f"# Erreur\n\n{report.get('error', 'Erreur inconnue')}\n"

    lines = []
    overall = report["overall"]
    skills = report["skills"]
    company = report["company"]
    location = report["location"]
    salary = report["salary"]

    # Header
    lines.append(f"# Rapport d'analyse : {report['job_title']}")
    lines.append("")
    lines.append(f"**Entreprise** : {report['company_name']}")
    lines.append(f"**URL** : {report['url']}")
    lines.append(f"**Genere le** : {report['generated_at']}")
    lines.append(f"**Famille de poste** : {report['role_family']}")
    lines.append("")

    # Verdict
    verdict = overall["verdict"]
    score = overall["score"]
    lines.append(f"## Verdict : {verdict} ({score}/100)")
    lines.append("")
    lines.append(f"_{overall['verdict_detail']}_")
    lines.append("")

    # Summary table
    lines.append("| Dimension | Score | Poids |")
    lines.append("|-----------|-------|-------|")
    w = overall["weights"]
    lines.append(f"| Competences | {w['skills']['score']}/100 | {w['skills']['weight']} |")
    lines.append(f"| Salaire | {w['salary']['score']}/100 | {w['salary']['weight']} |")
    lines.append(f"| Localisation | {w['location']['score']}/100 | {w['location']['weight']} |")
    lines.append(f"| Entreprise | {w['company']['score']}/100 | {w['company']['weight']} |")
    lines.append(f"| **Global** | **{score}/100** | |")
    lines.append("")

    # --- Section 1: Skills ---
    lines.append("---")
    lines.append("")
    lines.append(f"## 1. Competences ({skills['score']}/100)")
    lines.append("")

    if skills["matched_skills"]:
        lines.append("### Competences matchees")
        lines.append("")
        lines.append("| Competence | Niveau | Pertinence |")
        lines.append("|------------|--------|------------|")
        for s in skills["matched_skills"]:
            lines.append(f"| {s['name']} | {s.get('level', '-')} | {s.get('relevance', '-')} |")
        lines.append("")

    if skills["missing_skills"]:
        lines.append("### Competences manquantes")
        lines.append("")
        lines.append("| Competence | Maitrise actuelle | Criticite |")
        lines.append("|------------|-------------------|-----------|")
        for g in skills["missing_skills"]:
            have_label = {0: "Aucune", 1: "Notions", 2: "Intermediaire"}.get(
                g.get("have", 0), str(g.get("have", 0))
            )
            lines.append(f"| {g['name']} | {have_label} | {g.get('criticality', '-')} |")
        lines.append("")

    if skills["bonus_skills"]:
        lines.append("### Competences bonus (profil mais pas demandees)")
        lines.append("")
        for s in skills["bonus_skills"]:
            lines.append(f"- {s['name']} (niveau {s.get('level', '-')})")
        lines.append("")

    if skills["experience_required"]:
        lines.append(f"**Experience requise** : {skills['experience_required']}")
        if skills["experience_profile"]:
            lines.append(f"**Experience profil** : {skills['experience_profile']}")
        if skills["experience_match"]:
            match_labels = {
                "ok": "Suffisante",
                "proche": "Proche du requis",
                "insuffisant": "Insuffisante",
            }
            lines.append(f"**Evaluation** : {match_labels.get(skills['experience_match'], skills['experience_match'])}")
        lines.append("")

    # --- Section 2: Company ---
    lines.append("---")
    lines.append("")
    lines.append(f"## 2. Entreprise ({company['score']}/100)")
    lines.append("")
    lines.append(f"- **Nom** : {company['company_name']}")
    lines.append(f"- **Type** : {company['company_type']}")
    lines.append(f"- **Secteur** : {company['sector']}")

    if company["glassdoor_rating"]:
        lines.append(f"- **Glassdoor** : {company['glassdoor_rating']}/5")
    if company["indeed_rating"]:
        lines.append(f"- **Indeed** : {company['indeed_rating']}/5")
    if not company["ratings_scraped"]:
        lines.append("- _Ratings non scrapes (allow_scrape=false ou donnees indisponibles)_")
        lines.append("- _L'agent peut completer cette section avec des recherches manuelles._")

    lines.append("")

    if company["positive_indicators"]:
        lines.append("**Points positifs** :")
        for ind in company["positive_indicators"]:
            lines.append(f"- {ind}")
        lines.append("")

    if company["negative_indicators"]:
        lines.append("**Points d'attention** :")
        for ind in company["negative_indicators"]:
            lines.append(f"- {ind}")
        lines.append("")

    # --- Section 3: Location ---
    lines.append("---")
    lines.append("")
    lines.append(f"## 3. Localisation ({location['score']}/100)")
    lines.append("")
    if location["location_detected"]:
        lines.append(f"- **Lieu detecte** : {location['location_detected']}")
    if location["distance_km"] is not None:
        lines.append(f"- **Distance** : {location['distance_km']} km ({location['distance_label']})")
    else:
        lines.append(f"- **Distance** : inconnue")
    lines.append(f"- **Remote** : {location['remote']}")
    if location["commute"]:
        lines.append(f"- **Trajet estime** : {location['commute']}")
    lines.append("")

    # --- Section 4: Salary ---
    lines.append("---")
    lines.append("")
    lines.append(f"## 4. Salaire ({salary['score']}/100)")
    lines.append("")

    sp = salary["salary_parsed"]
    salary_display = sp.get('display', '-') or '-'
    if len(salary_display) > 80:
        salary_display = "Non specifie"
    lines.append(f"- **Salaire detecte** : {salary_display}")
    lines.append(f"- **Type** : {sp.get('type', 'inconnu')}")

    if salary["market_position"]:
        lines.append(f"- **Position marche** : {salary['market_position']}")

    lines.append(f"- **Reference marche ({salary['market_level']})** : "
                 f"{salary['market_cdi']}k {salary['currency']} (CDI) / "
                 f"{salary['market_tjm']} {salary['currency']}/j (TJM)")
    lines.append(f"- **Region** : {report.get('market_data_region', '-')}")

    eq = salary.get("equivalence", {})
    if eq.get("cdi_equivalent"):
        lines.append(f"- **Equivalent CDI** : ~{eq['cdi_equivalent']}k {eq.get('currency', 'EUR')}")
    if eq.get("tjm_equivalent"):
        lines.append(f"- **Equivalent TJM** : ~{eq['tjm_equivalent']} {eq.get('currency', 'EUR')}/j")

    lines.append("")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Save report
# ---------------------------------------------------------------------------

def save_report(report: dict, markdown: str) -> dict:
    """Save report as .md and .json in storage. Returns file paths used."""
    store = get_storage()
    store.ensure_dir()

    # Build filename - strict sanitisation to prevent path traversal
    company = report.get("company_name", "unknown")
    # Only keep ASCII alphanumeric + hyphens
    company_slug = re.sub(r"[^a-zA-Z0-9]", "-", company).strip("-").lower()
    company_slug = re.sub(r"-+", "-", company_slug)[:30]
    # Reject any remaining traversal attempt
    if not company_slug or ".." in company_slug or "/" in company_slug:
        company_slug = "unknown"
    date_str = datetime.now().strftime("%Y-%m-%d")

    md_name = f"reports/report-{company_slug}-{date_str}.md"
    json_name = f"reports/report-{company_slug}-{date_str}.json"

    store.write_text(md_name, markdown)
    store.write_json(json_name, report)

    return {"md": md_name, "json": json_name}
