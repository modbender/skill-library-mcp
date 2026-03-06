import argparse
import json
import sys

from numinous_api import (
    DEFAULT_BASE_URL,
    NuminousError,
    normalize_topics,
    parse_cutoff_iso,
    predict_job,
)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Numinous forecast (event mode, x402): pass title/description/cutoff and get p in [0,1]."
    )
    p.add_argument(
        "--title", required=True, help="Binary event title phrased as a yes/no question"
    )
    p.add_argument(
        "--description", required=True, help="Event description / resolution context"
    )
    p.add_argument(
        "--cutoff",
        required=True,
        help='ISO datetime when the event resolves/evaluates by (e.g. "2026-12-31T23:59:59Z")',
    )
    p.add_argument(
        "--topics",
        default="",
        help='Optional topics (comma/space separated), e.g. "sports" or "earnings, general"',
    )
    args = p.parse_args()

    base_url = DEFAULT_BASE_URL
    topics = normalize_topics(args.topics)
    cutoff_iso = parse_cutoff_iso(args.cutoff)

    try:
        result = predict_job(
            base_url=base_url,
            forecaster_name="pool_based_miner_forecaster",
            title=args.title,
            description=args.description,
            cutoff_iso=cutoff_iso,
            topics=topics,
            query=None,
        )
    except (NuminousError, ValueError) as e:
        print(
            json.dumps(
                {
                    "ok": False,
                    "prediction": None,
                    "forecaster_name": None,
                    "forecasted_at": None,
                    "metadata": None,
                    "error": str(e),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 2

    job = (result or {}).get("job") or {}
    r = job.get("result") or {}
    out = {
        "ok": bool(result.get("ok")),
        "prediction": r.get("prediction"),
        "forecaster_name": r.get("forecaster_name"),
        "forecasted_at": r.get("forecasted_at"),
        "metadata": r.get("metadata"),
        "error": result.get("error"),
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if out["ok"] else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise SystemExit(130)
