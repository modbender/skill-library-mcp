#!/usr/bin/env python3
"""
Jina Reader - Web content extraction tool
Extracts clean markdown from any URL using Jina Reader API
"""

import sys
import json
import argparse
from urllib.parse import urlparse
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests module not found. Install with: pip install requests")
    sys.exit(1)


def extract_content(url: str, output_format: str = "markdown", timeout: int = 30) -> dict:
    """
    Extract content from URL using Jina Reader API

    Args:
        url: The URL to extract content from
        output_format: Output format - 'markdown' or 'json'
        timeout: Request timeout in seconds

    Returns:
        Dictionary with content and metadata
    """
    # Normalize URL
    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'

    jina_url = f"https://r.jina.ai/http://{url.replace('http://', '').replace('https://', '')}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; JinaReader/1.0)'
    }

    try:
        response = requests.get(jina_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        content = response.text

        if output_format == "json":
            # Try to extract metadata from response
            lines = content.split('\n')
            metadata = {}
            markdown_content = []

            current_field = None
            for line in lines:
                if line.startswith('Title:'):
                    metadata['title'] = line.replace('Title:', '').strip()
                elif line.startswith('URL Source:'):
                    metadata['url'] = line.replace('URL Source:', '').strip()
                elif line.startswith('Published Time:'):
                    metadata['published'] = line.replace('Published Time:', '').strip()
                elif line.startswith('Markdown Content:'):
                    current_field = 'content'
                elif current_field == 'content':
                    markdown_content.append(line)

            return {
                'status': 'success',
                'metadata': metadata,
                'content': '\n'.join(markdown_content)
            }
        else:
            return {
                'status': 'success',
                'content': content
            }

    except requests.exceptions.Timeout:
        return {
            'status': 'error',
            'error': f'Request timeout after {timeout} seconds'
        }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def main():
    parser = argparse.ArgumentParser(
        description='Extract clean markdown content from any URL using Jina Reader API'
    )
    parser.add_argument('url', help='URL to extract content from')
    parser.add_argument(
        '-f', '--format',
        choices=['markdown', 'json'],
        default='markdown',
        help='Output format (default: markdown)'
    )
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Save output to file'
    )

    args = parser.parse_args()

    result = extract_content(args.url, args.format, args.timeout)

    if result['status'] == 'error':
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.format == 'json':
        output = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        output = result['content']

    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"Saved to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
