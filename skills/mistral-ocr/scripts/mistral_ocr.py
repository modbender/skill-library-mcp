#!/usr/bin/env python3
"""
Mistral OCR Tool - Convert PDF/images to Markdown/JSON/HTML

Usage:
    1. Set API key: export MISTRAL_API_KEY=your_api_key
    2. Run: python3 mistral_ocr.py -i input.pdf -f markdown

Get API key: https://console.mistral.ai/home
"""

from mistralai import Mistral
from pathlib import Path
import base64
import os
import argparse
import json


MISTRAL_API_URL = "https://console.mistral.ai/home"


def get_api_key():
    """Get API Key from environment variable."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("""
[!] Error: MISTRAL_API_KEY environment variable is not set.

To use this tool, you need a Mistral API key:

1. Visit: https://console.mistral.ai/home
2. Sign up/Login and create an API key
3. Set the environment variable:
   
   export MISTRAL_API_KEY=your_api_key

For permanent setup, add the line above to your ~/.zshrc or ~/.bashrc
        """)
        raise SystemExit(1)
    return api_key


def replace_html_entities(text):
    """Replace HTML entities with regular characters (for Typora compatibility)."""
    replacements = {
        "&gt;": ">",
        "&lt;": "<",
        "&amp;": "&",
        "&quot;": '"',
        "&#39;": "'",
        "&nbsp;": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def save_images_from_page(page, images_dir, page_num):
    """Save images from page and return modified markdown."""
    page_images = {}
    
    for img in page.images:
        try:
            # Parse base64 data
            if "," in img.image_base64:
                img_data = base64.b64decode(img.image_base64.split(',')[1])
            else:
                img_data = base64.b64decode(img.image_base64)
            
            img_path = images_dir / f"page{page_num}_{img.id}.png"
            with open(img_path, 'wb') as f:
                f.write(img_data)
            page_images[img.id] = str(img_path)
        except Exception as e:
            print(f"[!] Failed to save image: {e}")
    
    # Replace image paths in markdown
    page_md = page.markdown
    for img_id, img_path in page_images.items():
        page_md = page_md.replace(f"![{img_id}]({img_id})", f"![{img_id}]({img_path})")
        page_md = page_md.replace(f"]({img_id})", f"]({img_path})")
    
    return page_md


def process_pdf(input_path, output_format="markdown", output_dir=None):
    """Process PDF file."""
    input_path = Path(input_path)
    
    if output_dir is None:
        output_dir = Path.cwd() / "ocr_result"
    else:
        output_dir = Path(output_dir)
    
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    client = Mistral(api_key=get_api_key())
    
    print(f"[*] Processing: {input_path.name}")
    
    # Upload file
    uploaded_file = client.files.upload(
        file={
            "file_name": input_path.stem,
            "content": input_path.read_bytes(),
        },
        purpose="ocr",
    )
    
    # Get signed URL
    signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
    
    # OCR processing
    result = client.ocr.process(
        document={"document_url": signed_url.url},
        model="mistral-ocr-latest",
        include_image_base64=True
    )
    
    print(f"[*] Total pages: {len(result.pages)}")
    
    if output_format == "markdown":
        all_markdown = []
        for i, page in enumerate(result.pages):
            page_md = save_images_from_page(page, images_dir, i + 1)
            page_md = replace_html_entities(page_md)
            all_markdown.append(page_md)
        
        output_path = output_dir / "result.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(all_markdown))
        print(f"[+] Markdown saved: {output_path}")
        
    elif output_format == "json":
        output_data = []
        for i, page in enumerate(result.pages):
            page_md = save_images_from_page(page, images_dir, i + 1)
            page_md = replace_html_entities(page_md)
            output_data.append({
                "page": i + 1,
                "markdown": page_md,
                "images": [img.id for img in page.images]
            })
        
        output_path = output_dir / "result.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"[+] JSON saved: {output_path}")
        
    elif output_format == "html":
        all_html = []
        for i, page in enumerate(result.pages):
            page_md = save_images_from_page(page, images_dir, i + 1)
            page_md = replace_html_entities(page_md)
            all_html.append(f"<div class='page'><h2>Page {i+1}</h2>{page_md}</div>")
        
        html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>{input_path.stem}</title></head>
<body>{"".join(all_html)}</body>
</html>"""
        
        output_path = output_dir / "result.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"[+] HTML saved: {output_path}")
    
    print(f"[*] Images saved: {images_dir}")
    return output_dir


def main():
    parser = argparse.ArgumentParser(
        description="Mistral OCR - Convert PDF/images to Markdown/JSON/HTML"
    )
    parser.add_argument("-i", "--input", required=True, help="Input file path")
    parser.add_argument("-f", "--format", choices=["markdown", "json", "html"], 
                       default="markdown", help="Output format")
    parser.add_argument("-o", "--output", help="Output directory")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"[!] File not found: {args.input}")
        return
    
    process_pdf(args.input, args.format, args.output)


if __name__ == "__main__":
    main()
