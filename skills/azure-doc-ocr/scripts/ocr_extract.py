#!/usr/bin/env python3
"""
Single file OCR using Azure Document Intelligence REST API v4.0.

Extract text and structured data from PDFs and images using Azure's
Document Intelligence service with various prebuilt models.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests


CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
    ".bmp": "image/bmp",
}

API_VERSION = "2024-11-30"
MAX_POLL_TIME = 300
POLL_INTERVAL = 2


def get_credentials():
    """Get Azure Document Intelligence credentials from environment."""
    endpoint = os.environ.get("AZURE_DOC_INTEL_ENDPOINT")
    key = os.environ.get("AZURE_DOC_INTEL_KEY")

    if not endpoint:
        print("Error: AZURE_DOC_INTEL_ENDPOINT environment variable not set", file=sys.stderr)
        sys.exit(1)
    if not key:
        print("Error: AZURE_DOC_INTEL_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    return endpoint.rstrip("/"), key


def analyze_document(endpoint, key, model, file_path=None, url=None, pages=None):
    """
    Submit document for analysis and return operation location.

    Args:
        endpoint: Azure Document Intelligence endpoint
        key: API subscription key
        model: Model ID (e.g., prebuilt-read)
        file_path: Path to local file (optional if url provided)
        url: URL to document (optional if file_path provided)
        pages: Page selection string (e.g., "1-3,5")

    Returns:
        Operation location URL for polling
    """
    analyze_url = f"{endpoint}/documentintelligence/documentModels/{model}:analyze"
    params = {"api-version": API_VERSION}

    if pages:
        params["pages"] = pages

    headers = {"Ocp-Apim-Subscription-Key": key}

    if url:
        headers["Content-Type"] = "application/json"
        body = {"urlSource": url}
        response = requests.post(analyze_url, params=params, headers=headers, json=body)
    else:
        ext = Path(file_path).suffix.lower()
        content_type = CONTENT_TYPES.get(ext)
        if not content_type:
            print(f"Error: Unsupported file extension '{ext}'", file=sys.stderr)
            print(f"Supported: {', '.join(CONTENT_TYPES.keys())}", file=sys.stderr)
            sys.exit(1)

        headers["Content-Type"] = content_type
        with open(file_path, "rb") as f:
            body = f.read()
        response = requests.post(analyze_url, params=params, headers=headers, data=body)

    if response.status_code != 202:
        print(f"Error: Failed to submit document (HTTP {response.status_code})", file=sys.stderr)
        try:
            error_detail = response.json()
            print(f"Details: {json.dumps(error_detail, indent=2)}", file=sys.stderr)
        except Exception:
            print(f"Response: {response.text}", file=sys.stderr)
        sys.exit(1)

    operation_location = response.headers.get("Operation-Location")
    if not operation_location:
        print("Error: No Operation-Location header in response", file=sys.stderr)
        sys.exit(1)

    return operation_location


def poll_result(operation_location, key):
    """
    Poll for analysis result until completed or timeout.

    Args:
        operation_location: URL to poll for results
        key: API subscription key

    Returns:
        Analysis result JSON
    """
    headers = {"Ocp-Apim-Subscription-Key": key}
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed > MAX_POLL_TIME:
            print(f"Error: Polling timeout after {MAX_POLL_TIME} seconds", file=sys.stderr)
            sys.exit(1)

        response = requests.get(operation_location, headers=headers)

        if response.status_code != 200:
            print(f"Error: Failed to poll status (HTTP {response.status_code})", file=sys.stderr)
            print(f"Response: {response.text}", file=sys.stderr)
            sys.exit(1)

        result = response.json()
        status = result.get("status")

        if status == "succeeded":
            return result
        elif status == "failed":
            error = result.get("error", {})
            print(f"Error: Analysis failed", file=sys.stderr)
            print(f"Code: {error.get('code')}", file=sys.stderr)
            print(f"Message: {error.get('message')}", file=sys.stderr)
            sys.exit(1)
        elif status in ("notStarted", "running"):
            time.sleep(POLL_INTERVAL)
        else:
            print(f"Error: Unknown status '{status}'", file=sys.stderr)
            sys.exit(1)


def format_text(result):
    """Extract plain text from analysis result."""
    analyze_result = result.get("analyzeResult", {})
    content = analyze_result.get("content", "")
    return content


def format_markdown(result):
    """Format result as markdown with structure."""
    analyze_result = result.get("analyzeResult", {})
    output_parts = []

    # Add content
    content = analyze_result.get("content", "")
    if content:
        output_parts.append(content)

    # Add tables if present
    tables = analyze_result.get("tables", [])
    for i, table in enumerate(tables):
        output_parts.append(f"\n\n## Table {i + 1}\n")
        rows = {}
        for cell in table.get("cells", []):
            row_idx = cell.get("rowIndex", 0)
            col_idx = cell.get("columnIndex", 0)
            text = cell.get("content", "")
            if row_idx not in rows:
                rows[row_idx] = {}
            rows[row_idx][col_idx] = text

        if rows:
            col_count = max(max(cols.keys()) + 1 for cols in rows.values()) if rows else 0
            for row_idx in sorted(rows.keys()):
                row_cells = [rows[row_idx].get(c, "") for c in range(col_count)]
                output_parts.append("| " + " | ".join(row_cells) + " |")
                if row_idx == 0:
                    output_parts.append("|" + "|".join(["---"] * col_count) + "|")

    return "\n".join(output_parts)


def format_json(result):
    """Return raw JSON result."""
    return json.dumps(result, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from documents using Azure Document Intelligence"
    )
    parser.add_argument(
        "file_path",
        nargs="?",
        help="Path to document file (PDF or image)"
    )
    parser.add_argument(
        "--url",
        help="URL to document (use instead of file_path)"
    )
    parser.add_argument(
        "--model",
        default="prebuilt-read",
        help="Model ID (default: prebuilt-read)"
    )
    parser.add_argument(
        "--format",
        choices=["text", "markdown", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--pages",
        help="Page selection (e.g., '1-3,5,7-10')"
    )

    args = parser.parse_args()

    if not args.file_path and not args.url:
        parser.error("Either file_path or --url must be provided")

    if args.file_path and args.url:
        parser.error("Cannot specify both file_path and --url")

    if args.file_path and not os.path.isfile(args.file_path):
        print(f"Error: File not found: {args.file_path}", file=sys.stderr)
        sys.exit(1)

    endpoint, key = get_credentials()

    # Submit for analysis
    operation_location = analyze_document(
        endpoint, key, args.model,
        file_path=args.file_path,
        url=args.url,
        pages=args.pages
    )

    # Poll for result
    result = poll_result(operation_location, key)

    # Format output
    if args.format == "text":
        output = format_text(result)
    elif args.format == "markdown":
        output = format_markdown(result)
    else:
        output = format_json(result)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
