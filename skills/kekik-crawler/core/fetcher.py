import asyncio
from collections import defaultdict
from time import monotonic
from urllib.parse import urlparse

from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from backends.scrapling_backend import fetch as scrapling_fetch


class ScraplingCrawler:
    def __init__(self, concurrency=6, per_domain_delay=0.35, verify_ssl=True):
        self.sem = asyncio.Semaphore(concurrency)
        self.per_domain_delay = per_domain_delay
        self.verify_ssl = verify_ssl
        self.last_hit = defaultdict(float)

    async def _respect_delay(self, domain: str):
        now = monotonic()
        wait = self.per_domain_delay - (now - self.last_hit[domain])
        if wait > 0:
            await asyncio.sleep(wait)
        self.last_hit[domain] = monotonic()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(0.3, 2.0), reraise=True)
    async def fetch_one(self, url: str):
        domain = (urlparse(url).hostname or "").lower()
        async with self.sem:
            await self._respect_delay(domain)
            return await asyncio.to_thread(
                scrapling_fetch,
                url,
                15.0,
                self.verify_ssl,
                {"User-Agent": "kekik-crawler/1.0"},
            )
