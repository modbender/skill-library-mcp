"""
DeepRead Form Fill — Python Reference Implementation

Upload a PDF form + JSON data → get back a filled PDF.

Only contacts: api.deepread.tech
Requires: DEEPREAD_API_KEY environment variable
"""

import json
import os
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

API_BASE = "https://api.deepread.tech"


def get_api_key() -> str:
    """Read the API key from the DEEPREAD_API_KEY environment variable."""
    key = os.environ.get("DEEPREAD_API_KEY")
    if not key:
        print("Error: DEEPREAD_API_KEY environment variable is not set.", file=sys.stderr)
        print("Get a free key at https://www.deepread.tech/dashboard", file=sys.stderr)
        sys.exit(1)
    return key


def submit_form_fill(
    pdf_path: str,
    form_fields: dict,
    api_key: str,
    webhook_url: str | None = None,
    idempotency_key: str | None = None,
) -> dict:
    """Submit a PDF form for filling.

    POST /v1/form-fill (multipart/form-data)

    Args:
        pdf_path: Path to the PDF form file
        form_fields: Dict of field names → values (e.g. {"name": "Jane Doe"})
        api_key: DeepRead API key (sk_live_...)
        webhook_url: Optional URL to receive results when done
        idempotency_key: Optional key to prevent duplicate submissions

    Returns:
        {"id": "<job_id>", "status": "queued"}
    """
    # Build multipart form data manually (stdlib only)
    boundary = "----DeepReadFormBoundary"
    body = b""

    # Add PDF file
    filename = os.path.basename(pdf_path)
    with open(pdf_path, "rb") as f:
        file_data = f.read()

    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
    body += b"Content-Type: application/pdf\r\n\r\n"
    body += file_data
    body += b"\r\n"

    # Add form_fields as JSON string
    body += f"--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="form_fields"\r\n\r\n'
    body += json.dumps(form_fields).encode()
    body += b"\r\n"

    # Add optional webhook_url
    if webhook_url:
        body += f"--{boundary}\r\n".encode()
        body += b'Content-Disposition: form-data; name="webhook_url"\r\n\r\n'
        body += webhook_url.encode()
        body += b"\r\n"

    # Add optional idempotency_key
    if idempotency_key:
        body += f"--{boundary}\r\n".encode()
        body += b'Content-Disposition: form-data; name="idempotency_key"\r\n\r\n'
        body += idempotency_key.encode()
        body += b"\r\n"

    body += f"--{boundary}--\r\n".encode()

    req = Request(
        f"{API_BASE}/v1/form-fill",
        data=body,
        headers={
            "X-API-Key": api_key,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )

    try:
        with urlopen(req) as resp:
            return json.loads(resp.read())
    except HTTPError as exc:
        error_body = exc.read().decode()
        print(f"Error {exc.code}: {error_body}", file=sys.stderr)
        sys.exit(1)


def poll_for_result(job_id: str, api_key: str, interval: int = 5) -> dict:
    """Poll until the job is completed or failed.

    GET /v1/form-fill/{job_id}

    Args:
        job_id: Job UUID from submit response
        api_key: DeepRead API key
        interval: Seconds between polls (default: 5)

    Returns:
        Full job detail response including filled_form_url and report
    """
    while True:
        req = Request(
            f"{API_BASE}/v1/form-fill/{job_id}",
            headers={"X-API-Key": api_key},
        )

        with urlopen(req) as resp:
            data = json.loads(resp.read())

        status = data["status"]
        if status == "completed":
            return data
        if status == "failed":
            print(f"Job failed: {data.get('error_message', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)

        # Still processing
        time.sleep(interval)


def main() -> None:
    """Fill a PDF form from command line arguments.

    Usage: python form_fill.py <pdf_path> <json_path>

    json_path should contain a JSON object like:
    {"full_name": "Jane Doe", "dob": "1990-03-15"}
    """
    if len(sys.argv) < 3:
        print("Usage: python form_fill.py <pdf_path> <form_fields.json>", file=sys.stderr)
        sys.exit(1)

    pdf_path = sys.argv[1]
    json_path = sys.argv[2]

    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    with open(json_path) as f:
        form_fields = json.load(f)

    api_key = get_api_key()

    # Submit
    print(f"Submitting {os.path.basename(pdf_path)} with {len(form_fields)} fields...")
    job = submit_form_fill(pdf_path, form_fields, api_key)
    job_id = job["id"]
    print(f"Job {job_id} — status: {job['status']}")

    # Poll
    print("Waiting for result...")
    result = poll_for_result(job_id, api_key)

    # Summary
    print()
    print(f"Status: {result['status']}")
    print(f"Fields: {result.get('fields_filled', 0)}/{result.get('fields_detected', 0)} filled, "
          f"{result.get('fields_verified', 0)} verified, "
          f"{result.get('fields_hil_flagged', 0)} need review")
    print(f"Time: {result.get('duration_seconds', 0):.1f}s")
    print(f"Download: {result.get('filled_form_url', 'N/A')}")


if __name__ == "__main__":
    main()
