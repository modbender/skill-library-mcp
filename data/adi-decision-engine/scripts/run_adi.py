from __future__ import annotations

import argparse
import sys
from typing import Any

from _runtime import AdiRuntimeError, read_input_payload, run_request_data, validate_request_data, write_json


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and execute an ADI DecisionRequest from a JSON file or stdin."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a JSON DecisionRequest file, or '-' to read from stdin.",
    )
    parser.add_argument(
        "--policy",
        default=None,
        help="Optional policy override: balanced, risk_averse, or exploratory.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        source, payload = read_input_payload(args.input)
        if not isinstance(payload, dict):
            raise AdiRuntimeError(
                f"Expected a JSON object in {source}; received {type(payload).__name__}."
            )

        validate_request_data(payload)
        result: dict[str, Any] = run_request_data(payload, policy_override=args.policy)
        write_json(result)
        return 0
    except AdiRuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"error: unexpected failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
