#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow"]
# ///
"""Print images and PDFs to any CUPS printer.

PPD-aware: reads paper sizes, margins, resolution, and duplex from the
printer's PPD file at runtime.
"""

import argparse
import json as json_mod
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)


def _get_pil():
    """Lazy import PIL - only needed for image conversion."""
    try:
        from PIL import Image
        return Image
    except ImportError:
        print("Error: PIL/Pillow not installed. Run: pip install Pillow", file=sys.stderr)
        sys.exit(1)


IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
PRINTABLE_EXTENSIONS = IMAGE_EXTENSIONS | {'.pdf'}


def is_image(file_path):
    """Check if file is an image based on extension."""
    return file_path.suffix.lower() in IMAGE_EXTENSIONS


def _resolve_allowed_roots() -> list[Path]:
    """Build the list of directories from which printing is allowed.

    Allowed roots (in order):
      1. OPENCLAW_WORKSPACE env var
      2. CWD (if it contains a skills/ directory — likely a workspace)
      3. /tmp
    """
    roots: list[Path] = []

    ws = os.environ.get("OPENCLAW_WORKSPACE")
    if ws:
        roots.append(Path(ws).resolve())

    cwd = Path.cwd().resolve()
    if (cwd / "skills").is_dir() and cwd not in roots:
        roots.append(cwd)

    roots.append(Path("/tmp").resolve())
    return roots


def _validate_file_path(file_path: Path) -> Path:
    """Validate and resolve a file path for printing.

    Security checks:
      1. Resolve symlinks, then verify the *real* path is inside an
         allowed root (workspace or /tmp). This lets symlinks within
         the workspace work while blocking ``ln -s ~/.ssh/id_rsa x.pdf``.
      2. Verify the *resolved* file has a printable extension.
    """
    if not file_path.exists():
        raise ValueError(f"Not a file: {file_path}")

    resolved = file_path.resolve()

    # Must be a regular file (not a device, directory, etc.)
    if not resolved.is_file():
        raise ValueError(f"Not a regular file: {file_path}")

    # The resolved (real) path must be inside an allowed root
    allowed = _resolve_allowed_roots()
    if not any(resolved == root or resolved.is_relative_to(root) for root in allowed):
        raise ValueError(
            f"File is outside the allowed directories "
            f"(workspace, /tmp): {resolved}"
        )

    # Check the resolved file's extension (the actual file on disk)
    if resolved.suffix.lower() not in PRINTABLE_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {resolved.suffix}. "
            f"Supported: {', '.join(sorted(PRINTABLE_EXTENSIONS))}"
        )

    return resolved


def _validate_printer_name(name: str) -> str:
    """Validate printer name to prevent injection via crafted names.

    CUPS printer names contain only alphanumeric, hyphen, underscore, and period.
    """
    if not re.match(r'^[\w.\-]+$', name):
        raise ValueError(f"Invalid printer name: {name!r}")
    return name


def get_default_printer():
    """Get the system default printer name."""
    result = subprocess.run(['lpstat', '-d'], capture_output=True, text=True)
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            if line.startswith("system default destination:"):
                return line.split(":", 1)[1].strip()
    return None


def get_printer_specs(printer):
    """Get paper size, imageable area, and resolution from PPD file.

    Returns dict with:
      media: str (e.g. 'A4')
      page_w, page_h: float (points)
      img_x1, img_y1, img_x2, img_y2: float (imageable area in points)
      dpi: int
      duplex: str or None
    """
    specs = {
        'media': 'A4', 'page_w': 595.28, 'page_h': 841.89,
        'img_x1': 0, 'img_y1': 0, 'img_x2': 595.28, 'img_y2': 841.89,
        'dpi': 300, 'duplex': None,
    }

    safe_name = _validate_printer_name(printer)
    ppd_path = Path(f"/etc/cups/ppd/{safe_name}.ppd")
    if not ppd_path.exists():
        ppd_path = Path(f"/private/etc/cups/ppd/{safe_name}.ppd")
    if not ppd_path.exists():
        return specs

    ppd = ppd_path.read_text()

    def ppd_val(key):
        for line in ppd.splitlines():
            if line.startswith(f"*{key}:"):
                return line.split(":", 1)[1].strip().strip('"')
        return None

    # Default media
    media = ppd_val("DefaultPageSize") or "A4"
    specs['media'] = media

    # Resolution
    res_str = ppd_val("DefaultResolution") or "300x300dpi"
    try:
        specs['dpi'] = int(res_str.split("x")[0])
    except ValueError:
        specs['dpi'] = 300

    # Duplex
    duplex = ppd_val("DefaultDuplex")
    specs['duplex'] = duplex if duplex and duplex != "None" else None

    # Paper dimensions for default media
    for line in ppd.splitlines():
        if line.startswith(f"*PaperDimension {media}:"):
            dims = line.split('"')[1].split()
            if len(dims) == 2:
                specs['page_w'] = float(dims[0])
                specs['page_h'] = float(dims[1])
        elif line.startswith(f"*ImageableArea {media}:"):
            dims = line.split('"')[1].split()
            if len(dims) == 4:
                specs['img_x1'] = float(dims[0])
                specs['img_y1'] = float(dims[1])
                specs['img_x2'] = float(dims[2])
                specs['img_y2'] = float(dims[3])

    return specs


def convert_image_to_pdf(image_path, specs):
    """Convert image to PDF sized for the target printer's current media.

    Uses the printer's PPD specs for page size, imageable area, and resolution.
    """
    Image = _get_pil()
    img = Image.open(image_path)

    # Convert to RGB if needed (for PNG with transparency, etc.)
    if img.mode in ('RGBA', 'LA', 'P'):
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = rgb_img
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Create temporary PDF
    temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    temp_pdf.close()

    dpi = specs['dpi']

    # Full page size in pixels at printer DPI
    page_w_px = int(specs['page_w'] / 72.0 * dpi)
    page_h_px = int(specs['page_h'] / 72.0 * dpi)

    # Imageable (printable) area in pixels
    img_x1 = int(specs['img_x1'] / 72.0 * dpi)
    img_y1 = int(specs['img_y1'] / 72.0 * dpi)
    img_x2 = int(specs['img_x2'] / 72.0 * dpi)
    img_y2 = int(specs['img_y2'] / 72.0 * dpi)
    printable_w = img_x2 - img_x1
    printable_h = img_y2 - img_y1

    # Scale image to fit within printable area, preserving aspect ratio
    img_aspect = img.width / img.height
    printable_aspect = printable_w / printable_h

    if img_aspect > printable_aspect:
        new_width = printable_w
        new_height = int(printable_w / img_aspect)
    else:
        new_height = printable_h
        new_width = int(printable_h * img_aspect)

    # Resize image at full printer resolution
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Create full page canvas and center image within printable area
    canvas = Image.new('RGB', (page_w_px, page_h_px), (255, 255, 255))
    x_offset = img_x1 + (printable_w - new_width) // 2
    y_offset = img_y1 + (printable_h - new_height) // 2
    canvas.paste(img_resized, (x_offset, y_offset))

    # Save as PDF at printer DPI
    canvas.save(temp_pdf.name, "PDF", resolution=float(dpi))

    media = specs['media']
    pt_to_mm = 25.4 / 72.0
    w_mm = specs['page_w'] * pt_to_mm
    h_mm = specs['page_h'] * pt_to_mm
    print(f"[print] Generated PDF: {media} ({w_mm:.0f}×{h_mm:.0f}mm) at {dpi} DPI", file=sys.stderr)

    return temp_pdf.name


def _detect_pdf_orientation(pdf_path):
    """Detect whether a PDF's first page is portrait or landscape.

    Parses the MediaBox from the raw PDF bytes.  Returns 'portrait',
    'landscape', or None if detection fails.
    """
    try:
        data = Path(pdf_path).read_bytes()[:8192]  # first 8KB is enough
        # Match /MediaBox [x1 y1 x2 y2]  (ints or floats)
        m = re.search(
            rb'/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]',
            data,
        )
        if m:
            x1, y1, x2, y2 = (float(v) for v in m.groups())
            w, h = x2 - x1, y2 - y1
            return 'portrait' if h > w else 'landscape'
    except Exception:
        pass
    return None


def print_file(file_path, printer=None, extra_options=None):
    """Print file to printer using lp command.

    Args:
        extra_options: List of CUPS option strings like
            ``["InputSlot=tray-1", "cupsPrintQuality=High"]``.

    Returns (success: bool, job_id: str or None).
    """
    if not printer:
        printer = get_default_printer()
        if not printer:
            print("Error: No default printer set. Use --printer to specify one.", file=sys.stderr)
            return False, None

    specs = get_printer_specs(printer)

    cmd = [
        'lp',
        '-d', printer,
        str(file_path),
        '-o', f'media={specs["media"]}',
        '-o', 'fit-to-page',
    ]

    # Add duplex if the printer supports it
    # Detect document orientation for correct binding:
    #   portrait  → long-edge  (book-style flip left/right)
    #   landscape → short-edge (book-style flip left/right)
    if specs['duplex']:
        orientation = _detect_pdf_orientation(file_path)
        if orientation == 'landscape':
            cmd.extend(['-o', 'sides=two-sided-short-edge'])
        else:
            # Default to long-edge (portrait / unknown)
            cmd.extend(['-o', 'sides=two-sided-long-edge'])

    # Add any extra CUPS options
    for opt in (extra_options or []):
        cmd.extend(['-o', opt])

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        output = result.stdout.strip()
        # Parse job ID from lp output like "request id is HP_...-123 (1 file(s))"
        job_id = None
        m = re.search(r'request id is (\S+)', output)
        if m:
            job_id = m.group(1)
        return True, job_id
    else:
        print(f"Print failed: {result.stderr}", file=sys.stderr)
        return False, None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_list(args):
    """List available printers."""
    result = subprocess.run(['lpstat', '-p', '-d'], capture_output=True, text=True)
    if result.returncode != 0:
        if args.json:
            print(json_mod.dumps({"error": "Could not list printers"}))
        else:
            print("Error: Could not list printers", file=sys.stderr)
        return 1

    # Parse default printer
    default = None
    for line in result.stdout.splitlines():
        if line.startswith("system default destination:"):
            default = line.split(":", 1)[1].strip()

    # Parse printer entries
    printers = []
    for line in result.stdout.splitlines():
        if line.startswith("printer "):
            parts = line.split()
            name = parts[1]
            status = "idle" if "idle" in line else "busy" if "printing" in line else "unknown"
            enabled = "enabled" in line
            printers.append({
                "name": name,
                "status": status,
                "enabled": enabled,
                "default": name == default,
            })

    if args.json:
        print(json_mod.dumps(printers, indent=2))
    else:
        if not printers:
            print("No printers found.")
            return 0
        for p in printers:
            tag = " (default)" if p["default"] else ""
            state = f"{p['status']}, {'enabled' if p['enabled'] else 'disabled'}"
            print(f"  {p['name']}  [{state}]{tag}")

    return 0


def cmd_info(args):
    """Show printer info from PPD file."""
    printer = args.printer or get_default_printer()
    if not printer:
        msg = "No default printer set. Use --printer to specify one."
        if args.json:
            print(json_mod.dumps({"error": msg}))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        return 1

    # Find PPD file
    try:
        safe_name = _validate_printer_name(printer)
    except ValueError as e:
        msg = str(e)
        if args.json:
            print(json_mod.dumps({"error": msg}))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        return 1

    ppd_path = Path(f"/etc/cups/ppd/{safe_name}.ppd")
    if not ppd_path.exists():
        ppd_path = Path(f"/private/etc/cups/ppd/{safe_name}.ppd")
    if not ppd_path.exists():
        msg = f"No PPD file found for {printer}"
        if args.json:
            print(json_mod.dumps({"error": msg}))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        return 1

    ppd = ppd_path.read_text()
    pt_to_mm = 25.4 / 72.0

    def ppd_val(key):
        for line in ppd.splitlines():
            if line.startswith(f"*{key}:"):
                return line.split(":", 1)[1].strip().strip('"')
        return None

    # General info
    info = {"printer": printer}
    field_map = [
        ("Manufacturer", "manufacturer"),
        ("ModelName", "model"),
        ("ColorDevice", "color"),
        ("Throughput", "pages_per_min"),
        ("DefaultPageSize", "default_paper"),
        ("DefaultDuplex", "default_duplex"),
    ]
    for ppd_key, json_key in field_map:
        val = ppd_val(ppd_key)
        if val:
            info[json_key] = val

    # Parse resolution into structured object
    res_str = ppd_val("DefaultResolution")
    if res_str:
        import re as _re
        m = _re.match(r"(\d+)(?:x(\d+))?\s*dpi", res_str, _re.IGNORECASE)
        if m:
            x_dpi = int(m.group(1))
            y_dpi = int(m.group(2)) if m.group(2) else x_dpi
            info["resolution"] = {"x_dpi": x_dpi, "y_dpi": y_dpi}
        else:
            info["resolution"] = res_str  # fallback to raw string

    # Parse paper sizes with margins
    paper_dims = {}
    imageable = {}
    for line in ppd.splitlines():
        if line.startswith("*PaperDimension "):
            name = line.split()[1].rstrip(":")
            dims = line.split('"')[1].split()
            if len(dims) == 2:
                paper_dims[name] = (float(dims[0]), float(dims[1]))
        elif line.startswith("*ImageableArea "):
            name = line.split()[1].rstrip(":")
            dims = line.split('"')[1].split()
            if len(dims) == 4:
                imageable[name] = tuple(float(d) for d in dims)

    # Parse input slots
    slots = []
    for line in ppd.splitlines():
        if line.startswith("*InputSlot "):
            slots.append(line.split()[1].rstrip(":"))
    if slots:
        info["trays"] = slots

    # Paper sizes
    default_paper = ppd_val("DefaultPageSize")
    paper_list = []
    for name in sorted(paper_dims.keys()):
        w, h = paper_dims[name]
        entry = {
            "name": name,
            "width_mm": round(w * pt_to_mm, 1),
            "height_mm": round(h * pt_to_mm, 1),
            "default": name == default_paper,
        }
        if name in imageable:
            x1, y1, x2, y2 = imageable[name]
            entry["margins_mm"] = {
                "left": round(x1 * pt_to_mm, 1),
                "bottom": round(y1 * pt_to_mm, 1),
                "right": round((w - x2) * pt_to_mm, 1),
                "top": round((h - y2) * pt_to_mm, 1),
            }
        paper_list.append(entry)
    info["paper_sizes"] = paper_list

    if args.json:
        print(json_mod.dumps(info, indent=2))
    else:
        print(f"Printer: {printer}\n")

        display_fields = [
            ("manufacturer", "Manufacturer"),
            ("model", "Model"),
            ("resolution", "Resolution"),
            ("color", "Color"),
            ("pages_per_min", "Pages/min"),
            ("default_paper", "Default paper"),
            ("default_duplex", "Default duplex"),
        ]
        for key, label in display_fields:
            if key in info:
                val = info[key]
                if key == "resolution" and isinstance(val, dict):
                    if val["x_dpi"] == val["y_dpi"]:
                        val = f"{val['x_dpi']} dpi"
                    else:
                        val = f"{val['x_dpi']}x{val['y_dpi']} dpi"
                print(f"  {label}: {val}")

        if slots:
            print(f"  Trays: {', '.join(slots)}")

        if paper_list:
            print(f"\nPaper sizes ({len(paper_list)}):\n")
            for p in paper_list:
                tag = " (default)" if p["default"] else ""
                margin_str = ""
                if "margins_mm" in p:
                    m = p["margins_mm"]
                    vals = [m["left"], m["bottom"], m["right"], m["top"]]
                    if all(abs(v - vals[0]) < 0.1 for v in vals):
                        margin_str = f"  margins: {vals[0]:.1f}mm"
                    else:
                        margin_str = f"  margins: L{m['left']:.1f} B{m['bottom']:.1f} R{m['right']:.1f} T{m['top']:.1f}mm"
                print(f"  {p['name']}: {p['width_mm']:.0f} × {p['height_mm']:.0f} mm{margin_str}{tag}")

    return 0


def cmd_options(args):
    """Show options/capabilities for a printer."""
    printer = args.printer or get_default_printer()
    if not printer:
        msg = "No default printer set. Use --printer to specify one."
        if args.json:
            print(json_mod.dumps({"error": msg}))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        return 1

    try:
        printer = _validate_printer_name(printer)
    except ValueError as e:
        msg = str(e)
        if args.json:
            print(json_mod.dumps({"error": msg}))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        return 1

    result = subprocess.run(['lpoptions', '-p', printer, '-l'], capture_output=True, text=True)
    if result.returncode != 0:
        msg = f"Could not get options for {printer}"
        if args.json:
            print(json_mod.dumps({"error": msg}))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        return 1

    options = []
    for line in result.stdout.splitlines():
        if '/' in line and ':' in line:
            key_label, _, values_str = line.partition(':')
            option, _, label = key_label.partition('/')
            values = values_str.strip().split()

            current = None
            all_values = []
            for v in values:
                if v.startswith('*'):
                    current = v[1:]
                    all_values.append(current)
                else:
                    all_values.append(v)

            options.append({
                "option": option.strip(),
                "label": label.strip(),
                "current": current,
                "values": all_values,
            })

    if args.json:
        print(json_mod.dumps(options, indent=2))
    else:
        print(f"Options for {printer}:\n")
        for opt in options:
            current_str = f" = {opt['current']}" if opt['current'] else ""
            print(f"  {opt['label']}{current_str}")
            if len(opt['values']) > 1:
                print(f"    Options: {', '.join(opt['values'])}")

    return 0


def cmd_print(args):
    """Print a file."""
    try:
        file_path = _validate_file_path(args.file)
    except ValueError as e:
        msg = str(e)
        if args.json:
            print(json_mod.dumps({"ok": False, "error": msg}))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        return 1

    printer = args.printer or get_default_printer()
    if not printer:
        msg = "No default printer set. Use --printer to specify one."
        if args.json:
            print(json_mod.dumps({"ok": False, "error": msg}))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        return 1

    try:
        printer = _validate_printer_name(printer)
    except ValueError as e:
        msg = str(e)
        if args.json:
            print(json_mod.dumps({"ok": False, "error": msg}))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        return 1

    file_to_print = file_path
    temp_pdf = None

    # Handle images by converting to PDF first
    if is_image(file_path):
        if not args.json:
            print("[print] Converting image to PDF...", file=sys.stderr)
        try:
            specs = get_printer_specs(printer)
            temp_pdf = convert_image_to_pdf(file_path, specs)
            file_to_print = Path(temp_pdf)
        except Exception as e:
            msg = f"Error converting image: {e}"
            if args.json:
                print(json_mod.dumps({"ok": False, "error": msg}))
            else:
                print(msg, file=sys.stderr)
            return 1

    success, job_id = print_file(file_to_print, printer, extra_options=args.option)

    # Clean up temp file
    if temp_pdf:
        Path(temp_pdf).unlink(missing_ok=True)

    if args.json:
        result = {
            "ok": success,
            "printer": printer,
            "file": str(file_path),
        }
        if job_id:
            result["job_id"] = job_id
        print(json_mod.dumps(result, indent=2))
    else:
        if success:
            id_str = f" (job {job_id})" if job_id else ""
            print(f"[print] ✓ Sent to {printer}{id_str}")

    return 0 if success else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description='Print images and PDFs to any CUPS printer'
    )
    subparsers = parser.add_subparsers(dest='command')

    # list
    sub_list = subparsers.add_parser('list', help='List available printers')
    sub_list.add_argument('--json', action='store_true', help='JSON output')
    sub_list.set_defaults(func=cmd_list)

    # info
    sub_info = subparsers.add_parser('info', help='Show printer specs (paper sizes, margins, capabilities)')
    sub_info.add_argument('--printer', default=None, help='Printer name (default: system default)')
    sub_info.add_argument('--json', action='store_true', help='JSON output')
    sub_info.set_defaults(func=cmd_info)

    # options
    sub_options = subparsers.add_parser('options', help='Show CUPS options for a printer')
    sub_options.add_argument('--printer', default=None, help='Printer name (default: system default)')
    sub_options.add_argument('--json', action='store_true', help='JSON output')
    sub_options.set_defaults(func=cmd_options)

    # print
    sub_print = subparsers.add_parser('print', help='Print a file (PDF or image)')
    sub_print.add_argument('file', type=Path, help='File to print')
    sub_print.add_argument('--printer', default=None, help='Printer name (default: system default)')
    sub_print.add_argument('-o', '--option', action='append', metavar='KEY=VALUE',
                           help='CUPS option (repeatable, e.g. -o InputSlot=tray-1)')
    sub_print.add_argument('--json', action='store_true', help='JSON output')
    sub_print.set_defaults(func=cmd_print)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main() or 0)
