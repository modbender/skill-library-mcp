#!/usr/bin/env python3
"""
MinerU PDF Parser with Persistent Output
Wrapper for MinerU MCP that preserves generated files.

Usage: python /Users/lwj04/clawd/skills/mineru-pdf/parse.py <pdf_path> <output_dir> [options]

Or from OpenClaw:
bash command="python /Users/lwj04/clawd/skills/mineru-pdf/parse.py <pdf_path> <output_dir> [options]"
"""
import asyncio
import argparse
import sys
from pathlib import Path


async def parse_pdf(pdf_path: str, output_dir: str,
                  backend: str = "pipeline",
                  formula_enable: bool = True,
                  table_enable: bool = True,
                  start_page: int = 0,
                  end_page: int = -1) -> int:
    """
    Parse PDF with MinerU and save to persistent output directory.

    Args:
        pdf_path: Path to PDF file
        output_dir: Where to save generated files (will be created if needed)
        backend: Processing backend (pipeline, vlm-mlx-engine, vlm-transformers)
        formula_enable: Whether to enable formula recognition
        table_enable: Whether to enable table recognition
        start_page: Starting page (0-indexed)
        end_page: Ending page (-1 for all pages)

    Returns:
        0 on success, 1 on error
    """
    # Import MinerU
    from mineru.cli.common import aio_do_parse

    # Validate input
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return 1

    if not pdf_path.suffix.lower() == '.pdf':
        print(f"❌ Error: Not a PDF file: {pdf_path}")
        return 1

    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📖 PDF: {pdf_path}")
    print(f"📁 Output: {output_dir}")
    print(f"⚙️  Backend: {backend}")
    print(f"   Formula: {'✅' if formula_enable else '❌'}")
    print(f"   Table: {'✅' if table_enable else '❌'}")
    print(f"   Pages: {start_page} → {end_page if end_page >= 0 else 'end'}")
    print()

    # Read PDF
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    pdf_name = pdf_path.stem

    # Parse with MinerU
    try:
        await aio_do_parse(
            output_dir=str(output_dir),
            pdf_file_names=[pdf_name],
            pdf_bytes_list=[pdf_bytes],
            p_lang_list=["ch", "en"],  # Chinese + English
            backend=backend,
            parse_method="auto",
            formula_enable=formula_enable,
            table_enable=table_enable,
            server_url=None,
            f_draw_layout_bbox=False,
            f_draw_span_bbox=False,
            f_dump_md=True,
            f_dump_middle_json=False,
            f_dump_model_output=False,
            f_dump_orig_pdf=False,
            f_dump_content_list=False,
            start_page_id=start_page,
            end_page_id=end_page if end_page >= 0 else 99999,
        )
    except Exception as e:
        print(f"❌ Error during parsing: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Find generated files
    parse_method = "vlm" if backend.startswith("vlm") else "auto"
    md_file = output_dir / pdf_name / parse_method / f"{pdf_name}.md"

    if md_file.exists():
        print(f"✅ Parsing completed successfully!")
        print(f"📄 Markdown: {md_file}")
        print(f"📊 Size: {md_file.stat().st_size:,} bytes")

        # Also save a copy to root of output_dir for easier access
        copy_path = output_dir / f"{pdf_name}_parsed.md"
        copy_path.write_text(md_file.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"📋 Copy: {copy_path}")

        # List generated images
        images_dir = md_file.parent / "images"
        if images_dir.exists():
            images = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
            print(f"🖼️  Images: {len(images)} files in {images_dir}")
            for img in images[:5]:  # Show first 5
                print(f"      - {img.name}")
            if len(images) > 5:
                print(f"      ... and {len(images) - 5} more")

        print()
        print(f"📂 Output directory structure:")
        print(f"   {output_dir}/")
        print(f"   ├── {pdf_name}/")
        print(f"   │   └── {parse_method}/")
        print(f"   │       ├── {pdf_name}.md")
        print(f"   │       └── images/")
        print(f"   └── {pdf_name}_parsed.md")

        return 0
    else:
        print(f"❌ Error: Failed to generate markdown output")
        print(f"   Expected: {md_file}")
        print(f"   Output directory contents:")
        if output_dir.exists():
            for item in sorted(output_dir.rglob("*")):
                if item.is_file():
                    print(f"      - {item.relative_to(output_dir)}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="MinerU PDF Parser with Persistent Output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse entire PDF
  python parse.py document.pdf ./output

  # Parse specific pages (1-3, 0-indexed)
  python parse.py document.pdf ./output --start-page 0 --end-page 2

  # Use Apple Silicon optimization
  python parse.py document.pdf ./output --backend vlm-mlx-engine

  # Text only (faster, no tables/formulas)
  python parse.py document.pdf ./output --no-table --no-formula
        """
    )

    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("output_dir", help="Output directory (will be created if needed)")

    parser.add_argument("--backend", default="pipeline",
                        choices=["pipeline", "vlm-mlx-engine", "vlm-transformers"],
                        help="Processing backend (default: pipeline)")
    parser.add_argument("--no-formula", action="store_false", dest="formula_enable",
                        help="Disable formula recognition (faster)")
    parser.add_argument("--no-table", action="store_false", dest="table_enable",
                        help="Disable table recognition (faster)")
    parser.add_argument("--start-page", type=int, default=0,
                        help="Start page (0-indexed, default: 0)")
    parser.add_argument("--end-page", type=int, default=-1,
                        help="End page (default: -1 for all pages)")

    args = parser.parse_args()

    return asyncio.run(parse_pdf(
        pdf_path=args.pdf_path,
        output_dir=args.output_dir,
        backend=args.backend,
        formula_enable=args.formula_enable,
        table_enable=args.table_enable,
        start_page=args.start_page,
        end_page=args.end_page
    ))


if __name__ == "__main__":
    sys.exit(main())
