import argparse
import sys
import time
from playwright.sync_api import sync_playwright

def browse(url, action, visible=False):
    print(f"\n🌍 INITIALIZING CLAW BROWSER...")
    print(f"🎯 TARGET: {url}")
    print(f"👀 MODE: {'VISIBLE' if visible else 'HEADLESS'}")
    
    with sync_playwright() as p:
        # slow_mo=1000 makes it easier to watch in videos
        browser = p.chromium.launch(headless=not visible, slow_mo=1000)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()
        
        try:
            print("🚀 Navigating to page...")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Wait for dynamic content
            time.sleep(2)

            if action == "read":
                print("📖 Reading content...")
                title = page.title()
                
                # Extract body text and clean up
                content = page.evaluate("document.body.innerText")
                clean_content = ' '.join(content.split())[:5000] 
                
                print(f"\n{'='*20} PAGE REPORT {'='*20}")
                print(f"TITLE: {title}")
                print(f"SUMMARY:\n{clean_content}...")
                print(f"{'='*50}\n")

            elif action == "screenshot":
                filename = "evidence.png"
                page.screenshot(path=filename)
                print(f"📸 Screenshot captured: {filename}")

        except Exception as e:
            print(f"❌ BROWSER ERROR: {e}")
        finally:
            print("🔒 Closing browser session.")
            browser.close()

def main():
    parser = argparse.ArgumentParser(description="Claw Browser Tool using Playwright")
    parser.add_argument("--url", required=True, help="URL to visit")
    parser.add_argument("--action", choices=["read", "screenshot"], default="read", help="Action to perform")
    parser.add_argument("--visible", action="store_true", help="Show browser UI (requires GUI/XServer)")
    
    args = parser.parse_args()
    
    browse(args.url, args.action, visible=args.visible)

if __name__ == "__main__":
    main()