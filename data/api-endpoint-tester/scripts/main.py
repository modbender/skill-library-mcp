#!/usr/bin/env python3
"""
API Endpoint Tester - CLI tool to test REST API endpoints
"""

import argparse
import json
import os
import sys
import time
from typing import Dict, Any, Optional
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError, SSLError

def make_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Any] = None,
    timeout: int = 10,
    verify_ssl: bool = True,
    allow_redirects: bool = True
) -> Dict[str, Any]:
    """
    Make an HTTP request and return standardized response.
    """
    start_time = time.time()
    
    # Normalize method
    method = method.upper()
    if method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
        raise ValueError(f"Unsupported HTTP method: {method}")
    
    # Prepare headers
    request_headers = headers or {}
    
    # Prepare body
    data = None
    json_data = None
    
    if body is not None:
        # If body is a dict and Content-Type suggests JSON, send as JSON
        content_type = request_headers.get("Content-Type", "").lower()
        if isinstance(body, dict) and ("application/json" in content_type or content_type == ""):
            json_data = body
        else:
            data = body
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=request_headers,
            json=json_data,
            data=data,
            timeout=timeout,
            verify=verify_ssl,
            allow_redirects=allow_redirects
        )
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Try to parse JSON response, fall back to text
        try:
            response_body = response.json()
        except ValueError:
            response_body = response.text
        
        return {
            "status": "success",
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response_body,
            "response_time_ms": response_time_ms,
            "url": url,
            "method": method
        }
    
    except Timeout:
        return {
            "status": "error",
            "error_message": f"Request timed out after {timeout} seconds",
            "url": url,
            "method": method
        }
    except ConnectionError:
        return {
            "status": "error",
            "error_message": "Connection failed - check URL and network",
            "url": url,
            "method": method
        }
    except SSLError:
        return {
            "status": "error",
            "error_message": "SSL certificate verification failed",
            "url": url,
            "method": method
        }
    except RequestException as e:
        return {
            "status": "error",
            "error_message": str(e),
            "url": url,
            "method": method
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Unexpected error: {str(e)}",
            "url": url,
            "method": method
        }

def parse_json_arg(value: str) -> Any:
    """Parse JSON string argument, or return raw string if invalid."""
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        # If it's not JSON, return as string
        return value

def run(args):
    """Execute the API test."""
    # Parse headers and body from JSON strings
    headers = parse_json_arg(args.headers)
    body = parse_json_arg(args.body)
    
    # Validate URL
    if not args.url:
        return {
            "status": "error",
            "error_message": "URL is required"
        }
    
    # Validate URL format
    if not args.url.startswith(("http://", "https://")):
        return {
            "status": "error",
            "error_message": "URL must start with http:// or https://"
        }
    
    # Validate timeout
    if args.timeout <= 0:
        return {
            "status": "error",
            "error_message": "Timeout must be positive"
        }
    
    # Validate output file path is within skill directory
    if args.output_file:
        try:
            skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_path = os.path.abspath(args.output_file)
            if not output_path.startswith(skill_dir):
                return {
                    "status": "error",
                    "error_message": f"Output file must be within skill directory: {skill_dir}"
                }
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Invalid output file path: {str(e)}"
            }
    
    # Make the request
    result = make_request(
        url=args.url,
        method=args.method,
        headers=headers,
        body=body,
        timeout=args.timeout,
        verify_ssl=args.verify_ssl,
        allow_redirects=args.allow_redirects
    )
    
    # Check expected status if provided
    if args.expected_status is not None and result.get("status") == "success":
        if result.get("status_code") != args.expected_status:
            result["status"] = "error"
            result["error_message"] = f"Expected status {args.expected_status}, got {result.get('status_code')}"
    
    # Output to file if requested
    if args.output_file and result.get("status") == "success":
        try:
            with open(args.output_file, "w") as f:
                json.dump(result, f, indent=2)
        except Exception as e:
            result["status"] = "error"
            result["error_message"] = f"Failed to write output file: {str(e)}"
    
    return result

def main():
    parser = argparse.ArgumentParser(
        description="Test REST API endpoints with various HTTP methods, headers, and payloads."
    )
    parser.add_argument(
        "command",
        choices=["run", "help"],
        help="Command to execute"
    )
    
    # Required arguments for 'run'
    parser.add_argument(
        "--url",
        help="Target URL for the request"
    )
    parser.add_argument(
        "--method",
        default="GET",
        choices=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
        help="HTTP method (default: GET)"
    )
    parser.add_argument(
        "--headers",
        default="{}",
        help="JSON string of headers (default: {})"
    )
    parser.add_argument(
        "--body",
        help="Request body (JSON or raw string)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)"
    )
    parser.add_argument(
        "--expected-status",
        type=int,
        help="Expected HTTP status code (will error if mismatch)"
    )
    parser.add_argument(
        "--verify-ssl",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Verify SSL certificates (default: true)"
    )
    parser.add_argument(
        "--allow-redirects",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Follow redirects (default: true)"
    )
    parser.add_argument(
        "--output-file",
        help="Save response to file (optional)"
    )
    
    args = parser.parse_args()
    
    if args.command == "run":
        result = run(args)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()