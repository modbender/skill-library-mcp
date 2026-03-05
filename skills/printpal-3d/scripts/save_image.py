#!/usr/bin/env python3
"""
Save a base64-encoded image to disk.

Used when images are pasted into the OpenClaw chat interface.
The image data comes as base64 and needs to be saved to disk
before it can be used with PrintPal.
"""

import argparse
import base64
import os
import sys
from datetime import datetime
from pathlib import Path


def get_timestamp():
    """Get timestamp for unique filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def detect_format(base64_data):
    """Detect image format from base64 header or data."""
    # Check for data URI prefix
    if base64_data.startswith('data:'):
        header = base64_data.split(',')[0]
        if 'image/png' in header:
            return 'png'
        elif 'image/jpeg' in header or 'image/jpg' in header:
            return 'jpg'
        elif 'image/gif' in header:
            return 'gif'
        elif 'image/webp' in header:
            return 'webp'
    
    # Try to detect from magic bytes
    try:
        # Remove data URI prefix if present
        if base64_data.startswith('data:'):
            base64_data = base64_data.split(',', 1)[1]
        
        # Decode first few bytes to check magic numbers
        decoded = base64.b64decode(base64_data[:32])
        
        if decoded[:8] == b'\x89PNG\r\n\x1a\n':
            return 'png'
        elif decoded[:2] == b'\xff\xd8':
            return 'jpg'
        elif decoded[:6] in (b'GIF87a', b'GIF89a'):
            return 'gif'
        elif decoded[:4] == b'RIFF' and decoded[8:12] == b'WEBP':
            return 'webp'
    except:
        pass
    
    # Default to png
    return 'png'


def main():
    parser = argparse.ArgumentParser(
        description="Save a base64-encoded image to disk"
    )
    parser.add_argument(
        "--data", "-d",
        required=True,
        help="Base64-encoded image data (with or without data: URI prefix)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=os.environ.get("PRINTPAL_OUTPUT_DIR", "printpal-output"),
        help="Output directory for saved image"
    )
    parser.add_argument(
        "--filename", "-f",
        help="Output filename (default: auto-generated with timestamp)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Detect format
    img_format = detect_format(args.data)
    
    # Generate filename
    timestamp = get_timestamp()
    if args.filename:
        filename = args.filename
        if not filename.endswith(f'.{img_format}'):
            filename = f"{filename}.{img_format}"
    else:
        filename = f"uploaded_{timestamp}.{img_format}"
    
    output_path = output_dir / filename
    
    # Extract base64 data (remove data URI prefix if present)
    base64_data = args.data
    if base64_data.startswith('data:'):
        base64_data = base64_data.split(',', 1)[1]
    
    # Decode and save
    try:
        image_data = base64.b64decode(base64_data)
        with open(output_path, 'wb') as f:
            f.write(image_data)
        
        result = {
            "success": True,
            "path": str(output_path),
            "format": img_format,
            "size": len(image_data)
        }
        
        if args.json:
            import json
            print(json.dumps(result, indent=2))
        else:
            print(f"Image saved: {output_path}")
            print(f"Format: {img_format}")
            print(f"Size: {len(image_data)} bytes")
        
        return 0
        
    except Exception as e:
        result = {
            "success": False,
            "path": None,
            "error": str(e)
        }
        
        if args.json:
            import json
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
