#!/usr/bin/env python3
"""
ProductAI Batch Photo Generator

Process multiple product images with consistent styling.
"""

import argparse
import sys
import time
import re
from pathlib import Path
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

from productai_client import create_client_from_config


# Rate limit: 15 requests per minute = 1 request per 4 seconds
RATE_LIMIT_SECONDS = 4.0


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal.
    
    Args:
        filename: Original filename
    
    Returns:
        Safe filename with only alphanumeric, dash, underscore, dot
    """
    # Remove path separators and parent references
    safe_name = filename.replace('/', '_').replace('\\', '_').replace('..', '_')
    
    # Keep only safe characters
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', safe_name)
    
    # Prevent hidden files
    if safe_name.startswith('.'):
        safe_name = '_' + safe_name[1:]
    
    return safe_name


def download_image(url: str, output_path: Path) -> None:
    """Download image from URL to local file."""
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def process_single_image(
    image_url: str,
    prompt: str,
    output_dir: Path,
    model: str,
    client
) -> dict:
    """
    Process a single image with rate limiting.
    
    Args:
        image_url: URL of source image
        prompt: Generation prompt
        output_dir: Output directory
        model: Model to use
        client: ProductAI client instance
    
    Returns:
        dict with results
    """
    start_time = time.time()
    
    try:
        # Extract filename from URL for output naming
        url_path = image_url.split('/')[-1].split('?')[0]
        safe_name = sanitize_filename(url_path)
        base_name = Path(safe_name).stem
        
        print(f"Processing {safe_name}...")
        
        # Generate
        job = client.generate(image_url, prompt, model)
        job_id = job['id']
        
        # Wait for completion
        image_result_url = client.wait_for_completion(job_id)
        
        # Download result
        output_path = output_dir / f"{base_name}_generated.png"
        download_image(image_result_url, output_path)
        
        elapsed = time.time() - start_time
        print(f"✓ {safe_name} → {output_path.name} ({elapsed:.1f}s)")
        
        return {
            'input': image_url,
            'output': str(output_path),
            'status': 'success',
            'job_id': job_id
        }
        
    except Exception as e:
        print(f"✗ {image_url}: {e}", file=sys.stderr)
        return {
            'input': image_url,
            'output': None,
            'status': 'error',
            'error': str(e)
        }


def rate_limited_process(image_urls: List[str], prompt: str, output_dir: Path, model: str, client, max_workers: int = 3):
    """
    Process images with rate limiting (15 req/min).
    
    Args:
        image_urls: List of image URLs
        prompt: Generation prompt
        output_dir: Output directory
        model: Model to use
        client: ProductAI client
        max_workers: Max concurrent workers (default: 3 to stay under 15 req/min)
    """
    results = []
    last_request_time = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        
        for image_url in image_urls:
            # Rate limiting: ensure minimum time between requests
            elapsed = time.time() - last_request_time
            if elapsed < RATE_LIMIT_SECONDS:
                time.sleep(RATE_LIMIT_SECONDS - elapsed)
            
            future = executor.submit(
                process_single_image,
                image_url,
                prompt,
                output_dir,
                model,
                client
            )
            futures.append(future)
            last_request_time = time.time()
        
        # Collect results
        for future in as_completed(futures):
            results.append(future.result())
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Batch process product images with ProductAI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Process multiple images with same prompt
  %(prog)s --images url1 url2 url3 --prompt "white background" --output-dir ./results
  
  # Use a different model
  %(prog)s --images url1 url2 --prompt "luxury setting" --model nanobananapro --output-dir ./results
  
  # From a text file (one URL per line)
  %(prog)s --input-file urls.txt --prompt "studio lighting" --output-dir ./results

Note: Rate limited to 15 requests/minute to comply with API limits.
        '''
    )
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--images',
        nargs='+',
        help='Image URLs to process'
    )
    input_group.add_argument(
        '--input-file',
        type=Path,
        help='Text file with image URLs (one per line)'
    )
    
    parser.add_argument(
        '--prompt',
        required=True,
        help='Generation prompt to apply to all images'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        required=True,
        help='Output directory for generated images'
    )
    parser.add_argument(
        '--model',
        default='nanobanana',
        choices=['gpt-low', 'gpt-medium', 'gpt-high', 'kontext-pro', 'nanobanana', 'nanobananapro', 'seedream'],
        help='Model to use (default: nanobanana)'
    )
    parser.add_argument(
        '--max-workers',
        type=int,
        default=3,
        help='Maximum concurrent workers (default: 3, max recommended: 3 to stay under 15 req/min)'
    )
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to config.json'
    )
    
    args = parser.parse_args()
    
    # Load image URLs
    if args.images:
        image_urls = args.images
    else:
        with open(args.input_file) as f:
            image_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not image_urls:
        print("Error: No image URLs provided", file=sys.stderr)
        sys.exit(1)
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Batch processing {len(image_urls)} images")
    print(f"Model: {args.model}")
    print(f"Prompt: {args.prompt}")
    print(f"Output: {args.output_dir}")
    print(f"Rate limit: {RATE_LIMIT_SECONDS}s between requests")
    print()
    
    try:
        # Create client
        client = create_client_from_config(args.config)
        
        # Process with rate limiting
        results = rate_limited_process(
            image_urls,
            args.prompt,
            args.output_dir,
            args.model,
            client,
            max_workers=args.max_workers
        )
        
        # Summary
        success_count = sum(1 for r in results if r['status'] == 'success')
        error_count = len(results) - success_count
        
        print()
        print("=" * 60)
        print(f"Batch processing complete!")
        print(f"  ✓ Success: {success_count}")
        print(f"  ✗ Errors: {error_count}")
        print(f"  Output: {args.output_dir}")
        
    except KeyboardInterrupt:
        print("\n\nCancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
