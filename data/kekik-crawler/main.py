import argparse
import asyncio
from pathlib import Path

from crawler import run
from presets import PRESETS
from core.search_engines import build_multi_query_urls


def parse_args():
    p = argparse.ArgumentParser(description="kekik-crawler")
    p.add_argument("--urls", nargs="+", help="Başlangıç URL listesi")
    p.add_argument("--queries", nargs="+", help="Arama sorguları (çoklu motor)")
    p.add_argument("--out", default="outputs/out.jsonl", help="Çıktı JSONL dosyası")
    p.add_argument("--max-pages", type=int, default=50)
    p.add_argument("--concurrency", type=int, default=10)
    p.add_argument("--per-domain-delay", type=float, default=0.35)
    p.add_argument("--plugins", default="plugins", help="Plugin dizini")
    p.add_argument("--cache", default="outputs/cache.sqlite3", help="SQLite cache dosyası")
    p.add_argument("--no-robots", action="store_true", help="robots.txt kontrolünü kapat")
    p.add_argument("--insecure", action="store_true", help="SSL doğrulamayı kapat (test amaçlı)")
    p.add_argument("--preset", choices=["person-research", "deep-research"], help="Hazır araştırma preset'i")
    p.add_argument("--mode", choices=["normal", "wide", "deep"], default="normal", help="Araştırma modu")
    p.add_argument("--checkpoint", default="outputs/checkpoint.json", help="Checkpoint dosyası")
    p.add_argument("--no-resume", action="store_true", help="Checkpoint'ten devam etme")
    p.add_argument("--report", default="outputs/report.json", help="Özet rapor dosyası")
    return p.parse_args()


def main():
    args = parse_args()

    if args.preset:
        p = PRESETS[args.preset]
        args.mode = p["mode"]
        args.max_pages = p["max_pages"]
        args.concurrency = p["concurrency"]
        if p.get("no_robots"):
            args.no_robots = True

    urls = list(args.urls or [])
    if args.queries:
        urls.extend(build_multi_query_urls(args.queries))
    if not urls:
        raise SystemExit("--urls veya --queries vermelisin")

    use_robots = not args.no_robots

    out_path = Path(args.out)
    report_path = Path(args.report)
    cache_path = Path(args.cache)
    checkpoint_path = Path(args.checkpoint)
    for p in [out_path, report_path, cache_path, checkpoint_path]:
        if p.parent:
            p.parent.mkdir(parents=True, exist_ok=True)

    asyncio.run(
        run(
            urls=urls,
            out_path=out_path,
            plugin_dir=Path(args.plugins),
            max_pages=args.max_pages,
            concurrency=args.concurrency,
            per_domain_delay=args.per_domain_delay,
            use_robots=use_robots,
            cache_path=cache_path,
            verify_ssl=not args.insecure,
            checkpoint_path=checkpoint_path,
            resume=not args.no_resume,
            mode=args.mode,
            report_path=report_path,
        )
    )
    print(f"Bitti. Çıktı: {args.out} | Rapor: {args.report}")


if __name__ == "__main__":
    main()
