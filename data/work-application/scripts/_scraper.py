"""
_scraper.py - Job scraper for the work-application skill.
Port of scripts/job-scraper/scraper.js from Puppeteer to Playwright Python.
Requires: playwright, playwright-stealth (optional, for anti-bot bypass).

Usage:
    import asyncio
    from _scraper import scrape_all, filter_jobs, deduplicate
    jobs = asyncio.run(scrape_all(config))
"""

import asyncio
import logging
import re
import unicodedata
from datetime import datetime, timedelta
from urllib.parse import urlencode

from playwright.async_api import async_playwright, Browser, BrowserContext

# Optional stealth plugin
try:
    from playwright_stealth import stealth_async
except ImportError:
    stealth_async = None

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Lowercase, NFD normalize, remove accents, keep alphanumeric only."""
    text = (text or "").lower()
    text = unicodedata.normalize("NFD", text)
    text = re.sub(r"[\u0300-\u036f]", "", text)  # strip combining diacriticals
    text = re.sub(r"[^a-z0-9]", "", text)
    return text.strip()


def _parse_relative_date(text: str) -> str:
    """Parse French relative dates to DD/MM/YYYY string.

    Handles: 'il y a X jours/semaines/mois/heures', "aujourd'hui", 'hier'.
    """
    now = datetime.now()
    lower = (text or "").lower()

    day_match = re.search(r"il y a (\d+)\s*jour", lower)
    week_match = re.search(r"il y a (\d+)\s*semaine", lower)
    month_match = re.search(r"il y a (\d+)\s*mois", lower)
    hour_match = re.search(r"il y a (\d+)\s*heure", lower)

    if day_match:
        dt = now - timedelta(days=int(day_match.group(1)))
    elif week_match:
        dt = now - timedelta(weeks=int(week_match.group(1)))
    elif month_match:
        months = int(month_match.group(1))
        month = now.month - months
        year = now.year
        while month < 1:
            month += 12
            year -= 1
        dt = now.replace(year=year, month=month)
    elif hour_match or "aujourd'hui" in lower or "aujourd\u2019hui" in lower:
        dt = now
    elif "hier" in lower:
        dt = now - timedelta(days=1)
    else:
        return ""

    return dt.strftime("%d/%m/%Y")


# ---------------------------------------------------------------------------
# JobScraper
# ---------------------------------------------------------------------------

class JobScraper:
    """Async job scraper supporting 5 French platforms."""

    def __init__(self, config: dict):
        self.config = config
        self.rate_limit = config.get("scraper", {}).get("rate_limit_ms", 2000) / 1000
        self.scroll_timeout = config.get("scraper", {}).get("scroll_timeout_ms", 5000) / 1000

    # ------------------------------------------------------------------
    # Browser helpers
    # ------------------------------------------------------------------

    async def _launch_browser(self) -> tuple[Browser, BrowserContext]:
        """Launch Chromium headless with stealth (if available)."""
        self._pw = await async_playwright().start()
        browser = await self._pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
        )
        return browser, context

    async def _auto_scroll(self, page) -> None:
        """Scroll 500px increments, stop at scrollHeight or 5000px."""
        await page.evaluate(
            """async () => {
                await new Promise((resolve) => {
                    let totalHeight = 0;
                    const distance = 500;
                    const timer = setInterval(() => {
                        const scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;
                        if (totalHeight >= scrollHeight || totalHeight > 5000) {
                            clearInterval(timer);
                            resolve();
                        }
                    }, 200);
                });
            }"""
        )
        await asyncio.sleep(1)

    async def _accept_cookies(self, page) -> None:
        """Try common cookie consent selectors, click first found."""
        selectors = [
            "#onetrust-accept-btn-handler",
            "#didomi-notice-agree-button",
            'button[id*="accept"]',
            'button[class*="accept"]',
            '[data-testid="cookie-accept"]',
            '[data-cky-tag="accept-button"]',
            ".cky-btn-accept",
        ]
        for sel in selectors:
            try:
                btn = page.locator(sel).first
                if await btn.is_visible(timeout=500):
                    await btn.click()
                    await asyncio.sleep(1)
                    return
            except Exception:
                continue

    # ------------------------------------------------------------------
    # URL builders
    # ------------------------------------------------------------------

    def _build_url(self, platform: str, params: dict) -> str:
        """Build search URL for *platform* with *params*."""

        if platform == "free-work":
            base = "https://www.free-work.com/fr/tech-it/jobs"
            qp: dict[str, str] = {}
            if params.get("query"):
                qp["query"] = params["query"]
            contracts = params.get("contracts")
            if contracts == "contractor":
                qp["contracts"] = "contractor"
            elif contracts == "cdi":
                qp["contracts"] = "worker"
            qp["freshness"] = "7"
            return f"{base}?{urlencode(qp)}"

        if platform == "wttj":
            base = "https://www.welcometothejungle.com/fr/jobs"
            qp = {}
            if params.get("query"):
                qp["query"] = params["query"]
            qp["refinementList[offices.country_code][]"] = "FR"
            if params.get("location"):
                qp["aroundLatLng"] = "48.8566,2.3522"
                qp["aroundRadius"] = str((params.get("radius") or 30) * 1000)
            return f"{base}?{urlencode(qp)}"

        if platform == "apec":
            base = "https://www.apec.fr/candidat/recherche-emploi.html/emploi"
            qp = {}
            if params.get("query"):
                qp["motsCles"] = params["query"]
            location = params.get("location", "")
            if location == "Paris":
                qp["lieux"] = "75"
            elif location == "IDF":
                # Multiple lieux values - append manually after urlencode
                pass
            url = f"{base}?{urlencode(qp)}"
            if location == "IDF":
                url += "&lieux=75&lieux=91&lieux=78"
            return url

        if platform == "hellowork":
            base = "https://www.hellowork.com/fr-fr/emploi/recherche.html"
            qp = {}
            if params.get("query"):
                qp["k"] = params["query"]
            if params.get("location"):
                qp["l"] = params["location"]
            return f"{base}?{urlencode(qp)}"

        if platform == "lehibou":
            base = "https://www.lehibou.com/recherche/annonces"
            qp = {
                "countryId": "96dfb63e-9d8f-4720-a9cd-0aa660525aed",
                "cityId": params.get(
                    "cityId", "a1a5262e-1a59-4280-9560-99476055d4ae"
                ),
                "radius": str(params.get("radius", "30")),
            }
            if params.get("query"):
                qp["titles"] = params["query"]
            return f"{base}?{urlencode(qp)}"

        raise ValueError(f"Unknown platform: {platform}")

    # ------------------------------------------------------------------
    # Platform scrapers
    # ------------------------------------------------------------------

    async def _scrape_free_work(self, page, params: dict) -> list[dict]:
        """Scrape Free-Work job listings."""
        try:
            await page.wait_for_selector(
                'a[href*="/job-mission/"]', timeout=15000
            )
        except Exception:
            pass

        await asyncio.sleep(3)
        await self._auto_scroll(page)

        jobs = await page.evaluate(
            """() => {
                const jobs = [];
                const cards = document.querySelectorAll('div.mb-4.relative.rounded-lg');

                cards.forEach(card => {
                    try {
                        const link = card.querySelector('a[href*="/job-mission/"]');
                        if (!link) return;

                        const fullText = card.innerText;
                        const lines = fullText.split('\\n').map(l => l.trim()).filter(l => l);

                        const isFreelance = lines.includes('Freelance') || lines.includes('Mission freelance');
                        const isCDI = lines.includes('CDI') || lines.some(l => l.includes('Offre d'));

                        let title = '';
                        const titleIdx = lines.findIndex(l =>
                            l === 'Mission freelance' ||
                            l.includes('Offre d')
                        );
                        if (titleIdx >= 0 && lines[titleIdx + 1]) {
                            title = lines[titleIdx + 1];
                        } else {
                            title = lines.find(l => l.length > 10 && l.length < 80 && !l.includes('Publi\\u00e9e') && !l.includes('\\u20ac')) || lines[0];
                        }

                        let date = '';
                        const dateLine = lines.find(l => l.startsWith('Publi\\u00e9e le') || l.includes('Publi\\u00e9e') || l.includes('il y a'));
                        if (dateLine) {
                            const absDateMatch = dateLine.match(/(\\d{2}\\/\\d{2}\\/\\d{4})/);
                            if (absDateMatch) {
                                date = absDateMatch[1];
                            } else {
                                const d = new Date();
                                const dayMatch = dateLine.match(/il y a (\\d+)\\s*jour/i);
                                const weekMatch = dateLine.match(/il y a (\\d+)\\s*semaine/i);
                                const monthMatch = dateLine.match(/il y a (\\d+)\\s*mois/i);
                                const hourMatch = dateLine.match(/il y a (\\d+)\\s*heure/i);

                                if (dayMatch) {
                                    d.setDate(d.getDate() - parseInt(dayMatch[1]));
                                    date = d.toLocaleDateString('fr-FR');
                                } else if (weekMatch) {
                                    d.setDate(d.getDate() - parseInt(weekMatch[1]) * 7);
                                    date = d.toLocaleDateString('fr-FR');
                                } else if (monthMatch) {
                                    d.setMonth(d.getMonth() - parseInt(monthMatch[1]));
                                    date = d.toLocaleDateString('fr-FR');
                                } else if (hourMatch || dateLine.toLowerCase().includes("aujourd'hui")) {
                                    date = d.toLocaleDateString('fr-FR');
                                } else if (dateLine.toLowerCase().includes('hier')) {
                                    d.setDate(d.getDate() - 1);
                                    date = d.toLocaleDateString('fr-FR');
                                }
                            }
                        }

                        const tjmLine = lines.find(l => /^\\d+[-\\u2013]?\\d*\\s*\\u20ac/.test(l));
                        const tjm = tjmLine || '-';

                        const locationLine = lines.find(l =>
                            l.includes('France') ||
                            l.includes('Paris') ||
                            l.includes('\\u00cele-de-France') ||
                            l.includes('Remote')
                        );
                        const location = locationLine || '-';

                        const companyEl = card.querySelector('img[alt]:not([alt=""])');
                        const company = companyEl?.alt || '-';

                        if (title && link.href) {
                            jobs.push({
                                title: title,
                                company: company,
                                location: location,
                                salary: tjm,
                                type: isFreelance ? 'Freelance' : (isCDI ? 'CDI' : '-'),
                                url: link.href,
                                date: date,
                                platform: 'Free-Work'
                            });
                        }
                    } catch (e) {
                        // skip card
                    }
                });

                return jobs;
            }"""
        )
        return jobs or []

    async def _scrape_wttj(self, page, params: dict) -> list[dict]:
        """Scrape Welcome to the Jungle job listings."""
        try:
            await page.wait_for_selector(
                'li[data-testid="search-results-list-item-wrapper"]',
                timeout=15000,
            )
        except Exception:
            pass

        await asyncio.sleep(2)
        await self._auto_scroll(page)

        jobs = await page.evaluate(
            """() => {
                const jobs = [];
                const cards = document.querySelectorAll('li[data-testid="search-results-list-item-wrapper"]');

                cards.forEach(card => {
                    try {
                        const link = card.querySelector('a[href*="/companies/"][href*="/jobs/"]');
                        if (!link) return;

                        const text = card.innerText;
                        const lines = text.split('\\n').map(l => l.trim()).filter(l => l);

                        let titleIdx = lines.findIndex(l => l === 'Recrute activement !');
                        let title = titleIdx !== -1 ? lines[titleIdx + 1] : lines[0];

                        const imgAlt = card.querySelector('img[alt]')?.alt;
                        let company = imgAlt || lines[titleIdx !== -1 ? titleIdx + 2 : 1] || '-';

                        let location = '-';
                        let contractType = 'CDI';
                        const contractTypes = ['CDI', 'CDD', 'Stage', 'Alternance', 'Freelance', 'Int\\u00e9rim'];
                        const knownCities = ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Bordeaux', 'Nantes', 'Lille', 'Nice', 'Boulogne', 'Montrouge', 'Issy', 'Levallois', 'Neuilly', 'Puteaux', 'La D\\u00e9fense', 'Massy', 'Saclay', '\\u00c9vry', 'Palaiseau'];

                        for (const line of lines) {
                            for (const ct of contractTypes) {
                                if (line === ct || line.startsWith(ct + ' ')) {
                                    contractType = ct;
                                }
                            }
                            for (const city of knownCities) {
                                if (line.includes(city)) {
                                    location = line;
                                    break;
                                }
                            }
                        }

                        const hasTeletravail = lines.some(l => l.includes('T\\u00e9l\\u00e9travail') || l.includes('t\\u00e9l\\u00e9travail'));
                        if (hasTeletravail && location === '-') {
                            location = 'T\\u00e9l\\u00e9travail';
                        }

                        let date = '-';
                        for (const line of lines) {
                            const dayMatch = line.match(/il y a (\\d+)\\s*jour/i);
                            const weekMatch = line.match(/il y a (\\d+)\\s*semaine/i);
                            const monthMatch = line.match(/il y a (\\d+)\\s*mois/i);
                            const hourMatch = line.match(/il y a (\\d+)\\s*heure/i);

                            const d = new Date();
                            if (dayMatch) {
                                d.setDate(d.getDate() - parseInt(dayMatch[1]));
                                date = d.toLocaleDateString('fr-FR');
                                break;
                            } else if (weekMatch) {
                                d.setDate(d.getDate() - parseInt(weekMatch[1]) * 7);
                                date = d.toLocaleDateString('fr-FR');
                                break;
                            } else if (monthMatch) {
                                d.setMonth(d.getMonth() - parseInt(monthMatch[1]));
                                date = d.toLocaleDateString('fr-FR');
                                break;
                            } else if (hourMatch || line.toLowerCase().includes("aujourd'hui")) {
                                date = d.toLocaleDateString('fr-FR');
                                break;
                            } else if (line.toLowerCase().includes('hier')) {
                                d.setDate(d.getDate() - 1);
                                date = d.toLocaleDateString('fr-FR');
                                break;
                            }
                        }

                        const fullUrl = link.href.startsWith('http') ? link.href : 'https://www.welcometothejungle.com' + link.getAttribute('href');

                        if (title && title !== 'Recrute activement !') {
                            jobs.push({
                                title: title,
                                company: company,
                                location: location,
                                salary: '-',
                                type: contractType,
                                url: fullUrl,
                                date: date,
                                platform: 'WTTJ'
                            });
                        }
                    } catch (e) {
                        // skip card
                    }
                });

                return jobs;
            }"""
        )
        return jobs or []

    async def _scrape_apec(self, page, params: dict) -> list[dict]:
        """Scrape APEC job listings."""
        # Accept cookies (APEC uses OneTrust)
        try:
            btn = page.locator("#onetrust-accept-btn-handler")
            if await btn.is_visible(timeout=3000):
                await btn.click()
                await asyncio.sleep(1)
        except Exception:
            pass

        try:
            await page.wait_for_selector(".card-offer", timeout=15000)
        except Exception:
            pass

        await asyncio.sleep(2)
        await self._auto_scroll(page)

        jobs = await page.evaluate(
            """() => {
                const jobs = [];
                const links = document.querySelectorAll('a[href*="/detail-offre/"]');

                links.forEach(link => {
                    try {
                        const card = link.closest('.card-offer') || link.parentElement;
                        const text = card?.innerText || '';
                        const lines = text.split('\\n').map(l => l.trim()).filter(l => l);

                        const company = lines[0] || '-';
                        const title = lines[1] || '-';
                        const salaryLine = lines.find(l => l.includes('k\\u20ac') || l.includes('K\\u20ac'));
                        const locationLine = lines.find(l => l.includes(' - 75') || l.includes('Paris') || l.includes('\\u00cele-de-France'));
                        const dateLine = lines.find(l => /\\d{2}\\/\\d{2}\\/\\d{4}/.test(l));
                        const contractLine = lines.find(l => l === 'CDI' || l === 'CDD');

                        const cleanUrl = link.href.split('?')[0];

                        if (title && title !== '-') {
                            jobs.push({
                                title: title,
                                company: company,
                                location: locationLine || 'Paris',
                                salary: salaryLine || '-',
                                type: contractLine || 'CDI',
                                url: cleanUrl,
                                date: dateLine || new Date().toLocaleDateString('fr-FR'),
                                platform: 'Apec'
                            });
                        }
                    } catch (e) {}
                });

                return jobs;
            }"""
        )
        return jobs or []

    async def _scrape_hellowork(self, page, params: dict) -> list[dict]:
        """Scrape HelloWork job listings."""
        # Accept cookies (HelloWork uses Didomi)
        try:
            btn = page.locator("#didomi-notice-agree-button")
            if await btn.is_visible(timeout=3000):
                await btn.click()
                await asyncio.sleep(1)
        except Exception:
            pass

        try:
            await page.wait_for_selector('a[href*="/emplois/"]', timeout=15000)
        except Exception:
            pass

        await asyncio.sleep(2)
        await self._auto_scroll(page)

        jobs = await page.evaluate(
            """() => {
                const jobs = [];
                const links = document.querySelectorAll('a[href*="/emplois/"]');

                links.forEach(link => {
                    try {
                        if (!link.href.match(/\\/emplois\\/\\d+\\.html/)) return;

                        const card = link.closest('li, article, div') || link.parentElement;
                        const text = card?.innerText || link.innerText;
                        const lines = text.split('\\n').map(l => l.trim()).filter(l => l);

                        const title = lines[0] || '-';
                        const company = lines[1] || '-';
                        const location = lines[2] || '-';
                        const contractType = lines.find(l => l === 'CDI' || l === 'CDD' || l === 'Freelance') || 'CDI';
                        const salaryLine = lines.find(l => l.includes('\\u20ac / an') || l.includes('\\u20ac/an'));
                        const dateLine = lines.find(l => l.includes('il y a') || l.includes('jour'));

                        if (title && title !== '-' && title !== "Voir l'offre") {
                            jobs.push({
                                title: title,
                                company: company,
                                location: location,
                                salary: salaryLine || '-',
                                type: contractType,
                                url: link.href,
                                date: dateLine || new Date().toLocaleDateString('fr-FR'),
                                platform: 'HelloWork'
                            });
                        }
                    } catch (e) {}
                });

                return jobs;
            }"""
        )
        return jobs or []

    async def _scrape_lehibou(self, page, params: dict) -> list[dict]:
        """Scrape LeHibou job listings."""
        # LeHibou needs extra time (Cloudflare + SPA)
        await asyncio.sleep(3)

        try:
            await page.wait_for_selector('a[href*="/annonce/"]', timeout=15000)
        except Exception:
            pass

        await asyncio.sleep(2)

        jobs = await page.evaluate(
            """() => {
                const jobs = [];
                const links = document.querySelectorAll('a[href*="/annonce/"]');

                links.forEach(link => {
                    try {
                        const card = link.closest('div') || link.parentElement;
                        const text = card?.innerText || link.innerText;
                        const lines = text.split('\\n').map(l => l.trim()).filter(l => l);

                        const title = lines[0] || '';

                        if (!title || title.length < 5 || title.includes("S'inscrire") || title.includes('Se connecter')) {
                            return;
                        }

                        const rateLine = lines.find(l => l.includes('\\u20ac/jour'));
                        const rateMatch = rateLine?.match(/(\\d+)\\s*\\u20ac\\/jour/);
                        const rate = rateMatch ? rateMatch[1] + ' \\u20ac/jour' : '-';

                        const knownCities = ['Paris', 'Massy', '\\u00c9vry', 'Dourdan', 'Villiers', 'Palaiseau', 'Saclay', 'Orsay', 'Versailles', 'Chartres', 'Rambouillet'];
                        let location = '-';
                        for (const city of knownCities) {
                            const cityLine = lines.find(l => l.toLowerCase().includes(city.toLowerCase()) && l.length < 50);
                            if (cityLine) {
                                location = cityLine;
                                break;
                            }
                        }

                        const durationLine = lines.find(l => l.includes('mois') || l.includes('semaine'));

                        const ageLine = lines.find(l => l.includes('Publi\\u00e9e il y a'));
                        const ageMatch = ageLine?.match(/(\\d+)\\s*(jour|mois|semaine)/);
                        let date = new Date().toLocaleDateString('fr-FR');
                        if (ageMatch) {
                            const num = parseInt(ageMatch[1]);
                            const unit = ageMatch[2];
                            const d = new Date();
                            if (unit.startsWith('jour')) d.setDate(d.getDate() - num);
                            if (unit.startsWith('semaine')) d.setDate(d.getDate() - num * 7);
                            if (unit.startsWith('mois')) d.setMonth(d.getMonth() - num);
                            date = d.toLocaleDateString('fr-FR');
                        }

                        const type = 'Freelance';

                        const isLeHibou = lines.some(l => l.includes('Mission LeHibou'));
                        const company = isLeHibou ? 'LeHibou' : 'Externe';

                        if (title && link.href) {
                            jobs.push({
                                title: title,
                                company: company,
                                location: location,
                                salary: rate,
                                type: type,
                                url: link.href,
                                date: date,
                                platform: 'LeHibou'
                            });
                        }
                    } catch (e) {}
                });

                return jobs;
            }"""
        )
        return jobs or []

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    _PLATFORM_SCRAPERS = {
        "free-work": "_scrape_free_work",
        "wttj": "_scrape_wttj",
        "apec": "_scrape_apec",
        "hellowork": "_scrape_hellowork",
        "lehibou": "_scrape_lehibou",
    }

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    async def scrape_all(self) -> list[dict]:
        """Launch browser, run every search defined in config, return jobs."""
        browser, context = await self._launch_browser()
        all_jobs: list[dict] = []

        try:
            for search in self.config.get("searches", []):
                platform = search.get("platform", "")
                params = search.get("params", {})
                name = search.get("name", platform)

                scraper_method_name = self._PLATFORM_SCRAPERS.get(platform)
                if scraper_method_name is None:
                    logger.warning("Platform '%s' not supported, skipping.", platform)
                    continue

                url = self._build_url(platform, params)
                logger.info("Search: %s  |  URL: %s", name, url)

                try:
                    page = await context.new_page()

                    # Apply stealth if available
                    if stealth_async is not None:
                        await stealth_async(page)

                    # Special handling for LeHibou (Cloudflare protection)
                    if platform == "lehibou":
                        await page.goto(
                            "https://www.lehibou.com",
                            wait_until="networkidle",
                            timeout=45000,
                        )
                        await asyncio.sleep(3)
                        # Accept cookies on homepage
                        try:
                            cookie_btn = page.locator(
                                '[data-cky-tag="accept-button"], .cky-btn-accept'
                            ).first
                            if await cookie_btn.is_visible(timeout=2000):
                                await cookie_btn.click()
                                await asyncio.sleep(1)
                        except Exception:
                            pass

                    # Navigate to search URL
                    await page.goto(url, wait_until="networkidle", timeout=45000)

                    # Generic cookie acceptance
                    await self._accept_cookies(page)
                    await asyncio.sleep(1.5)

                    # Run the platform-specific scraper
                    scraper_method = getattr(self, scraper_method_name)
                    jobs = await scraper_method(page, params)
                    logger.info("  -> %d raw jobs from %s", len(jobs), platform)

                    all_jobs.extend(jobs)
                    await page.close()

                except Exception as exc:
                    logger.error("  Error on %s: %s", name, exc)

                # Rate limit between searches
                await asyncio.sleep(self.rate_limit)

        finally:
            await context.close()
            await browser.close()
            await self._pw.stop()

        return all_jobs


# ---------------------------------------------------------------------------
# Module-level functions
# ---------------------------------------------------------------------------

def filter_jobs(
    jobs: list[dict],
    filters: dict,
    already_applied: set | None = None,
) -> list[dict]:
    """Filter jobs by date, location, TJM and salary.

    Port of filterJobs from scraper.js.

    *filters* keys used:
        maxAge (int, days), locations (list[str]),
        excludeLocations (list[str]), minTJM (int), minSalary (int).
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    max_age = filters.get("maxAge", 7)
    cutoff = today - timedelta(days=max_age)

    locations = [loc.lower() for loc in filters.get("locations", [])]
    exclude_locations = [loc.lower() for loc in filters.get("excludeLocations", [])]
    min_tjm = filters.get("minTJM")
    min_salary = filters.get("minSalary")

    result: list[dict] = []

    for job in jobs:
        # --- Date filter ---
        date_str = job.get("date", "")
        if date_str and date_str != "-":
            parts = date_str.split("/")
            if len(parts) == 3:
                try:
                    job_date = datetime(
                        int(parts[2]), int(parts[1]), int(parts[0])
                    )
                    if job_date < cutoff:
                        continue
                except (ValueError, IndexError):
                    pass

        # --- Location exclusion ---
        job_loc = (job.get("location") or "").lower()
        if exclude_locations:
            if any(loc in job_loc for loc in exclude_locations):
                continue

        # --- Location inclusion ---
        if locations and job.get("location", "-") != "-":
            matches_location = any(loc in job_loc for loc in locations)
            is_remote = "remote" in job_loc or "télétravail" in job_loc or "teletravail" in job_loc
            is_idf = "île-de-france" in job_loc or "ile-de-france" in job_loc or "idf" in job_loc
            if not matches_location and not is_remote and not is_idf:
                continue

        # --- TJM filter (Freelance) ---
        if job.get("type") == "Freelance" and min_tjm and job.get("salary", "-") != "-":
            tjm_match = re.search(r"(\d+)", job["salary"])
            if tjm_match:
                tjm = int(tjm_match.group(1))
                if tjm < min_tjm and tjm > 100:
                    continue

        # --- Salary filter (CDI) ---
        if job.get("type") == "CDI" and min_salary and job.get("salary", "-") != "-":
            sal_match = re.search(r"(\d+)", job["salary"])
            if sal_match:
                sal = int(sal_match.group(1))
                # Salary often expressed in k euro on Apec, e.g. "55k"
                if sal < 1000:
                    sal *= 1000
                if sal < min_salary:
                    continue

        result.append(job)

    return result


def deduplicate(
    jobs: list[dict],
    already_applied: set | None = None,
) -> list[dict]:
    """Deduplicate jobs by URL and normalized title+company.

    Port of deduplicateJobs from scraper.js.

    *already_applied* is an optional set of "company:title" keys (normalized).
    """
    already_applied = already_applied or set()

    seen_urls: set[str] = set()
    seen_keys: set[str] = set()
    excluded = {"duplicates": 0, "applied": 0}

    result: list[dict] = []

    for job in jobs:
        url = job.get("url", "")
        # 1. Check URL
        if url in seen_urls:
            excluded["duplicates"] += 1
            continue
        seen_urls.add(url)

        # 2. Check title+company
        key = f"{_normalize(job.get('company', ''))}:{_normalize(job.get('title', ''))}"
        if key in seen_keys:
            excluded["duplicates"] += 1
            continue
        seen_keys.add(key)

        # 3. Exact match against already applied
        if key in already_applied:
            excluded["applied"] += 1
            continue

        # 4. Fuzzy match against already applied (partial)
        is_applied = False
        job_company = _normalize(job.get("company", ""))
        job_title = _normalize(job.get("title", ""))
        for applied_key in already_applied:
            parts = applied_key.split(":", 1)
            if len(parts) != 2:
                continue
            applied_company, applied_title = parts
            if applied_company and (
                job_company in applied_company or applied_company in job_company
            ):
                if applied_title and (
                    job_title in applied_title or applied_title in job_title
                ):
                    is_applied = True
                    break

        if is_applied:
            excluded["applied"] += 1
            continue

        result.append(job)

    if excluded["duplicates"] or excluded["applied"]:
        logger.info(
            "Dedup: %d duplicates, %d already applied",
            excluded["duplicates"],
            excluded["applied"],
        )

    return result


# ---------------------------------------------------------------------------
# Convenience wrapper
# ---------------------------------------------------------------------------

async def scrape_all(config: dict) -> list[dict]:
    """Create a JobScraper and run scrape_all()."""
    scraper = JobScraper(config)
    return await scraper.scrape_all()
