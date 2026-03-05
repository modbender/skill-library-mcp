from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable, List, Sequence


def _get_api_key(cli_value: str | None) -> str:
    if cli_value:
        return cli_value
    api_key = os.getenv("POE_API_KEY")
    if api_key:
        return api_key
    return ""


def _upload_files(file_paths: Sequence[str], api_key: str):
    import importlib

    fp = importlib.import_module("fastapi_poe")

    attachments: List[object] = []
    for path in file_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        with open(path, "rb") as handle:
            attachment = fp.upload_file_sync(handle, api_key=api_key)
        attachments.append(attachment)
    return attachments


def _build_response(
    messages: Iterable[object],
    model_id: str,
    api_key: str,
):
    import importlib

    fp = importlib.import_module("fastapi_poe")

    text_parts: List[str] = []
    attachments: List[object] = []
    for partial in fp.get_bot_response_sync(
        messages=list(messages),
        bot_name=model_id,
        api_key=api_key,
    ):
        if getattr(partial, "text", None):
            text_parts.append(partial.text)
        if getattr(partial, "attachment", None):
            attachments.append(partial.attachment)
    return "".join(text_parts).strip(), attachments


def main() -> int:
    parser = argparse.ArgumentParser(description="Poe model client")
    parser.add_argument("--message", required=True, help="User message to send")
    parser.add_argument("--file", action="append", default=[], help="Path to upload")
    parser.add_argument(
        "--model-id",
        required=True,
        help="Concrete model id (e.g. Gemini-2.5-Pro)",
    )
    parser.add_argument(
        "--api-key",
        help="Poe API key (overrides POE_API_KEY env var)",
    )
    args = parser.parse_args()

    api_key = _get_api_key(args.api_key)
    if not api_key:
        print("Missing Poe API key. Provide --api-key or set POE_API_KEY.")
        return 1

    attachments = _upload_files(args.file, api_key) if args.file else []
    import importlib

    fp = importlib.import_module("fastapi_poe")

    user_message = fp.ProtocolMessage(
        role="user",
        content=args.message,
        attachments=attachments,
    )

    response_text, response_attachments = _build_response(
        messages=[user_message],
        model_id=args.model_id,
        api_key=api_key,
    )

    print(f"Model used: {args.model_id}\n")
    if response_text:
        print(response_text)
    else:
        print("(No response text returned)")

    if response_attachments:
        print("\nAttachments:")
        for attachment in response_attachments:
            name = getattr(attachment, "name", "unknown")
            content_type = getattr(attachment, "content_type", "unknown")
            url = getattr(attachment, "url", "")
            print(f"- {name} ({content_type}) {url}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
