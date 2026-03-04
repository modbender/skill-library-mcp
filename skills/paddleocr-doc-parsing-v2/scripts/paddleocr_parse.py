#!/usr/bin/env python3
"""
PaddleOCR Async Document Parser

Supports both sync and async parsing modes.
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

import requests


def get_env_or_exit(name: str) -> str:
    """Get environment variable or exit with error."""
    value = os.environ.get(name)
    if not value:
        print(f"Error: {name} environment variable is required", file=sys.stderr)
        print(f"Set it with: export {name}=\"your_value_here\"", file=sys.stderr)
        sys.exit(1)
    return value


def sync_parse(file_path: str, file_type: int, api_url: str, token: str, verbose: bool = False) -> dict:
    """Synchronous document parsing."""
    
    if file_path.startswith("http"):
        # URL mode
        payload = {
            "file": file_path,
            "fileType": file_type,
            "useDocOrientationClassify": False,
            "useDocUnwarping": False,
        }
    else:
        # Local file mode
        path = Path(file_path)
        if not path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        
        file_bytes = path.read_bytes()
        file_data = base64.b64encode(file_bytes).decode("ascii")
        
        payload = {
            "file": file_data,
            "fileType": file_type,
            "useDocOrientationClassify": False,
            "useDocUnwarping": False,
        }
    
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    
    if verbose:
        print(f"Making sync request to: {api_url}", file=sys.stderr)
    
    response = requests.post(api_url, json=payload, headers=headers, timeout=600)
    
    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}", file=sys.stderr)
        print(response.text, file=sys.stderr)
        sys.exit(1)
    
    return response.json()


def async_parse(file_path: str, model: str, job_url: str, token: str, verbose: bool = False) -> dict:
    """Asynchronous document parsing."""
    
    headers = {
        "Authorization": f"bearer {token}",
    }
    
    optional_payload = {
        "useDocOrientationClassify": False,
        "useDocUnwarping": False,
        "useChartRecognition": False,
    }
    
    if verbose:
        print(f"Processing file: {file_path}", file=sys.stderr)
    
    if file_path.startswith("http"):
        # URL Mode
        headers["Content-Type"] = "application/json"
        payload = {
            "fileUrl": file_path,
            "model": model,
            "optionalPayload": optional_payload
        }
        job_response = requests.post(job_url, json=payload, headers=headers)
    else:
        # Local File Mode
        path = Path(file_path)
        if not path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        
        data = {
            "model": model,
            "optionalPayload": json.dumps(optional_payload)
        }
        with open(file_path, "rb") as f:
            files = {"file": f}
            job_response = requests.post(job_url, headers=headers, data=data, files=files)
    
    if verbose:
        print(f"Response status: {job_response.status_code}", file=sys.stderr)
    
    if job_response.status_code != 200:
        print(f"Error: HTTP {job_response.status_code}", file=sys.stderr)
        print(job_response.text, file=sys.stderr)
        sys.exit(1)
    
    job_id = job_response.json()["data"]["jobId"]
    print(f"Job submitted. ID: {job_id}", file=sys.stderr)
    
    # Poll for results
    jsonl_url = ""
    while True:
        job_result = requests.get(f"{job_url}/{job_id}", headers=headers)
        job_result.raise_for_status()
        
        data = job_result.json()["data"]
        state = data["state"]
        
        if state == 'pending':
            if verbose:
                print("Status: pending", file=sys.stderr)
        elif state == 'running':
            try:
                progress = data['extractProgress']
                total = progress['totalPages']
                extracted = progress['extractedPages']
                print(f"Status: running ({extracted}/{total} pages)", file=sys.stderr)
            except KeyError:
                if verbose:
                    print("Status: running...", file=sys.stderr)
        elif state == 'done':
            extracted = data['extractProgress']['extractedPages']
            print(f"Status: done ({extracted} pages extracted)", file=sys.stderr)
            jsonl_url = data['resultUrl']['jsonUrl']
            break
        elif state == "failed":
            error_msg = data.get('errorMsg', 'Unknown error')
            print(f"Error: Job failed - {error_msg}", file=sys.stderr)
            sys.exit(1)
        
        time.sleep(5)
    
    # Fetch JSONL results
    if jsonl_url:
        jsonl_response = requests.get(jsonl_url)
        jsonl_response.raise_for_status()
        
        lines = jsonl_response.text.strip().split('\n')
        results = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                result = json.loads(line)["result"]
                results.extend(result.get("layoutParsingResults", []))
            except (json.JSONDecodeError, KeyError) as e:
                if verbose:
                    print(f"Warning: Failed to parse line: {e}", file=sys.stderr)
                continue
        
        return {"result": {"layoutParsingResults": results}}
    
    return {}


def main():
    parser = argparse.ArgumentParser(description="Parse documents using PaddleOCR API")
    parser.add_argument("input", help="Input file path or URL")
    parser.add_argument("-t", "--type", choices=["image", "pdf"], default="image",
                       help="File type (default: image)")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--async-mode", action="store_true", 
                       help="Use async mode (for large files)")
    
    args = parser.parse_args()
    
    # Get configuration from environment
    token = get_env_or_exit("PADDLEOCR_ACCESS_TOKEN")
    
    if args.async_mode:
        job_url = get_env_or_exit("PADDLEOCR_JOB_URL")
        model = os.environ.get("PADDLEOCR_MODEL", "PaddleOCR-VL-1.5")
        result = async_parse(args.input, model, job_url, token, args.verbose)
    else:
        api_url = get_env_or_exit("PADDLEOCR_API_URL")
        file_type_code = 0 if args.type == "pdf" else 1
        result = sync_parse(args.input, file_type_code, api_url, token, args.verbose)
    
    # Output result
    output = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        Path(args.output).write_text(output)
        print(f"Output saved to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
