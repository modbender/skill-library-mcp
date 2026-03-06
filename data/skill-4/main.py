#!/usr/bin/env python3
"""website-monitor: Check uptime, response time, and content changes."""

import sys
import argparse
import hashlib
import time
import json
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def check_url(url, timeout=10, expected_status=200, contains=None, prev_hash=None):
    """Check a single URL and return results dict."""
    result = {
        'url': url,
        'status': None,
        'response_time_ms': None,
        'up': False,
        'content_hash': None,
        'content_changed': None,
        'contains_text': None,
        'error': None,
        'content_length': None,
    }

    headers = {'User-Agent': 'website-monitor/1.0 (ClawHub)'}
    req = Request(url, headers=headers)

    start = time.monotonic()
    try:
        resp = urlopen(req, timeout=timeout)
        elapsed = (time.monotonic() - start) * 1000
        body = resp.read()

        result['status'] = resp.status
        result['response_time_ms'] = round(elapsed, 1)
        result['up'] = resp.status == expected_status
        result['content_length'] = len(body)

        # Content hash
        h = hashlib.sha256(body).hexdigest()[:16]
        result['content_hash'] = h
        if prev_hash:
            result['content_changed'] = h != prev_hash

        # Contains check
        if contains:
            try:
                text = body.decode('utf-8', errors='replace')
                result['contains_text'] = contains in text
            except Exception:
                result['contains_text'] = False

    except HTTPError as e:
        elapsed = (time.monotonic() - start) * 1000
        result['status'] = e.code
        result['response_time_ms'] = round(elapsed, 1)
        result['up'] = e.code == expected_status
        result['error'] = str(e.reason)
    except URLError as e:
        elapsed = (time.monotonic() - start) * 1000
        result['response_time_ms'] = round(elapsed, 1)
        result['error'] = str(e.reason)
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        result['response_time_ms'] = round(elapsed, 1)
        result['error'] = str(e)

    return result


def print_result(r):
    """Pretty-print a single check result."""
    icon = '✅' if r['up'] else '❌'
    print(f"{icon} {r['url']}")
    if r['status']:
        print(f"   Status: {r['status']}")
    print(f"   Response: {r['response_time_ms']}ms")
    if r['content_length'] is not None:
        print(f"   Size: {r['content_length']} bytes")
    if r['content_hash']:
        print(f"   Hash: {r['content_hash']}")
    if r['content_changed'] is not None:
        print(f"   Changed: {'YES ⚠️' if r['content_changed'] else 'No'}")
    if r['contains_text'] is not None:
        print(f"   Contains text: {'Yes' if r['contains_text'] else 'No ⚠️'}")
    if r['error']:
        print(f"   Error: {r['error']}")


def main():
    parser = argparse.ArgumentParser(description='Website uptime and change monitor')
    parser.add_argument('urls', nargs='+', help='URLs to check')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout in seconds')
    parser.add_argument('--expect', type=int, default=200, help='Expected HTTP status')
    parser.add_argument('--contains', help='Check if response contains this text')
    parser.add_argument('--hash-check', help='Previous content hash to detect changes')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    results = []
    for url in args.urls:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        r = check_url(url, args.timeout, args.expect, args.contains, args.hash_check)
        results.append(r)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print_result(r)
            if r != results[-1]:
                print()

    # Exit 1 if any site is down
    if not all(r['up'] for r in results):
        sys.exit(1)


if __name__ == '__main__':
    main()
