import argparse
import json
import sys

from numinous_api import (
    DEFAULT_BASE_URL,
    NuminousError,
    normalize_topics,
    predict_job,
)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Numinous forecast (query mode, x402): pass a natural-language question and get p in [0,1]."
    )
    p.add_argument("query", help="Natural-language forecasting question")
    p.add_argument(
        "--topics",
        default="",
        help='Optional topics (comma/space separated), e.g. "sports" or "earnings, general"',
    )
    args = p.parse_args()

    base_url = DEFAULT_BASE_URL
    topics = normalize_topics(args.topics)

    try:
        result = predict_job(
            base_url=base_url,
            forecaster_name="pool_based_miner_forecaster",
            title=None,
            description=None,
            cutoff_iso=None,
            topics=topics,
            query=args.query,
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
                    "parsed_fields": None,
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
        "parsed_fields": r.get("parsed_fields"),
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
