#!/usr/bin/env python3
"""
Generate LLM cost report image with smart cropping.
Usage: python3 generate_report_image.py [--today|--yesterday|--period week|month]
"""
import argparse
import os
import sys
from pathlib import Path

# Add scripts dir to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from html2image import Html2Image
from PIL import Image
from fetch_usage import UsageStore
from datetime import datetime, timedelta


def generate_image(start_date: str = None, end_date: str = None, output_path: str = None):
    """Generate cost report image with smart cropping."""
    
    # Default: today
    if not start_date:
        today = datetime.now()
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    
    # Use script directory as working dir
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Determine trusted output directory
    # 1. User provided output_path
    # 2. OPENCLAW_WORKSPACE environment variable
    # 3. Project root (parent of script_dir)
    workspace = os.environ.get("OPENCLAW_WORKSPACE")
    project_root = script_dir.parent
    
    if output_path:
        final_output_path = Path(output_path)
    elif workspace:
        final_output_path = Path(workspace) / "llm-cost-report.png"
    else:
        final_output_path = project_root / "llm-cost-report.png"
    
    # Temporary files for processing
    # Use the same directory as final output for intermediate files to stay in "trusted" zone
    output_dir = final_output_path.parent
    html_path = output_dir / "llm-cost-report.html"
    raw_png_path = output_dir / "llm-cost-report-raw.png"
    
    print(f"Generating report for {start_date} ~ {end_date}")
    
    # Fetch data
    store = UsageStore()
    data = store.get_daily_summary(start_date, end_date)
    
    if not data:
        print("No data found for the specified period")
        return None
    
    # Import here to generate HTML
    from html_report import generate_html_report
    html = generate_html_report(store, start_date, end_date)
    
    # Save HTML
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML saved to {html_path}")
    
    # Generate image with html2image
    hti = Html2Image()
    hti.output_path = str(output_dir)
    # High-resolution PPT viewport (1440p style ratio, increased height for safety)
    hti.size = (1200, 1000) 
    hti.screenshot(url=str(html_path), save_as=raw_png_path.name)
    
    # Verify raw image was created
    if not raw_png_path.exists() or raw_png_path.stat().st_size < 100:
        print(f"Error: Failed to generate raw image at {raw_png_path}")
        return None

    # Smart crop: detect content bounds
    try:
        img = Image.open(raw_png_path)
        w, h = img.size
        data = img.load()
        bg = data[0, 0]  # Background color from top-left
        
        # Find content bounds
        # Use a slightly lower threshold to catch subtle text/borders at the bottom
        threshold = 5
        top, bottom, left, right = h, 0, w, 0
        for y in range(h):
            for x in range(w):
                p = data[x, y]
                if abs(p[0]-bg[0]) > threshold or abs(p[1]-bg[1]) > threshold or abs(p[2]-bg[2]) > threshold:
                    top, bottom = min(top, y), max(bottom, y)
                    left, right = min(left, x), max(right, x)
        
        # Crop with generous padding to ensure rounded corners and shadows are visible
        padding_x = 40
        padding_y = 50
        left = max(0, left - padding_x)
        top = max(0, top - padding_y)
        right = min(w, right + padding_x)
        bottom = min(h, bottom + padding_y)
        
        cropped = img.crop((left, top, right, bottom))
        
        # Save to final path
        cropped.save(final_output_path)
    except Exception as e:
        print(f"Error during image processing: {e}")
        return None
    finally:
        # Cleanup temp files
        if html_path.exists(): html_path.unlink()
        if raw_png_path.exists(): raw_png_path.unlink()
    
    # Final validation
    if not final_output_path.exists() or final_output_path.stat().st_size < 100:
        print(f"Error: Final image missing or invalid at {final_output_path}")
        return None

    final_w = right - left
    final_h = bottom - top
    print(f"Generated: {final_w}x{final_h} -> {final_output_path}")
    
    return str(final_output_path)


def main():
    parser = argparse.ArgumentParser(description="Generate LLM cost report image")
    parser.add_argument("--today", action="store_true", help="Today's report")
    parser.add_argument("--yesterday", action="store_true", help="Yesterday's report")
    parser.add_argument("--period", choices=["week", "month"], help="Period: week or month")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    parser.add_argument("--output", "-o", help="Output path")
    
    args = parser.parse_args()
    
    today = datetime.now()
    
    if args.today:
        start = end = today.strftime("%Y-%m-%d")
    elif args.yesterday:
        yesterday = today - timedelta(days=1)
        start = end = yesterday.strftime("%Y-%m-%d")
    elif args.period == "week":
        start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
    elif args.period == "month":
        start = today.replace(day=1).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
    elif args.start and args.end:
        start, end = args.start, args.end
    else:
        # Default: this month
        start = today.replace(day=1).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    res = generate_image(start, end, args.output)
    if not res:
        sys.exit(1)


if __name__ == "__main__":
    main()
