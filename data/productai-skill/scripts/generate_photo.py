#!/usr/bin/env python3
"""
ProductAI Photo Generator

Generate professional AI product photos from existing images.
"""

import argparse
import sys
from pathlib import Path
from typing import List
import requests

from productai_client import create_client_from_config, ProductAIClient


AVAILABLE_MODELS = {
    'gpt-low': 'GPT Low Quality (2 tokens)',
    'gpt-medium': 'GPT Medium Quality (3 tokens)',
    'gpt-high': 'GPT High Quality (8 tokens)',
    'kontext-pro': 'Kontext Pro (3 tokens)',
    'nanobanana': 'Nano Banana (3 tokens)',
    'nanobananapro': 'Nano Banana Pro (8 tokens)',
    'seedream': 'Seedream (3 tokens)'
}


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
        description='Generate AI-powered product photos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Generate with custom background
  %(prog)s --image product.jpg --prompt "modern living room" --output result.png
  
  # Use multiple reference images (nanobanana/seedream support 2 images)
  %(prog)s --image product1.jpg product2.jpg --prompt "Combine both products" --output result.png
  
  # High quality output
  %(prog)s --image product.jpg --prompt "studio background" --model nanobananapro --output hq.png
  
  # Just get the job ID (don't wait)
  %(prog)s --image product.jpg --prompt "white background" --no-wait

Available Models:
  gpt-low         GPT Low Quality (2 tokens)
  gpt-medium      GPT Medium Quality (3 tokens)
  gpt-high        GPT High Quality (8 tokens)
  kontext-pro     Kontext Pro (3 tokens)
  nanobanana      Nano Banana (3 tokens) - DEFAULT
  nanobananapro   Nano Banana Pro (8 tokens)
  seedream        Seedream (3 tokens)
        '''
    )
    
    parser.add_argument(
        '--image',
        required=True,
        nargs='+',
        help='Image URL(s) to process. Can be single URL or multiple URLs for models that support it.'
    )
    parser.add_argument(
        '--prompt',
        required=True,
        help='Text description of desired output (e.g., "modern living room background")'
    )
    parser.add_argument(
        '--model',
        default='nanobanana',
        choices=list(AVAILABLE_MODELS.keys()),
        help='Model to use for generation (default: nanobanana)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output file path (e.g., result.png). If not specified, prints image URL only.'
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
    
    try:
        # Create client
        client = create_client_from_config(args.config)
        
        # If resuming existing job
        if args.job_id:
            print(f"Checking status of job {args.job_id}...")
            image_url = client.wait_for_completion(
                args.job_id,
                poll_interval=args.poll_interval,
                timeout=args.timeout
            )
        else:
            # Prepare image URL(s)
            image_url_input = args.image[0] if len(args.image) == 1 else args.image
            
            # Validate multi-image support
            if isinstance(image_url_input, list) and len(image_url_input) > 1:
                multi_image_models = ['nanobanana', 'nanobananapro', 'seedream']
                if args.model not in multi_image_models:
                    print(f"Error: Model '{args.model}' does not support multiple images.", file=sys.stderr)
                    print(f"Use one of: {', '.join(multi_image_models)}", file=sys.stderr)
                    sys.exit(1)
                if len(image_url_input) > 2:
                    print("Error: Maximum 2 reference images supported", file=sys.stderr)
                    sys.exit(1)
            
            # Start generation
            print(f"Generating with model: {AVAILABLE_MODELS[args.model]}")
            if isinstance(image_url_input, list):
                print(f"Reference images: {len(image_url_input)}")
                for i, url in enumerate(image_url_input, 1):
                    print(f"  {i}. {url}")
            else:
                print(f"Image: {image_url_input}")
            print(f"Prompt: {args.prompt}")
            print()
            
            job = client.generate(
                image_url=image_url_input,
                prompt=args.prompt,
                model=args.model
            )
            
            job_id = job['id']
            print(f"✓ Job created: {job_id}")
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
        
        print(f"\n✓ Generation complete!")
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
