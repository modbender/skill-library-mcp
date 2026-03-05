from __future__ import annotations

import argparse
import sys

from _runtime import AdiRuntimeError, read_input_payload, validate_request_data


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate an ADI DecisionRequest from a JSON file or stdin."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a JSON DecisionRequest file, or '-' to read from stdin.",
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

        normalized = validate_request_data(payload)
        options = len(normalized.get("options", []))
        criteria = len(normalized.get("criteria", []))
        policy_name = normalized.get("policy_name", "balanced")
        print(
            f"valid DecisionRequest: options={options}, criteria={criteria}, policy={policy_name}, source={source}"
        )
        return 0
    except AdiRuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"error: unexpected failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
