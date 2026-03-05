#!/usr/bin/env python3
"""
Debug script to inspect ELBA page state when stuck.
Connects to existing browser session and dumps DOM.
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def _state_root() -> Path:
    new = Path.home() / ".openclaw" / "raiffeisen-elba"
    legacy = Path.home() / ".moltbot" / "raiffeisen-elba"
    return legacy if legacy.exists() and not new.exists() else new

PROFILE_DIR = _state_root() / ".pw-profile"

def main():
    if not PROFILE_DIR.exists():
        print("ERROR: No browser session found.")
        sys.exit(1)
    
    print("Connecting to browser session...")
    
    with sync_playwright() as p:
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=False,
                viewport={"width": 1280, "height": 800}
            )
            
            # Get the first page
            pages = context.pages
            if not pages:
                print("ERROR: No pages found in browser session.")
                sys.exit(1)
            
            page = pages[0]
            
            print(f"\nCurrent URL: {page.url}")
            print(f"Page title: {page.title()}")
            
            # Get page content
            print("\n" + "="*60)
            print("PAGE HTML:")
            print("="*60)
            html = page.content()
            print(html)
            print("="*60)
            
            # Get visible text
            print("\n" + "="*60)
            print("VISIBLE TEXT:")
            print("="*60)
            try:
                body_text = page.locator('body').inner_text()
                print(body_text[:2000])  # First 2000 chars
            except Exception as e:
                print(f"Could not get body text: {e}")
            print("="*60)
            
            # Check for specific elements
            print("\n" + "="*60)
            print("ELEMENT CHECKS:")
            print("="*60)
            
            # Check for dok-row-item
            doc_rows = page.locator('dok-row-item').count()
            print(f"dok-row-item count: {doc_rows}")
            
            # Check for date filters
            from_date = page.locator('input[formcontrolname="fromDate"]').count()
            to_date = page.locator('input[formcontrolname="toDate"]').count()
            print(f"Date filter inputs: from={from_date}, to={to_date}")
            
            # Check for loading indicators
            loading = page.locator('[class*="loading"]').count()
            spinner = page.locator('[class*="spinner"]').count()
            print(f"Loading indicators: loading={loading}, spinner={spinner}")
            
            print("="*60)
            
            context.close()
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    main()
