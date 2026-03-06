#!/usr/bin/env python3
"""
QR Code Generator
Generate QR codes from text, URLs, or other data.
"""

import sys
import os

try:
    import qrcode
except ImportError:
    print("Error: qrcode library not installed", file=sys.stderr)
    print("Install with: pip install qrcode[pil]", file=sys.stderr)
    sys.exit(1)


def generate_qrcode(data: str, output_file: str = "qrcode.png") -> str:
    """
    Generate a QR code from the given data.
    
    Args:
        data: The text or URL to encode in the QR code
        output_file: Path to save the QR code image (default: qrcode.png)
    
    Returns:
        Path to the generated QR code file
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,  # Controls the size (1-40)
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,  # Size of each box in pixels
        border=4,  # Border size in boxes
    )
    
    # Add data
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create an image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Save the image
    img.save(output_file)
    
    # Get absolute path
    abs_path = os.path.abspath(output_file)
    
    return abs_path


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        print("Usage: python agent.py <text_or_url> [output_file.png]", file=sys.stderr)
        print("Example: python agent.py 'https://example.com' qr.png", file=sys.stderr)
        sys.exit(1)
    
    data = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "qrcode.png"
    
    try:
        result_path = generate_qrcode(data, output_file)
        print(f"QR code generated successfully: {result_path}")
        return 0
    except Exception as e:
        print(f"Error generating QR code: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
