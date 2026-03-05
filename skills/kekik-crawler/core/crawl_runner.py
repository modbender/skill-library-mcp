import asyncio
from pathlib import Path
from urllib.parse import urlparse

import orjson
from selectolax.parser import HTMLParser

from core.checkpoint import load_checkpoint, save_checkpoint
from core.errors import classify_error, classify_status
from core.fetcher import ScraplingCrawler
from core.metrics import Metrics
from core.mode import apply_mode_limits, link_limit_for_mode
from core.plugin_manager import PluginManager
from core.robots import robots_allow
from core.storage import CacheDB
from core.urlutils import canonicalize


class CrawlRunner:
    def __init__(
        self,
        urls,
        out_path: Path,
        plugin_dir: Path,
        max_pages=80,
        concurrency=6,
        per_domain_delay=0.35,
        use_robots=True,
        cache_path: Path = Path("outputs/cache.sqlite3"),
        verify_ssl=True,
        checkpoint_path: Path = Path("outputs/checkpoint.json"),
        resume=True,
        mode="normal",
        report_path: Path = Path("outputs/report.json"),
    ):
        max_pages, per_domain_delay = apply_mode_limits(mode, max_pages, per_domain_delay)

        self.max_pages = max_pages
        self.concurrency = concurrency
        self.use_robots = use_robots
        self.verify_ssl = verify_ssl
        self.checkpoint_path = checkpoint_path
        self.resume = resume
        self.mode = mode
        self.report_path = report_path

        self.crawler = ScraplingCrawler(concurrency=concurrency, per_domain_delay=per_domain_delay, verify_ssl=verify_ssl)
        self.plugins = PluginManager(plugin_dir)
        self.cache = CacheDB(cache_path)
        self.metrics = Metrics()
        self.ua = "kekik-crawler/1.0"

        self.queue = [canonicalize(u) for u in urls]
        self.seen = set()

        self.out_path = out_path
        self.link_limit = link_limit_for_mode(mode)

    def _restore_checkpoint(self):
        if not self.resume:
            return
        queue, seen = load_checkpoint(self.checkpoint_path)
        if queue is not None and seen is not None:
            self.queue, self.seen = queue, seen

    async def _build_batch(self):
        batch = []
        while self.queue and len(batch) < self.concurrency and len(self.seen) + len(batch) < self.max_pages:
            url = canonicalize(self.queue.pop(0))
            if url in self.seen:
                continue

            domain = (urlparse(url).hostname or "").lower()
            if self.use_robots and domain not in PluginManager.SEARCH_DOMAINS:
                if not await robots_allow(url, self.ua, self.verify_ssl):
                    batch.append((url, None, "blocked_by_robots"))
                    self.seen.add(url)
                    continue

            self.seen.add(url)
            batch.append((url, domain, None))
        return batch

    def _enqueue_links(self, links):
        for link in links[: self.link_limit]:
            c = canonicalize(link)
            if c.startswith("http") and c not in self.seen:
                self.queue.append(c)

    def _write_jsonl(self, out, payload: dict):
        out.write(orjson.dumps(payload) + b"\n")

    async def _process_results(self, out, batch, results):
        for (req_url, _domain, pre_error), result in zip(batch, results):
            domain = (urlparse(req_url).hostname or "").lower()

            if pre_error:
                self._write_jsonl(out, {"url": req_url, "ok": False, "error": pre_error})
                self.metrics.add_fail(domain, pre_error)
                continue

            if isinstance(result, Exception):
                code = classify_error(result)
                self._write_jsonl(out, {"url": req_url, "ok": False, "error": code, "detail": str(result)})
                self.metrics.add_fail(domain, code)
                continue

            final_url, html, status, _meta = result
            final_url = canonicalize(final_url)
            domain = (urlparse(final_url).hostname or "").lower()

            if status >= 400:
                code = classify_status(status)
                self._write_jsonl(out, {"url": final_url, "ok": False, "error": code})
                self.metrics.add_fail(domain, code)
                continue

            self.cache.put(final_url, status, html.encode("utf-8", "ignore"))
            tree = HTMLParser(html)
            data = self.plugins.for_domain(domain).extract(final_url, html, tree)
            self._write_jsonl(out, {"url": final_url, "ok": True, "domain": domain, "data": data})
            self.metrics.add_ok(domain)
            self._enqueue_links(data.get("links", []))

    async def run(self):
        self._restore_checkpoint()

        with self.out_path.open("wb") as out:
            loops = 0
            while self.queue and len(self.seen) < self.max_pages:
                loops += 1
                batch = await self._build_batch()
                if not batch:
                    continue

                fetch_tasks = [self.crawler.fetch_one(url) for (url, _domain, pre_error) in batch if not pre_error]
                fetched = await asyncio.gather(*fetch_tasks, return_exceptions=True) if fetch_tasks else []

                # pre_error olanları da eski sırada koruyarak sonuç listesine yerleştir
                merged_results = []
                idx = 0
                for _url, _domain, pre_error in batch:
                    if pre_error:
                        merged_results.append(None)
                    else:
                        merged_results.append(fetched[idx])
                        idx += 1

                await self._process_results(out, batch, merged_results)

                if loops % 2 == 0:
                    save_checkpoint(self.checkpoint_path, self.queue, self.seen)

        save_checkpoint(self.checkpoint_path, self.queue, self.seen)
        self.report_path.write_bytes(orjson.dumps(self.metrics.summary()))


async def run(**kwargs):
    runner = CrawlRunner(**kwargs)
    await runner.run()
