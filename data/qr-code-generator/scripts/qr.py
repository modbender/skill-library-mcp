#!/usr/bin/env python3
"""
QR Code Generator - Create customizable QR codes

Generate QR codes for URLs, text, WiFi, vCards, and more with custom styling.

Requires: pip install qrcode[pil] segno
"""

import argparse
import json
import sys
import csv
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer
except ImportError:
    print("Error: qrcode library not installed", file=sys.stderr)
    print("Install with: pip install qrcode[pil]", file=sys.stderr)
    sys.exit(1)

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Error: Pillow library not installed", file=sys.stderr)
    print("Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)

try:
    import segno
except ImportError:
    segno = None


# ============================================================================
# Data Type Formatters
# ============================================================================

def format_url(data: str) -> str:
    """Format URL data"""
    if not data.startswith(('http://', 'https://')):
        return f"https://{data}"
    return data


def format_wifi(ssid: str, password: str = "", security: str = "WPA", hidden: bool = False) -> str:
    """Format WiFi credentials"""
    security = security.upper()
    if security not in ['WPA', 'WEP', 'nopass']:
        security = 'WPA'
    
    hidden_str = 'true' if hidden else 'false'
    
    if security == 'nopass':
        return f"WIFI:T:{security};S:{ssid};H:{hidden_str};;"
    else:
        return f"WIFI:T:{security};S:{ssid};P:{password};H:{hidden_str};;"


def format_vcard(
    name: str,
    phone: Optional[str] = None,
    phone_home: Optional[str] = None,
    phone_work: Optional[str] = None,
    email: Optional[str] = None,
    organization: Optional[str] = None,
    title: Optional[str] = None,
    url: Optional[str] = None,
    address: Optional[str] = None
) -> str:
    """Format vCard (contact card)"""
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{name}"
    ]
    
    if phone:
        lines.append(f"TEL;TYPE=CELL:{phone}")
    if phone_home:
        lines.append(f"TEL;TYPE=HOME:{phone_home}")
    if phone_work:
        lines.append(f"TEL;TYPE=WORK:{phone_work}")
    if email:
        lines.append(f"EMAIL:{email}")
    if organization:
        lines.append(f"ORG:{organization}")
    if title:
        lines.append(f"TITLE:{title}")
    if url:
        lines.append(f"URL:{url}")
    if address:
        lines.append(f"ADR:;;{address}")
    
    lines.append("END:VCARD")
    return "\n".join(lines)


def format_email(email: str, subject: Optional[str] = None, body: Optional[str] = None) -> str:
    """Format mailto link"""
    result = f"mailto:{email}"
    params = []
    
    if subject:
        params.append(f"subject={subject}")
    if body:
        params.append(f"body={body}")
    
    if params:
        result += "?" + "&".join(params)
    
    return result


def format_phone(phone: str) -> str:
    """Format phone number"""
    return f"tel:{phone}"


def format_sms(phone: str, message: Optional[str] = None) -> str:
    """Format SMS"""
    result = f"sms:{phone}"
    if message:
        result += f"?body={message}"
    return result


def format_geo(
    latitude: float,
    longitude: float,
    altitude: Optional[float] = None,
    location_name: Optional[str] = None
) -> str:
    """Format geographic location"""
    if altitude is not None:
        return f"geo:{latitude},{longitude},{altitude}"
    return f"geo:{latitude},{longitude}"


def format_event(
    title: str,
    start: str,
    end: str,
    location: Optional[str] = None,
    description: Optional[str] = None
) -> str:
    """Format calendar event (iCalendar)"""
    lines = [
        "BEGIN:VEVENT",
        f"SUMMARY:{title}",
        f"DTSTART:{start.replace('-', '').replace(':', '')}",
        f"DTEND:{end.replace('-', '').replace(':', '')}"
    ]
    
    if location:
        lines.append(f"LOCATION:{location}")
    if description:
        lines.append(f"DESCRIPTION:{description}")
    
    lines.append("END:VEVENT")
    return "\n".join(lines)


# ============================================================================
# QR Code Generation
# ============================================================================

def parse_color(color_str: str) -> tuple:
    """Parse color string to RGB tuple"""
    color_str = color_str.lower().strip()
    
    # Named colors
    colors = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128),
        'pink': (255, 192, 203),
        'brown': (165, 42, 42),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128),
    }
    
    if color_str in colors:
        return colors[color_str]
    
    # Hex color (#RRGGBB)
    if color_str.startswith('#'):
        hex_color = color_str[1:]
        if len(hex_color) == 6:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # RGB color (rgb(r,g,b))
    if color_str.startswith('rgb(') and color_str.endswith(')'):
        rgb_values = color_str[4:-1].split(',')
        if len(rgb_values) == 3:
            return tuple(int(v.strip()) for v in rgb_values)
    
    # Default to black
    return (0, 0, 0)


def generate_qr_code(
    data: str,
    output_path: str = "qrcode.png",
    fg_color: str = "black",
    bg_color: str = "white",
    error_correction: str = "M",
    box_size: int = 10,
    border: int = 4,
    logo_path: Optional[str] = None,
    logo_size: int = 20,
    output_format: str = "png"
) -> bool:
    """Generate QR code with customization options"""
    
    # Map error correction
    error_levels = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H
    }
    error_level = error_levels.get(error_correction.upper(), qrcode.constants.ERROR_CORRECT_M)
    
    # Create QR code
    qr = qrcode.QRCode(
        version=None,  # Auto-determine version
        error_correction=error_level,
        box_size=box_size,
        border=border,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    # Parse colors
    fill_color = parse_color(fg_color)
    back_color = parse_color(bg_color) if bg_color.lower() != 'transparent' else None
    
    # Generate image
    if output_format == "terminal":
        # Print to terminal
        qr.print_ascii(invert=True)
        return True
    
    # Create PIL image
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    
    # Add logo if specified
    if logo_path:
        try:
            logo = Image.open(logo_path)
            
            # Calculate logo size
            qr_width, qr_height = img.size
            logo_max_size = int(qr_width * (logo_size / 100))
            
            # Resize logo
            logo.thumbnail((logo_max_size, logo_max_size), Image.LANCZOS)
            
            # Calculate position (center)
            logo_pos = (
                (qr_width - logo.width) // 2,
                (qr_height - logo.height) // 2
            )
            
            # Paste logo
            img.paste(logo, logo_pos, logo if logo.mode == 'RGBA' else None)
            
        except Exception as e:
            print(f"Warning: Could not add logo: {e}", file=sys.stderr)
    
    # Save image
    try:
        if output_format == "svg":
            # Use segno for SVG if available
            if segno:
                qr_segno = segno.make(data, error=error_correction.lower())
                qr_segno.save(
                    output_path,
                    scale=box_size,
                    border=border,
                    dark=fg_color,
                    light=bg_color if bg_color.lower() != 'transparent' else None
                )
            else:
                print("Warning: segno library not available for SVG output", file=sys.stderr)
                img.save(output_path)
        elif output_format == "pdf":
            img.save(output_path, "PDF")
        elif output_format == "eps":
            img.save(output_path, "EPS")
        else:  # PNG
            img.save(output_path)
        
        return True
    
    except Exception as e:
        print(f"Error saving QR code: {e}", file=sys.stderr)
        return False


# ============================================================================
# Batch Processing
# ============================================================================

def process_batch_txt(input_file: str, output_dir: str, args: argparse.Namespace) -> int:
    """Process batch from text file (one entry per line)"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    count = 0
    with open(input_file, 'r') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            output_file = output_path / f"qr_{i:03d}.{args.format}"
            
            if generate_qr_code(
                data=line,
                output_path=str(output_file),
                fg_color=args.fg_color,
                bg_color=args.bg_color,
                error_correction=args.error_correction,
                box_size=args.box_size,
                border=args.border,
                logo_path=args.logo,
                logo_size=args.logo_size,
                output_format=args.format
            ):
                print(f"Generated: {output_file.name}", file=sys.stderr)
                count += 1
    
    return count


def process_batch_csv(input_file: str, output_dir: str, args: argparse.Namespace) -> int:
    """Process batch from CSV file"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    count = 0
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader, 1):
            # Determine data based on type
            if args.type == "vcard":
                data = format_vcard(
                    name=row.get('name', ''),
                    phone=row.get('phone'),
                    email=row.get('email'),
                    organization=row.get('organization'),
                    title=row.get('title')
                )
            else:
                data = row.get('data', row.get('url', ''))
            
            output_file = row.get('filename', f"qr_{i:03d}.{args.format}")
            output_file = output_path / output_file
            
            if generate_qr_code(
                data=data,
                output_path=str(output_file),
                fg_color=args.fg_color,
                bg_color=args.bg_color,
                error_correction=args.error_correction,
                box_size=args.box_size,
                border=args.border,
                logo_path=args.logo,
                logo_size=args.logo_size,
                output_format=args.format
            ):
                print(f"Generated: {output_file.name}", file=sys.stderr)
                count += 1
    
    return count


def process_batch_json(input_file: str, output_dir: str, args: argparse.Namespace) -> int:
    """Process batch from JSON file"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(input_file, 'r') as f:
        configs = json.load(f)
    
    count = 0
    for i, config in enumerate(configs, 1):
        data = config.get('data', '')
        
        # Format data based on type
        qr_type = config.get('type', 'url')
        if qr_type == 'wifi':
            data = format_wifi(
                config.get('ssid', ''),
                config.get('password', ''),
                config.get('security', 'WPA'),
                config.get('hidden', False)
            )
        
        output_file = config.get('output', f"qr_{i:03d}.{args.format}")
        output_file = output_path / output_file
        
        if generate_qr_code(
            data=data,
            output_path=str(output_file),
            fg_color=config.get('fg_color', args.fg_color),
            bg_color=config.get('bg_color', args.bg_color),
            error_correction=config.get('error_correction', args.error_correction),
            box_size=config.get('box_size', args.box_size),
            border=config.get('border', args.border),
            logo_path=config.get('logo', args.logo),
            logo_size=config.get('logo_size', args.logo_size),
            output_format=config.get('format', args.format)
        ):
            print(f"Generated: {output_file.name}", file=sys.stderr)
            count += 1
    
    return count


# ============================================================================
# Main Function
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate customizable QR codes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple URL
  %(prog)s "https://example.com"
  
  # WiFi credentials
  %(prog)s --type wifi --ssid "MyNetwork" --password "secret123"
  
  # Contact card
  %(prog)s --type vcard --name "John Doe" --phone "+1234567890" --email "john@example.com"
  
  # Custom colors and logo
  %(prog)s "https://company.com" --fg-color blue --bg-color white --logo logo.png
  
  # Batch generation
  %(prog)s --batch urls.txt --output-dir qrcodes/
        """
    )
    
    # Main data argument
    parser.add_argument(
        "data",
        nargs="?",
        help="Data to encode (URL, text, etc.)"
    )
    
    # General options
    parser.add_argument(
        "--type",
        choices=["url", "text", "wifi", "vcard", "email", "phone", "sms", "geo", "event"],
        default="url",
        help="Type of data to encode (default: url)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="qrcode.png",
        help="Output filename (default: qrcode.png)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["png", "svg", "pdf", "eps", "terminal"],
        default="png",
        help="Output format (default: png)"
    )
    
    # Customization
    parser.add_argument(
        "--fg-color",
        default="black",
        help="Foreground color (default: black)"
    )
    
    parser.add_argument(
        "--bg-color",
        default="white",
        help="Background color (default: white)"
    )
    
    parser.add_argument(
        "--error-correction",
        choices=["L", "M", "Q", "H"],
        default="M",
        help="Error correction level (default: M)"
    )
    
    parser.add_argument(
        "--box-size",
        type=int,
        default=10,
        help="Box size in pixels (default: 10)"
    )
    
    parser.add_argument(
        "--border",
        type=int,
        default=4,
        help="Border size in modules (default: 4)"
    )
    
    parser.add_argument(
        "--logo",
        help="Logo image path to embed"
    )
    
    parser.add_argument(
        "--logo-size",
        type=int,
        default=20,
        help="Logo size as percentage of QR code (default: 20)"
    )
    
    # WiFi options
    parser.add_argument("--ssid", help="WiFi SSID")
    parser.add_argument("--password", help="WiFi password")
    parser.add_argument("--security", choices=["WPA", "WEP", "nopass"], default="WPA", help="WiFi security")
    parser.add_argument("--hidden", action="store_true", help="Hidden network")
    
    # vCard options
    parser.add_argument("--name", help="Contact name")
    parser.add_argument("--phone", help="Phone number")
    parser.add_argument("--phone-home", help="Home phone")
    parser.add_argument("--phone-work", help="Work phone")
    parser.add_argument("--email", help="Email address")
    parser.add_argument("--organization", help="Organization")
    parser.add_argument("--title", help="Job title")
    parser.add_argument("--url", help="Website URL")
    parser.add_argument("--address", help="Address")
    
    # Email options
    parser.add_argument("--subject", help="Email subject")
    parser.add_argument("--body", help="Email body")
    
    # SMS options
    parser.add_argument("--message", help="SMS message")
    
    # Geo options
    parser.add_argument("--latitude", type=float, help="Latitude")
    parser.add_argument("--longitude", type=float, help="Longitude")
    parser.add_argument("--altitude", type=float, help="Altitude")
    parser.add_argument("--location-name", help="Location name")
    
    # Event options
    parser.add_argument("--event-title", help="Event title")
    parser.add_argument("--event-start", help="Event start (ISO format)")
    parser.add_argument("--event-end", help="Event end (ISO format)")
    parser.add_argument("--event-location", help="Event location")
    parser.add_argument("--event-description", help="Event description")
    
    # Batch options
    parser.add_argument("--batch", help="Batch input file (txt, csv, json)")
    parser.add_argument("--output-dir", default="qrcodes", help="Output directory for batch")
    
    args = parser.parse_args()
    
    # Handle batch processing
    if args.batch:
        input_path = Path(args.batch)
        
        if not input_path.exists():
            print(f"Error: Input file not found: {args.batch}", file=sys.stderr)
            sys.exit(1)
        
        count = 0
        if input_path.suffix == '.txt':
            count = process_batch_txt(args.batch, args.output_dir, args)
        elif input_path.suffix == '.csv':
            count = process_batch_csv(args.batch, args.output_dir, args)
        elif input_path.suffix == '.json':
            count = process_batch_json(args.batch, args.output_dir, args)
        else:
            print(f"Error: Unsupported batch file format: {input_path.suffix}", file=sys.stderr)
            sys.exit(1)
        
        print(f"\nGenerated {count} QR codes in {args.output_dir}/", file=sys.stderr)
        return
    
    # Single QR code generation
    if not args.data and args.type not in ['wifi', 'vcard', 'email', 'phone', 'sms', 'geo', 'event']:
        parser.error("Data argument required (or use --type with specific options)")
    
    # Format data based on type
    data = args.data or ""
    
    if args.type == "url":
        data = format_url(data)
    elif args.type == "text":
        pass  # Use as-is
    elif args.type == "wifi":
        if not args.ssid:
            parser.error("--ssid required for WiFi QR codes")
        data = format_wifi(args.ssid, args.password or "", args.security, args.hidden)
    elif args.type == "vcard":
        if not args.name:
            parser.error("--name required for vCard QR codes")
        data = format_vcard(
            args.name, args.phone, args.phone_home, args.phone_work,
            args.email, args.organization, args.title, args.url, args.address
        )
    elif args.type == "email":
        if not args.email:
            parser.error("--email required for email QR codes")
        data = format_email(args.email, args.subject, args.body)
    elif args.type == "phone":
        if not args.phone:
            parser.error("--phone required for phone QR codes")
        data = format_phone(args.phone)
    elif args.type == "sms":
        if not args.phone:
            parser.error("--phone required for SMS QR codes")
        data = format_sms(args.phone, args.message)
    elif args.type == "geo":
        if args.latitude is None or args.longitude is None:
            parser.error("--latitude and --longitude required for geo QR codes")
        data = format_geo(args.latitude, args.longitude, args.altitude, args.location_name)
    elif args.type == "event":
        if not all([args.event_title, args.event_start, args.event_end]):
            parser.error("--event-title, --event-start, --event-end required for event QR codes")
        data = format_event(
            args.event_title, args.event_start, args.event_end,
            args.event_location, args.event_description
        )
    
    # Generate QR code
    success = generate_qr_code(
        data=data,
        output_path=args.output,
        fg_color=args.fg_color,
        bg_color=args.bg_color,
        error_correction=args.error_correction,
        box_size=args.box_size,
        border=args.border,
        logo_path=args.logo,
        logo_size=args.logo_size,
        output_format=args.format
    )
    
    if success and args.format != "terminal":
        print(f"QR code generated: {args.output}", file=sys.stderr)
        print(f"Data: {data[:100]}{'...' if len(data) > 100 else ''}", file=sys.stderr)
    elif not success:
        sys.exit(1)


if __name__ == "__main__":
    main()