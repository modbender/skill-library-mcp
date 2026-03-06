#!/usr/bin/env python3
"""
ProductAI Image Upscaler

Upscale images using professional AI upscaling technology.
"""

import argparse
import sys
from pathlib import Path
import requests

from productai_client import create_client_from_config


def download_image(url: str, output_path: Path) -> None:
    """Download image from URL to local file."""
    print(f"Downloading image to {output_path}...")
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"✓ Saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Upscale images using ProductAI (20 tokens per upscale)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Upscale an image
  %(prog)s --image https://example.com/product.jpg --output upscaled.png
  
  # Just get the job ID (don't wait)
  %(prog)s --image https://example.com/product.jpg --no-wait
  
  # Resume existing job
  %(prog)s --job-id 12345 --output upscaled.png
        '''
    )
    
    parser.add_argument(
        '--image',
        help='Image URL to upscale'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output file path (e.g., upscaled.png). If not specified, prints image URL only.'
    )
    parser.add_argument(
        '--no-wait',
        action='store_true',
        help="Don't wait for completion, just print job ID and exit"
    )
    parser.add_argument(
        '--poll-interval',
        type=int,
        default=5,
        help='Seconds to wait between status checks (default: 5)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='Maximum seconds to wait for completion (default: 300)'
    )
    parser.add_argument(
        '--job-id',
        type=int,
        help='Resume waiting for an existing job ID instead of creating new job'
    )
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to config.json (default: ~/.openclaw/workspace/productai/config.json)'
    )
    
    args = parser.parse_args()
    
    # Validation
    if not args.job_id and not args.image:
        parser.error("Either --image or --job-id is required")
    
    try:
        # Create client
        client = create_client_from_config(args.config)
        
        # If resuming existing job
        if args.job_id:
            print(f"Checking status of upscale job {args.job_id}...")
            image_url = client.wait_for_completion(
                args.job_id,
                poll_interval=args.poll_interval,
                timeout=args.timeout
            )
        else:
            # Start upscale
            print(f"Upscaling image: {args.image}")
            print("Cost: 20 tokens (Magnific Precision Upscale)")
            print()
            
            job = client.upscale(args.image)
            
            job_id = job['id']
            print(f"✓ Upscale job created: {job_id}")
            print(f"  Status: {job['status']}")
            
            if args.no_wait:
                print()
                print("Not waiting for completion (--no-wait specified)")
                print(f"To check status later: {sys.argv[0]} --job-id {job_id} --output <file>")
                sys.exit(0)
            
            print()
            print("Waiting for completion...")
            image_url = client.wait_for_completion(
                job_id,
                poll_interval=args.poll_interval,
                timeout=args.timeout
            )
        
        print(f"\n✓ Upscale complete!")
        print(f"Image URL: {image_url}")
        
        # Download if output specified
        if args.output:
            download_image(image_url, args.output)
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nRun scripts/setup.py first to configure API credentials.", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nCancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
