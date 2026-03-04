#!/usr/bin/env python3
"""
Fix font transparency in PPTX files to work around PDF export font embedding bug.

PowerPoint's "Export to PDF" sometimes fails to embed downloaded/custom fonts,
substituting built-in defaults instead — even when fonts are marked embeddable
and "Embed fonts" is checked. Setting a minimal transparency (1%) on text runs
with 0% transparency forces PowerPoint to properly embed the fonts in PDF output.

Usage:
    python fix_font_transparency.py input.pptx [output.pptx] [--transparency 1]
"""

import argparse
import os
import zipfile
import tempfile
import shutil
from xml.etree import ElementTree as ET

# OOXML namespaces
NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}

for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)

EXTRA_NS = {
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "dgm": "http://schemas.openxmlformats.org/drawingml/2006/diagram",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
    "o": "urn:schemas-microsoft-com:office:office",
    "v": "urn:schemas-microsoft-com:vml",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}
for prefix, uri in EXTRA_NS.items():
    ET.register_namespace(prefix, uri)


def alpha_value(transparency_pct):
    """Convert transparency percentage (0-100) to OOXML alpha value (0-100000)."""
    return str(int((100 - transparency_pct) * 1000))


def get_alpha_pct(fill_elem):
    """Get the current alpha percentage (0-100000 scale) from a fill element."""
    for color_tag in [f"{{{NS['a']}}}srgbClr", f"{{{NS['a']}}}schemeClr",
                      f"{{{NS['a']}}}sysClr", f"{{{NS['a']}}}prstClr",
                      f"{{{NS['a']}}}hslClr", f"{{{NS['a']}}}scrgbClr"]:
        color_elem = fill_elem.find(color_tag)
        if color_elem is not None:
            alpha_elem = color_elem.find(f"{{{NS['a']}}}alpha")
            if alpha_elem is not None:
                val = alpha_elem.get("val")
                if val:
                    return float(val)
            else:
                return 100000.0
    return None


def add_alpha_to_color(fill_elem, alpha_val):
    """Add alpha element to the color child of a fill element. Returns True if modified."""
    for color_tag in [f"{{{NS['a']}}}srgbClr", f"{{{NS['a']}}}schemeClr",
                      f"{{{NS['a']}}}sysClr", f"{{{NS['a']}}}prstClr",
                      f"{{{NS['a']}}}hslClr", f"{{{NS['a']}}}scrgbClr"]:
        color_elem = fill_elem.find(color_tag)
        if color_elem is not None:
            alpha_elem = ET.SubElement(color_elem, f"{{{NS['a']}}}alpha")
            alpha_elem.set("val", alpha_val)
            return True
    return False


def process_slide_xml(xml_bytes, transparency_pct):
    """Process a slide XML, adding transparency to fully-opaque text runs."""
    tree = ET.ElementTree(ET.fromstring(xml_bytes))
    root = tree.getroot()
    target_alpha = alpha_value(transparency_pct)
    modified = 0

    for rpr in root.iter(f"{{{NS['a']}}}rPr"):
        modified += _process_run_props(rpr, target_alpha)
    for defrpr in root.iter(f"{{{NS['a']}}}defRPr"):
        modified += _process_run_props(defrpr, target_alpha)
    for eparpr in root.iter(f"{{{NS['a']}}}endParaRPr"):
        modified += _process_run_props(eparpr, target_alpha)

    output = ET.tostring(root, encoding="unicode", xml_declaration=True)
    return output.encode("utf-8"), modified


def _process_run_props(rpr_elem, target_alpha):
    """Process a single run properties element. Returns 1 if modified, 0 otherwise."""
    solid_fill = rpr_elem.find(f"{{{NS['a']}}}solidFill")
    if solid_fill is not None:
        current_alpha = get_alpha_pct(solid_fill)
        if current_alpha is not None and current_alpha >= 100000:
            if add_alpha_to_color(solid_fill, target_alpha):
                return 1
    return 0


def fix_pptx(input_path, output_path, transparency_pct=1.0):
    """Fix font transparency in a PPTX file."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    stats = {"slides_modified": 0, "runs_modified": 0, "slides_total": 0}

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_output = os.path.join(tmpdir, "output.pptx")

        with zipfile.ZipFile(input_path, "r") as zin, \
             zipfile.ZipFile(tmp_output, "w", zipfile.ZIP_DEFLATED) as zout:

            for item in zin.infolist():
                data = zin.read(item.filename)

                if (item.filename.startswith("ppt/slides/slide") and
                        item.filename.endswith(".xml")):
                    stats["slides_total"] += 1
                    new_data, count = process_slide_xml(data, transparency_pct)
                    if count > 0:
                        stats["slides_modified"] += 1
                        stats["runs_modified"] += count
                        data = new_data

                zout.writestr(item, data)

        shutil.copy2(tmp_output, output_path)

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Fix font transparency in PPTX to ensure PDF export embeds fonts correctly."
    )
    parser.add_argument("input", help="Input PPTX file path")
    parser.add_argument("output", nargs="?", help="Output PPTX file path (default: input with _fixed suffix)")
    parser.add_argument(
        "--transparency", "-t", type=float, default=1.0,
        help="Transparency percentage to apply (default: 1%%)"
    )

    args = parser.parse_args()

    if not args.output:
        base, ext = os.path.splitext(args.input)
        args.output = f"{base}_fixed{ext}"

    print(f"Processing: {args.input}")
    print(f"Transparency: {args.transparency}%%")

    stats = fix_pptx(args.input, args.output, args.transparency)

    print(f"Output: {args.output}")
    print(f"Slides: {stats['slides_modified']}/{stats['slides_total']} modified")
    print(f"Text runs: {stats['runs_modified']} patched with {args.transparency}% transparency")


if __name__ == "__main__":
    main()
