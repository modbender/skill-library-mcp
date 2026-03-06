#!/usr/bin/env python3
"""
Fetch academic papers from Sci-Hub given a DOI.
"""

import sys
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

def clean_doi(doi):
    """Clean DOI string, removing https://doi.org/ prefix if present."""
    doi = doi.strip()
    # Remove common prefixes
    doi = re.sub(r'^https?://doi\.org/', '', doi)
    doi = re.sub(r'^doi:', '', doi, flags=re.IGNORECASE)
    return doi

def fetch_paper(doi, output_dir=".", sci_hub_domain="https://www.sci-hub.su"):
    """
    Fetch a paper from Sci-Hub given its DOI.
    
    Args:
        doi: Paper DOI (with or without https://doi.org/ prefix)
        output_dir: Directory to save PDF
        sci_hub_domain: Sci-Hub domain to use
    
    Returns:
        Path to downloaded PDF file, or None if failed
    """
    doi = clean_doi(doi)
    print(f"🔍 Fetching paper: {doi}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create filename from DOI
    safe_doi = doi.replace('/', '_').replace('\\', '_')
    pdf_filename = f"paper_{safe_doi}.pdf"
    pdf_path = output_path / pdf_filename
    temp_html = output_path / "temp_scihub.html"
    
    # Step 1: Fetch the Sci-Hub page
    sci_hub_url = f"{sci_hub_domain}/{doi}"
    print(f"   Loading: {sci_hub_url}")
    
    curl_cmd = [
        'curl', '-L', sci_hub_url,
        '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        '-o', str(temp_html),
        '-s'
    ]
    
    try:
        subprocess.run(curl_cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to fetch Sci-Hub page: {e}")
        return None
    
    # Step 2: Extract PDF URL from HTML
    try:
        html_content = temp_html.read_text()
    except Exception as e:
        print(f"❌ Failed to read HTML: {e}")
        return None
    
    # Look for PDF path in the HTML (Sci-Hub uses fetch('/storage/...pdf'))
    pdf_match = re.search(r"fetch\('(/storage/[^']+\.pdf)'", html_content)
    
    if not pdf_match:
        # Try alternative pattern (embed src)
        pdf_match = re.search(r'src="(/storage/[^"]+\.pdf)"', html_content)
    
    if not pdf_match:
        print(f"❌ Could not find PDF link in Sci-Hub page")
        print(f"   Check manually: {sci_hub_url}")
        temp_html.unlink()
        return None
    
    pdf_path_on_scihub = pdf_match.group(1)
    pdf_url = f"{sci_hub_domain}{pdf_path_on_scihub}"
    
    print(f"   Found PDF: {pdf_path_on_scihub}")
    
    # Step 3: Download the PDF
    curl_cmd = [
        'curl', '-L', pdf_url,
        '-H', 'User-Agent: Mozilla/5.0',
        '-o', str(pdf_path),
        '-s'
    ]
    
    try:
        subprocess.run(curl_cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download PDF: {e}")
        temp_html.unlink()
        return None
    
    # Clean up temp file
    temp_html.unlink()
    
    # Verify PDF was downloaded
    if pdf_path.exists() and pdf_path.stat().st_size > 0:
        size_kb = pdf_path.stat().st_size / 1024
        print(f"✅ Downloaded: {pdf_filename} ({size_kb:.1f} KB)")
        return pdf_path
    else:
        print(f"❌ Download failed or file is empty")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fetch_paper.py <DOI> [output_dir]")
        print("\nExample:")
        print("  fetch_paper.py 10.1038/nature12345")
        print("  fetch_paper.py https://doi.org/10.1016/j.cell.2023.01.001 ./papers/")
        sys.exit(1)
    
    doi = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    result = fetch_paper(doi, output_dir)
    
    if result:
        print(f"\n📁 Saved to: {result}")
        sys.exit(0)
    else:
        sys.exit(1)
