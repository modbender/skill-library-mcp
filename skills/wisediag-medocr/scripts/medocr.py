#!/usr/bin/env python3
"""
WiseDiag MedOcr CLI - Convert PDF to Markdown via WiseDiag OCR API

Usage:
    1. Set API key: export WISEDIAG_API_KEY=your_api_key
    2. Run: python medocr.py -i input.pdf

Get API key: https://chat.wisediag.com/apiKeyManage
"""

import argparse
import os
import sys
import time
import threading
from pathlib import Path

import requests


DEFAULT_SERVICE_URL = "https://openapi.wisediag.com"
DEFAULT_DPI = 200
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def get_api_key():
    """Get API Key from environment variable."""
    api_key = os.environ.get("WISEDIAG_API_KEY")
    if not api_key:
        print("""
[!] Error: WISEDIAG_API_KEY environment variable is not set.

To use this tool, you need a WiseDiag API key:

1. Visit: https://chat.wisediag.com/apiKeyManage
2. Sign up/Login and create an API key
3. Set the environment variable:
   
   export WISEDIAG_API_KEY=your_api_key

For permanent setup, add the line above to your ~/.zshrc or ~/.bashrc
        """)
        raise SystemExit(1)
    return api_key


class ProgressIndicator:
    """Show elapsed time while waiting for OCR processing."""

    def __init__(self):
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join()
        # Clear the progress line
        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()

    def _run(self):
        start = time.time()
        while not self._stop.is_set():
            elapsed = int(time.time() - start)
            mins, secs = divmod(elapsed, 60)
            sys.stdout.write(f"\r[*] OCR processing... {mins:02d}:{secs:02d} elapsed")
            sys.stdout.flush()
            self._stop.wait(1)


def _upload_with_retry(endpoint, input_path, headers, params, max_retries=MAX_RETRIES):
    """Upload PDF and call OCR API with automatic retry on failure."""
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            with open(input_path, "rb") as f:
                files = {"file": (input_path.name, f, "application/pdf")}
                resp = requests.post(
                    endpoint, files=files, params=params,
                    headers=headers, timeout=600,
                )

            # Auth error — no point retrying
            if resp.status_code == 401:
                print(f"\n[!] Authentication failed. Please check your API key.")
                print(f"    Get a valid key at: https://chat.wisediag.com/apiKeyManage")
                return None

            # Success
            if resp.status_code == 200:
                return resp

            # Server error — worth retrying
            last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
            if attempt < max_retries:
                print(f"\n[!] Attempt {attempt}/{max_retries} failed ({last_error})")
                print(f"    Retrying in {RETRY_DELAY}s ...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"\n[!] All {max_retries} attempts failed. Last error: {last_error}")
                return None

        except requests.Timeout:
            last_error = "Request timed out (600s)"
            if attempt < max_retries:
                print(f"\n[!] Attempt {attempt}/{max_retries} timed out.")
                print(f"    Retrying in {RETRY_DELAY}s ...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"\n[!] All {max_retries} attempts timed out.")
                return None

        except requests.ConnectionError:
            last_error = "Connection refused"
            if attempt < max_retries:
                print(f"\n[!] Attempt {attempt}/{max_retries}: cannot connect to service.")
                print(f"    Retrying in {RETRY_DELAY}s ...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"\n[!] All {max_retries} attempts failed: cannot connect to service.")
                return None

        except Exception as e:
            last_error = str(e)
            if attempt < max_retries:
                print(f"\n[!] Attempt {attempt}/{max_retries} failed: {e}")
                print(f"    Retrying in {RETRY_DELAY}s ...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"\n[!] All {max_retries} attempts failed: {e}")
                return None

    return None


def process_pdf(input_path, output_dir=None, service_url=DEFAULT_SERVICE_URL, dpi=DEFAULT_DPI):
    """Process a PDF file via the WiseDiag MedOcr API."""
    input_path = Path(input_path)

    if output_dir is None:
        output_dir = Path.cwd() / "WiseDiag-MedOcr-1.0.0"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    api_key = get_api_key()
    file_size = input_path.stat().st_size
    file_size_mb = file_size / (1024 * 1024)

    print(f"[*] Processing: {input_path.name} ({file_size_mb:.1f} MB)")
    print(f"[*] DPI: {dpi}")

    endpoint = f"{service_url}/v1/ocr/pdf"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"dpi": dpi}

    # Upload and process with retry + progress indicator
    progress = ProgressIndicator()
    progress.start()

    resp = _upload_with_retry(endpoint, input_path, headers, params)

    progress.stop()

    if resp is None:
        return None

    data = resp.json()
    total_pages = data.get("total_pages", 0)
    elapsed = data.get("elapsed_seconds", 0)

    print(f"[*] Total pages: {total_pages}")
    print(f"[*] Processing time: {elapsed:.1f}s")

    # Print usage info
    usage = data.get("usage")
    if usage:
        print(f"[*] Usage: completion_tokens={usage.get('completion_tokens')}, "
              f"ocr_pic_size={usage.get('ocr_pic_size')}, "
              f"total_tokens={usage.get('total_tokens')}")

    # Save combined markdown — use input PDF filename
    markdown = data.get("markdown", "")
    output_path = output_dir / f"{input_path.stem}.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"[+] Markdown saved: {output_path}")

    return output_dir


def main():
    parser = argparse.ArgumentParser(
        description="WiseDiag MedOcr CLI - Convert PDF to Markdown"
    )
    parser.add_argument("-i", "--input", required=True, help="Input PDF file path")
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument(
        "--service-url",
        default=DEFAULT_SERVICE_URL,
        help=f"MedOcr API URL (default: {DEFAULT_SERVICE_URL})",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=DEFAULT_DPI,
        help=f"PDF rendering DPI (default: {DEFAULT_DPI})",
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[!] File not found: {args.input}")
        return

    if not args.input.lower().endswith(".pdf"):
        print(f"[!] Only PDF files are supported: {args.input}")
        return

    process_pdf(args.input, args.output, args.service_url, args.dpi)


if __name__ == "__main__":
    main()
